# -*- coding: utf-8 -*-
"""
تثبيت وإزالة تطبيقات متجر علي جدي **خارج واجهة المنصّة** — معيار Ali12 / store_consent_v2.

الاستخدام (من جذر المستودع):
  python scripts/ali12_store_install.py list
  python scripts/ali12_store_install.py install dental_assistant
  python scripts/ali12_store_install.py install euqid --parent "D:\\مسار\\أب"
  python scripts/ali12_store_install.py uninstall dental_assistant

التثبيت الافتراضي: مجلد «تطبيقات علي جدي» على سطح المكتب (أو ALIJADDI_APPS_ROOT).
تحديثات الإصدارات: تظهر في متجر المنصّة بعد مزامنة السجل؛ إعادة تشغيل نفس أمر install تستبدل المجلد.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.addon_manager import (  # noqa: E402
    install_model_sync,
    load_installed,
    uninstall_model,
)
from services.model_catalog import load_qt_models  # noqa: E402
from services.paths import apps_root  # noqa: E402
from services.platform_store import PLATFORM_STORE_ID  # noqa: E402
from services.store_install_standard import STORE_INSTALL_CONTRACT_VERSION  # noqa: E402


def _find_model(model_id: str) -> dict | None:
    mid = (model_id or "").strip()
    for m in load_qt_models():
        if m.get("id") == mid:
            return m
    return None


def cmd_list() -> int:
    rows = load_qt_models()
    for m in sorted(rows, key=lambda x: x.get("id", "")):
        mid = m.get("id", "")
        if m.get("store_only"):
            continue
        print(f"{mid}\t{m.get('version', '')}\t{m.get('name', '')}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    mid = args.model_id.strip()
    if mid == PLATFORM_STORE_ID:
        print(
            "منصّة علي جدي تُحدَّث عبر مثبّت Windows (Setup.exe) أو ZIP — ليس عبر هذا الأمر.",
            file=sys.stderr,
        )
        return 2
    m = _find_model(mid)
    if not m:
        print(f"لم يُعثر على نموذج: {mid}", file=sys.stderr)
        return 1
    if not m.get("active", True):
        print("هذا التطبيق غير مفعّل في الكتالوج.", file=sys.stderr)
        return 1
    url = (m.get("download_url") or "").strip()
    if not url:
        print("لا يوجد رابط تنزيل في التعريف.", file=sys.stderr)
        return 1
    folder = (m.get("folder") or mid).strip()
    ver = (m.get("version") or "").strip() or "0"
    parent = Path(args.parent).expanduser().resolve() if args.parent else apps_root().resolve()
    name = (m.get("name") or mid).strip()

    def _prog(s: str) -> None:
        print(s, flush=True)

    ok, msg = install_model_sync(
        mid,
        url,
        folder,
        ver,
        display_name=name,
        apps_parent=parent,
        install_contract=STORE_INSTALL_CONTRACT_VERSION,
        on_progress=_prog,
    )
    print(msg)
    return 0 if ok else 1


def cmd_uninstall(args: argparse.Namespace) -> int:
    mid = args.model_id.strip()
    if mid == PLATFORM_STORE_ID:
        print("لا تُزال المنصّة بهذا الأمر.", file=sys.stderr)
        return 2
    m = _find_model(mid)
    if m:
        folder = (m.get("folder") or mid).strip()
    else:
        prev = load_installed().get(mid) or {}
        folder = (prev.get("folder") or mid).strip()
    ok, msg = uninstall_model(mid, folder)
    print(msg)
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Ali12 — تثبيت تطبيقات متجر علي جدي من سطر الأوامر")
    sub = ap.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="عرض معرفات التطبيقات المتاحة")
    p_list.set_defaults(func=lambda _a: cmd_list())

    p_in = sub.add_parser("install", help="تنزيل وتثبيت تطبيق")
    p_in.add_argument("model_id", help="معرف التطبيق (مثل dental_assistant)")
    p_in.add_argument(
        "--parent",
        help="مجلد الأب للتثبيت (افتراضي: حاضنة «تطبيقات علي جدي»)",
        default="",
    )
    p_in.set_defaults(func=cmd_install)

    p_un = sub.add_parser("uninstall", help="إزالة تطبيق مثبّت")
    p_un.add_argument("model_id")
    p_un.set_defaults(func=cmd_uninstall)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
