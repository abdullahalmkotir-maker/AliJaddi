"""إشعارات Toast عائمة أنيقة — PySide6."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

from ui.theme_qt import SUCCESS, DANGER, PRIMARY, STAR


_ICONS = {"success": "✓", "error": "✗", "info": "ℹ", "warning": "⚠"}
_COLORS = {"success": SUCCESS, "error": DANGER, "info": PRIMARY, "warning": STAR}


class Toast(QWidget):
    """Floating notification that auto-hides after a few seconds."""

    def __init__(self, parent: QWidget, text: str, kind: str = "info", duration_ms: int = 3500):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        color = _COLORS.get(kind, PRIMARY)
        icon = _ICONS.get(kind, "ℹ")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setStyleSheet(
            f"background: {color}; border-radius: 12px; padding: 10px 20px;"
        )
        c_lay = QHBoxLayout(container)
        c_lay.setContentsMargins(16, 10, 16, 10)
        c_lay.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("color: #FFF; font-size: 16px; font-weight: bold; background: transparent;")
        c_lay.addWidget(icon_lbl)

        msg_lbl = QLabel(text)
        msg_lbl.setStyleSheet("color: #FFF; font-size: 13px; font-weight: 500; background: transparent;")
        msg_lbl.setFont(QFont("Segoe UI", 11))
        msg_lbl.setWordWrap(True)
        c_lay.addWidget(msg_lbl, 1)

        layout.addWidget(container)

        self.setMinimumWidth(280)
        self.setMaximumWidth(500)
        self.adjustSize()

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)

        self._fade_in = QPropertyAnimation(self._opacity, b"opacity")
        self._fade_in.setDuration(300)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.OutCubic)

        self._fade_out = QPropertyAnimation(self._opacity, b"opacity")
        self._fade_out.setDuration(500)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.InCubic)
        self._fade_out.finished.connect(self._cleanup)

        self._duration = duration_ms

    def show_toast(self):
        parent = self.parentWidget()
        if parent:
            pw = parent.width()
            x = (pw - self.width()) // 2
            y = 70
            global_pos = parent.mapToGlobal(parent.rect().topLeft())
            self.move(global_pos.x() + x, global_pos.y() + y)

        self.show()
        self._fade_in.start()
        QTimer.singleShot(self._duration, self._start_fade_out)

    def _start_fade_out(self):
        self._fade_out.start()

    def _cleanup(self):
        self.close()
        self.deleteLater()


def show_toast(parent: QWidget, text: str, kind: str = "info", duration_ms: int = 3500):
    """Convenience function to show a toast notification."""
    t = Toast(parent, text, kind, duration_ms)
    t.show_toast()
    return t
