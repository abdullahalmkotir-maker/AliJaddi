"""
جسر PySide6 للتطبيقات المشغّلة من منصّة AliJaddi — مواءمة الألوان والخط دون نسخ يدوي.

الاستخدام في تطبيق فرعي (بعد QApplication):

    from PySide6.QtWidgets import QApplication
    from alijaddi.qt_host_bridge import apply_host_theme, is_hosted_launch

    app = QApplication(sys.argv)
    if is_hosted_launch():
        apply_host_theme(app)

متغيرات البيئة التي تضبطها المنصّة:
    ALIJADDI_PLATFORM_HOST=1
    ALIJADDI_THEME=dark|light
    ALIJADDI_APPS_ROOT=...  # جذر تنزيلات تطبيقات المتجر (افتراضي: .alijaddi/downloads)
"""
from __future__ import annotations

import os

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from alijaddi.visual_identity import (
    DANGER,
    theme_tokens,
    parse_theme_from_env,
)


def is_hosted_launch() -> bool:
    """هل العملية أُطلقت من لوحة تشغيل المنصّة؟"""
    v = (os.environ.get("ALIJADDI_PLATFORM_HOST") or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def host_prefers_dark() -> bool:
    """الوضع الداكن من البيئة أو افتراضي داكن."""
    parsed = parse_theme_from_env(os.environ.get("ALIJADDI_THEME"))
    if parsed is not None:
        return parsed
    return True


def fusion_stylesheet_for_host(dark: bool | None = None) -> str:
    """QSS مختصر يكفي لنوافذ أدوات صغيرة (متوافق مع منصّة AliJaddi)."""
    d = host_prefers_dark() if dark is None else dark
    t = theme_tokens(d)
    hover = t["primary_hover"]
    tab_hover_bg = "rgba(255,255,255,0.06)" if d else "rgba(0,0,0,0.06)"
    return f"""
        QMainWindow, QDialog {{ background-color: {t["bg"]}; }}
        QWidget {{ color: {t["text"]}; }}
        QLabel {{ background: transparent; }}
        QScrollArea {{ border: none; background: transparent; }}
        QLineEdit {{
            background: {t["card"]}; border: 1px solid {t["border"]};
            border-radius: 12px; padding: 10px 14px; font-size: 14px; color: {t["text"]};
            selection-background-color: {t["primary"]};
        }}
        QLineEdit:focus {{ border-color: {t["primary"]}; }}
        QPushButton {{
            border: none; border-radius: 10px; padding: 8px 18px;
            font-weight: 600; font-size: 13px;
        }}
        QPushButton#primary {{ background: {t["primary"]}; color: #FFF; }}
        QPushButton#primary:hover {{ background: {hover}; }}
        QPushButton#danger {{ background: {DANGER}; color: #FFF; }}
        QPushButton#outline {{
            background: transparent; border: 1px solid {t["border"]}; color: {t["text2"]};
        }}
        QPushButton#outline:hover {{ background: {tab_hover_bg}; }}
        QFrame#card {{
            background: {t["card"]}; border: 1px solid {t["border"]}; border-radius: 16px;
        }}
        QToolTip {{
            background: {t["card"]}; color: {t["text"]};
            border: 1px solid {t["border"]}; border-radius: 6px; padding: 4px 8px;
        }}
    """


def apply_host_theme(app: QApplication, dark: bool | None = None) -> bool:
    """
    يطبّق Fusion + QSS موحّد. إن كان dark=None يُقرأ من ALIJADDI_THEME.
    يعيد True إذا طُبّق النمط.
    """
    if dark is None:
        dark = host_prefers_dark()
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.PreferNoHinting)
    app.setFont(font)
    app.setStyleSheet(fusion_stylesheet_for_host(dark))
    return True
