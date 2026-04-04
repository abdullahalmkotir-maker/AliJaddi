# -*- coding: utf-8 -*-
"""
سرب مساعدي المنصّة — فصل هموم التوجيه عن محرّك Ali12:

- **Ali12:** تثبيت المتجر، Inno/ZIP، أخطاء التحميل/الفك (محرّك ``12/ali12_engine.py``).
- **Hassan12:** مكتبة ``12/hassan12_engine.py`` (محمّل ``Hassan12.py``) — خدمات، بوابات، ومدير مسارات/مجلدات التنزيلات.
- **Hussein12:** مكتبة ``12/hussein12_engine.py`` (محمّل ``Hussein12.py``) — تدريب JSONL، BentoML، كثافة كلمات المجال.

المحرّك القواعدي يبقى ``Ali12.resolve_ali12``؛ هذا الملف يحدد **معرّف المساعد** للتتبع والتدريب متعدد الرؤوس.
"""
from __future__ import annotations

import json
import re
from typing import Any, Final

from Hassan12 import (
    HASSAN12_ASSISTANT_ID as HASSAN12_ID,
    hassan12_meta,
    hassan_keyword_density,
)
from Hussein12 import (
    HUSSEIN12_ASSISTANT_ID as HUSSEIN12_ID,
    hussein12_meta,
    hussein_keyword_density,
)

ALI12_FALLBACK: Final = "Ali12"
def squad_assistants_meta() -> list[dict[str, str]]:
    """وصف ثابت للواجهات والوثائق."""
    hm = hassan12_meta()
    hum = hussein12_meta()
    return [
        {
            "id": ALI12_FALLBACK,
            "role_ar": "تثبيت وتشغيل تطبيقات المتجر ومنصّة ويندوز",
            "focus": "store_consent_v2, PyInstaller, Inno, hosted launch",
        },
        {
            "id": hm["id"],
            "role_ar": hm["role_ar"],
            "focus": hm["focus"],
        },
        {
            "id": hum["id"],
            "role_ar": hum["role_ar"],
            "focus": hum["focus"],
        },
    ]


def _normalize_context_blob(*parts: str) -> str:
    t = " ".join(p for p in parts if p).strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def _token_set(text: str) -> set[str]:
    if not text:
        return set()
    return set(re.findall(r"[\w\u0600-\u06FF]+", text.lower()))


def _keyword_density(blob: str, keywords: frozenset[str]) -> float:
    """نسبة رموز النص التي تطابق مجالاً معيناً — مناسبة لمجموعات كلمات كبيرة."""
    words = _token_set(blob)
    if not words:
        return 0.0
    inter = words & keywords
    if not inter:
        return 0.0
    return len(inter) / len(words)


def pick_assistant_id_for_context(*text_parts: str) -> str:
    """
    يختار المساعد الأنسب بناءً على نص السياق (سؤال المستخدم، رسالة الخطأ، detail…).
    الافتراضي Ali12 إن لم تُحدَّد إشارة قوية.
    """
    blob = _normalize_context_blob(*text_parts)
    if not blob:
        return ALI12_FALLBACK
    d_hussein = hussein_keyword_density(blob)
    d_hassan = hassan_keyword_density(blob)
    # Hussein له أولوية عند تعادل شبه كامل أو كثافة أعلى
    if d_hussein > d_hassan + 0.02 or (d_hussein >= 0.18 and d_hussein >= d_hassan):
        return HUSSEIN12_ID
    if d_hassan >= 0.12:
        return HASSAN12_ID
    return ALI12_FALLBACK


def pick_assistant_for_telemetry_detail(detail: dict[str, Any] | None, event_kind: str = "") -> str:
    """يستخرج نصوص آمنة من detail ثم يوجّه."""
    d = detail or {}
    chunks: list[str] = [event_kind or ""]
    for k in ("error", "user_question", "message", "note", "phase", "context"):
        v = d.get(k)
        if isinstance(v, str):
            chunks.append(v)
    try:
        chunks.append(json.dumps(d, ensure_ascii=False))
    except (TypeError, ValueError):
        pass
    return pick_assistant_id_for_context(*chunks)


def apply_human_correction(row: dict[str, Any], human_resolution: str) -> dict[str, Any]:
    """ينسخ صف التدريب/التتبع ويضيف أو يحدّث حقل التصحيح البشري."""
    out = dict(row)
    out["human_resolution"] = (human_resolution or "").strip()
    return out
