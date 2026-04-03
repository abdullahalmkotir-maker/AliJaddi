# -*- coding: utf-8 -*-
"""
بطاقة «علي جدي» داخل متجر التطبيقات — يقرأ إصدار المنصّة من ``registry.json`` (حقل ``platform``)
بعد مزامنة السجل من المستودع، ويقارنه بـ ``alijaddi.__version__`` لعرض زر تحديث.
"""
from __future__ import annotations

from typing import Any, Optional

from alijaddi import __version__ as ALIJADDI_VERSION
from services.addon_manager import is_remote_version_newer

PLATFORM_STORE_ID = "alijaddi_platform"
_GITHUB_RELEASES_LATEST = "https://github.com/abdullahalmkotir-maker/AliJaddi/releases/latest"


def registry_platform_version(registry: dict[str, Any] | None) -> str:
    if not registry or not isinstance(registry, dict):
        return ""
    return str(registry.get("platform") or "").strip()


def platform_store_local_version() -> str:
    return str(ALIJADDI_VERSION or "").strip()


def platform_store_update_version(registry: dict[str, Any] | None) -> Optional[str]:
    """إصدار أحدث من سجل المتجر يغلب الإصدار المحلي، أو None."""
    remote = registry_platform_version(registry)
    local = platform_store_local_version()
    if remote and is_remote_version_newer(remote, local):
        return remote
    return None


def platform_releases_open_url() -> str:
    """رابط صفحة آخر إصدار على GitHub (تنزيل Setup / ZIP)."""
    return _GITHUB_RELEASES_LATEST
