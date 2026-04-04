# -*- coding: utf-8 -*-
import Hassan12 as h12

from services.assistants_squad import pick_assistant_id_for_context


def test_hassan12_ids():
    assert h12.HASSAN12_ASSISTANT_ID == "Hassan12"


def test_hassan_keyword_density():
    assert h12.hassan_keyword_density("grpc gateway kafka microservice") > 0
    assert h12.hassan_keyword_density("مجلد تنزيلات مسار") > 0


def test_pick_hassan_for_files_context():
    assert pick_assistant_id_for_context("أين مجلد التنزيلات للمتجر") == "Hassan12"


def test_list_store_app_folders_returns_list():
    rows = h12.list_store_app_folders(max_items=50)
    assert isinstance(rows, list)


def test_hassan12_training_payload():
    row = h12.hassan12_training_payload(
        event_kind="path_help",
        model_id="platform",
        user_message_snippet="{}",
        hint_ar="تلميح",
    )
    assert row["assistant_id"] == "Hassan12"


def test_hassan12_meta():
    m = h12.hassan12_meta()
    assert m["id"] == "Hassan12"
