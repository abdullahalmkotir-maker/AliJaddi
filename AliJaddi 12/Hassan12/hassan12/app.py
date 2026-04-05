# -*- coding: utf-8 -*-
"""مدير الملفات Hassan12 — واجهة رئيسية."""

from __future__ import annotations

import json
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk

from ali12.export_ops import write_policy_bundle_zip, write_training_json
from hassan12.ai_advisor import advise, advise_operation
from hassan12.explorer_learn import (
    known_profile_folders,
    open_in_explorer,
    read_lnk_target,
    save_learned_bundle,
    snapshot_tree,
)
from hassan12.operations import PolicyError, execute_approved
from hassan12.policy_store import PendingRequest, PolicyStore, RequestKind
from hassan12.security_kb import merged_training_snippets
from hassan12.watcher import start_watching

APP_TITLE = "مدير الملفات Hassan12"


def repo_root() -> Path:
    """مجلد المشروع: .../AliJaddi 12/Hassan12"""
    return Path(__file__).resolve().parent.parent


def default_protected_root() -> Path:
    """المجلد المحمي افتراضياً: «مجلد_محمي» داخل مجلد المشروع (يُنشأ إن لم يوجد)."""
    r = repo_root()
    protected = r / "مجلد_محمي"
    protected.mkdir(parents=True, exist_ok=True)
    return protected


class Hassan12App:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.minsize(900, 580)
        self.root.geometry("1024x640")

        self.protected_root = default_protected_root()
        self.policy = PolicyStore(Path.home() / ".hassan12_policy")
        self.selected_path: Path | None = None
        self._observer = None

        self._build()
        self._refresh_tree()
        self._refresh_pending()

    def _is_inside_protected(self, p: Path) -> bool:
        try:
            p.resolve().relative_to(self.protected_root.resolve())
            return True
        except ValueError:
            return False

    def _build(self) -> None:
        top = ttk.Frame(self.root, padding=6)
        top.pack(fill=tk.X)

        ttk.Label(top, text="المجلد المحمي (الجذر):").pack(side=tk.RIGHT, padx=4)
        self.var_root = tk.StringVar(value=str(self.protected_root))
        ttk.Entry(top, textvariable=self.var_root, width=70).pack(
            side=tk.RIGHT, fill=tk.X, expand=True, padx=4
        )
        ttk.Button(top, text="تغيير الجذر...", command=self._pick_root).pack(
            side=tk.RIGHT, padx=2
        )
        ttk.Button(
            top,
            text="إنشاء مجلد محمي داخل المشروع",
            command=self._ensure_protected_subfolder,
        ).pack(side=tk.RIGHT, padx=2)

        nb = ttk.Notebook(self.root)
        nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        tab_files = ttk.Frame(nb)
        tab_queue = ttk.Frame(nb)
        tab_ai = ttk.Frame(nb)
        tab_kb = ttk.Frame(nb)
        tab_explorer = ttk.Frame(nb)
        tab_ali12 = ttk.Frame(nb)
        tab_apps = ttk.Frame(nb)

        nb.add(tab_files, text="الملفات والمجلدات")
        nb.add(tab_queue, text="طابور الموافقات")
        nb.add(tab_ai, text="مستشار ذكاء اصطناعي")
        nb.add(tab_kb, text="مكتبة سد الثغرات")
        nb.add(tab_explorer, text="المستكشف والتعلم")
        nb.add(tab_ali12, text="Ali12 — تثبيت وتصدير")
        nb.add(tab_apps, text="التطبيقات والإضافات")

        self._build_files_tab(tab_files)
        self._build_queue_tab(tab_queue)
        self._build_ai_tab(tab_ai)
        self._build_kb_tab(tab_kb)
        self._build_explorer_tab(tab_explorer)
        self._build_ali12_tab(tab_ali12)
        self._build_apps_tab(tab_apps)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_files_tab(self, parent: ttk.Frame) -> None:
        outer = ttk.Panedwindow(parent, orient=tk.HORIZONTAL)
        outer.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(outer, padding=4)
        right = ttk.Frame(outer, padding=4)
        outer.add(left, weight=2)
        outer.add(right, weight=1)

        self.tree = ttk.Treeview(left, columns=("type",), displaycolumns=(), show="tree")
        sy = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sy.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sy.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self._tree_item_to_path: dict[str, str] = {}

        self.lbl_sel = ttk.Label(right, text="لا يوجد تحديد", wraplength=320)
        self.lbl_sel.pack(anchor=tk.W, pady=4)

        bf = ttk.Frame(right)
        bf.pack(fill=tk.X, pady=6)
        ttk.Button(bf, text="طلب حذف (يتطلب موافقة)", command=self._request_delete).pack(
            fill=tk.X, pady=2
        )
        ttk.Button(bf, text="طلب نقل (يتطلب موافقة)", command=self._request_move).pack(
            fill=tk.X, pady=2
        )
        ttk.Button(
            bf, text="طلب إرسال/نسخ خارجي (يتطلب موافقة)", command=self._request_send
        ).pack(fill=tk.X, pady=2)
        ttk.Button(bf, text="تحديث الشجرة", command=self._refresh_tree).pack(fill=tk.X, pady=8)

        self.var_watch = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            right,
            text="مراقبة التغييرات (سجل فقط — pip install watchdog)",
            variable=self.var_watch,
            command=self._toggle_watch,
        ).pack(anchor=tk.W, pady=4)

        ttk.Label(
            right,
            text=(
                "لا يُنفَّذ الحذف أو النقل أو الإرسال مباشرة دون طابور الموافقات. "
                "المسار يجب أن يكون داخل الجذر المحمي."
            ),
            wraplength=340,
            foreground="#444",
        ).pack(anchor=tk.W, pady=8)

    def _build_queue_tab(self, parent: ttk.Frame) -> None:
        cols = ("kind", "source", "dest", "status", "reason")
        self.qtree = ttk.Treeview(parent, columns=cols, show="headings", height=16)
        titles = {
            "kind": "النوع",
            "source": "المصدر",
            "dest": "الوجهة",
            "status": "الحالة",
            "reason": "السبب",
        }
        for c in cols:
            self.qtree.heading(c, text=titles[c])
            self.qtree.column(c, width=160 if c != "source" else 220)
        sy = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.qtree.yview)
        self.qtree.configure(yscrollcommand=sy.set)
        self.qtree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        sy.pack(side=tk.RIGHT, fill=tk.Y, pady=4)

        bf = ttk.Frame(parent)
        bf.pack(fill=tk.X, padx=4, pady=4)
        ttk.Button(bf, text="تحديث القائمة", command=self._refresh_pending).pack(side=tk.RIGHT, padx=4)
        ttk.Button(bf, text="موافقة وتنفيذ", command=self._approve_and_run).pack(side=tk.RIGHT, padx=4)
        ttk.Button(bf, text="رفض الطلب", command=self._reject_selected).pack(side=tk.RIGHT, padx=4)

        self.qtree.bind("<Double-1>", lambda e: self._approve_and_run())

    def _build_ai_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent,
            text="اسأل عن إدارة الملفات، النسخ الاحتياطي، أو مخاطر فقدان البيانات.",
        ).pack(anchor=tk.W, padx=8, pady=4)
        self.ai_in = scrolledtext.ScrolledText(parent, height=5, wrap=tk.WORD)
        self.ai_in.pack(fill=tk.X, padx=8, pady=4)
        bf = ttk.Frame(parent)
        bf.pack(fill=tk.X, padx=8)
        self.var_net = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            bf,
            text="اتصال API (HASSAN12_AI_BASE و HASSAN12_AI_KEY)",
            variable=self.var_net,
        ).pack(side=tk.RIGHT)
        ttk.Button(bf, text="استشارة", command=self._run_ai).pack(side=tk.RIGHT, padx=6)
        self.ai_out = scrolledtext.ScrolledText(parent, height=18, wrap=tk.WORD)
        self.ai_out.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _build_kb_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent,
            text="عينات سياسات؛ التصدير يتم عبر Ali12.",
        ).pack(anchor=tk.W, padx=8, pady=4)
        self.kb_text = scrolledtext.ScrolledText(parent, height=22, wrap=tk.WORD)
        self.kb_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self._reload_kb_view()
        bf = ttk.Frame(parent)
        bf.pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(bf, text="تصدير JSON للتدريب (Ali12)", command=self._export_training).pack(
            side=tk.RIGHT
        )
        ttk.Button(bf, text="إعادة تحميل العرض", command=self._reload_kb_view).pack(
            side=tk.RIGHT, padx=6
        )

    def _reload_kb_view(self) -> None:
        data = merged_training_snippets(self.policy.base_dir)
        lines = [json.dumps(x, ensure_ascii=False, indent=2) for x in data]
        self.kb_text.delete("1.0", tk.END)
        self.kb_text.insert(tk.END, "\n\n".join(lines))

    def _build_apps_tab(self, parent: ttk.Frame) -> None:
        txt = (
            "إدارة البرامج والإضافات من إعدادات ويندوز والمتصفح.\n\n"
            "Hassan12 يحمي الملفات داخل الجذر المحمي بموافقات مسجّلة."
        )
        st = scrolledtext.ScrolledText(parent, height=14, wrap=tk.WORD)
        st.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        st.insert(tk.END, txt)
        st.config(state=tk.DISABLED)

        bf = ttk.Frame(parent)
        bf.pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(
            bf,
            text="فتح إعدادات التطبيقات",
            command=lambda: os.startfile("ms-settings:appsfeatures"),  # noqa: S606
        ).pack(side=tk.RIGHT)
        ttk.Button(
            bf,
            text="التطبيقات الافتراضية",
            command=lambda: os.startfile("ms-settings:defaultapps"),  # noqa: S606
        ).pack(side=tk.RIGHT, padx=6)

    def _export_training(self) -> None:
        path = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="حفظ ملف التدريب (Ali12)",
        )
        if not path:
            return
        try:
            write_training_json(self.policy.base_dir, Path(path))
        except OSError as e:
            messagebox.showerror(APP_TITLE, str(e))
            return
        messagebox.showinfo(APP_TITLE, "تم التصدير عبر Ali12.")

    def _export_bundle_zip(self) -> None:
        path = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".zip",
            filetypes=[("ZIP", "*.zip")],
            title="حفظ حزمة السياسات (Ali12)",
        )
        if not path:
            return
        try:
            write_policy_bundle_zip(self.policy.base_dir, Path(path))
        except OSError as e:
            messagebox.showerror(APP_TITLE, str(e))
            return
        messagebox.showinfo(APP_TITLE, "تم إنشاء الحزمة عبر Ali12.")

    def _build_ali12_tab(self, parent: ttk.Frame) -> None:
        proj = repo_root()
        intro = (
            f"موقع المشروع الحالي:\n{proj}\n\n"
            "Ali12 — التثبيت والتصدير.\n\n"
            "من الطرفية داخل هذا المجلد:\n"
            f"  cd \"{proj}\"\n"
            "  python run_ali12.py install\n"
            "  python run_ali12.py export-training --out تدريب.json\n"
            "  python run_ali12.py export-bundle --out حزمة.zip\n"
            "  python run_ali12.py generate-synthetic --out بيانات_10k.jsonl --count 10000\n\n"
            "أو نفّذ Install-Ali12.ps1 بعد الموافقة على مربع الحوار."
        )
        st = scrolledtext.ScrolledText(parent, height=12, wrap=tk.WORD)
        st.pack(fill=tk.X, padx=8, pady=4)
        st.insert(tk.END, intro)
        st.config(state=tk.DISABLED)

        bf = ttk.Frame(parent)
        bf.pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(bf, text="تصدير JSON للتدريب", command=self._export_training).pack(side=tk.RIGHT)
        ttk.Button(bf, text="تصدير ZIP", command=self._export_bundle_zip).pack(side=tk.RIGHT, padx=6)

        ttk.Label(
            parent,
            text=f"مجلد السياسات: {self.policy.base_dir}",
            wraplength=760,
        ).pack(anchor=tk.W, padx=8)

    def _build_explorer_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent,
            text="التكامل مع مستكشف الملفات وتعلّم هيكل المجلدات (أسماء فقط).",
            wraplength=780,
        ).pack(anchor=tk.W, padx=8, pady=6)

        bf = ttk.Frame(parent)
        bf.pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(bf, text="فتح المحمي في المستكشف", command=self._explorer_open_root).pack(
            side=tk.RIGHT, padx=4
        )
        ttk.Button(bf, text="فتح المحدد في المستكشف", command=self._explorer_open_selected).pack(
            side=tk.RIGHT, padx=4
        )

        bf2 = ttk.Frame(parent)
        bf2.pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(bf2, text="تعلّم من مجلد", command=self._learn_from_folder_dialog).pack(
            side=tk.RIGHT, padx=4
        )
        ttk.Button(bf2, text="تعلّم من مجلدات ويندوز المعروفة", command=self._learn_from_known_profile).pack(
            side=tk.RIGHT, padx=4
        )
        ttk.Button(bf2, text="استيراد File Explorer.lnk", command=self._learn_from_explorer_lnk).pack(
            side=tk.RIGHT, padx=4
        )

        self.ex_log = scrolledtext.ScrolledText(parent, height=16, wrap=tk.WORD)
        self.ex_log.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def _explorer_open_root(self) -> None:
        try:
            open_in_explorer(self.protected_root.resolve(), select=False)
        except OSError as e:
            messagebox.showerror(APP_TITLE, str(e))

    def _explorer_open_selected(self) -> None:
        p = self._require_selection()
        if not p:
            return
        try:
            open_in_explorer(p.resolve(), select=p.is_file())
        except OSError as e:
            messagebox.showerror(APP_TITLE, str(e))

    def _ex_msg(self, s: str) -> None:
        self.ex_log.insert(tk.END, s + "\n")
        self.ex_log.see(tk.END)

    def _learn_from_folder_dialog(self) -> None:
        d = filedialog.askdirectory(parent=self.root, title="مجلد للتعلم منه")
        if not d:
            return
        snap = snapshot_tree(Path(d), max_depth=2, max_nodes=200)
        path = save_learned_bundle(self.policy.base_dir, f"مجلد:{Path(d).name}", snap)
        self._ex_msg(f"حُفظ في: {path}")
        self._reload_kb_view()

    def _learn_from_known_profile(self) -> None:
        kf = known_profile_folders()
        shallow: dict = {"known_folders_snapshot": {}, "labels": list(kf.keys())}
        for label, pstr in list(kf.items())[:12]:
            shallow["known_folders_snapshot"][label] = snapshot_tree(
                Path(pstr), max_depth=1, max_nodes=50
            )
        path = save_learned_bundle(self.policy.base_dir, "مجلدات_ملف_ويندوز", shallow)
        self._ex_msg(f"حُفظ في: {path}")
        self._reload_kb_view()

    def _learn_from_explorer_lnk(self) -> None:
        candidates = [
            Path.home() / "OneDrive" / "Desktop" / "File Explorer.lnk",
            Path.home() / "Desktop" / "File Explorer.lnk",
        ]
        lnk: Path | None = None
        for c in candidates:
            if c.is_file():
                lnk = c
                break
        if lnk is None:
            lnk_str = filedialog.askopenfilename(
                parent=self.root,
                filetypes=[("اختصار", "*.lnk"), ("الكل", "*.*")],
                title="اختر File Explorer.lnk",
            )
            if not lnk_str:
                messagebox.showwarning(APP_TITLE, "لم يُعثر على الاختصار.")
                return
            lnk = Path(lnk_str)
        if not lnk.is_file():
            messagebox.showwarning(APP_TITLE, "مسار الاختصار غير صالح.")
            return
        target = read_lnk_target(lnk)
        if not target:
            messagebox.showwarning(APP_TITLE, "تعذر قراءة هدف الاختصار.")
            return
        tpath = Path(target)
        if tpath.is_dir():
            snap = snapshot_tree(tpath, max_depth=2, max_nodes=200)
            payload = {"lnk": str(lnk), "target": target, **snap}
        elif tpath.is_file():
            payload = {"lnk": str(lnk), "target": target, "note": "الهدف ملف"}
        else:
            payload = {"lnk": str(lnk), "target": target, "note": "الهدف غير موجود محلياً"}
        path = save_learned_bundle(self.policy.base_dir, "من_اختصار_Explorer", payload)
        self._ex_msg(f"الهدف: {target}\n{path}")
        try:
            if tpath.is_dir():
                open_in_explorer(tpath, select=False)
        except OSError:
            pass
        self._reload_kb_view()

    def _pick_root(self) -> None:
        d = filedialog.askdirectory(parent=self.root, title="اختر المجلد المحمي")
        if d:
            self.protected_root = Path(d)
            self.var_root.set(str(self.protected_root))
            self._refresh_tree()

    def _ensure_protected_subfolder(self) -> None:
        r = repo_root()
        p = r / "مجلد_محمي"
        p.mkdir(parents=True, exist_ok=True)
        self.protected_root = p
        self.var_root.set(str(p))
        self._refresh_tree()
        messagebox.showinfo(APP_TITLE, f"تم إنشاء/اختيار:\n{p}")

    def _on_tree_select(self, _e=None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        pth = self._tree_item_to_path.get(iid)
        if not pth:
            return
        p = Path(pth)
        self.selected_path = p
        self.lbl_sel.config(text=f"المحدد:\n{p}")

    def _refresh_tree(self) -> None:
        for x in self.tree.get_children():
            self.tree.delete(x)
        self._tree_item_to_path.clear()
        root = Path(self.var_root.get().strip())
        if not root.is_dir():
            self.protected_root = root
            return
        self.protected_root = root.resolve()
        r_id = str(self.protected_root)
        self.tree.insert(
            "",
            tk.END,
            iid=r_id,
            text=self.protected_root.name or str(self.protected_root),
            open=True,
        )
        self._tree_item_to_path[r_id] = str(self.protected_root)

        def add_children(node_id: str, folder: Path, depth: int) -> None:
            if depth > 6:
                return
            try:
                entries = sorted(folder.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            except PermissionError:
                return
            for ch in entries:
                if ch.name.startswith(".hassan12"):
                    continue
                cid = str(ch.resolve())
                self.tree.insert(
                    node_id,
                    tk.END,
                    iid=cid,
                    text=ch.name + ("/" if ch.is_dir() else ""),
                    open=False,
                )
                self._tree_item_to_path[cid] = cid
                if ch.is_dir():
                    add_children(cid, ch, depth + 1)

        add_children(r_id, self.protected_root, 0)

    def _require_selection(self) -> Path | None:
        if self.selected_path is None:
            messagebox.showwarning(APP_TITLE, "اختر عنصراً من الشجرة.")
            return None
        if not self._is_inside_protected(self.selected_path):
            messagebox.showerror(APP_TITLE, "المسار خارج المجلد المحمي.")
            return None
        return self.selected_path

    def _request_delete(self) -> None:
        p = self._require_selection()
        if not p:
            return
        reason = simpledialog.askstring(APP_TITLE, "سبب طلب الحذف:", parent=self.root)
        if not reason:
            messagebox.showwarning(APP_TITLE, "السبب مطلوب.")
            return
        msg = advise_operation("delete", str(p))
        if not messagebox.askyesno(APP_TITLE, msg + "\n\nتأكيد طلب الحذف؟"):
            return
        self.policy.enqueue(RequestKind.DELETE, p, None, reason)
        self._refresh_pending()
        messagebox.showinfo(APP_TITLE, "أُرسل الطلب إلى الطابور.")

    def _request_move(self) -> None:
        p = self._require_selection()
        if not p:
            return
        dst_root = filedialog.askdirectory(parent=self.root, title="وجهة النقل (ضمن المحمي)")
        if not dst_root:
            return
        dest = Path(dst_root) / p.name
        if not self._is_inside_protected(dest.parent) and not self._is_inside_protected(dest):
            messagebox.showerror(APP_TITLE, "وجهة النقل يجب أن تكون ضمن المحمي.")
            return
        reason = simpledialog.askstring(APP_TITLE, "سبب النقل:", parent=self.root)
        if not reason:
            return
        if not messagebox.askyesno(APP_TITLE, advise_operation("move", str(p)) + f"\n\nإلى:\n{dest}"):
            return
        self.policy.enqueue(RequestKind.MOVE, p, dest, reason)
        self._refresh_pending()

    def _request_send(self) -> None:
        p = self._require_selection()
        if not p:
            return
        if not messagebox.askyesno(APP_TITLE, "سيُنسخ المحتوى للوجهة. متابعة؟"):
            return
        dst = filedialog.askdirectory(parent=self.root, title="وجهة الإرسال")
        if not dst:
            return
        dest = Path(dst) / p.name
        dest_name = simpledialog.askstring(APP_TITLE, "اسم المُوافِق/المرسل:", parent=self.root)
        if not dest_name:
            return
        reason = simpledialog.askstring(APP_TITLE, "وصف الوجهة والغرض:", parent=self.root)
        if not reason:
            return
        reason = f"{dest_name}: {reason}"
        if not messagebox.askyesno(APP_TITLE, advise_operation("send", str(p)) + f"\n\nإلى:\n{dest}"):
            return
        self.policy.enqueue(RequestKind.SEND, p, dest, reason)
        self._refresh_pending()

    def _refresh_pending(self) -> None:
        for x in self.qtree.get_children():
            self.qtree.delete(x)
        for req in self.policy.list_pending():
            self.qtree.insert(
                "",
                tk.END,
                iid=req.id,
                values=(req.kind, req.source, req.destination, req.status, req.reason[:80]),
            )

    def _get_selected_queue_id(self) -> str | None:
        sel = self.qtree.selection()
        if not sel:
            messagebox.showwarning(APP_TITLE, "اختر صفاً في الطابور.")
            return None
        return sel[0]

    def _approve_and_run(self) -> None:
        rid = self._get_selected_queue_id()
        if rid is None:
            return
        raw = self.policy.get_request(rid)
        if not raw:
            return
        if raw.get("status") == "approved":
            req = PendingRequest(
                id=raw["id"],
                kind=raw["kind"],
                source=raw["source"],
                destination=raw.get("destination", ""),
                reason=raw.get("reason", ""),
                created_utc=raw.get("created_utc", ""),
                status="approved",
                approver=raw.get("approver", ""),
                approved_utc=raw.get("approved_utc", ""),
            )
        else:
            approver = simpledialog.askstring(APP_TITLE, "اسم الموافق:", parent=self.root)
            if not approver:
                return
            req = self.policy.approve(rid, approver)
            if req is None:
                messagebox.showerror(APP_TITLE, "تعذر الموافقة.")
                return

        if not messagebox.askyesno(APP_TITLE, "تنفيذ العملية الآن؟"):
            self._refresh_pending()
            return
        try:
            execute_approved(req)
        except (PolicyError, OSError) as e:
            messagebox.showerror(APP_TITLE, str(e))
            return
        self.policy.mark_done(req.id)
        self._refresh_pending()
        self._refresh_tree()
        messagebox.showinfo(APP_TITLE, "تم التنفيذ.")

    def _reject_selected(self) -> None:
        rid = self._get_selected_queue_id()
        if rid is None:
            return
        name = simpledialog.askstring(APP_TITLE, "اسم الرافض:", parent=self.root) or "unknown"
        note = simpledialog.askstring(APP_TITLE, "ملاحظة:", parent=self.root) or ""
        self.policy.reject(rid, name, note)
        self._refresh_pending()

    def _run_ai(self) -> None:
        text = self.ai_in.get("1.0", tk.END).strip()
        if not text:
            return
        self.ai_out.delete("1.0", tk.END)
        self.ai_out.insert(tk.END, advise(text, prefer_network=self.var_net.get()))

    def _toggle_watch(self) -> None:
        if self.var_watch.get():
            self._observer = start_watching(self.protected_root)
            if self._observer is None:
                self.var_watch.set(False)
                messagebox.showwarning(APP_TITLE, "ثبّت watchdog: pip install -r requirements.txt")
        else:
            if self._observer:
                self._observer.stop()
                self._observer.join(timeout=2)
                self._observer = None

    def _on_close(self) -> None:
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=2)
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    Hassan12App().run()


if __name__ == "__main__":
    main()
