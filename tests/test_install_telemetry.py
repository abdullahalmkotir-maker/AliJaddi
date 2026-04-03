"""سجل أحداث التثبيت المحلي."""
from __future__ import annotations

import json

from services.install_telemetry import emit_install_event


def test_emit_install_event_local_jsonl(monkeypatch, tmp_path):
    logf = tmp_path / "t.jsonl"
    monkeypatch.setattr("services.install_telemetry._TELEMETRY_FILE", logf)
    emit_install_event(
        "install_ok",
        model_id="euqid",
        success=True,
        detail={"version": "1.0.0", "folder": "Euqid"},
    )
    lines = logf.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["event_kind"] == "install_ok"
    assert row["model_id"] == "euqid"
    assert row["success"] is True
    assert row["detail"]["version"] == "1.0.0"
