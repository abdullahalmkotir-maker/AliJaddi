"""بيانات النماذج — مع تقييم وحالة وأيقونات."""
from __future__ import annotations
import flet as ft

MODELS = [
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
    },
]

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
