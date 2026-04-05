"""أدوار بسيطة من data/roles.json."""
import json
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)
_cache = None


def _load() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    p = Path("data/roles.json")
    try:
        _cache = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error("roles: %s", e)
        _cache = {"user": {"level": 4, "permissions": ["view"]}}
    return _cache


def get_role_level(role: str) -> int:
    return _load().get(role, {}).get("level", 99)


def is_admin() -> bool:
    try:
        import streamlit as st

        return get_role_level(st.session_state.get("role", "user")) == 1
    except ImportError:
        return False
