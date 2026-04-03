"""نافذة تنزيل التطبيق مع شريط تقدم — PySide6."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QFrame,
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QFont

from ui.theme_qt import (
    ThemeManager, create_model_icon,
    PRIMARY, SUCCESS, DANGER, ACCENT_CYAN,
)


def _fmt_size(b: int) -> str:
    if b < 1024:
        return f"{b} B"
    if b < 1024 * 1024:
        return f"{b / 1024:.1f} KB"
    return f"{b / (1024 * 1024):.1f} MB"


def _fmt_speed(bps: int) -> str:
    if bps < 1024:
        return f"{bps} B/s"
    if bps < 1024 * 1024:
        return f"{bps / 1024:.0f} KB/s"
    return f"{bps / (1024 * 1024):.1f} MB/s"


def _fmt_eta(remaining_bytes: int, speed: int) -> str:
    if speed <= 0:
        return "..."
    secs = remaining_bytes / speed
    if secs < 60:
        return f"{int(secs)} ث"
    if secs < 3600:
        return f"{int(secs // 60)} د {int(secs % 60)} ث"
    return f"{int(secs // 3600)} س {int((secs % 3600) // 60)} د"


class DownloadDialog(QDialog):
    """نافذة تحميل مع شريط تقدم، سرعة التحميل، والوقت المتبقي."""

    progress_update = Signal(int, int, int, int, str)

    def __init__(self, model_name: str, model_color: str, theme: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme = theme
        self._cancelled = False

        self.setWindowTitle(f"تنزيل التطبيق — {model_name}")
        self.setFixedSize(480, 300)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        # Model header
        hdr = QHBoxLayout()
        icon_lbl = QLabel()
        letter = model_name[0] if model_name else "?"
        icon_lbl.setPixmap(create_model_icon(letter, model_color, 48))
        icon_lbl.setFixedSize(48, 48)
        hdr.addWidget(icon_lbl)

        hdr_col = QVBoxLayout()
        hdr_col.setSpacing(2)
        name_lbl = QLabel(model_name)
        name_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        hdr_col.addWidget(name_lbl)
        self.phase_lbl = QLabel("جارٍ الاتصال...")
        self.phase_lbl.setStyleSheet(f"color: {theme.text2}; font-size: 12px;")
        hdr_col.addWidget(self.phase_lbl)
        hdr.addLayout(hdr_col, 1)
        layout.addLayout(hdr)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {theme.border};
                border: none;
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {model_color}, stop:1 {PRIMARY});
                border-radius: 6px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        # Percentage
        self.pct_lbl = QLabel("0%")
        self.pct_lbl.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.pct_lbl.setAlignment(Qt.AlignCenter)
        self.pct_lbl.setStyleSheet(f"color: {model_color};")
        layout.addWidget(self.pct_lbl)

        # Details row
        details = QHBoxLayout()
        details.setSpacing(20)
        self.size_lbl = QLabel("0 / 0 MB")
        self.size_lbl.setStyleSheet(f"color: {theme.text2}; font-size: 12px;")
        self.size_lbl.setAlignment(Qt.AlignCenter)
        details.addWidget(self.size_lbl)

        sep1 = QLabel("•")
        sep1.setStyleSheet(f"color: {theme.border};")
        details.addWidget(sep1)

        self.speed_lbl = QLabel("0 KB/s")
        self.speed_lbl.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 12px; font-weight: 600;")
        self.speed_lbl.setAlignment(Qt.AlignCenter)
        details.addWidget(self.speed_lbl)

        sep2 = QLabel("•")
        sep2.setStyleSheet(f"color: {theme.border};")
        details.addWidget(sep2)

        self.eta_lbl = QLabel("الوقت المتبقي: ...")
        self.eta_lbl.setStyleSheet(f"color: {theme.text2}; font-size: 12px;")
        self.eta_lbl.setAlignment(Qt.AlignCenter)
        details.addWidget(self.eta_lbl)
        layout.addLayout(details)

        layout.addStretch()

        # Cancel button
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("outline")
        self.cancel_btn.setMinimumHeight(38)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_btn)

        self.progress_update.connect(self._on_progress)

    @Slot(int, int, int, int, str)
    def _on_progress(self, pct: int, downloaded: int, total: int, speed: int, phase: str):
        if self._cancelled:
            return

        self.progress_bar.setValue(pct)
        self.pct_lbl.setText(f"{pct}%")

        if phase == "connecting":
            self.phase_lbl.setText("جارٍ الاتصال بالخادم...")
        elif phase == "downloading":
            self.phase_lbl.setText("جارٍ التحميل...")
            self.size_lbl.setText(f"{_fmt_size(downloaded)} / {_fmt_size(total)}")
            self.speed_lbl.setText(_fmt_speed(speed))
            remaining = total - downloaded
            self.eta_lbl.setText(f"المتبقي: {_fmt_eta(remaining, speed)}")
        elif phase == "extracting":
            self.phase_lbl.setText("جارٍ فك الضغط وتثبيت الملفات...")
            self.speed_lbl.setText("—")
            self.eta_lbl.setText("يكاد ينتهي...")
        elif phase == "done":
            self.phase_lbl.setText("✓ تم التثبيت بنجاح!")
            self.phase_lbl.setStyleSheet(f"color: {SUCCESS}; font-size: 13px; font-weight: 600;")
            self.pct_lbl.setText("✓")
            self.pct_lbl.setStyleSheet(f"color: {SUCCESS};")
            self.cancel_btn.setText("إغلاق")
            self.cancel_btn.setStyleSheet(
                f"background: {SUCCESS}; color: #FFF; border-radius: 10px; "
                f"padding: 6px 14px; font-weight: 600; font-size: 13px; border: none;"
            )
            self.speed_lbl.setText("—")
            self.eta_lbl.setText("اكتمل")
        elif phase == "error":
            self.phase_lbl.setText("فشل التحميل")
            self.phase_lbl.setStyleSheet(f"color: {DANGER}; font-size: 13px; font-weight: 600;")
            self.cancel_btn.setText("إغلاق")

    def _on_cancel(self):
        self._cancelled = True
        self.reject()

    def emit_progress(self, pct, downloaded, total, speed, phase):
        self.progress_update.emit(pct, downloaded, total, speed, phase)
