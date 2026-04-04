"""
جسر توافقية — يعيد تصدير واجهة المزامنة للكود القديم.
المنطق الكامل في platform_sync.py (موحّد مع AliJaddi / Cloud / Account).
"""
from platform_sync import (  # noqa: F401
    sync_payload_to_cloud,
    fetch_payload_from_cloud,
    build_sync_payload,
    fetch_user_stars,
    load_platform_session,
    save_platform_session,
    clear_platform_session,
)

__all__ = [
    "sync_payload_to_cloud",
    "fetch_payload_from_cloud",
    "build_sync_payload",
    "fetch_user_stars",
    "load_platform_session",
    "save_platform_session",
    "clear_platform_session",
]
