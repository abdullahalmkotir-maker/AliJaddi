"""اختبارات سجل الإضافات — أوفلاين، كاش، خيط المزامنة."""
from __future__ import annotations

import threading

from services.addon_manager import (
    check_update,
    get_registry_offline_first,
    install_model_sync,
    is_remote_version_newer,
    refresh_registry_background,
    version_sort_tuple,
)


def test_offline_first_prefers_nonempty_local(monkeypatch):
    local = {"schema_version": 2, "models": [{"id": "a", "version": "1.0.0"}]}
    monkeypatch.setattr(
        "services.addon_manager.fetch_registry_local",
        lambda: local,
    )
    monkeypatch.setattr(
        "services.addon_manager.cache_get",
        lambda _k: {"schema_version": 2, "models": [{"id": "b", "version": "2"}]},
    )
    assert get_registry_offline_first() == local


def test_offline_first_uses_cache_when_local_models_empty(monkeypatch):
    monkeypatch.setattr(
        "services.addon_manager.fetch_registry_local",
        lambda: {"schema_version": 2, "models": []},
    )
    cached = {"schema_version": 2, "models": [{"id": "cached", "version": "3"}]}
    monkeypatch.setattr("services.addon_manager.cache_get", lambda _k: cached)
    assert get_registry_offline_first() == cached


def test_check_update_uses_passed_registry(monkeypatch):
    reg = {"models": [{"id": "m1", "version": "2.0.0"}]}
    monkeypatch.setattr("services.addon_manager.installed_version", lambda _mid: "1.0.0")
    assert check_update("m1", reg) == "2.0.0"


def test_check_update_none_when_same_version(monkeypatch):
    reg = {"models": [{"id": "m1", "version": "1.0.0"}]}
    monkeypatch.setattr("services.addon_manager.installed_version", lambda _mid: "1.0.0")
    assert check_update("m1", reg) is None


def test_check_update_none_when_remote_older(monkeypatch):
    reg = {"models": [{"id": "m1", "version": "1.0.0"}]}
    monkeypatch.setattr("services.addon_manager.installed_version", lambda _mid: "2.0.0")
    assert check_update("m1", reg) is None


def test_version_sort_tuple_orders_semverish():
    assert version_sort_tuple("0.3.10") > version_sort_tuple("0.3.9")
    assert is_remote_version_newer("1.2.0", "1.1.9")
    assert not is_remote_version_newer("1.0.0", "2.0.0")


def test_install_model_sync_waits_for_callback(monkeypatch):
    def fake_install(*_a, on_done=None, **_k):
        if on_done:
            on_done(True, "تم")

    monkeypatch.setattr("services.addon_manager.install_model", fake_install)
    ok, msg = install_model_sync("x", "http://example/z.zip", "F", "1.0")
    assert ok is True
    assert msg == "تم"


def test_refresh_registry_background_remote_ok(monkeypatch):
    remote = {"schema_version": 2, "models": [{"id": "r", "version": "9"}]}
    monkeypatch.setattr("services.addon_manager.fetch_registry_github", lambda: remote)
    monkeypatch.setattr("services.addon_manager.fetch_registry_supabase", lambda: None)

    done = threading.Event()
    result: list = []

    def on_complete(reg, reached_remote):
        result.append((reg, reached_remote))
        done.set()

    refresh_registry_background(on_complete)
    assert done.wait(timeout=8)
    assert result[0][1] is True
    assert result[0][0] == remote


def test_refresh_registry_background_fallback_offline(monkeypatch):
    monkeypatch.setattr("services.addon_manager.fetch_registry_github", lambda: None)
    monkeypatch.setattr("services.addon_manager.fetch_registry_supabase", lambda: None)
    local = {"schema_version": 2, "models": [{"id": "l", "version": "1"}]}
    monkeypatch.setattr("services.addon_manager.get_registry_offline_first", lambda: local)

    done = threading.Event()
    result: list = []

    def on_complete(reg, reached_remote):
        result.append((reg, reached_remote))
        done.set()

    refresh_registry_background(on_complete)
    assert done.wait(timeout=8)
    assert result[0][1] is False
    assert result[0][0] == local
