# -*- coding: utf-8 -*-
"""
تكامل **BentoML** ونشر النماذج — طبقة تخطيط وإرشاد داخل المستودع.

- لا يُشترَط تثبيت ``bentoml`` لتشغيل منصّة Qt؛ استخدم ``pip install -e ".[bentoml]"`` عند بناء خدمة نموذج فعلية.
- التوجيه نحو **Hussein12** (دورة حياة النموذج، batching، GPU، خطوط أنابيب) أو **Hassan12** (بوابات، طوابير، جدولة، تكامل Go/gRPC) يتم عبر ``assistants_squad`` + كلمات مفتاحية موسّعة.
"""
from __future__ import annotations

from typing import Any

from Hassan12 import hassan12_domain_hint_ar
from Hussein12 import bento_ml_roadmap, hussein12_domain_hint_ar
from services.assistants_squad import pick_assistant_id_for_context


def squad_ops_hint_ar(text: str) -> dict[str, Any]:
    """
    يحدّد المساعد ويعيد إرشاداً قصيراً عربياً حسب المجال (BentoML / بنية / تثبيت).
    """
    t = (text or "").strip()
    aid = pick_assistant_id_for_context(t)
    tl = t.lower()
    bentish = any(
        k in tl
        for k in (
            "bentoml",
            "bento",
            "batching",
            "inference",
            "serving",
            "onnx",
            "gpu",
            "cuda",
        )
    )
    hints = {
        "Hussein12": hussein12_domain_hint_ar(t, bentish=bentish),
        "Hassan12": hassan12_domain_hint_ar(t),
        "Ali12": "لمشاكل تثبيت المنصّة أو تطبيقات المتجر: راجع Ali12 ومسار store_consent_v2 ومدير التنزيلات.",
    }
    out: dict[str, Any] = {
        "assistant_id": aid,
        "hint_ar": hints.get(aid, hints["Ali12"]),
    }
    if bentish:
        out["bento_roadmap"] = bento_ml_roadmap()
    return out
