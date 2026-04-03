"""إعدادات مشتركة لاختبارات AliJaddi."""
from __future__ import annotations

import os

# Qt بدون نافذة — ضروري لبيئات CI وسيرفرات العرض
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
