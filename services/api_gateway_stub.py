# -*- coding: utf-8 -*-
"""
بوابة REST تجريبية (FastAPI) — خطوة أولى نحو فصل طبقة HTTP عن سطح المكتب.

تشغيل (بعد تثبيت الاعتمادات الاختيارية)::

    pip install -e ".[api]"
    uvicorn services.api_gateway_stub:create_app --factory --host 127.0.0.1 --port 8012

لا تُشغَّل تلقائياً مع ``main_qt.py``؛ مخصصة للتوسّع واختبارات التكامل.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import FastAPI


def create_app() -> "FastAPI":
    from fastapi import Body, FastAPI

    from services.assistants_squad import pick_assistant_id_for_context, squad_assistants_meta
    from services.bento_integration_stub import bento_ml_roadmap, squad_ops_hint_ar

    app = FastAPI(title="AliJaddi gateway stub", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str | bool]:
        return {"ok": True, "service": "alijaddi-gateway-stub"}

    @app.get("/squad/assistants")
    def assistants() -> dict[str, list[dict[str, str]]]:
        return {"assistants": squad_assistants_meta()}

    @app.post("/squad/route")
    def route_squad(data: dict[str, Any] = Body(default_factory=dict)) -> dict[str, str]:
        t = str(data.get("text", "") or "")
        return {"assistant_id": pick_assistant_id_for_context(t)}

    @app.get("/ops/bento-roadmap")
    def bento_roadmap() -> dict[str, list[dict[str, str]]]:
        return {"steps": bento_ml_roadmap()}

    @app.post("/ops/squad-hint")
    def squad_hint(data: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
        t = str(data.get("text", "") or "")
        return squad_ops_hint_ar(t)

    return app
