"""
كتالوج التطبيقات الموحّد — مصدر واحد لـ Qt و CLI (manifests + دمج ذكي + احتياطي).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from services.addon_manager import version_sort_tuple
from services.paths import bundle_root

# أيقونات نصية للـ CLI / تقارير الحالة (ليست مفاتيح Flet)
_LAUNCHER_ICON: dict[str, str] = {
    "zakhrafatan": "🎨",
    "euqid": "📜",
    "tahlil": "📊",
    "mudir": "📣",
    "sniper_perspective": "🎯",
    "dental_assistant": "🦷",
}


def launcher_display_icon(model_id: str) -> str:
    return _LAUNCHER_ICON.get(model_id, "📱")


def cloud_table_for(model_id: str) -> str:
    return "social_post_queue" if model_id == "mudir" else "model_user_data"


def _sort_by_version_desc(elist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        elist,
        key=lambda x: (
            version_sort_tuple(str(x.get("version", ""))),
            str(x.get("id", "")),
        ),
        reverse=True,
    )


def _sort_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """بطاقات ``store_pin`` أولاً، ثم أحدث إصدارات داخل كل مجموعة."""
    pinned = [x for x in entries if x.get("store_pin")]
    rest = [x for x in entries if not x.get("store_pin")]
    return _sort_by_version_desc(pinned) + _sort_by_version_desc(rest)


def read_manifest_dicts(manifests_dir: Path) -> list[dict[str, Any]]:
    if not manifests_dir.is_dir():
        return []
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for f in sorted(manifests_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            mid = str(data.get("id", f.stem))
            if mid in seen:
                continue
            seen.add(mid)
            data["id"] = mid
            out.append(data)
        except Exception:
            continue
    return _sort_entries(out)


# احتياطي عند غياب مجلد manifests (تثبيت تالف أو بيئة اختبار)
_FALLBACK_ENTRIES: list[dict[str, Any]] = [
    {
        "id": "zakhrafatan",
        "name": "زخرفة",
        "desc": "توليد وتصنيف الزخارف العربية بالذكاء الاصطناعي",
        "icon": "PALETTE_ROUNDED",
        "color": "#8B5CF6",
        "folder": "Zakhrafatan",
        "launch": "streamlit run main.py",
        "rating": 4.8,
        "users": 142,
        "active": True,
        "version": "1.0.0",
        "size_mb": 85,
        "download_url": "",
        "category": "ai-art",
    },
    {
        "id": "euqid",
        "name": "عقد",
        "desc": "إدارة وتحليل العقود الذكية",
        "icon": "DESCRIPTION_ROUNDED",
        "color": "#F97316",
        "folder": "Euqid",
        "launch": "python main.py",
        "rating": 4.9,
        "users": 208,
        "active": True,
        "version": "1.0.0",
        "size_mb": 45,
        "download_url": "",
        "category": "productivity",
    },
    {
        "id": "tahlil",
        "name": "تحليل",
        "desc": "تحليل بيانات واستبيانات ذكي",
        "icon": "ANALYTICS_ROUNDED",
        "color": "#3B82F6",
        "folder": "statistics",
        "launch": "streamlit run app.py",
        "rating": 4.7,
        "users": 95,
        "active": True,
        "version": "1.0.0",
        "size_mb": 60,
        "download_url": "",
        "category": "data-analysis",
    },
    {
        "id": "mudir",
        "name": "مدير التواصل",
        "desc": "جدولة ونشر المحتوى على المنصات الاجتماعية",
        "icon": "CAMPAIGN_ROUNDED",
        "color": "#06B6D4",
        "folder": "Mudir Altawasul",
        "launch": "python run_desktop.py",
        "rating": 4.6,
        "users": 73,
        "active": True,
        "version": "0.2.1-beta",
        "size_mb": 35,
        "download_url": "",
        "category": "social-media",
    },
    {
        "id": "sniper_perspective",
        "name": "منظور القناص",
        "desc": "تتبع الأهداف بـ YOLO وكاميرا الويب",
        "icon": "TRACK_CHANGES_ROUNDED",
        "color": "#EF4444",
        "folder": "SniperPerspective_Project",
        "launch": "python SniperPerspective.py",
        "rating": 0,
        "users": 0,
        "active": False,
        "version": "0.2.1-beta",
        "size_mb": 120,
        "download_url": "",
        "category": "computer-vision",
    },
    {
        "id": "dental_assistant",
        "name": "مساعد طبيب الأسنان",
        "desc": "إدارة عيادة الأسنان — تجربة تجريبية مع 198 مستخدم زائر؛ أحمد فلاح؛ Streamlit + مزامنة AliJaddi Cloud",
        "icon": "MEDICAL_SERVICES_ROUNDED",
        "color": "#0D9488",
        "folder": "AhmadFalahDentalAssistant",
        "launch": "streamlit run main.py",
        "rating": 4.6,
        "users": 198,
        "active": True,
        "version": "1.3.2",
        "size_mb": 50,
        "download_url": "https://raw.githubusercontent.com/abdullahalmkotir-maker/AliJaddi/main/packaging/dental_assistant.zip",
        "category": "medical",
    },
]


def merge_catalog_entries(
    from_disk: list[dict[str, Any]],
    fallback: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """من القرص أولاً؛ يُكمّل بالاحتياطي للمعرفات الناقصة. إن القرص فارغ يُستخدم الاحتياطي كاملاً."""
    disk = list(from_disk)
    if not disk:
        return _sort_entries([dict(x) for x in fallback])
    seen = {str(x.get("id", "")) for x in disk}
    for row in fallback:
        rid = str(row.get("id", ""))
        if rid and rid not in seen:
            disk.append(dict(row))
            seen.add(rid)
    return _sort_entries(disk)


def load_raw_merged_entries(root: Path | None = None) -> list[dict[str, Any]]:
    root = root or bundle_root()
    disk = read_manifest_dicts(root / "addons" / "manifests")
    return merge_catalog_entries(disk, _FALLBACK_ENTRIES)


def normalize_qt_model(m: dict[str, Any]) -> dict[str, Any]:
    """صيغة البطاقات في ui/main_window (بدون اعتماد على Flet)."""
    mid = str(m.get("id", ""))
    return {
        "id": mid,
        "name": str(m.get("name", mid)),
        "desc": str(m.get("desc", "")),
        "color": str(m.get("color", "#3B82F6")),
        "folder": str(m.get("folder", mid)),
        "launch": str(m.get("launch", "")),
        "rating": float(m.get("rating", 0) or 0),
        "users": int(m.get("users", 0) or 0),
        "active": bool(m.get("active", True)),
        "version": str(m.get("version", "1.0.0")),
        "size_mb": int(m.get("size_mb", 0) or 0),
        "download_url": str(m.get("download_url", "")),
        "category": str(m.get("category", "")),
        "store_only": bool(m.get("store_only", False)),
        "store_pin": bool(m.get("store_pin", False)),
    }


def load_qt_models(root: Path | None = None) -> list[dict[str, Any]]:
    return [normalize_qt_model(x) for x in load_raw_merged_entries(root)]


def entries_to_launcher_registry(
    entries: list[dict[str, Any]],
) -> dict[str, dict[str, str]]:
    """قاموس معلومات التشغيل لـ alijaddi.models (بدون TypedDict هنا لتفادي دوران الاستيراد)."""
    reg: dict[str, dict[str, str]] = {}
    for m in entries:
        mid = str(m.get("id", ""))
        if not mid or m.get("store_only"):
            continue
        reg[mid] = {
            "name": str(m.get("name", mid)),
            "description": str(m.get("desc", "")),
            "icon": launcher_display_icon(mid),
            "project_folder": str(m.get("folder", "")),
            "launch_cmd": str(m.get("launch", "")),
            "cloud_table": cloud_table_for(mid),
        }
    return reg
