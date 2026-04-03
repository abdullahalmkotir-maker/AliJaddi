# -*- coding: utf-8 -*-
from __future__ import annotations

import services.platform_store as ps


def test_platform_update_from_registry(monkeypatch):
    monkeypatch.setattr(ps, "ALIJADDI_VERSION", "0.4.1-beta")
    reg = {"platform": "0.4.1-beta", "models": []}
    assert ps.platform_store_update_version(reg) is None
    assert ps.platform_store_update_version({"platform": "0.4.1-beta"}) is None


def test_platform_update_when_remote_newer(monkeypatch):
    monkeypatch.setattr(ps, "ALIJADDI_VERSION", "0.4.0-beta")
    assert ps.platform_store_update_version({"platform": "0.4.1-beta"}) == "0.4.1-beta"


def test_registry_platform_version_empty():
    assert ps.registry_platform_version({}) == ""
    assert ps.registry_platform_version(None) == ""
