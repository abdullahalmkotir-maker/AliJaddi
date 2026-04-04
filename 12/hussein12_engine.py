# -*- coding: utf-8 -*-
"""
Hussein12 — مكتبة التدريب ونشر النماذج داخل مجلد ``12`` (مع Ali12).

- كثافة كلمات مفتاحية لتوجيه السرب (JSONL، BentoML، GPU، human_resolution…).
- خطة BentoML مقترحة وإرشاد عربي للتغذية والتصدير.
- صفوف تدريب موحّدة عبر ``Ali12.training_payload_stub`` مع ``assistant_id=Hussein12``.
"""
from __future__ import annotations

import re
from typing import Any, Final, Optional

HUSSEIN12_ASSISTANT_ID: Final = "Hussein12"
HUSSEIN12_ENGINE_VERSION: Final = "v1_training_serving"
HUSSEIN12_DISPLAY_AR: Final = "حسين 12"

# كلمات مجال Hussein12 — مصدر واحد لـ assistants_squad و bento_serving/routing
HUSSEIN_KEYWORDS: Final[frozenset[str]] = frozenset(
    {
        "jsonl",
        "training",
        "train",
        "seed",
        "human_resolution",
        "pipeline",
        "asyncio",
        "telemetry",
        "dataset",
        "تدريب",
        "بذور",
        "تصدير",
        "تصحيح",
        "خط_أنابيب",
        "أنابيب",
        "bentoml",
        "bento",
        "batching",
        "batch",
        "gpu",
        "cuda",
        "inference",
        "serving",
        "onnx",
        "docker",
        "kubernetes",
        "k8s",
        "mlflow",
        "نشر",
        "استدلال",
    }
)


def _token_set(text: str) -> set[str]:
    if not text:
        return set()
    return set(re.findall(r"[\w\u0600-\u06FF]+", text.lower()))


def hussein_keyword_density(blob: str) -> float:
    """نسبة تطابق رموز النص مع مجال Hussein12 (0..1)."""
    words = _token_set(blob)
    if not words:
        return 0.0
    inter = words & HUSSEIN_KEYWORDS
    if not inter:
        return 0.0
    return len(inter) / len(words)


def bento_ml_roadmap() -> list[dict[str, str]]:
    """خطوات نشر/تدريب مقترحة — تُعرض في API أو الواجهة."""
    return [
        {
            "step": "1",
            "title_ar": "تعبئة النموذج (BentoML)",
            "detail_ar": "حوّل نموذجك إلى Service مع تعريف API؛ فعّل adaptive batching عند الحاجة واضبط موارد GPU في ملف البيئة/الحاوية.",
        },
        {
            "step": "2",
            "title_ar": "Bento وDocker",
            "detail_ar": "ابنِ Bento (كود + تبعيات + أثر) ثم صورة Docker لبيئة متكررة؛ اختبر محلياً قبل الدفع للسجل.",
        },
        {
            "step": "3",
            "title_ar": "خدمات مصغّرة",
            "detail_ar": "افصل: مصادقة، كتالوج تطبيقات، خدمة استدلال؛ تواصل عبر REST/gRPC وطبقات رسائل عند الحاجة.",
        },
        {
            "step": "4",
            "title_ar": "دمج مع لغات أخرى",
            "detail_ar": "استدعِ خدمة Bento عبر HTTP من Go أو Java؛ Rust/PyO3 للمسار الحسابي الثقيل داخل بايثون عند القياس.",
        },
        {
            "step": "5",
            "title_ar": "تغذية Hussein12",
            "detail_ar": "سجّل فشل النشر/الاستدلال في telemetry؛ صدّر JSONL مع human_resolution من 12/seeds؛ أعد ضبط القواعد أو التدريب.",
        },
    ]


def hussein12_domain_hint_ar(text: str, *, bentish: bool) -> str:
    """إرشاد قصير لمجال Hussein12 (يُدمج في squad_ops_hint_ar)."""
    if bentish:
        return (
            "لبنتوML: عرّف Service واضح، راقب زمن الاستدلال والدُفعات؛ "
            "فعّل GPU في تعريف الحاوية؛ سجّل أخطاء الاستدلال لتغذية Hussein12 عبر JSONL وhuman_resolution."
        )
    return (
        "لخطوط التدريب والبيانات: صدّر telemetry، أثر human_resolution، وأعد بناء بذور 12/seeds/*_seed.jsonl."
    )


def hussein12_training_payload(
    *,
    event_kind: str,
    model_id: str,
    user_message_snippet: str,
    hint_ar: str,
    resolution_label: str = "",
    signals: Optional[dict[str, Any]] = None,
    rule_id: str = "",
    confidence: Optional[float] = None,
) -> dict[str, Any]:
    """صف تدريب موحّد باسم Hussein12 (نفس مخطط Ali12 JSONL)."""
    from Ali12 import training_payload_stub

    return training_payload_stub(
        event_kind=event_kind,
        model_id=model_id,
        user_message_snippet=user_message_snippet,
        ali12_hint_ar=hint_ar,
        resolution_label=resolution_label,
        ali12_signals=signals,
        ali12_rule_id=rule_id,
        ali12_confidence=confidence,
        assistant_id=HUSSEIN12_ASSISTANT_ID,
    )


def hussein12_meta() -> dict[str, str]:
    return {
        "id": HUSSEIN12_ASSISTANT_ID,
        "role_ar": "تغذية التدريب، BentoML/نشر النماذج، وتصحيح الأخطاء",
        "focus": "JSONL, human_resolution, BentoML serving, batching, GPU hints",
        "engine": HUSSEIN12_ENGINE_VERSION,
        "bundle_dir": "12",
    }
