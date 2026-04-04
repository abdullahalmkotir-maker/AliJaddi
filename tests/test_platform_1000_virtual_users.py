# -*- coding: utf-8 -*-
"""
محاكاة 1000 مستخدم افتراضي: توجيه السرب متزامناً، طلبات ASGI للبوابة، وسجل الإطلاقات.
"""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

N_VIRTUAL = 1000


def _valid_assistant_ids() -> set[str]:
    from Hassan12 import HASSAN12_ASSISTANT_ID
    from Hussein12 import HUSSEIN12_ASSISTANT_ID
    from services.assistants_squad import ALI12_FALLBACK

    return {ALI12_FALLBACK, HASSAN12_ASSISTANT_ID, HUSSEIN12_ASSISTANT_ID}


def test_1000_threads_squad_routing():
    from services.assistants_squad import (
        pick_assistant_for_telemetry_detail,
        pick_assistant_id_for_context,
        squad_assistants_meta,
    )

    valid = _valid_assistant_ids()

    def one(i: int) -> str:
        blob = (
            f"zip inno {i}" if i % 4 == 0 else f"bentoml jsonl {i}" if i % 4 == 1 else f"api kafka {i}"
        )
        a = pick_assistant_id_for_context("ctx", blob)
        b = pick_assistant_for_telemetry_detail(
            {"user_question": blob, "error": str(i % 9)},
            "launch_fail",
        )
        assert a in valid
        assert b in valid
        m = squad_assistants_meta()
        assert len(m) == 3
        return a

    with ThreadPoolExecutor(max_workers=64) as ex:
        futures = [ex.submit(one, i) for i in range(N_VIRTUAL)]
        for f in as_completed(futures):
            f.result()


@pytest.fixture()
def isolated_local_store(tmp_path, monkeypatch):
    import services.local_store as ls

    monkeypatch.setattr(ls, "_DIR", tmp_path)
    monkeypatch.setattr(ls, "_SETTINGS_FILE", tmp_path / "settings.json")
    monkeypatch.setattr(ls, "_SESSION_FILE", tmp_path / "session.json")
    monkeypatch.setattr(ls, "_STATS_FILE", tmp_path / "usage_stats.json")
    monkeypatch.setattr(ls, "_CACHE_FILE", tmp_path / "cloud_cache.json")
    yield ls


def test_1000_concurrent_record_launch(isolated_local_store):
    ls = isolated_local_store

    def bump(_: int) -> None:
        ls.record_launch("concurrent_model")

    with ThreadPoolExecutor(max_workers=64) as ex:
        list(ex.map(bump, range(N_VIRTUAL)))

    st = ls.get_model_stats("concurrent_model")
    assert st["launches"] == N_VIRTUAL
    assert ls.get_all_stats()["total_launches"] == N_VIRTUAL


def test_1000_asgi_gateway_requests():
    httpx = pytest.importorskip("httpx")
    from services.api_gateway_stub import create_app

    app = create_app()

    async def _run() -> None:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            sem = asyncio.Semaphore(80)

            async def one(i: int) -> None:
                async with sem:
                    h = await client.get("/health")
                    h.raise_for_status()
                    body = {"text": f"zip bentoml kafka service {i % 11}"}
                    r = await client.post("/squad/route", json=body)
                    r.raise_for_status()
                    data = r.json()
                    assert data.get("assistant_id") in _valid_assistant_ids()

            await asyncio.gather(*(one(i) for i in range(N_VIRTUAL)))

    asyncio.run(_run())
