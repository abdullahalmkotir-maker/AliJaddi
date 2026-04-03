"""سجل النماذج في الحزمة alijaddi."""
from __future__ import annotations

import alijaddi.models as models


def test_model_registry_has_core_apps():
    assert "euqid" in models.MODEL_REGISTRY
    assert "zakhrafatan" in models.MODEL_REGISTRY
    assert models.MODEL_REGISTRY["euqid"]["launch_cmd"]


def test_cloud_only_entries():
    assert "legal" in models.MODEL_REGISTRY
    assert models.MODEL_REGISTRY["legal"]["project_folder"] == ""


def test_get_model_and_get_ai_models():
    assert models.get_model("nope") is None
    ai = models.get_ai_models()
    assert "euqid" in ai
    assert "legal" not in ai


def test_refresh_registry_stable():
    before = dict(models.MODEL_REGISTRY)
    models.refresh_registry()
    after = models.MODEL_REGISTRY
    assert set(before.keys()) == set(after.keys())
