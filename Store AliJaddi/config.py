"""إعدادات «متجر علي جدّي» — نسخة مستقلة داخل Store AliJaddi."""
import os
import warnings
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

DATABASE_PATH = "data/users.db"
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8502))
API_DEBUG = os.getenv("API_DEBUG", "false").lower() in ("1", "true", "yes")

# المشروع الرسمي: nzevwjghbvrrmmshnvem (يُستبدل عبر .env عند الحاجة)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://nzevwjghbvrrmmshnvem.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
CLOUD_SYNC_APPLY_STARS = os.getenv("CLOUD_SYNC_APPLY_STARS", "true").lower() in ("1", "true", "yes")

AVAILABLE_MODELS = {
    "legal": {"name": "قانون", "description": "استعلامات قانونية", "icon": "⚖️"},
    "maps": {"name": "خرائط", "description": "خرائط", "icon": "🗺️"},
    "adich": {"name": "أدّيش", "description": "أدّيش — خدمة سحابية", "icon": "✨"},
    "sniper": {"name": "قناص", "description": "لعبة تفاعلية", "icon": "🎯"},
    "euqid": {"name": "عقد", "description": "Euqid", "icon": "📜"},
    "tahlil": {"name": "تحليل", "description": "تحليل بيانات", "icon": "📊"},
    "zakhrafatan": {"name": "زخرفة", "description": "Zakhrafatan", "icon": "🎨"},
    "sniper_perspective": {"name": "منظور القناص", "description": "YOLO", "icon": "🎯"},
    "mudir": {"name": "مدير التواصل", "description": "social_post_queue", "icon": "📣"},
    "dental_assistant": {"name": "مساعد طبيب الأسنان", "description": "عيادة", "icon": "🦷"},
    "qanun_example": {"name": "مثال قانون", "description": "qanun", "icon": "📋"},
    "alijaddi": {"name": "متجر علي جدّي", "description": "الكتالوج والتطبيقات", "icon": "🌟"},
}

try:
    from auth_model.model_ids import CANONICAL_MODEL_IDS

    _unk = set(AVAILABLE_MODELS) - CANONICAL_MODEL_IDS
    if _unk:
        warnings.warn(f"AVAILABLE_MODELS غير مدرج في CANONICAL_MODEL_IDS: {_unk}", stacklevel=2)
except ImportError:
    pass

LOGGING_FILE = "logs/ali_jaddi_store.log"
