"""بيانات النماذج — بدون Flet؛ مفاتيح أيقونات نصية."""
from __future__ import annotations

from services.models_data import STORE_ITEMS, get_models, load_models_from_manifests


def test_get_models_have_string_icons():
    models = get_models()
    assert len(models) >= 1
    for m in models:
        assert isinstance(m.get("icon"), str)
        assert m["id"]


def test_load_models_matches_get_models():
    a = load_models_from_manifests()
    b = get_models()
    assert len(a) == len(b)


def test_store_items_are_plain_dicts():
    assert len(STORE_ITEMS) >= 1
    for it in STORE_ITEMS:
        assert isinstance(it["icon"], str)
