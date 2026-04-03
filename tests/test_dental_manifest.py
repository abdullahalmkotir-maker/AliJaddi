"""تعريف مساعد طبيب الأسنان — اتساق المجلد والتشغيل والإحصاءات."""
from __future__ import annotations

import json
from pathlib import Path


def _dental_path() -> Path:
    root = Path(__file__).resolve().parents[1]
    return root / "addons" / "manifests" / "dental_assistant.json"


def test_dental_manifest_structure():
    p = _dental_path()
    assert p.is_file(), f"missing {p}"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["id"] == "dental_assistant"
    assert data["folder"] == "AhmadFalahDentalAssistant"
    assert data["launch"] == "streamlit run main.py"
    assert data["users"] == 198
    assert float(data["rating"]) >= 4.0
    url = data.get("download_url", "")
    assert url.startswith("https://")
    assert "dental_assistant" in url.lower()
