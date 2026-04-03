"""
بيانات النماذج — تحميل ديناميكي من السجل المحلي + GitHub + Supabase.
يحتفظ بقائمة ثابتة كـ fallback إذا لم يتوفر السجل.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import flet as ft

# خريطة أسماء الأيقونات → كائنات Flet
_ICON_MAP = {
    "PALETTE_ROUNDED": ft.Icons.PALETTE_ROUNDED,
    "DESCRIPTION_ROUNDED": ft.Icons.DESCRIPTION_ROUNDED,
    "ANALYTICS_ROUNDED": ft.Icons.ANALYTICS_ROUNDED,
    "CAMPAIGN_ROUNDED": ft.Icons.CAMPAIGN_ROUNDED,
    "TRACK_CHANGES_ROUNDED": ft.Icons.TRACK_CHANGES_ROUNDED,
    "SMART_TOY_ROUNDED": ft.Icons.SMART_TOY_ROUNDED,
    "CODE_ROUNDED": ft.Icons.CODE_ROUNDED,
    "SCIENCE_ROUNDED": ft.Icons.SCIENCE_ROUNDED,
    "PSYCHOLOGY_ROUNDED": ft.Icons.PSYCHOLOGY_ROUNDED,
    "TRANSLATE_ROUNDED": ft.Icons.TRANSLATE_ROUNDED,
    "IMAGE_ROUNDED": ft.Icons.IMAGE_ROUNDED,
    "BRUSH_ROUNDED": ft.Icons.BRUSH_ROUNDED,
    "AUTO_AWESOME_ROUNDED": ft.Icons.AUTO_AWESOME_ROUNDED,
    "MEDICAL_SERVICES_ROUNDED": ft.Icons.MEDICAL_SERVICES_ROUNDED,
}


def _resolve_icon(name: str):
    if not name:
        return ft.Icons.SMART_TOY_ROUNDED
    return _ICON_MAP.get(name, ft.Icons.SMART_TOY_ROUNDED)


# ═══════════════════════ FALLBACK (ثابتة) ═══════════════════════

_BUILTIN_MODELS = [
    {
        "id": "zakhrafatan",
        "name": "زخرفة",
        "desc": "توليد وتصنيف الزخارف العربية بالذكاء الاصطناعي",
        "icon": ft.Icons.PALETTE_ROUNDED,
        "color": "#8B5CF6",
        "folder": "Zakhrafatan",
        "launch": "streamlit run main.py",
        "rating": 4.8,
        "users": 142,
        "active": True,
        "version": "1.0.0",
        "size_mb": 85,
        "download_url": "https://github.com/abdullahalmkotir-maker/AliJaddi/releases/download/models-v1.0/zakhrafatan.zip",
        "category": "ai-art",
    },
    {
        "id": "euqid",
        "name": "عقد",
        "desc": "إدارة وتحليل العقود الذكية",
        "icon": ft.Icons.DESCRIPTION_ROUNDED,
        "color": "#F97316",
        "folder": "Euqid",
        "launch": "python main.py",
        "rating": 4.9,
        "users": 208,
        "active": True,
        "version": "1.0.0",
        "size_mb": 45,
        "download_url": "https://github.com/abdullahalmkotir-maker/AliJaddi/releases/download/models-v1.0/euqid.zip",
        "category": "productivity",
    },
    {
        "id": "tahlil",
        "name": "تحليل",
        "desc": "تحليل بيانات واستبيانات ذكي",
        "icon": ft.Icons.ANALYTICS_ROUNDED,
        "color": "#3B82F6",
        "folder": "tahlil",
        "launch": "python launcher.py",
        "rating": 4.7,
        "users": 95,
        "active": True,
        "version": "1.0.0",
        "size_mb": 60,
        "download_url": "https://github.com/abdullahalmkotir-maker/AliJaddi/releases/download/models-v1.0/tahlil.zip",
        "category": "data-analysis",
    },
    {
        "id": "mudir",
        "name": "مدير التواصل",
        "desc": "جدولة ونشر المحتوى على المنصات الاجتماعية",
        "icon": ft.Icons.CAMPAIGN_ROUNDED,
        "color": "#06B6D4",
        "folder": "Mudir Altawasul",
        "launch": "python run_desktop.py",
        "rating": 4.6,
        "users": 73,
        "active": True,
        "version": "1.0.0",
        "size_mb": 35,
        "download_url": "https://github.com/abdullahalmkotir-maker/AliJaddi/releases/download/models-v1.0/mudir.zip",
        "category": "social-media",
    },
    {
        "id": "sniper_perspective",
        "name": "منظور القناص",
        "desc": "تتبع الأهداف بـ YOLO وكاميرا الويب",
        "icon": ft.Icons.TRACK_CHANGES_ROUNDED,
        "color": "#EF4444",
        "folder": "SniperPerspective_Project",
        "launch": "python SniperPerspective.py",
        "rating": 0,
        "users": 0,
        "active": False,
        "version": "0.1.0-beta",
        "size_mb": 120,
        "download_url": "",
        "category": "computer-vision",
    },
]


def _manifest_to_model(m: dict) -> dict:
    """تحويل manifest JSON إلى صيغة MODELS المستخدمة في الواجهة."""
    return {
        "id": m["id"],
        "name": m.get("name", m["id"]),
        "desc": m.get("desc", ""),
        "icon": _resolve_icon(m.get("icon", "")),
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
    """يقرأ جميع ملفات manifests المحلية ويحوّلها لقائمة نماذج."""
    here = Path(__file__).resolve()
    manifests_dir = None
    for p in here.parents:
        if p.name == "AliJaddi":
            manifests_dir = p / "addons" / "manifests"
            break
    if not manifests_dir or not manifests_dir.is_dir():
        return []

    models = []
    seen_ids = set()
    for f in sorted(manifests_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text("utf-8"))
            mid = data.get("id", f.stem)
            if mid not in seen_ids:
                seen_ids.add(mid)
                models.append(_manifest_to_model(data))
        except Exception:
            continue
    return models


def get_models() -> list[dict]:
    """نماذج ديناميكية: manifests أولاً، ثم fallback ثابت."""
    dynamic = load_models_from_manifests()
    if dynamic:
        builtin_ids = {m["id"] for m in dynamic}
        for fallback in _BUILTIN_MODELS:
            if fallback["id"] not in builtin_ids:
                dynamic.append(fallback)
        return dynamic
    return list(_BUILTIN_MODELS)


# للتوافق مع الكود الحالي
MODELS = get_models()


STORE_ITEMS = [
    {"name": "فتح نموذج إضافي",     "cost": 50,  "icon": ft.Icons.LOCK_OPEN_ROUNDED,   "color": "#3B82F6"},
    {"name": "ثيم حصري",            "cost": 30,  "icon": ft.Icons.COLOR_LENS_ROUNDED,   "color": "#8B5CF6"},
    {"name": "شارة مستخدم مميز",     "cost": 100, "icon": ft.Icons.VERIFIED_ROUNDED,     "color": "#F59E0B"},
    {"name": "تحليل متقدم (30 يوم)", "cost": 80,  "icon": ft.Icons.INSIGHTS_ROUNDED,     "color": "#22C55E"},
    {"name": "مساحة تخزين سحابية",   "cost": 60,  "icon": ft.Icons.CLOUD_UPLOAD_ROUNDED, "color": "#06B6D4"},
]

LEADERBOARD = [
    {"name": "أحمد",   "stars": 520, "rank": 1},
    {"name": "فاطمة",  "stars": 480, "rank": 2},
    {"name": "محمد",   "stars": 390, "rank": 3},
    {"name": "زينب",   "stars": 310, "rank": 4},
    {"name": "علي",    "stars": 275, "rank": 5},
    {"name": "نور",    "stars": 210, "rank": 6},
    {"name": "حسن",    "stars": 185, "rank": 7},
]
