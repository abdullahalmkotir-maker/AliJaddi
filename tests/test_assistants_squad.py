# -*- coding: utf-8 -*-
from __future__ import annotations

import pytest

from services.assistants_squad import (
    HASSAN12_ID,
    HUSSEIN12_ID,
    apply_human_correction,
    pick_assistant_for_telemetry_detail,
    pick_assistant_id_for_context,
    squad_assistants_meta,
)


def test_squad_meta_lists_three():
    m = squad_assistants_meta()
    ids = {x["id"] for x in m}
    assert "Ali12" in ids
    assert HASSAN12_ID in ids
    assert HUSSEIN12_ID in ids


def test_route_hassan_microservices():
    assert pick_assistant_id_for_context("split the platform into microservices with grpc") == HASSAN12_ID


def test_route_hussein_training():
    assert pick_assistant_id_for_context("تصدير ملف jsonl للتدريب مع human_resolution") == HUSSEIN12_ID


def test_route_default_ali12():
    assert pick_assistant_id_for_context("فشل التحميل zip") == "Ali12"


def test_pick_from_telemetry_detail():
    assert (
        pick_assistant_for_telemetry_detail({"error": "fastapi service timeout"}, "install_fail")
        == HASSAN12_ID
    )
    assert (
        pick_assistant_for_telemetry_detail({"user_question": "asyncio pipeline training"}, "launch_fail")
        == HUSSEIN12_ID
    )


def test_apply_human_correction():
    row = {"assistant_id": "Ali12", "input_snippet": "{}"}
    out = apply_human_correction(row, "  أعد المحاولة بعد تحديث المسار  ")
    assert out["human_resolution"] == "أعد المحاولة بعد تحديث المسار"


def test_gateway_stub_fastapi():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from services.api_gateway_stub import create_app

    client = TestClient(create_app())
    assert client.get("/health").json().get("ok") is True
    r = client.post("/squad/route", json={"text": "grpc gateway golang"})
    assert r.json().get("assistant_id") == HASSAN12_ID


def test_route_bentoml_to_hussein():
    assert pick_assistant_id_for_context("bentoml adaptive batching inference gpu cuda") == HUSSEIN12_ID


def test_route_kafka_to_hassan():
    assert pick_assistant_id_for_context("kafka topic between microservices") == HASSAN12_ID


def test_bento_roadmap_and_squad_hint():
    from services.bento_integration_stub import bento_ml_roadmap, squad_ops_hint_ar

    assert len(bento_ml_roadmap()) >= 4
    h = squad_ops_hint_ar("bentoml serving onnx batching")
    assert h["assistant_id"] == HUSSEIN12_ID
    assert "bento_roadmap" in h
    assert h["bento_roadmap"][0]["step"] == "1"


def test_gateway_bento_ops():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from services.api_gateway_stub import create_app

    c = TestClient(create_app())
    steps = c.get("/ops/bento-roadmap").json().get("steps", [])
    assert len(steps) >= 4
    r = c.post("/ops/squad-hint", json={"text": "rabbitmq queue workers"})
    assert r.json().get("assistant_id") == HASSAN12_ID
