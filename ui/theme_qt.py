"""AliJaddi Qt Theme — Dark / Light + RTL Arabic."""
from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QPixmap, QPainter
from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import QApplication

from services.local_store import load_settings, set_setting

from alijaddi.visual_identity import (
    L_BG,
    L_HEADER,
    L_CARD,
    L_TEXT,
    L_TEXT2,
    L_BORDER,
    D_BG,
    D_HEADER,
    D_CARD,
    D_TEXT,
    D_TEXT2,
    D_BORDER,
    PRIMARY,
    PRIMARY_D,
    DANGER,
    SUCCESS,
    STAR,
    STAR_D,
    ACCENT_CYAN,
)


class ThemeManager:
    def __init__(self):
        s = load_settings()
        self._dark = s.get("theme", "dark") == "dark"

    # ─── properties ───
    @property
    def is_dark(self):
        return self._dark

    def toggle(self):
        self._dark = not self._dark
        set_setting("theme", "dark" if self._dark else "light")

    @property
    def bg(self):
        return D_BG if self._dark else L_BG

    @property
    def header(self):
        return D_HEADER if self._dark else L_HEADER

    @property
    def card(self):
        return D_CARD if self._dark else L_CARD

    @property
    def text(self):
        return D_TEXT if self._dark else L_TEXT

    @property
    def text2(self):
        return D_TEXT2 if self._dark else L_TEXT2

    @property
    def border(self):
        return D_BORDER if self._dark else L_BORDER

    @property
    def primary(self):
        return PRIMARY_D if self._dark else PRIMARY

    @property
    def star_color(self):
        return STAR_D if self._dark else STAR

    # ─── apply ───
    def apply(self, app: QApplication):
        app.setStyle("Fusion")
        font = QFont("Segoe UI", 10)
        font.setHintingPreference(QFont.PreferNoHinting)
        app.setFont(font)
        app.setStyleSheet(self._qss())

    def _qss(self) -> str:
        t = self
        hover_primary = PRIMARY if t._dark else PRIMARY_D
        return f"""
            QMainWindow, QDialog {{ background-color: {t.bg}; }}
            QWidget {{ color: {t.text}; }}
            QLabel {{ background: transparent; }}

            /* Scroll */
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{
                background: {t.bg}; width: 8px; border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {t.border}; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

            /* Inputs */
            QLineEdit {{
                background: {t.card}; border: 1px solid {t.border};
                border-radius: 12px; padding: 10px 14px;
                font-size: 14px; color: {t.text};
                selection-background-color: {t.primary};
            }}
            QLineEdit:focus {{ border-color: {t.primary}; }}

            /* Buttons */
            QPushButton {{
                border: none; border-radius: 10px;
                padding: 8px 18px; font-weight: 600; font-size: 13px;
            }}
            QPushButton#primary {{ background: {t.primary}; color: #FFF; }}
            QPushButton#primary:hover {{ background: {hover_primary}; }}
            QPushButton#danger  {{ background: {DANGER}; color: #FFF; }}
            QPushButton#outline {{
                background: transparent; border: 1px solid {t.border}; color: {t.text2};
            }}
            QPushButton#outline:hover {{ background: rgba(255,255,255,0.05); }}

            /* Tabs — وضوح أعلى مثل متاجر التطبيقات */
            QTabBar::tab {{
                min-height: 40px; padding: 10px 18px; margin: 4px 2px 0 2px;
                font-size: 13px; font-weight: 500; color: {t.text2};
                border: none; border-radius: 10px 10px 0 0;
                background: transparent;
            }}
            QTabBar::tab:selected {{
                color: {t.text}; font-weight: 700;
                background: rgba(59, 130, 246, 0.14);
                border-bottom: 3px solid {t.primary};
            }}
            QTabBar::tab:hover:!selected {{
                color: {t.text};
                background: {"rgba(0,0,0,0.06)" if not t._dark else "rgba(255,255,255,0.06)"};
            }}
            QTabWidget::pane {{ border: none; background: {t.bg}; }}

            /* Card frame */
            QFrame#card {{
                background: {t.card}; border: 1px solid {t.border}; border-radius: 16px;
            }}
            QFrame#headerBar {{
                background: {t.header}; border-bottom: 1px solid {t.border};
            }}
            QFrame#accentTop {{
                border: none; border-top-left-radius: 16px; border-top-right-radius: 16px;
            }}
            QFrame#footerBar {{
                background: {t.header}; border-top: 1px solid {t.border};
            }}

            /* Switch */
            QCheckBox {{ spacing: 8px; }}
            QCheckBox::indicator {{
                width: 38px; height: 20px; border-radius: 10px;
                border: 1px solid {t.border}; background: {t.border};
            }}
            QCheckBox::indicator:checked {{
                background: {t.primary}; border-color: {t.primary};
            }}

            /* Tooltips */
            QToolTip {{
                background: {t.card}; color: {t.text};
                border: 1px solid {t.border}; border-radius: 6px; padding: 4px 8px;
            }}

            /* Dock — لوحة تشغيل التطبيقات داخل المنصّة */
            QDockWidget#hostedAppDock {{
                color: {t.text};
            }}
            QDockWidget#hostedAppDock::title {{
                background: {t.header};
                padding: 10px 12px;
                border-bottom: 1px solid {t.border};
                font-weight: 600;
            }}
        """


def create_model_icon(letter: str, color: str, size: int = 44) -> QPixmap:
    """Colored rounded-rect with a letter — used for model cards."""
    dpr = 2
    real = size * dpr
    pm = QPixmap(real, real)
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(color))
    p.setPen(Qt.NoPen)
    r = size // 3
    p.drawRoundedRect(QRect(0, 0, size, size), r, r)
    p.setPen(QColor("#FFFFFF"))
    f = p.font()
    f.setPixelSize(size * 55 // 100)
    f.setBold(True)
    p.setFont(f)
    p.drawText(QRect(0, 0, size, size), Qt.AlignCenter, letter)
    p.end()
    return pm
