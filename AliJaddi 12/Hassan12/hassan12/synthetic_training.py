# -*- coding: utf-8 -*-
"""
توليد بيانات تدريب اصطناعية لـ Hassan12: استخدامات افتراضية لمستكشف الملفات
وسد ثغرات وظواهر فقدان/اضطراب بيانات.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

VIRTUAL_PATHS = [
    r"C:\Users\المستخدم\Desktop\Hassan12",
    r"C:\Users\المستخدم\Documents\مشاريع",
    r"C:\Users\المستخدم\Downloads",
    r"C:\Users\المستخدم\OneDrive\Documents",
    r"D:\أرشيف\2024",
    r"C:\Users\المستخدم\Pictures\نسخ_احتياطية",
    r"\\SERVER\موارد\مشترك",
    r"C:\Users\المستخدم\Videos\تسجيلات",
    r"E:\نسخ_احتياطية_أسبوعية",
    r"C:\Users\المستخدم\AliJaddi\AliJaddi 12\Hassan12\مجلد_محمي",
    r"C:\Users\المستخدم\AppData\Local\Hassan12\app",
    r"\\NAS\نسخ\مستندات",
    r"C:\مشاريع\بناء_مكتبة_تدريب",
]

FOLDER_NAMES = [
    "مشاريع_جارية",
    "عقود",
    "فواتير_2024",
    "أرشيف_مكتمل",
    "مسودات",
    "نسخ_OneDrive",
    "تصدير_Ali12",
]

SORT_MODES = ["الاسم", "تاريخ التعديل", "النوع", "الحجم"]

EXPLORER_ACTIONS = [
    "فتح المجلد في مستكشف الملفات",
    "عرض التفاصيل بدل الأيقونات",
    "فرز العناصر حسب {sort}",
    "إنشاء مجلد فرعي جديد باسم «{fname}»",
    "تمييز ملفات حديثة للمراجعة",
    "نسخ مسار المجلد من شريط العنوان",
    "البحث داخل المجلد عن امتداد معيّن",
    "معاينة صور دون فتح التطبيق الافتراضي",
    "ضغط مجموعة ملفات في أرشيف مؤقت للمراجعة",
    "إعادة تسمية دفعة بقالب تاريخي",
]

SECURITY_MEASURES = [
    "تفعيل سجل الإصدارات في OneDrive قبل أي حذف جماعي",
    "إدخال عملية الحذف في طابور موافقات Hassan12 مع سبب مكتوب",
    "أخذ لقطة هيكل المجلد (أسماء فقط) في مكتبة التعلم",
    "التحقق من وجود نسخة على قرص خارجي أو سحابة ثانوية",
    "تعطيل أدوات التنظيف التلقائي للمسارات المحمية",
    "تثبيت التحديثات من المصدر الرسمي فقط",
    "مراجعة سياسات المزامنات المتعددة على نفس المجلد",
    "تصدير حزمة سجلات Ali12 بعد الحوادث للتحليل",
    "فصل البيانات الحساسة في مجلد محمي بصلاحيات NTFS",
    "استخدام Ali12 لتصدير JSON تدريب بعد كل حادثة ظاهرة",
]

PHENOMENA = [
    ("اختفاء ملفات بعد إعادة تشغيل الجهاز", "كتابة غير مكتملة أو قرص ممتلئ", "فحص السجل واستعادة من الإصدارات"),
    ("مجلد يظهر فارغاً رغم وجود مساحة مستخدمة", "عرض مخفي أو فهرس معطوب", "إعادة فتح المستكشف وتحديث العرض"),
    ("ملفات تُحذف تلقائياً بعد ساعات", "مزامنة سحابة تحذف عند حذف نسخة أخرى", "مراجعة سلة المحذوفات والسحابة وسجل المزامنة"),
    ("بطء شديد عند فتح مجلد كبير", "فحص القرص أو عدد ملفات ضخم", "فرز حسب النوع أو تقسيم الأرشيف"),
    ("تعارض بين نسختين من نفس الملف", "عمل نسختين على جهازين دون مزامنة", "دمج يدوي مع الاحتفاظ بنسخة بتاريخ"),
    ("رفض الحذف «قيد الاستخدام»", "تطبيق يوفّ الملف", "إغلاق التطبيقات أو إعادة التشغيل"),
    ("اختفاء اختصارات .lnk فقط", "مسار الهدف تغيّر أو حُذف", "إعادة ربط الاختصار أو استيراده من Ali12/Hassan12"),
    ("ازدواج مجلدات OneDrive", "مسار مزدوج سطح مكتب/OneDrive", "توحيد مسار العمل داخل Hassan12 المحمي"),
    ("صفر بايت يظهر في ملفات حديثة", "انقطاع أثناء الحفظ أو مشكلة شبكة", "إعادة التحميل من المصدر أو الاستعادة"),
    ("تغيّر أيقونات الملفات دون تغيير المحتوى", "ارتباط الامتداد تغيّر", "تثبيت الافتراضي أو فتح بـ«اختيار التطبيق»"),
    ("مجلد يُنقل إلى سلة المحذوفات دون تدخل واضح", "اختصار لوحة مفاتيح أو برنامج صيانة", "مراجعة سجل Hassan12 وسلة المحذوفات"),
    ("عدم ظهور ملفات جديدة بعد التصدير", "مسار حفظ خاطئ أو تأخير الفهرسة", "تحديث المستكشف ومراجعة مجلد التصدير في Ali12"),
]

HASSAN12_SCENARIOS = [
    "طلب حذف يمر عبر طابور الموافقات ثم التنفيذ بعد تسجيل الاسم",
    "طلب إرسال خارج الجذر المحمي يتطلب وصف الوجهة واسم المُوافق",
    "تصدير تدريب عبر Ali12 بصيغة JSON ثم دمجها في خط أنابيب التعلم",
    "تثبيت من Install-Ali12.ps1 بعد موافقة صريحة من المستخدم",
    "مراقبة Watchdog تسجل أحداثاً دون منع مستكشف ويندوز مباشرة",
    "تعلّم من لقطة مستكشف (أسماء فقط) يُخزَّن في learned_from_explorer.json",
]

USER_QUERY_TEMPLATES = [
    "في المسار {path} كيف أنظم الملفات مثل مستكشف ويندوز؟",
    "ظاهرة: {sym} — ما تفسيرك وما الإجراء؟",
    "أريد {action} بأمان مع Hassan12",
    "ما ثغرة محتملة في {ctx} وكيف أسدّها؟",
    "سيناريو افتراضي رقم {n}: مستخدم ينفّذ {action} ثم يطلب حذفاً",
]


def _pick(rng: random.Random, seq: list[Any]) -> Any:
    return seq[rng.randrange(len(seq))]


def _build_explorer_pair(rng: random.Random, idx: int) -> dict[str, Any]:
    path = _pick(rng, VIRTUAL_PATHS)
    fname = _pick(rng, FOLDER_NAMES)
    sort = _pick(rng, SORT_MODES)
    tpl = _pick(rng, EXPLORER_ACTIONS)
    action = tpl.format(sort=sort, fname=fname)
    sym, _, _ = PHENOMENA[rng.randrange(len(PHENOMENA))]
    user = rng.choice(USER_QUERY_TEMPLATES).format(
        path=path,
        sym=sym,
        action=action,
        ctx="مزامنة المجلدات",
        n=idx + 1,
    )
    assistant = (
        f"استخدام افتراضي #{idx+1} (مستكشف): نفّذ «{action}» على «{path}». "
        f"أبقِ التنظيم متسقاً: مجلدات فرعية حسب الغرض أو التاريخ؛ "
        f"تجنّب تكرار نفس الملف بين التنزيلات والمستندات؛ "
        f"للمسارات المحمية يفضّل تسجيل أي حذف لاحقاً عبر Hassan12."
    )
    return _record(idx, "explorer", user, assistant)


def _build_security_pair(rng: random.Random, idx: int) -> dict[str, Any]:
    path = _pick(rng, VIRTUAL_PATHS)
    measure = _pick(rng, SECURITY_MEASURES)
    user = (
        f"سد ثغرة بيانات (افتراضي #{idx+1}): المسار «{path}». "
        f"ما الإجراء الموصى به؟"
    )
    assistant = (
        f"إغلاق الثغرة: {measure}. "
        f"تحقق من أن المسار ضمن نطاق النسخ الاحتياطي؛ "
        f"إذا وُجد تعارض مزامنة، أوقف المزامنة المزدوجة على نفس الجذر؛ "
        f"وثّق القرار في سجل Ali12 عند التصدير."
    )
    return _record(idx, "security_patch", user, assistant)


def _build_phenomenon_pair(rng: random.Random, idx: int) -> dict[str, Any]:
    sym, cause, fix = PHENOMENA[rng.randrange(len(PHENOMENA))]
    user = f"ظاهرة مرصودة (افتراضي #{idx+1}): {sym}. ما السبب والعلاج؟"
    assistant = (
        f"تفسير محتمل: {cause}. إجراء مقترح: {fix}. "
        f"أضف مراقبة مستكشف (لقطة هيكل) إذا تكرّت الظاهرة؛ "
        f"لا تحذف دفعة واحدة قبل التأكد من الإصدارات."
    )
    return _record(idx, "phenomenon", user, assistant)


def _build_hassan12_pair(rng: random.Random, idx: int) -> dict[str, Any]:
    scen = _pick(rng, HASSAN12_SCENARIOS)
    user = f"سياسة Hassan12 (افتراضي #{idx+1}): كيف يُطبَّق «{scen}»؟"
    assistant = (
        f"التطبيق العملي: {scen}. "
        f"Ali12 يتولى التثبيت والتصدير؛ الواجهة الرئيسية تدير الموافقات والسجل؛ "
        f"بيانات التدريب الاصطناعية تُغذّي النموذج دون استبدال موافقة المستخدم الحقيقية."
    )
    return _record(idx, "hassan12_policy", user, assistant)


def _record(idx: int, domain: str, user: str, assistant: str) -> dict[str, Any]:
    return {
        "id": idx,
        "domain": domain,
        "locale": "ar",
        "source": "hassan12_synthetic_virtual",
        "messages": [
            {"role": "user", "content": user.strip()},
            {"role": "assistant", "content": assistant.strip()},
        ],
        "instruction": user.strip(),
        "output": assistant.strip(),
    }


@dataclass
class SyntheticGenerator:
    seed: int = 42
    weights: tuple[float, float, float, float] = (0.38, 0.32, 0.18, 0.12)

    def __post_init__(self) -> None:
        if not math.isclose(sum(self.weights), 1.0, rel_tol=0, abs_tol=1e-5):
            raise ValueError("weights يجب أن تجمع إلى 1")

    def stream(self, count: int) -> Iterator[dict[str, Any]]:
        rng = random.Random(self.seed)
        builders = (
            _build_explorer_pair,
            _build_security_pair,
            _build_phenomenon_pair,
            _build_hassan12_pair,
        )
        for i in range(count):
            r = rng.random()
            acc = 0.0
            chosen = 0
            for j, w in enumerate(self.weights):
                acc += w
                if r <= acc:
                    chosen = j
                    break
            yield builders[chosen](rng, i)

    def write_jsonl(self, path: Path, count: int) -> int:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        n = 0
        with path.open("w", encoding="utf-8") as f:
            for row in self.stream(count):
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                n += 1
        return n


def generate_default_10k(out_path: str | Path, seed: int = 42) -> Path:
    p = Path(out_path)
    SyntheticGenerator(seed=seed).write_jsonl(p, 10_000)
    return p.resolve()
