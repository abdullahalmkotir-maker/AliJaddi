# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def test_installed_app_path_uses_apps_parent(monkeypatch, tmp_path: Path):
    from services import addon_manager as am

    parent = tmp_path / "custom_host"
    parent.mkdir()
    app_folder = parent / "Euqid"
    app_folder.mkdir()

    def fake_load():
        return {
            "euqid": {
                "folder": "Euqid",
                "apps_parent": str(parent.resolve()),
                "version": "1.0.0",
            }
        }

    monkeypatch.setattr(am, "load_installed", fake_load)
    out = am.installed_app_path("euqid", "Euqid")
    assert out == app_folder.resolve()


def test_installed_app_path_falls_back_without_record(monkeypatch, tmp_path: Path):
    from services import addon_manager as am

    monkeypatch.setattr(am, "load_installed", lambda: {})
    monkeypatch.setattr(am, "app_dir", lambda name: tmp_path / "default" / name)
    out = am.installed_app_path("x", "Euqid")
    assert out == (tmp_path / "default" / "Euqid")
