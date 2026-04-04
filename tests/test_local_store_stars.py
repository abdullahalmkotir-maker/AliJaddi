# -*- coding: utf-8 -*-
import json
from pathlib import Path

import services.local_store as ls


def test_add_session_stars_no_session():
    assert ls.add_session_stars(5) == 0


def test_add_session_stars_updates_session(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ls, "_DIR", tmp_path)
    monkeypatch.setattr(ls, "_SESSION_FILE", tmp_path / "session.json")
    monkeypatch.setattr(ls, "_CACHE_FILE", tmp_path / "cloud_cache.json")
    monkeypatch.setattr(ls, "_SETTINGS_FILE", tmp_path / "settings.json")
    ls._write(ls._SESSION_FILE, {
        "email": "a@b.c",
        "user_id": "u1",
        "access_token": "tok",
        "refresh_token": "r",
        "stars": 10,
    })
    new = ls.add_session_stars(3)
    assert new == 13
    data = json.loads(ls._SESSION_FILE.read_text(encoding="utf-8"))
    assert data["stars"] == 13
