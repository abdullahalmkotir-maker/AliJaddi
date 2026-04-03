"""اختبارات كتالوج التطبيقات الموحّد."""
from __future__ import annotations

from pathlib import Path

from services import model_catalog as mc


def test_launcher_display_icon_known():
    assert mc.launcher_display_icon("euqid") == "📜"
    assert mc.launcher_display_icon("unknown_model") == "📱"


def test_cloud_table_for_mudir():
    assert mc.cloud_table_for("mudir") == "social_post_queue"
    assert mc.cloud_table_for("euqid") == "model_user_data"


def test_merge_empty_disk_uses_fallback():
    fb = [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}]
    out = mc.merge_catalog_entries([], fb)
    assert len(out) == 2
    assert {x["id"] for x in out} == {"a", "b"}


def test_merge_disk_plus_fallback_gap(tmp_path: Path):
    disk = [{"id": "x", "name": "X", "desc": "", "folder": "X", "version": "2.0"}]
    fb = [
        {"id": "x", "name": "IGNORED", "folder": "X", "version": "0.1"},
        {"id": "y", "name": "Y", "desc": "", "folder": "Y", "version": "1.0"},
    ]
    out = mc.merge_catalog_entries(disk, fb)
    ids = [x["id"] for x in out]
    assert ids == ["x", "y"]
    assert out[0]["name"] == "X"


def test_read_manifest_dicts_skips_bad_json(tmp_path: Path):
    d = tmp_path / "manifests"
    d.mkdir()
    (d / "good.json").write_text('{"id":"ok","name":"OK"}', encoding="utf-8")
    (d / "bad.json").write_text("{not json", encoding="utf-8")
    rows = mc.read_manifest_dicts(d)
    assert len(rows) == 1
    assert rows[0]["id"] == "ok"


def test_normalize_qt_model_defaults():
    m = mc.normalize_qt_model({"id": "t"})
    assert m["id"] == "t"
    assert m["active"] is True
    assert m["rating"] == 0.0
    assert m["users"] == 0


def test_load_qt_models_from_real_bundle():
    models = mc.load_qt_models()
    ids = {m["id"] for m in models}
    assert "euqid" in ids
    assert "zakhrafatan" in ids
    for m in models:
        assert "launch" in m
        assert "folder" in m


def test_entries_to_launcher_registry():
    entries = [{"id": "z", "name": "Z", "desc": "", "folder": "F", "launch": "python x.py"}]
    reg = mc.entries_to_launcher_registry(entries)
    assert reg["z"]["launch_cmd"] == "python x.py"
    assert reg["z"]["project_folder"] == "F"
