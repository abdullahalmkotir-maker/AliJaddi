# -*- coding: utf-8 -*-
"""منطق التوجيه داخل ``bento_serving/routing.py`` (متزامن مع assistants_squad)."""
from __future__ import annotations

import sys
from pathlib import Path

_BS = Path(__file__).resolve().parents[1] / "bento_serving"
if str(_BS) not in sys.path:
    sys.path.insert(0, str(_BS))

import routing as br  # noqa: E402


def test_bento_routing_hussein():
    assert br.pick_assistant_id_for_context("bentoml inference gpu batching") == br.HUSSEIN12_ID


def test_bento_routing_hassan():
    assert br.pick_assistant_id_for_context("kafka grpc microservices") == br.HASSAN12_ID


def test_bento_routing_ali12():
    assert br.pick_assistant_id_for_context("zip download failed") == br.ALI12_FALLBACK
