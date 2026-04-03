"""فحص تحديث المنصّة (مع محاكاة الشبكة)."""
from __future__ import annotations

from services.platform_update import check_platform_update, ReleaseInfo


def test_check_platform_update_newer(monkeypatch):
    class Resp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"tag_name": "v99.0.0-test", "html_url": "https://github.com/x/y"}

    monkeypatch.setattr("services.platform_update.httpx.get", lambda *a, **k: Resp())
    info = check_platform_update("0.1.0")
    assert isinstance(info, ReleaseInfo)
    assert info.ok is True
    assert info.has_newer is True
    assert "99.0.0-test" in info.tag_name or info.tag_name.startswith("99")


def test_check_platform_update_network_error(monkeypatch):
    def boom(*a, **k):
        raise OSError("no network")

    monkeypatch.setattr("services.platform_update.httpx.get", boom)
    info = check_platform_update()
    assert info.ok is False
