# -*- coding: utf-8 -*-
from services.squad12_paths import all_seed_jsonl, load_manifest, manifest_path, seeds_dir, squad_root


def test_squad_root_and_seeds_exist():
    root = squad_root()
    assert root.name == "12"
    assert (root / "manifest.json").is_file()
    sd = seeds_dir()
    assert sd.is_dir()
    seeds = all_seed_jsonl()
    names = {p.name for p in seeds}
    assert "Ali12_seed.jsonl" in names
    assert "Hassan12_seed.jsonl" in names
    assert "Hussein12_seed.jsonl" in names


def test_manifest_loads():
    m = load_manifest()
    assert m is not None
    assert m.get("schema_version") == 1
    aids = [a["id"] for a in m.get("assistants", [])]
    assert "Ali12" in aids
    assert "Hassan12" in aids
    assert "Hussein12" in aids


def test_manifest_path():
    assert manifest_path().name == "manifest.json"
