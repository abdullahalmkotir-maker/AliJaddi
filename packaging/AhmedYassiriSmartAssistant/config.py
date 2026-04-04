"""إعدادات مساعد طبيب الأسنان — تكامل مع AliJaddi / AliJaddi Cloud / AliJaddiAccount."""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = PROJECT_ROOT / "uploads"
BACKUPS_DIR = PROJECT_ROOT / "backups"
DB_PATH = DATA_DIR / "dental.db"

for _d in (DATA_DIR, UPLOADS_DIR, BACKUPS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ─── هوية النموذج (موحّدة مع core.model_catalog و manifests) ───
MODEL_ID = "yassiri_smart_assistant"
MODEL_NAME = "مساعد أحمد الياسري الذكي"
MODEL_VERSION = "1.0.1"
# عمود schema_version في جدول model_user_data (PostgREST)
MODEL_USER_DATA_SCHEMA_VERSION = 2

# ─── Supabase / AliJaddi Cloud ───
_DEFAULT_SUPABASE_URL = "https://mfhtnfxdfpelrgzonxov.supabase.co"
SUPABASE_URL = os.getenv("SUPABASE_URL", _DEFAULT_SUPABASE_URL).rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

CLOUD_SYNC_APPLY_STARS = os.getenv("CLOUD_SYNC_APPLY_STARS", "true").lower() in (
    "1", "true", "yes",
)

# ─── مسارات المشاريع الشقيقة (مثل AliJaddi/alijaddi/config.py) ───
def _sibling(name: str) -> Path:
    return PROJECT_ROOT.parent / name


def alijaddi_cloud_root() -> Path:
    raw = os.getenv("ALIJADDI_CLOUD_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return _sibling("AliJaddi Cloud")


def alijaddi_account_root() -> Path:
    raw = os.getenv("ALIJADDI_ACCOUNT_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return _sibling("AliJaddiAccount")


def alijaddi_platform_root() -> Path:
    raw = os.getenv("ALIJADDI_PLATFORM_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return _sibling("AliJaddi")


# ─── SQLite (عدة جلسات متصفح) ───
SQLITE_TIMEOUT_SEC = 30.0
SQLITE_BUSY_TIMEOUT_MS = 30000

ITEMS_PER_PAGE = 20
CURRENCY = "د.ع"

# ─── اختياري: تحميل .env من مجلد المشروع أو AliJaddi ───
def load_env_files() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    for path in (
        PROJECT_ROOT / ".env",
        alijaddi_platform_root() / ".env",
        alijaddi_account_root() / ".env",
    ):
        if path.is_file():
            load_dotenv(path, override=False)


load_env_files()

# إعادة قراءة المتغيرات بعد dotenv
SUPABASE_URL = os.getenv("SUPABASE_URL", _DEFAULT_SUPABASE_URL).rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

SESSION_TYPES = ["فحص أولي", "متابعة", "طارئ", "علاجي", "تجميلي", "جراحي"]
PROCEDURES = [
    "حشو مركب", "حشو أملغم", "حشو مؤقت",
    "خلع عادي", "خلع جراحي",
    "تنظيف عادي", "تنظيف عميق", "تلميع",
    "تبييض", "تبييض ليزر",
    "علاج عصب", "إعادة علاج عصب",
    "تركيب تاج", "تركيب جسر", "تركيب فينير",
    "زراعة", "ترقيع عظم",
    "تقويم أسنان", "تقويم شفاف",
    "قلع ضرس العقل",
    "تصريف خراج",
    "أشعة حول الذروة", "أشعة بانورامية", "أشعة CBCT",
    "فحص دوري",
    "مضاد حيوي", "مسكن ألم",
    "أخرى",
]
XRAY_TYPES = [
    "أشعة حول الذروة (Periapical)",
    "أشعة بانورامية (Panoramic/OPG)",
    "أشعة CBCT",
    "أشعة سيفالومترية (Cephalometric)",
    "أشعة Bitewing",
    "أخرى",
]
TOOTH_SURFACES = ["M (وسطي)", "O (إطباقي)", "D (بعيد)", "B (شفوي/دهليزي)", "L (لساني)", "I (قاطع)"]
APPOINTMENT_STATUSES = ["مؤكد", "مبدئي", "ملغى", "مكتمل", "لم يحضر"]
LAB_WORK_STATUSES = ["مُرسل للمختبر", "قيد التصنيع", "جاهز للاستلام", "مُستلم", "مُركّب"]
LAB_WORK_TYPES = ["تاج", "جسر", "طقم أسنان جزئي", "طقم أسنان كامل", "فينير", "تقويم شفاف", "حارس ليلي", "أخرى"]
TOOTH_NUMBERS = [str(i) for i in range(11, 19)] + [str(i) for i in range(21, 29)] + [str(i) for i in range(31, 39)] + [str(i) for i in range(41, 49)]
PRIMARY_COLOR = "#0D9488"
SECONDARY_COLOR = "#14B8A6"
ACCENT_COLOR = "#F59E0B"
DANGER_COLOR = "#EF4444"
SUCCESS_COLOR = "#22C55E"
