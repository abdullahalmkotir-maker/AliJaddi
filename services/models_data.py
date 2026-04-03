"""
بيانات النماذج — تحميل ديناميكي من السجل المحلي + GitHub + Supabase.
يُستخدم أساساً للتوافق والاختبارات؛ واجهة Qt تأخذ البيانات من ``model_catalog.load_qt_models``.
الأيقونات أسماء نصية (مفاتيح manifest) وليست كائنات واجهة.
"""
from __future__ import annotations

from services.model_catalog import load_raw_merged_entries
from services.paths import bundle_root
from services.platform_data import LEADERBOARD

_DEFAULT_ICON = "SMART_TOY_ROUNDED"


def _manifest_to_model(m: dict) -> dict:
    return {
        "id": m["id"],
        "name": m.get("name", m["id"]),
        "desc": m.get("desc", ""),
        "icon": (m.get("icon") or _DEFAULT_ICON).strip() or _DEFAULT_ICON,
        "color": m.get("color", "#3B82F6"),
        "folder": m.get("folder", m["id"]),
        "launch": m.get("launch", ""),
        "rating": m.get("rating", 0),
        "users": m.get("users", 0),
        "active": m.get("active", True),
        "version": m.get("version", "1.0.0"),
        "size_mb": m.get("size_mb", 0),
        "download_url": m.get("download_url", ""),
        "category": m.get("category", ""),
    }


def load_models_from_manifests() -> list[dict]:
    return [_manifest_to_model(x) for x in load_raw_merged_entries(bundle_root())]


def get_models() -> list[dict]:
    return load_models_from_manifests()


MODELS = get_models()

# عناصر وهمية للمتجر (أيقونات كمفاتيح نصية فقط)
STORE_ITEMS = [
    {"name": "فتح نموذج إضافي", "cost": 50, "icon": "LOCK_OPEN_ROUNDED", "color": "#3B82F6"},
    {"name": "ثيم حصري", "cost": 30, "icon": "COLOR_LENS_ROUNDED", "color": "#8B5CF6"},
    {"name": "شارة مستخدم مميز", "cost": 100, "icon": "VERIFIED_ROUNDED", "color": "#F59E0B"},
    {"name": "تحليل متقدم (30 يوم)", "cost": 80, "icon": "INSIGHTS_ROUNDED", "color": "#22C55E"},
    {"name": "مساحة تخزين سحابية", "cost": 60, "icon": "CLOUD_UPLOAD_ROUNDED", "color": "#06B6D4"},
]
