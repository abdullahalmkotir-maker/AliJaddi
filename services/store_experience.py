# -*- coding: utf-8 -*-
"""
تجربة المتجر من المستودع: أبرز التطبيقات، لوحة المتصدرين، نصوص السياسة.
يُجلب من GitHub (نفس فرع السجل) مع fallback محلي من ``addons/store_experience.json``.
"""
from __future__ import annotations

import json
from pathlib import Path
from threading import Thread
from typing import Any, Callable, Optional

import httpx

from services.addon_manager import cache_get, cache_set
from services.paths import bundle_root

_GITHUB_REPO = "abdullahalmkotir-maker/AliJaddi"
_GITHUB_BRANCH = "main"
_XP_JSON = "addons/store_experience.json"
_RAW_URL = f"https://raw.githubusercontent.com/{_GITHUB_REPO}/{_GITHUB_BRANCH}/{_XP_JSON}"
_CACHE_KEY = "store_experience"
_TIMEOUT = 18


def _bundle_path() -> Path:
    return bundle_root() / "addons" / "store_experience.json"


def fetch_store_experience_local() -> Optional[dict[str, Any]]:
    p = _bundle_path()
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def fetch_store_experience_github() -> Optional[dict[str, Any]]:
    try:
        r = httpx.get(_RAW_URL, timeout=_TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def get_store_experience_offline_first() -> dict[str, Any]:
    """محلي → كاش → {}."""
    loc = fetch_store_experience_local()
    if isinstance(loc, dict) and loc.get("schema_version"):
        return loc
    cached = cache_get(_CACHE_KEY)
    if isinstance(cached, dict) and cached.get("schema_version"):
        return cached
    if isinstance(loc, dict):
        return loc
    return {"schema_version": 1, "featured_model_ids": [], "contributors": []}


def refresh_store_experience_background(
    on_complete: Callable[[dict[str, Any], bool], None],
) -> None:
    """خيط خلفي: GitHub ثم كاش؛ on_complete(data, reached_remote)."""

    def _work():
        data = fetch_store_experience_github()
        remote = bool(data)
        if data:
            cache_set(_CACHE_KEY, data)
        else:
            data = get_store_experience_offline_first()
        on_complete(data, remote)

    Thread(target=_work, daemon=True).start()
