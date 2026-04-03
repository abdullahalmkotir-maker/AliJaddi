"""
خدمة التخزين المحلي — يعمل بدون انترنت.
يحفظ: إعدادات، جلسة تسجيل الدخول، مفضلات، إحصائيات الاستخدام، كاش سحابي.
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Optional

_DIR = Path.home() / ".alijaddi"
_DIR.mkdir(parents=True, exist_ok=True)

_SETTINGS_FILE = _DIR / "settings.json"
_SESSION_FILE = _DIR / "session.json"
_STATS_FILE = _DIR / "usage_stats.json"
_CACHE_FILE = _DIR / "cloud_cache.json"

_lock = Lock()


def _read(path: Path, default: Any = None) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text("utf-8"))
    except Exception:
        pass
    return default if default is not None else {}


def _write(path: Path, data: Any):
    with _lock:
        try:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
        except Exception:
            pass


# ═══════════════════════ SETTINGS ═══════════════════════

_DEFAULT_SETTINGS = {
    "theme": "dark",
    "language": "ar",
    "notifications": True,
    "auto_sync": True,
    "sync_stars": True,
    "first_run": True,
    "onboarding_dismissed": False,
}


def load_settings() -> dict:
    s = _read(_SETTINGS_FILE, _DEFAULT_SETTINGS.copy())
    for k, v in _DEFAULT_SETTINGS.items():
        s.setdefault(k, v)
    return s


def save_settings(s: dict):
    _write(_SETTINGS_FILE, s)


def get_setting(key: str, default=None):
    return load_settings().get(key, default)


def set_setting(key: str, value):
    s = load_settings()
    s[key] = value
    save_settings(s)


# ═══════════════════════ SESSION ═══════════════════════

def save_session(
    email: str,
    user_id: str,
    access_token: str,
    refresh_token: str,
    stars: int = 0,
    username: str = "",
    display_name: str = "",
):
    _write(_SESSION_FILE, {
        "email": email,
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "stars": stars,
        "username": username,
        "display_name": display_name,
        "saved_at": datetime.now().isoformat(),
    })


def load_session() -> Optional[dict]:
    data = _read(_SESSION_FILE)
    if data and data.get("access_token"):
        return data
    return None


def clear_session():
    _write(_SESSION_FILE, {})


# ═══════════════════════ USAGE STATS ═══════════════════════

def _load_stats() -> dict:
    return _read(_STATS_FILE, {
        "models": {},
        "favorites": [],
        "total_launches": 0,
        "last_model": None,
    })


def _save_stats(s: dict):
    _write(_STATS_FILE, s)


def record_launch(model_id: str):
    s = _load_stats()
    if model_id not in s["models"]:
        s["models"][model_id] = {"launches": 0, "total_seconds": 0, "first_used": None, "last_used": None}
    m = s["models"][model_id]
    m["launches"] += 1
    now = datetime.now().isoformat()
    if not m["first_used"]:
        m["first_used"] = now
    m["last_used"] = now
    s["total_launches"] += 1
    s["last_model"] = model_id
    _save_stats(s)


def get_model_stats(model_id: str) -> dict:
    s = _load_stats()
    return s["models"].get(model_id, {"launches": 0, "total_seconds": 0, "first_used": None, "last_used": None})


def get_all_stats() -> dict:
    return _load_stats()


def toggle_favorite(model_id: str) -> bool:
    """يبدّل المفضلة ويرجع True إذا أصبح مفضلاً."""
    s = _load_stats()
    if model_id in s["favorites"]:
        s["favorites"].remove(model_id)
        _save_stats(s)
        return False
    s["favorites"].append(model_id)
    _save_stats(s)
    return True


def is_favorite(model_id: str) -> bool:
    return model_id in _load_stats().get("favorites", [])


def get_last_model() -> Optional[str]:
    return _load_stats().get("last_model")


# ═══════════════════════ CLOUD CACHE ═══════════════════════

_CACHE_TTL = 3600  # ساعة واحدة


def cache_set(key: str, data: Any):
    c = _read(_CACHE_FILE, {})
    c[key] = {"data": data, "ts": time.time()}
    _write(_CACHE_FILE, c)


def cache_get(key: str) -> Optional[Any]:
    c = _read(_CACHE_FILE, {})
    entry = c.get(key)
    if entry and (time.time() - entry.get("ts", 0)) < _CACHE_TTL:
        return entry["data"]
    return None


def cache_clear():
    _write(_CACHE_FILE, {})
