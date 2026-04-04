# -*- coding: utf-8 -*-
"""
واجهة توافقية: محرّك Ali12 الفعلي في ``12/ali12_engine.py`` مع بذور التدريب في ``12/seeds/``.
يُحمَّل ديناميكياً ليعمل في المستودع وبعد PyInstaller (مجلد البيانات ``12``).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ENGINE_MODULE_NAME = "ali12_engine"


def _engine_file() -> Path:
    root = Path(__file__).resolve().parent
    p = root / "12" / "ali12_engine.py"
    if p.is_file():
        return p
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        p2 = Path(meipass) / "12" / "ali12_engine.py"
        if p2.is_file():
            return p2
    return root / "12" / "ali12_engine.py"


def _load_engine():
    path = _engine_file()
    spec = importlib.util.spec_from_file_location(_ENGINE_MODULE_NAME, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Ali12: لا يوجد محرّك في {path}")
    mod = importlib.util.module_from_spec(spec)
    # مطلوب لـ @dataclass داخل الملف المحمّل ديناميكياً
    sys.modules[_ENGINE_MODULE_NAME] = mod
    spec.loader.exec_module(mod)
    return mod


_engine = _load_engine()
# تصدير كل الأسماء العامة من المحرّك
for _name in dir(_engine):
    if _name.startswith("_"):
        continue
    globals()[_name] = getattr(_engine, _name)

__all__ = [n for n in dir(_engine) if not n.startswith("_")]
