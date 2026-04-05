# -*- coding: utf-8 -*-
"""مكتبة معرفية لسد الثغرات ومنع اختفاء البيانات دون سبب واضح."""

from __future__ import annotations

from pathlib import Path

PROMPTS_AR = [
    "قبل أي نقل أو حذف: تحقق من وجود نسخة احتياطية حديثة.",
    "لا ترسل ملفات حساسة دون تشفير وموافقة مكتوبة على الوجهة.",
    "فعّل الإصدارات (Version History) في OneDrive/SharePoint للمسارات المشمولة.",
    "راقب المساحة على القرص؛ امتلاء القرص يسبب فقداناً صامتاً أثناء الكتابة.",
    "تجنب تشغيل أدوات تنظيف تلقائية على مجلدات العمل دون استثناء المسارات المحمية.",
]

RULES_AR: dict[str, str] = {
    "delete": "الحذف يُنفّذ فقط بعد موافقة صريحة داخل مدير الملفات وتسجيل في السجل.",
    "move": "النقل يُعتبر تغييراً في موقع الحماية؛ يتطلب الموافقة على المسار المصدر والوجهة.",
    "send": "الإرسال إلى أي مكان خارج الجذر المحمي يتطلب وصف الوجهة والموافقة بالاسم.",
    "sync": "مزامنة السحابة قد تحذف محلياً إذا حُذف من السحابة؛ راجع سياسات المزامنة.",
}


def advice_for_operation(op: str, path: str = "") -> str:
    base = RULES_AR.get(op, PROMPTS_AR[0])
    if path:
        return f"{base}\n\nالمسار: {path}"
    return base


def explorer_organization_hints() -> list[dict[str, str]]:
    """ممارسات مستكشف الملفات في ويندوز للاقتراحات وليس للفرض."""
    return [
        {
            "role": "تنظيم_مستكشف",
            "content": (
                "مثل مستكشف الملفات: افصل المستندات عن التنزيلات؛ استخدم مجلداً للمشاريع وآخر للأرشيف؛ "
                "Avoid spaces in bulk automation paths؛ استخدم أسماء واضحة بالتاريخ عند الحاجة."
            ),
        },
        {
            "role": "تنظيم_مستكشف",
            "content": (
                "عرض التفاصيل والفرز حسب النوع/التاريخ يساعد المراجعة؛ المدير لا يغيّر عرض ويندوز بل يحاكي منطق التصنيف."
            ),
        },
    ]


def training_snippets() -> list[dict[str, str]]:
    """عينات يمكن توسيعها لتدريب نموذج لاحقاً."""
    base = [
        {
            "role": "سياسة",
            "content": "منع اختفاء البيانات: كل عملية حذف أو نقل تمر عبر طابور موافقات ولا تُنفَّذ تلقائياً.",
        },
        {
            "role": "سياسة",
            "content": "الإرسال الخارجي: يجب أن يذكر المستخدم اسم الوجهة والغرض قبل الموافقة.",
        },
        {
            "role": "سياسة",
            "content": "النسخ الاحتياطي: جدولة نسخ متزاعدة قبل أي عملية مجمّعة.",
        },
    ]
    return base + explorer_organization_hints()


def merged_training_snippets(policy_dir: Path | None) -> list[dict[str, str]]:
    """العينات الافتراضية + ما تعلّم من المستكشف (إن وُجد)."""
    from hassan12.explorer_learn import learned_to_training_entries

    out = list(training_snippets())
    if policy_dir is None:
        return out
    extra = learned_to_training_entries(policy_dir)
    return out + extra
