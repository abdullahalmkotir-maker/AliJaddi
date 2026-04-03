"""
لوحة تشغيل التطبيقات داخل المنصّة — QProcess + سجل موحّد + رابط Streamlit.
لا يُخفى النافذة الخارجية بالكامل (Streamlit/Qt تفتح نوافذها)، لكن المستخدم يبقى مرتبطاً بالمنصّة.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from services.install_telemetry import emit_install_event
from services.shell_launch import prepare_shell_command
from PySide6.QtCore import Qt, QProcess, QProcessEnvironment, QUrl
from PySide6.QtGui import QDesktopServices, QFont, QTextCursor, QGuiApplication
from PySide6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QFrame,
)

if TYPE_CHECKING:
    from ui.theme_qt import ThemeManager

STREAMLIT_URL_RE = re.compile(
    r"(https?://(?:127\.0\.0\.1|localhost):\d+[^\s]*)",
    re.IGNORECASE,
)
_LOG_MAX = 200_000


class HostedAppDock(QDockWidget):
    """شريط جانبي/سفلي: تشغيل مرتبط بالمنصّة مع مخرجات حيّة."""

    def __init__(self, theme: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme = theme
        self._streamlit_url: Optional[str] = None
        self.setObjectName("hostedAppDock")
        self.setWindowTitle("تشغيل داخل المنصّة — Ali12 يسجّل الأعطال للتعلم")
        self.setMinimumWidth(280)
        self.setFeatures(
            QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
        )

        wrap = QWidget()
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(10, 8, 10, 10)
        lay.setSpacing(8)

        self._title = QLabel("")
        self._title.setWordWrap(True)
        self._title.setStyleSheet(f"font-weight:700;color:{theme.text};font-size:14px;")
        lay.addWidget(self._title)

        self._hint_lbl = QLabel(
            "المجلد: «تطبيقات علي جدي» على سطح المكتب — راجع السجل للأخطاء؛ "
            "Streamlit: «فتح الواجهة» عند ظهور الرابط. أعطال التشغيل تُغذّي تدريب Ali12."
        )
        self._hint_lbl.setWordWrap(True)
        self._hint_lbl.setStyleSheet(f"color:{theme.text2};font-size:11px;")
        lay.addWidget(self._hint_lbl)

        self._url_row = QFrame()
        url_lay = QHBoxLayout(self._url_row)
        url_lay.setContentsMargins(0, 0, 0, 0)
        self._open_url_btn = QPushButton("فتح واجهة الويب (Streamlit)")
        self._open_url_btn.setVisible(False)
        self._open_url_btn.setCursor(Qt.PointingHandCursor)
        self._open_url_btn.clicked.connect(self._open_streamlit_url)
        url_lay.addWidget(self._open_url_btn)
        lay.addWidget(self._url_row)

        self.log = QTextEdit()
        self.log.setObjectName("hostedLog")
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Cascadia Mono", 10) if sys.platform == "win32" else QFont("Monospace", 10))
        self.log.setMinimumHeight(120)
        lay.addWidget(self.log, 1)

        btn_row = QHBoxLayout()
        self._stop_btn = QPushButton("إيقاف التشغيل")
        self._stop_btn.setCursor(Qt.PointingHandCursor)
        self._stop_btn.clicked.connect(self.stop)
        self._folder_btn = QPushButton("فتح مجلد التطبيق")
        self._folder_btn.setCursor(Qt.PointingHandCursor)
        self._folder_btn.clicked.connect(self._open_workdir)
        self._copy_btn = QPushButton("نسخ السجل")
        self._copy_btn.setObjectName("outline")
        self._copy_btn.setCursor(Qt.PointingHandCursor)
        self._copy_btn.clicked.connect(self._copy_log)
        self._clear_btn = QPushButton("مسح السجل")
        self._clear_btn.setObjectName("outline")
        self._clear_btn.setCursor(Qt.PointingHandCursor)
        self._clear_btn.clicked.connect(self._clear_log)
        btn_row.addWidget(self._stop_btn)
        btn_row.addWidget(self._folder_btn)
        btn_row.addWidget(self._copy_btn)
        btn_row.addWidget(self._clear_btn)
        btn_row.addStretch()
        lay.addLayout(btn_row)

        self.setWidget(wrap)
        self._apply_theme()

        self._proc = QProcess(self)
        self._proc.readyReadStandardOutput.connect(self._read_stdout)
        self._proc.readyReadStandardError.connect(self._read_stderr)
        self._proc.finished.connect(self._on_finished)
        self._proc.errorOccurred.connect(self._on_proc_error)

        self._cwd: Path = Path.cwd()
        self._app_title = ""
        self._model_id: str = ""
        self._prepared_cmd: str = ""

    def _apply_theme(self):
        t = self.theme
        self.log.setStyleSheet(
            f"QTextEdit#hostedLog {{ background:{t.card}; color:{t.text}; "
            f"border:1px solid {t.border}; border-radius:10px; padding:8px; }}"
        )

    def refresh_theme(self, theme: ThemeManager):
        self.theme = theme
        self._title.setStyleSheet(f"font-weight:700;color:{theme.text};font-size:14px;")
        self._hint_lbl.setStyleSheet(f"color:{theme.text2};font-size:11px;")
        self._apply_theme()

    def _read_stdout(self):
        data = bytes(self._proc.readAllStandardOutput()).decode("utf-8", errors="replace")
        self._append(data)

    def _read_stderr(self):
        data = bytes(self._proc.readAllStandardError()).decode("utf-8", errors="replace")
        self._append(data)

    def _append(self, text: str):
        if not text:
            return
        self.log.moveCursor(QTextCursor.MoveOperation.End)
        self.log.insertPlainText(text)
        doc = self.log.toPlainText()
        if len(doc) > _LOG_MAX:
            self.log.setPlainText(doc[-_LOG_MAX:])
        self.log.ensureCursorVisible()
        self._detect_streamlit_url(doc)

    def _detect_streamlit_url(self, doc: str):
        for m in STREAMLIT_URL_RE.finditer(doc):
            url = m.group(1).rstrip("/")
            if url and url != self._streamlit_url:
                self._streamlit_url = url
                self._open_url_btn.setVisible(True)
                self._open_url_btn.setToolTip(url)
                break

    def _open_streamlit_url(self):
        if self._streamlit_url:
            QDesktopServices.openUrl(QUrl(self._streamlit_url))

    def _open_workdir(self):
        if self._cwd.is_dir():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._cwd.resolve())))

    def _copy_log(self):
        cb = QGuiApplication.clipboard()
        if cb:
            cb.setText(self.log.toPlainText())

    def _clear_log(self):
        self.log.clear()
        self._append(f"المجلد: {self._cwd}\n(تم مسح السجل)\n\n")

    def _on_proc_error(self, _error: QProcess.ProcessError):
        self._append(f"\n✗ خطأ في العملية: {self._proc.errorString()}\n")
        self._stop_btn.setEnabled(True)

    def _on_finished(self, code: int, status: QProcess.ExitStatus):
        self._append(f"\n\n— انتهت العملية (رمز الخروج: {code}) —\n")
        if code != 0:
            emit_install_event(
                "launch_fail",
                model_id=self._model_id,
                success=False,
                detail={
                    "exit_code": int(code),
                    "title": self._app_title,
                    "cwd": str(self._cwd),
                    "launch_command": self._prepared_cmd,
                },
            )
        self._stop_btn.setEnabled(True)

    def stop(self):
        if self._proc.state() != QProcess.NotRunning:
            self._proc.kill()
            self._proc.waitForFinished(3000)
        self._stop_btn.setEnabled(True)

    def start_app(
        self,
        title: str,
        command: str,
        cwd: Path,
        env: dict,
        model_id: str = "",
    ):
        self.stop()
        self._app_title = title
        self._model_id = (model_id or "").strip()
        self._cwd = cwd
        self._title.setText(title)
        self.log.clear()
        self._streamlit_url = None
        self._open_url_btn.setVisible(False)
        self._append(f"المجلد: {cwd}\nالأمر: {command}\n\n")

        cmd_line = prepare_shell_command(command)
        self._prepared_cmd = (cmd_line[:500] if cmd_line else "").strip()
        if not cmd_line.strip():
            self._append("\n✗ أمر التشغيل فارغ — راجع manifest التطبيق.\n")
            emit_install_event(
                "launch_fail",
                model_id=self._model_id,
                success=False,
                detail={"phase": "empty_command", "title": title, "launch_command": ""},
            )
            self._stop_btn.setEnabled(True)
            self.show()
            return
        if os.name == "nt":
            shell = os.environ.get("COMSPEC", "cmd.exe")
            self._proc.setProgram(shell)
            self._proc.setArguments(["/c", cmd_line])
        else:
            self._proc.setProgram("/bin/sh")
            self._proc.setArguments(["-c", cmd_line])

        self._proc.setWorkingDirectory(str(cwd.resolve()))
        qenv = QProcessEnvironment.systemEnvironment()
        for k, v in env.items():
            if v is not None:
                qenv.insert(str(k), str(v))
        self._proc.setProcessEnvironment(qenv)

        self._stop_btn.setEnabled(False)
        self._proc.start()
        if not self._proc.waitForStarted(8000):
            self._append("\n✗ تعذّر بدء العملية — تحقق من تثبيت Python أو Streamlit في PATH.\n")
            emit_install_event(
                "launch_fail",
                model_id=self._model_id,
                success=False,
                detail={
                    "phase": "start_timeout",
                    "title": title,
                    "cwd": str(cwd),
                    "launch_command": self._prepared_cmd,
                },
            )
            self._stop_btn.setEnabled(True)
        else:
            self._stop_btn.setEnabled(True)
        self.show()
        self.raise_()
