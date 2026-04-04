"""إعدادات موحّدة: متغيرات البيئة ومسارات المشاريع الشقيقة."""
from __future__ import annotations

import os
from pathlib import Path

PLATFORM_ROOT = Path(__file__).resolve().parent.parent

# مرجع المشروع الموحّد مع AliJaddi Cloud و AliJaddiAccount (لوحة Supabase)
_DEFAULT_SUPABASE_URL = "https://mfhtnfxdfpelrgzonxov.supabase.co"
SUPABASE_URL = os.getenv("SUPABASE_URL", _DEFAULT_SUPABASE_URL).rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
CLOUD_SYNC_APPLY_STARS = os.getenv("CLOUD_SYNC_APPLY_STARS", "true").lower() in (
    "1", "true", "yes",
)


def _default_sibling(name: str) -> Path:
    return PLATFORM_ROOT.parent / name


def cloud_project_root() -> Path:
    raw = os.getenv("ALIJADDI_CLOUD_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return _default_sibling("AliJaddi Cloud")


def account_project_root() -> Path:
    raw = os.getenv("ALIJADDI_ACCOUNT_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return _default_sibling("AliJaddiAccount")
