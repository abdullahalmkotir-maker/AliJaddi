# -*- coding: utf-8 -*-
"""
مسارات مجلد ``12`` — سرب المساعدين (Ali12 / Hassan12 / Hussein12) وبذور التدريب.
يُستخدم في التصدير والواجهة وPyInstaller (``--add-data 12;12``).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from services.paths import bundle_root

SQUAD_DIR_NAME = "12"
MANIFEST_NAME = "manifest.json"
SEEDS_SUBDIR = "seeds"


def squad_root() -> Path:
    """جذر ``12`` بجانب جذر الحزمة (مستودع أو _MEIPASS)."""
    return (bundle_root() / SQUAD_DIR_NAME).resolve()


def seeds_dir() -> Path:
    return squad_root() / SEEDS_SUBDIR


def manifest_path() -> Path:
    return squad_root() / MANIFEST_NAME


def load_manifest() -> Optional[dict[str, Any]]:
    p = manifest_path()
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def all_seed_jsonl() -> list[Path]:
    d = seeds_dir()
    if not d.is_dir():
        return []
    return sorted(d.glob("*_seed.jsonl"))


def squad_summary_ar() -> str:
    m = load_manifest()
    if not m:
        return "مجلد 12 — بذور التدريب ومحرّك Ali12."
    return str(m.get("description_ar") or "")
