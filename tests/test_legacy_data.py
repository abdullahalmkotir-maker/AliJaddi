# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import services.legacy_data as ld


def test_resolve_prefers_downloads(tmp_path, monkeypatch):
    downloads = tmp_path / "dl"
    downloads.mkdir()
    app = downloads / "Euqid"
    app.mkdir()
    monkeypatch.setattr("services.legacy_data.desktop_candidates", lambda: [])

    p, src = ld.resolve_app_path_with_source("Euqid", downloads)
    assert p == app.resolve()
    assert src == ld.SOURCE_STORE_DOWNLOADS


def test_resolve_falls_back_to_legacy_host(tmp_path, monkeypatch):
    downloads = tmp_path / "dl"
    downloads.mkdir()
    desk = tmp_path / "Desktop"
    desk.mkdir()
    host = desk / ld.LEGACY_DESKTOP_HOST_DIR_NAME
    host.mkdir()
    legacy_app = host / "Mudir"
    legacy_app.mkdir()

    monkeypatch.setattr("services.legacy_data.desktop_candidates", lambda: [desk])

    p, src = ld.resolve_app_path_with_source("Mudir", downloads)
    assert p == legacy_app.resolve()
    assert src == ld.SOURCE_LEGACY_DESKTOP_HOST


def test_resolve_flat_desktop_folder(tmp_path, monkeypatch):
    downloads = tmp_path / "dl"
    downloads.mkdir()
    desk = tmp_path / "Desktop"
    desk.mkdir()
    flat = desk / "Tahlil"
    flat.mkdir()
    monkeypatch.setattr("services.legacy_data.desktop_candidates", lambda: [desk])

    p, src = ld.resolve_app_path_with_source("Tahlil", downloads)
    assert p == flat.resolve()
    assert src == ld.SOURCE_LEGACY_DESKTOP_FLAT
