# -*- coding: utf-8 -*-
"""
محمّل مكتبة Hussein12 — المنطق في ``12/hussein12_engine.py`` (مع Ali12 في ``12/``).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ENGINE_MODULE_NAME = "hussein12_engine"


def _engine_file() -> Path:
    root = Path(__file__).resolve().parent
    p = root / "12" / "hussein12_engine.py"
    if p.is_file():
        return p
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        p2 = Path(meipass) / "12" / "hussein12_engine.py"
        if p2.is_file():
            return p2
    return root / "12" / "hussein12_engine.py"


def _load_engine():
    path = _engine_file()
    spec = importlib.util.spec_from_file_location(_ENGINE_MODULE_NAME, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Hussein12: لا يوجد محرّك في {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_ENGINE_MODULE_NAME] = mod
    spec.loader.exec_module(mod)
    return mod


_engine = _load_engine()
for _name in dir(_engine):
    if _name.startswith("_"):
        continue
    globals()[_name] = getattr(_engine, _name)

__all__ = [n for n in dir(_engine) if not n.startswith("_")]
