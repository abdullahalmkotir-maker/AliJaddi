"""
بيانات عرض مشتركة بين واجهة Qt و Flet (لوحة المتصدرين، …).
"""
from __future__ import annotations

# احتياطي عند عدم جلب store_experience.json من المستودع
LEADERBOARD_FALLBACK = [
    {"name": "أحمد", "stars": 520, "rank": 1},
    {"name": "فاطمة", "stars": 480, "rank": 2},
    {"name": "محمد", "stars": 390, "rank": 3},
    {"name": "زينب", "stars": 310, "rank": 4},
    {"name": "علي", "stars": 275, "rank": 5},
    {"name": "نور", "stars": 210, "rank": 6},
    {"name": "حسن", "stars": 185, "rank": 7},
]

LEADERBOARD = LEADERBOARD_FALLBACK
