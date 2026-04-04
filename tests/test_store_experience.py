# -*- coding: utf-8 -*-
from services.store_experience import fetch_store_experience_local, get_store_experience_offline_first


def test_fetch_store_experience_local_has_schema():
    d = fetch_store_experience_local()
    assert isinstance(d, dict)
    assert d.get("schema_version") == 1
    assert isinstance(d.get("featured_model_ids"), list)
    assert isinstance(d.get("contributors"), list)


def test_get_store_experience_offline_first_non_empty():
    d = get_store_experience_offline_first()
    assert d.get("schema_version") == 1
    assert len(d.get("contributors", [])) >= 1
