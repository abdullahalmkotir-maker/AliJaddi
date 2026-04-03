"""
سجل النماذج — يُبنى من كتالوج manifests الموحّد (services.model_catalog)
مع إدخالات سحابية ثابتة بلا مجلد محلي.
"""
from __future__ import annotations

from typing import Dict, Optional, TypedDict


class ModelInfo(TypedDict):
    name: str
    description: str
    icon: str
    project_folder: str
    launch_cmd: str
    cloud_table: str


# إن فشل استيراد الكتالوج (بيئة ناقصة)
_FALLBACK_REGISTRY: Dict[str, ModelInfo] = {
    "euqid": {
        "name": "عقد",
        "description": "صياغة العقود وتحليل النصوص محلياً",
        "icon": "📜",
        "project_folder": "Euqid",
        "launch_cmd": "python main.py",
        "cloud_table": "model_user_data",
    },
    "tahlil": {
        "name": "تحليل",
        "description": "تحليل بيانات واستبيانات",
        "icon": "📊",
        "project_folder": "statistics",
        "launch_cmd": "streamlit run app.py",
        "cloud_table": "model_user_data",
    },
    "zakhrafatan": {
        "name": "زخرفة",
        "description": "توليد وتصنيف الزخارف العربية",
        "icon": "🎨",
        "project_folder": "Zakhrafatan",
        "launch_cmd": "streamlit run main.py",
        "cloud_table": "model_user_data",
    },
    "sniper_perspective": {
        "name": "منظور القناص",
        "description": "تتبع YOLO",
        "icon": "🎯",
        "project_folder": "SniperPerspective_Project",
        "launch_cmd": "python SniperPerspective.py",
        "cloud_table": "model_user_data",
    },
    "mudir": {
        "name": "مدير التواصل",
        "description": "جدولة ونشر",
        "icon": "📣",
        "project_folder": "Mudir Altawasul",
        "launch_cmd": "python run_desktop.py",
        "cloud_table": "social_post_queue",
    },
}

_CLOUD_ONLY: Dict[str, ModelInfo] = {
    "legal": {
        "name": "قانون",
        "description": "استعلامات قانونية وتحليل العقود",
        "icon": "⚖️",
        "project_folder": "",
        "launch_cmd": "",
        "cloud_table": "model_user_data",
    },
    "maps": {
        "name": "خرائط",
        "description": "عرض وتحليل الخرائط",
        "icon": "🗺️",
        "project_folder": "",
        "launch_cmd": "",
        "cloud_table": "model_user_data",
    },
    "adich": {
        "name": "أدّيش",
        "description": "نموذج أدّيش — عرض وربط مع السحابة",
        "icon": "✨",
        "project_folder": "",
        "launch_cmd": "",
        "cloud_table": "model_user_data",
    },
    "sniper": {
        "name": "قناص",
        "description": "لعبة تفاعلية",
        "icon": "🎯",
        "project_folder": "",
        "launch_cmd": "",
        "cloud_table": "model_user_data",
    },
}


def _build_registry() -> Dict[str, ModelInfo]:
    try:
        from services.model_catalog import load_raw_merged_entries, entries_to_launcher_registry
        from services.paths import bundle_root

        raw = load_raw_merged_entries(bundle_root())
        conv = entries_to_launcher_registry(raw)
        out: Dict[str, ModelInfo] = {}
        for mid, row in conv.items():
            out[mid] = ModelInfo(
                name=row["name"],
                description=row["description"],
                icon=row["icon"],
                project_folder=row["project_folder"],
                launch_cmd=row["launch_cmd"],
                cloud_table=row["cloud_table"],
            )
        for k, v in _CLOUD_ONLY.items():
            if k not in out:
                out[k] = v
        return out
    except Exception:
        out = dict(_FALLBACK_REGISTRY)
        for k, v in _CLOUD_ONLY.items():
            if k not in out:
                out[k] = v
        return out


MODEL_REGISTRY: Dict[str, ModelInfo] = _build_registry()


def get_ai_models() -> Dict[str, ModelInfo]:
    """يرجع فقط النماذج التي لها مشروع فعلي على سطح المكتب."""
    return {k: v for k, v in MODEL_REGISTRY.items() if v["project_folder"]}


def get_model(model_id: str) -> Optional[ModelInfo]:
    return MODEL_REGISTRY.get(model_id)


def refresh_registry() -> None:
    """للاختبارات أو إعادة تحميل الكتالوج بعد تغيير الملفات (نادر)."""
    global MODEL_REGISTRY
    MODEL_REGISTRY = _build_registry()
