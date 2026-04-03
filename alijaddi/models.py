"""
سجل النماذج الموحّد — يطابق:
  - core.model_catalog في AliJaddi Cloud (هجرات Supabase)
  - AVAILABLE_MODELS في AliJaddiAccount/config.py
  - CANONICAL_MODEL_IDS في AliJaddi Cloud/python/integration/model_ids.py
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


MODEL_REGISTRY: Dict[str, ModelInfo] = {
    "euqid": {
        "name": "عقد",
        "description": "صياغة العقود وتحليل النصوص محلياً، مع اختيار مزامنة ملخص النشاط مع منصة علي جدّي",
        "icon": "📜",
        "project_folder": "Euqid",
        "launch_cmd": "python main.py",
        "cloud_table": "model_user_data",
    },
    "tahlil": {
        "name": "تحليل",
        "description": "تحليل بيانات واستبيانات — tahlil",
        "icon": "📊",
        "project_folder": "tahlil",
        "launch_cmd": "python launcher.py",
        "cloud_table": "model_user_data",
    },
    "zakhrafatan": {
        "name": "زخرفة",
        "description": "Zakhrafatan — توليد وتصنيف الزخارف العربية بالذكاء الاصطناعي",
        "icon": "🎨",
        "project_folder": "Zakhrafatan",
        "launch_cmd": "streamlit run main.py",
        "cloud_table": "model_user_data",
    },
    "sniper_perspective": {
        "name": "منظور القناص",
        "description": "SniperPerspective — تتبع YOLO بكاميرا الويب",
        "icon": "🎯",
        "project_folder": "SniperPerspective_Project",
        "launch_cmd": "python SniperPerspective.py",
        "cloud_table": "model_user_data",
    },
    "mudir": {
        "name": "مدير التواصل",
        "description": "Mudir Altawasul — جدولة ونشر على المنصات الاجتماعية",
        "icon": "📣",
        "project_folder": "Mudir Altawasul",
        "launch_cmd": "python run_desktop.py",
        "cloud_table": "social_post_queue",
    },
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


def get_ai_models() -> Dict[str, ModelInfo]:
    """يرجع فقط النماذج التي لها مشروع فعلي على سطح المكتب."""
    return {k: v for k, v in MODEL_REGISTRY.items() if v["project_folder"]}


def get_model(model_id: str) -> Optional[ModelInfo]:
    return MODEL_REGISTRY.get(model_id)
