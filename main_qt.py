"""
AliJaddi — Beta 0.5.1
Desktop application powered by Qt for Python (PySide6).
Supports: Windows • macOS • Android
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv


def _load_env():
    """بعد التثبيت: ‎.env‎ بجانب ‎.exe‎؛ أثناء التطوير: بجانب ‎main_qt.py‎."""
    exe_dir = Path(sys.executable).resolve().parent
    dev_dir = Path(__file__).resolve().parent
    if getattr(sys, "frozen", False):
        load_dotenv(exe_dir / ".env")
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            load_dotenv(Path(meipass) / ".env")
    else:
        load_dotenv(dev_dir / ".env")


_load_env()

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from alijaddi import __version__ as ALIJADDI_VERSION
from services.paths import primary_icon_path
from ui.theme_qt import ThemeManager
from ui.main_window import MainWindow
from ui import i18n


def main():
    app = QApplication(sys.argv)
    i18n.apply_to_app(app)
    app.setApplicationName("AliJaddi")
    app.setOrganizationName("AliJaddi")
    app.setApplicationVersion(ALIJADDI_VERSION)

    icon_path = primary_icon_path()
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    theme = ThemeManager()
    theme.apply(app)

    window = MainWindow(theme)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
