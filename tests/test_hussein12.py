# -*- coding: utf-8 -*-
import Hussein12 as h12


def test_hussein12_ids():
    assert h12.HUSSEIN12_ASSISTANT_ID == "Hussein12"
    assert h12.HUSSEIN12_ENGINE_VERSION


def test_hussein_keyword_density():
    assert h12.hussein_keyword_density("jsonl training human_resolution") > 0
    assert h12.hussein_keyword_density("xyz abc noop") == 0.0


def test_bento_ml_roadmap():
    steps = h12.bento_ml_roadmap()
    assert len(steps) >= 5
    blob = " ".join(s.get("detail_ar", "") + s.get("title_ar", "") for s in steps)
    assert "Hussein12" in blob or "تغذية" in blob


def test_hussein12_training_payload():
    row = h12.hussein12_training_payload(
        event_kind="export_help",
        model_id="platform",
        user_message_snippet='{"q":"test"}',
        hint_ar="تلميح تجريبي",
        resolution_label="ok",
    )
    assert row["assistant_id"] == "Hussein12"
    assert row["ali12_suggested_reply_ar"] == "تلميح تجريبي"


def test_hussein12_meta():
    m = h12.hussein12_meta()
    assert m["id"] == "Hussein12"
    assert "12" in m.get("bundle_dir", "")
