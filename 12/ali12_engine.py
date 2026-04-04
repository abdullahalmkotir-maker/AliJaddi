# -*- coding: utf-8 -*-
"""
Ali12 — مساعد تثبيت وتشخيص أعطال **للنماذج والإضافات والتطبيقات** الموزّعة عبر منصّة علي جدّي.

**نطاق حالي (أقوى):** سطح المكتب — تثبيت المتجر عبر ``scripts/ali12_store_install.py`` (``store_consent_v2``، مدير تنزيلات ``~/.alijaddi/downloads``)، مثبّت المنصّة **Inno**، ZIP، تشغيل hosted، إزالة.
**قيد التوسّع:** جوال / PWA / غلاف — بذور التدريب في ``12/seeds/*_seed.jsonl`` (Ali12، Hassan12، Hussein12 عبر ``services/assistants_squad.py``).

محرّك **v2_weighted_jaccard:** قواعد مرجّحة + تداخل جاكارد (عربي/إنجليزي) + إشارات OS/مكدس؛ مخرجات جاهزة لـ JSONL دون تبعيات ثقيلة.
"""
from __future__ import annotations

import math
import re
import sys
from dataclasses import dataclass
from typing import Any, Callable, Optional

ALI12_ASSISTANT_ID = "Ali12"
ALI12_DISPLAY_AR = "علي 12"
ALI12_ENGINE_VERSION = "v2_weighted_jaccard"
# لا تُلحِق لاحقة «PATH/Python» على إجابات تثبيت المنصّة/المتجر/البناء (ضوضاء للمستخدم)
_HINT_NO_OS_STACK_SUFFIX = frozenset(
    {
        "platform_alijaddi_install",
        "platform_store_update",
        "store_install_folder",
        "release_tanzeel_build",
        "post_install_ux",
    }
)

# ─── تمثيل رياضي بسيط: تداخل جاكارد بين مجموعتين ───


def _token_set(text: str) -> set[str]:
    if not text:
        return set()
    return set(re.findall(r"[\w\u0600-\u06FF]+", text.lower()))


def jaccard_keywords(text: str, keywords: frozenset[str]) -> float:
    """تشابه جاكارد بين رموز النص والكلمات المفتاحية (معيّرة [0،1])."""
    words = _token_set(text)
    if not words or not keywords:
        return 0.0
    inter = words & keywords
    union = words | keywords
    return len(inter) / len(union) if union else 0.0


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ─── ملف تعريف المنصّة (أنظمة ولغات تشغيل) ───


def runtime_profile() -> dict[str, Any]:
    """لقطة متعددة المنصات للتدريب والتصحيح."""
    return {
        "os_family": sys.platform,
        "os_desc": __import__("platform").platform(),
        "machine": __import__("platform").machine(),
        "python_implementation": __import__("platform").python_implementation(),
        "python_version": sys.version.split()[0],
    }


def infer_stack_family(*text_parts: str) -> str:
    """استنتاج عائلة المكدس من أمر التشغيل أو السجل (توافق لغات/أدوات)."""
    t = " ".join(p for p in text_parts if p).lower()
    if "streamlit" in t:
        return "streamlit"
    if "npm" in t or "npx" in t or "node" in t:
        return "node"
    if "deno " in t or "deno run" in t:
        return "deno"
    if "cargo " in t or "rustc" in t:
        return "rust"
    if "go run" in t or "go build" in t:
        return "go"
    if "java " in t or "gradle" in t:
        return "jvm"
    if "python" in t or ".py" in t or "py " in t or "py -" in t:
        return "python"
    return "unknown"


def _os_hint_suffix(os_family: str) -> str:
    if os_family == "win32":
        return (
            " — **ويندوز:** تحقق من PATH لـ Python، واستثناء مجلد التطبيق مؤقتاً في Windows Security؛ "
            "جرّب `py -3` من مجلد المشروع."
        )
    if os_family == "darwin":
        return (
            " — **macOS:** جرّب من Terminal داخل مجلد التطبيق؛ راقب «الخصوصية والأمان» إن حُظر تنفيذ."
        )
    if os_family.startswith("linux"):
        return (
            " — **لينكس:** تثبيت `python3-venv` إن لزم؛ `chmod +x` للسكربتات؛ راقب صلاحيات المجلد."
        )
    return ""


def _stack_hint_suffix(stack: str) -> str:
    if stack == "streamlit":
        return " — **Streamlit:** `pip install streamlit` في بيئة المشروع؛ المنصّة تضيف `--server.headless` تلقائياً."
    if stack == "node":
        return " — **Node:** ثبّت LTS من nodejs.org؛ `npm install` داخل مجلد التطبيق إن وُجد package.json."
    if stack == "python":
        return " — **Python:** يفضّل `python -m venv .venv` ثم تفعيل البيئة وتثبيت requirements."
    return ""


@dataclass
class Ali12Context:
    event_kind: str
    message: str
    detail: dict[str, Any]
    msg_lower: str
    http: Optional[int]
    os_family: str
    stack: str
    combined_text: str


def _build_context(
    event_kind: str,
    message: str,
    detail: dict[str, Any],
) -> Ali12Context:
    d = detail or {}

    def _dump_snippet(obj: dict) -> str:
        try:
            import json as _j

            return _j.dumps(obj, ensure_ascii=False)[:400]
        except Exception:
            return ""

    msg_lower = f"{message} {d.get('error', '')}".lower()
    raw_http = d.get("http_status")
    try:
        http = int(raw_http) if raw_http is not None else None
    except (TypeError, ValueError):
        http = None
    cmd = str(d.get("launch_command", "") or d.get("command", "") or "")
    prof = runtime_profile()
    os_f = str(prof.get("os_family", ""))
    stack = infer_stack_family(cmd, message, _dump_snippet(d))

    mid = str(d.get("model_id", "") or "")
    combined = f"{msg_lower} {cmd} {_dump_snippet(d)} {mid}"
    return Ali12Context(
        event_kind=event_kind,
        message=message or "",
        detail=d,
        msg_lower=msg_lower,
        http=http,
        os_family=os_f,
        stack=stack,
        combined_text=combined,
    )


# ─── قواعد مرجّحة: دالة تعطي درجة ≥ 0 ───

RuleFn = Callable[[Ali12Context], float]


def _rule(
    rid: str,
    score_fn: RuleFn,
    hint_ar: str,
) -> tuple[str, RuleFn, str]:
    return (rid, score_fn, hint_ar)


def _default_rules() -> list[tuple[str, RuleFn, str]]:
    kw_zip = frozenset({"zip", "bad", "zipfile", "corrupt", "archive", "أرشيف"})
    kw_perm = frozenset({"permission", "denied", "access", "winerror", "errno", "رفض", "صلاحية"})
    kw_timeout = frozenset({"timeout", "timed", "out", "مهلة"})
    kw_ssl = frozenset({"ssl", "certificate", "tls", "cert", "شهادة"})
    kw_disk = frozenset({"no", "space", "enospc", "قرص", "مساحة"})
    kw_net = frozenset({"connection", "reset", "refused", "unreachable", "network", "اتصال"})

    def sc_no_url(ctx: Ali12Context) -> float:
        return 50.0 if ctx.event_kind == "install_no_url" else 0.0

    def sc_store_install_flow(ctx: Ali12Context) -> float:
        """تدفّق متجر (موافقة + مجلد أب) مثل Microsoft Store / Play — إلغاء الحوار أو المجلد أو صلاحيات."""
        ph = str(ctx.detail.get("phase", "") or "")
        if ph in ("folder_picker_cancelled", "consent_cancelled"):
            return 88.0
        flow = str(ctx.detail.get("install_flow", "") or "")
        if flow == "store_consent" and ph in (
            "folder_picker_cancelled",
            "consent_cancelled",
        ):
            return 88.0
        blob = f"{ctx.message} {ctx.combined_text}".lower()
        kw = frozenset(
            {
                "microsoft",
                "store",
                "google",
                "play",
                "مجلد",
                "موافقة",
                "صلاحية",
                "smartscreen",
                "تخزين",
                "folder_picker",
            }
        )
        s = 10.0 * jaccard_keywords(blob, kw)
        if "install_flow" in blob and "store" in blob:
            s += 8.0
        return s if s > 14.0 else 0.0

    def sc_platform_store_update(ctx: Ali12Context) -> float:
        """تحديث تطبيق المنصّة من متجر Qt مقابل سجل GitHub (`platform`)."""
        blob = f"{ctx.message} {ctx.combined_text}".lower()
        score = 8.0 * jaccard_keywords(
            blob,
            frozenset(
                {
                    "تحديث",
                    "منصة",
                    "المنصة",
                    "متجر",
                    "سجل",
                    "registry",
                    "github",
                    "releases",
                    "إصدار",
                    "اصدار",
                    "alijaddi_platform",
                }
            ),
        )
        for phrase in (
            "تحديث المنصة",
            "تحديث المنصّة",
            "من المتجر",
            "زر التحديث",
            "بطاقة المنصة",
            "صفحة الإصدارات",
            "تحديث علي",
            "platform_store",
        ):
            if phrase in blob:
                score += 26.0
        if "platform" in blob and ("تحديث" in blob or "update" in blob or "أحدث" in blob):
            score += 20.0
        mid = str(ctx.detail.get("model_id", "") or "").lower()
        if mid == "alijaddi_platform" and (
            "تحديث" in blob or "update" in blob or "store" in blob or "متجر" in blob
        ):
            score += 40.0
        return score if score > 24.0 else 0.0

    def sc_platform_alijaddi_install(ctx: Ali12Context) -> float:
        """منصّة علي جدّي: المعيار الرسمي مثبّت Inno (أسلوب Blender)؛ ZIP محمول مكمّل."""
        d = ctx.detail
        dist = str(d.get("distribution", "") or "").lower()
        if dist in ("inno_setup", "inno_blender_style"):
            return 97.0
        if str(d.get("product", "") or "").lower() == "alijaddi_platform":
            return 94.0
        if d.get("install_target") == "alijaddi_desktop":
            return 90.0
        blob = f"{ctx.message} {ctx.combined_text}".lower()
        if "لا أرى" in blob and "تنزيل" in blob:
            return 0.0
        inno_k = jaccard_keywords(
            blob,
            frozenset(
                {
                    "setup.exe",
                    "setup",
                    "inno",
                    "مثبت",
                    "قائمة ابدأ",
                    "برامج",
                    "ميزات",
                    "program files",
                    "uninstall",
                    "إزالة التثبيت",
                    "تطبيقات",
                }
            ),
        )
        strong = (
            "alijaddi.exe" in blob
            or "alijaddi-beta" in blob.replace(" ", "")
            or "alijaddi portable" in blob
            or "setup.exe" in blob
        )
        j = jaccard_keywords(
            blob,
            frozenset(
                {
                    "alijaddi",
                    "علي جدي",
                    "علي جدّي",
                    "منصة",
                    "بيتا",
                    "ويندوز",
                    "zip",
                    "smartscreen",
                    "فك",
                    "تشغيل",
                }
            ),
        )
        s = 18.0 * j + 22.0 * inno_k
        if strong:
            s += 42.0
        for phrase in (
            "كيف أثبت",
            "ثبت علي",
            "تثبيت المنصة",
            "منصة علي",
            "install alijaddi",
            "ملف setup",
            "مثبت علي",
        ):
            if phrase in blob:
                s += 14.0
        if "كيف أثبت" in blob and "منصة" in blob:
            s += 22.0
        if "setup" in blob and (
            "علي" in blob or "alijaddi" in blob or "منصة" in blob or "جدي" in blob
        ):
            s += 38.0
        if "euqid" in blob and "منصة" not in blob and "alijaddi" not in blob:
            s = min(s, 18.0)
        return s if s > 28.0 else 0.0

    def sc_http_404(ctx: Ali12Context) -> float:
        base = 40.0 if ctx.http == 404 or "404" in ctx.msg_lower else 0.0
        return base + 12.0 * jaccard_keywords(ctx.combined_text, frozenset({"404", "not", "found"}))

    def sc_http_403(ctx: Ali12Context) -> float:
        base = 38.0 if ctx.http == 403 or "403" in ctx.msg_lower else 0.0
        return base + 10.0 * jaccard_keywords(ctx.combined_text, frozenset({"403", "forbidden"}))

    def sc_http_5xx(ctx: Ali12Context) -> float:
        if ctx.http is not None and ctx.http >= 500:
            return 42.0 + min(5.0, ctx.http / 100.0)
        return 15.0 if "502" in ctx.msg_lower or "503" in ctx.msg_lower else 0.0

    def sc_zip(ctx: Ali12Context) -> float:
        return 35.0 * jaccard_keywords(ctx.combined_text, kw_zip) + (
            20.0 if "zip" in ctx.msg_lower else 0.0
        )

    def sc_perm(ctx: Ali12Context) -> float:
        j = jaccard_keywords(ctx.combined_text, kw_perm)
        bonus = 8.0 if ctx.os_family == "win32" else 5.0
        return 25.0 * j + bonus * j

    def sc_timeout(ctx: Ali12Context) -> float:
        return 28.0 * jaccard_keywords(ctx.combined_text, kw_timeout)

    def sc_ssl(ctx: Ali12Context) -> float:
        return 26.0 * jaccard_keywords(ctx.combined_text, kw_ssl)

    def sc_disk(ctx: Ali12Context) -> float:
        return 30.0 * jaccard_keywords(ctx.combined_text, kw_disk)

    def sc_net(ctx: Ali12Context) -> float:
        return 24.0 * jaccard_keywords(ctx.combined_text, kw_net)

    def sc_extract(ctx: Ali12Context) -> float:
        return 33.0 if ctx.detail.get("phase") == "extract" else 0.0

    def sc_release_tanzeel_help(ctx: Ali12Context) -> float:
        """لا تظهر حزمة البيتا تحت تنزيل — البناء لم يُشغَّل أو فشل قبل التعبئة."""
        blob = f"{ctx.message} {ctx.combined_text}".lower()
        if "تنزيل" not in blob and "dist" not in blob and "pyinstaller" not in blob and "pack_windows" not in blob:
            return 0.0
        score = 12.0 * jaccard_keywords(
            blob,
            frozenset({"تنزيل", "windows", "beta", "zip", "build", "dist", "بيتا", "setup"}),
        )
        if any(p in blob for p in ("لا أرى", "لماذا لا", "ليست", "مفقود", "missing", "empty", "غير موجود")):
            score += 28.0
        return score if score > 14.0 else 0.0

    def sc_euqid_contract_stack(ctx: Ali12Context) -> float:
        mid = str(ctx.detail.get("model_id", "") or "").lower()
        fol = str(ctx.detail.get("folder", "") or "").lower()
        if mid != "euqid" and fol != "euqid":
            return 0.0
        t = ctx.combined_text.lower()
        bonus = 0.0
        for needle in (
            "pywebview",
            "webview",
            "modulenotfound",
            "no module named",
            "fpdf",
            "docx",
            "arabic-reshaper",
            "badzipfile",
            "file is not a zip",
        ):
            if needle in t:
                bonus += 4.0
        j = jaccard_keywords(
            ctx.combined_text,
            frozenset({"pywebview", "webview", "module", "python", "pip", "requirements", "zip"}),
        )
        return 8.0 + bonus + 14.0 * j

    def sc_uninstall(ctx: Ali12Context) -> float:
        return 100.0 if ctx.event_kind == "uninstall_fail" else 0.0

    def sc_launch_empty(ctx: Ali12Context) -> float:
        return 100.0 if ctx.event_kind == "launch_fail" and ctx.detail.get("phase") == "empty_command" else 0.0

    def sc_launch_start(ctx: Ali12Context) -> float:
        if ctx.event_kind != "launch_fail":
            return 0.0
        if ctx.detail.get("phase") == "start_timeout":
            return 90.0
        # التتبع يمرّر message="" غالباً؛ combined_text يضم launch_command لالتقاط streamlit/node/python.
        return 15.0 * jaccard_keywords(
            ctx.combined_text,
            frozenset({"بدء", "تعذّر", "python", "streamlit", "node", "npm", "npx"}),
        )

    def sc_launch_exit(ctx: Ali12Context) -> float:
        if ctx.event_kind != "launch_fail":
            return 0.0
        ec = ctx.detail.get("exit_code")
        try:
            ecn = int(ec) if ec is not None else 0
        except (TypeError, ValueError):
            ecn = 0
        return 55.0 + min(20.0, float(abs(ecn))) if ecn != 0 else 0.0

    def sc_post_install_ux(ctx: Ali12Context) -> float:
        """بعد نجاح تثبيت من المتجر — أين الملفات وكيف التشغيل."""
        if ctx.event_kind != "install_ok":
            return 0.0
        d = ctx.detail
        if d.get("install_flow") == "store_folder_picker":
            return 24.0
        if d.get("apps_parent") or d.get("folder"):
            return 22.0
        return 6.0 * jaccard_keywords(ctx.combined_text, frozenset({"install", "folder", "ok", "تثبيت", "متجر"}))

    hints: list[tuple[str, RuleFn, str]] = [
        _rule(
            "install_no_url",
            sc_no_url,
            "لا يوجد رابط تحميل في السجل لهذا التطبيق. جرّب «تحديث السجل» أو انتظر رفع الإصدار على GitHub، "
            "أو انسخ المجلد يدوياً تحت مدير التنزيلات (.alijaddi/downloads) كما في الوثائق.",
        ),
        _rule(
            "platform_store_update",
            sc_platform_store_update,
            "**تحديث منصّة علي جدّي:** في **متجر التطبيقات** افتح بطاقة «علي جدي — المنصّة». إذا كان حقل **`platform`** في `addons/registry.json` على GitHub أحدث من إصدارك (`alijaddi.__version__`) يظهر زر التحديث → **صفحة إصدارات GitHub** لـ Setup.exe أو ZIP؛ أغلق المنصّة ثم ثبّت. **للمطوّر:** ارفع السجل مع تحديث `platform` ونسخة `alijaddi_platform`.",
        ),
        _rule(
            "store_install_folder",
            sc_store_install_flow,
            "**متجر المنصّة:** من الواجهة **«تنزيل وتثبيت»** على البطاقة (موافقة `store_consent_v2` + مجلد أب)، أو من الطرفية **Ali12:** `python scripts/ali12_store_install.py install <model_id>` — الافتراضي `.alijaddi/downloads` أو `--parent`. SmartScreen/مضاد فيروس: اسمح بالكتابة في المجلد.",
        ),
        _rule(
            "post_install_ux",
            sc_post_install_ux,
            "**بعد التثبيت:** الملفات في مجلد التطبيق تحت مدير التنزيلات أو المسار الذي اخترته. شغّل من «فتح التطبيق» في المنصّة أو من اختصار سطح المكتب إن وُجد.",
        ),
        _rule(
            "platform_alijaddi_install",
            sc_platform_alijaddi_install,
            "**منصّة ويندوز — معيار تطبيقات النظام:** `…-Setup.exe` من `تنزيل\\\\windows` → **Program Files** + قائمة ابدأ + إزالة من «التطبيقات». **مكمّل:** `…-Windows.zip` + `AliJaddi.exe`. "
            "UAC: وافق لـ Program Files. **بناء Setup:** Inno 6 (`ISCC` غالباً تحت `%LocalAppData%\\\\Programs\\\\Inno Setup 6` بعد winget)؛ `ALIJADDI_SKIP_INNO=1` للـZIP فقط. "
            "صامت: `/VERYSILENT /SUPPRESSMSGBOXES`. **تحديث المنصّة:** بطاقة المنصّة في المتجر + Releases؛ **تطبيقات المتجر:** زر «تنزيل وتثبيت» أو **Ali12 CLI**؛ مدير التنزيلات الافتراضي.",
        ),
        _rule(
            "http_404",
            sc_http_404,
            "الرابط غير موجود (404). قد يكون الملف أعيد تسميته على الإصدارات: افتح صفحة الإصدارات للمشروع وحدّث الـ manifest.",
        ),
        _rule(
            "http_403",
            sc_http_403,
            "الوصول مرفوض (403). تحقق من الشبكة أو VPN؛ إن استمرّ الأمر قد يكون الرابط خاصاً أو منتهي الصلاحية.",
        ),
        _rule(
            "http_5xx",
            sc_http_5xx,
            "خطأ من الخادم (5xx). أعد المحاولة لاحقاً؛ إن تكرّر، أبلغ الدعم مع وقت المحاولة.",
        ),
        _rule(
            "zip_corrupt",
            sc_zip,
            "ملف التحميل قد يكون تالفاً أو ليس ZIP صالحاً. امسح مجلد التثبيت الجزئي وأعد التنزيل؛ راقب مضاد الفيروسات أثناء الفك.",
        ),
        _rule(
            "permission",
            sc_perm,
            "مشكلة صلاحيات أو ملف مقفول. أغلق التطبيق إن كان يعمل من نفس المجلد، وراجع صلاحيات المجلد على منصّتك.",
        ),
        _rule(
            "timeout",
            sc_timeout,
            "انتهت مهلة التحميل أو الاتصال. تحقق من الشبكة وأعد المحاولة عند ضغط أقل على الرابط.",
        ),
        _rule(
            "ssl_tls",
            sc_ssl,
            "مشكلة شهادة SSL/TLS أو اعتراض الشبكة. جرّب شبكة أخرى، أو حدّث النظام/المتصفح، أو راقب برامج الفحص الوسطية.",
        ),
        _rule(
            "disk_space",
            sc_disk,
            "قد لا تكفي مساحة القرص لفك الضغط أو النسخ. وفّر عدة غيغابايت فراغ ثم أعد التثبيت.",
        ),
        _rule(
            "network_generic",
            sc_net,
            "فشل شبكة أثناء التنزيل. تحقق من الاتصال وجدار الحماية ثم أعد المحاولة.",
        ),
        _rule(
            "extract_phase",
            sc_extract,
            "فشل فك الضغط أو النسخ. تأكد من وجود مساحة كافية ومسار مدير التنزيلات صالح (.alijaddi/downloads أو ALIJADDI_APPS_ROOT).",
        ),
        _rule(
            "release_tanzeel_build",
            sc_release_tanzeel_help,
            "**تنزيل\\\\windows** يُملأ بالبناء فقط: **ZIP** [4/5] و**Setup.exe** [5/5] (يتطلب Inno 6 ما لم يُضبط `ALIJADDI_SKIP_INNO=1`). ليس بتغيير رقم البيتا في الملفات وحدها. "
            "من الجذر: **build_windows.bat** أو `powershell -File scripts\\\\build_windows_release.ps1` — أولاً **dist\\\\AliJaddi** (PyInstaller) ثم التعبئة. راجع خرج الطرفية إن توقف قبل [4/5] أو [5/5].",
        ),
        _rule(
            "euqid_contract_python_stack",
            sc_euqid_contract_stack,
            "تطبيق **عقد (Euqid)** يعتمد على Python وواجهة سطح مكتب (pywebview وحزم المستندات): من مجلد Euqid أنشئ بيئة `python -m venv .venv`، فعّلها، ثم `pip install -r requirements.txt` (أو ثبّت الحزم المذكورة في manifest). على ويندوز إن ظهر خطأ متعلق بـ WebView ثبّت **WebView2 Runtime** من Microsoft؛ إن استمرّ الخطأ انسخ كامل السجل من الطرفية.",
        ),
        _rule(
            "uninstall_fail",
            sc_uninstall,
            "تعذّرت الإزالة: قد يكون ملف مفتوحاً من تطبيق آخر. أغلق جميع النوافذ، ثم أعد المحاولة أو احذف المجلد يدوياً ثم حدّث المتجر.",
        ),
        _rule(
            "launch_empty_command",
            sc_launch_empty,
            "أمر التشغيل غير معرّف في manifest التطبيق. حدّث التطبيق من المتجر أو أبلغ مطوّر النموذج.",
        ),
        _rule(
            "launch_start_failed",
            sc_launch_start,
            "لم يبدأ البرنامج — ثبّت المفسّر/الأداة المطلوبة (Python، Streamlit، Node…) واضبط PATH؛ جرّب نفس الأمر من الطرفية داخل مجلد التطبيق.",
        ),
        _rule(
            "launch_nonzero_exit",
            sc_launch_exit,
            "انتهى التشغيل برمز خروج غير صفري. راجع السجل من الطرفية أو من التطبيق؛ غالباً نقص حزمة أو خطأ في السكربت — يُدرَّج ذلك لتدريب Ali12 (مجلد 12) على منصّة علي جدّي.",
        ),
    ]
    return hints


def resolve_ali12(
    *,
    event_kind: str,
    message: str = "",
    detail: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    يحلّ المشهد ويُرجع أفضل اقتراح + ثقة تقريبية + إشارات للتدريب/التحليل.
    """
    ctx = _build_context(event_kind, message, detail or {})
    rules = _default_rules()
    scored: list[tuple[str, float, str]] = []
    for rid, fn, hint in rules:
        s = float(fn(ctx))
        if s > 0:
            scored.append((rid, s, hint))

    scored.sort(key=lambda x: x[1], reverse=True)

    fallback = (
        "أعد المحاولة من «متجر التطبيقات». إن استمرّ الأمر، انسخ الرسالة والسجل — "
        "منصّة علي جدّي تجمع هذه الأنماط لتصحيح Ali12 ولاحقاً تدريب النموذج."
    )

    if not scored:
        best_hint = fallback
        best_id = "fallback"
        confidence = 0.25
    else:
        best_id, best_score, best_hint = scored[0]
        second = scored[1][1] if len(scored) > 1 else 0.0
        margin = best_score - second
        confidence = _clamp01(
            0.35 + 0.35 * math.tanh(best_score / 40.0) + 0.25 * math.tanh(margin / 25.0)
        )
        if best_id not in _HINT_NO_OS_STACK_SUFFIX:
            best_hint = best_hint + _stack_hint_suffix(ctx.stack) + _os_hint_suffix(ctx.os_family)
        if confidence < 0.42:
            best_hint += " — إن لم يُفدِ: راجع السجل الكامل أو أعد المحاولة بعد دقائق."

    top3 = [{"rule_id": r[0], "score": round(r[1], 3)} for r in scored[:3]]
    prof = runtime_profile()
    signals = {
        "engine": ALI12_ENGINE_VERSION,
        "os_family": prof["os_family"],
        "stack_family": ctx.stack,
        "http_status": ctx.http,
        "event_kind": ctx.event_kind,
        "top_rules": top3,
        "confidence": round(confidence, 4),
    }

    return {
        "hint_ar": best_hint,
        "rule_id": best_id,
        "confidence": round(confidence, 4),
        "signals": signals,
        "candidates_n": len(scored),
    }


def infer_install_event_kind_from_message(message: str, *, ok: bool) -> str:
    """يستنتج نوع الحدث من رسالة الواجهة عند غياب الحقل المنظم."""
    if ok:
        return "install_ok"
    m = (message or "").strip()
    if "رابط التنزيل غير متوفر" in m or "download_url" in m.lower():
        return "install_no_url"
    if "فشل التحميل" in m or "http" in m.lower():
        return "install_fail"
    return "install_fail"


def suggest_after_install_failure(
    *,
    event_kind: str,
    message: str = "",
    detail: Optional[dict[str, Any]] = None,
) -> str:
    """اقتراح نصي واحد (واجهات قديمة)."""
    return resolve_ali12(event_kind=event_kind, message=message, detail=detail)["hint_ar"]


def training_payload_stub(
    *,
    event_kind: str,
    model_id: str,
    user_message_snippet: str,
    ali12_hint_ar: str,
    resolution_label: str = "",
    ali12_signals: Optional[dict[str, Any]] = None,
    ali12_rule_id: str = "",
    ali12_confidence: Optional[float] = None,
    assistant_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    سجلّ موحّد لتصدير JSONL — يُفضّل إرفاق signals من resolve_ali12 أو من الحقل detail في التتبع.
    ``assistant_id`` يحدّد مساعد السرب (Ali12 / Hassan12 / Hussein12) عند الدمج مع ``services/assistants_squad``.
    """
    aid = (assistant_id or "").strip() or ALI12_ASSISTANT_ID
    row: dict[str, Any] = {
        "assistant_id": aid,
        "task": "install_help",
        "event_kind": event_kind,
        "model_id": model_id,
        "input_snippet": re.sub(r"\s+", " ", (user_message_snippet or ""))[:800],
        "ali12_suggested_reply_ar": ali12_hint_ar,
        "human_resolution": resolution_label,
        "ali12_engine": ALI12_ENGINE_VERSION,
    }
    if ali12_rule_id:
        row["ali12_rule_id"] = ali12_rule_id
    if ali12_confidence is not None:
        row["ali12_confidence"] = ali12_confidence
    if ali12_signals:
        row["ali12_signals"] = ali12_signals
    return row


def recompute_from_telemetry_row(row: dict[str, Any]) -> dict[str, Any]:
    """إعادة تشغيل محرك Ali12 على صف سجلّ محفوظ (لإعادة تصدير التدريب بعد ترقية الخوارزمية)."""
    d: dict[str, Any] = dict(row.get("detail")) if isinstance(row.get("detail"), dict) else {}
    mid = str(row.get("model_id", "") or "").strip()
    if mid and "model_id" not in d:
        d["model_id"] = mid
    return resolve_ali12(
        event_kind=str(row.get("event_kind", "")),
        message="",
        detail=d,
    )
