"""معرّفات النماذج — متوافقة مع جدول model_catalog في Supabase (تُعرَّف بهجرات مجلد AliJaddi Cloud)."""

CANONICAL_MODEL_IDS = frozenset({
    "legal", "maps", "adich", "sniper", "qanun_example", "euqid", "tahlil",
    "zakhrafatan", "sniper_perspective", "mudir", "dental_assistant", "alijaddi",
})

_FALLBACK_AR = {
    "legal": "قانون", "maps": "خرائط", "adich": "أدّيش", "sniper": "قناص",
    "qanun_example": "مثال قانون", "euqid": "عقد (Euqid)", "tahlil": "تحليل",
    "zakhrafatan": "زخرفة", "sniper_perspective": "منظور القناص",
    "mudir": "مدير التواصل", "dental_assistant": "مساعد طبيب الأسنان",
    "alijaddi": "علي جدّي — المركز",
}


def catalog_display_name(model_id: str) -> str:
    return _FALLBACK_AR.get(model_id, model_id)


def is_canonical_model_id(model_id: str) -> bool:
    return model_id in CANONICAL_MODEL_IDS
