# -*- coding: utf-8 -*-
"""
خدمة BentoML لمساعدي منصّة علي جدّي — نقطة استدلال خفيفة للتوجيه وخطّة Bento.

تشغيل محلي (من جذر المستودع بعد ``pip install -e ".[bentoml]"``)::

    cd bento_serving
    bentoml serve service.py:AliJaddiAssistantService --reload

بناء Bento::

    cd bento_serving
    bentoml build
"""
from __future__ import annotations

from bentoml import api, service

from routing import pick_assistant_id_for_context, pick_assistant_for_telemetry_detail


def _roadmap() -> list[dict[str, str]]:
    return [
        {
            "step": "1",
            "title_ar": "تعبئة النموذج (BentoML)",
            "detail_ar": "عرّف Service وAPI؛ فعّل batching عند الحاجة واضبط GPU في الحاوية.",
        },
        {
            "step": "2",
            "title_ar": "Bento وDocker",
            "detail_ar": "bentoml build ثم containerize لبيئة متكررة.",
        },
        {
            "step": "3",
            "title_ar": "تغذية المساعدين",
            "detail_ar": "telemetry → JSONL → human_resolution لـ Ali12/Hassan12/Hussein12.",
        },
    ]


@service(name="alijaddi_assistants")
class AliJaddiAssistantService:
    """واجهة استدلال للتوجيه نحو مساعد السرب وخطوات نشر النماذج."""

    @api(route="/health")
    def health(self) -> dict:
        return {"ok": True, "bento_service": "alijaddi_assistants"}

    @api(route="/squad/route")
    def squad_route(self, text: str = "") -> dict:
        t = (text or "").strip()
        aid = pick_assistant_id_for_context(t)
        out: dict = {"assistant_id": aid, "text_len": len(t)}
        tl = t.lower()
        if any(k in tl for k in ("bentoml", "bento", "inference", "serving", "gpu", "batching")):
            out["bento_roadmap"] = _roadmap()
        return out

    @api(route="/squad/from_telemetry_detail")
    def from_detail(self, detail_json: str = "{}", event_kind: str = "") -> dict:
        import json as _json

        try:
            d = _json.loads(detail_json or "{}")
            if not isinstance(d, dict):
                d = {}
        except _json.JSONDecodeError:
            d = {}
        return {
            "assistant_id": pick_assistant_for_telemetry_detail(d, event_kind),
            "event_kind": event_kind,
        }
