# -*- coding: utf-8 -*-
"""
توجيه مساعدي السرب — حزمة Bento؛ كثافات Hassan12 و Hussein12 من مجلد ``12``.
"""
from __future__ import annotations

import json
import re
from typing import Any, Final

from Hassan12 import HASSAN12_ASSISTANT_ID as HASSAN12_ID, hassan_keyword_density
from Hussein12 import HUSSEIN12_ASSISTANT_ID as HUSSEIN12_ID, hussein_keyword_density

ALI12_FALLBACK: Final = "Ali12"


def _normalize_context_blob(*parts: str) -> str:
    t = " ".join(p for p in parts if p).strip().lower()
    return re.sub(r"\s+", " ", t)


def pick_assistant_id_for_context(*text_parts: str) -> str:
    blob = _normalize_context_blob(*text_parts)
    if not blob:
        return ALI12_FALLBACK
    d_hussein = hussein_keyword_density(blob)
    d_hassan = hassan_keyword_density(blob)
    if d_hussein > d_hassan + 0.02 or (d_hussein >= 0.18 and d_hussein >= d_hassan):
        return HUSSEIN12_ID
    if d_hassan >= 0.12:
        return HASSAN12_ID
    return ALI12_FALLBACK


def pick_assistant_for_telemetry_detail(detail: dict[str, Any] | None, event_kind: str = "") -> str:
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
