"""
ألوان وهوية AliJaddi — مصدر واحد للمنصّة (theme_qt) ولتطبيقات PySide6 المشغّلة من الحاضنة.
"""
from __future__ import annotations

from typing import TypedDict


class ThemeTokens(TypedDict):
    bg: str
    header: str
    card: str
    text: str
    text2: str
    border: str
    primary: str
    primary_hover: str


# فاتح
L_BG = "#F5F7FA"
L_HEADER = "#FFFFFF"
L_CARD = "#FFFFFF"
L_TEXT = "#1E293B"
L_TEXT2 = "#64748B"
L_BORDER = "#E2E8F0"

# داكن
D_BG = "#121826"
D_HEADER = "#1E293B"
D_CARD = "#1E293B"
D_TEXT = "#F1F5F9"
D_TEXT2 = "#94A3B8"
D_BORDER = "#334155"

# علامة
PRIMARY = "#3B82F6"
PRIMARY_D = "#2563EB"
DANGER = "#EF4444"
SUCCESS = "#22C55E"
STAR = "#F59E0B"
STAR_D = "#FBBF24"
ACCENT_CYAN = "#06B6D4"


def theme_tokens(dark: bool) -> ThemeTokens:
    """رموز الألوان النشطة حسب الوضع."""
    if dark:
        return ThemeTokens(
            bg=D_BG,
            header=D_HEADER,
            card=D_CARD,
            text=D_TEXT,
            text2=D_TEXT2,
            border=D_BORDER,
            primary=PRIMARY_D,
            primary_hover=PRIMARY,
        )
    return ThemeTokens(
        bg=L_BG,
        header=L_HEADER,
        card=L_CARD,
        text=L_TEXT,
        text2=L_TEXT2,
        border=L_BORDER,
        primary=PRIMARY,
        primary_hover=PRIMARY_D,
    )


def parse_theme_from_env(value: str | None) -> bool | None:
    """None إن لم يُضبط؛ True داكن، False فاتح."""
    if value is None or not str(value).strip():
        return None
    v = str(value).strip().lower()
    if v in ("dark", "1", "true", "yes", "d"):
        return True
    if v in ("light", "0", "false", "no", "l"):
        return False
    return None
