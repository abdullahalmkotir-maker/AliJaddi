"""
AliJaddi — Beta 0.2
Desktop application powered by Qt for Python (PySide6).
Supports: Windows • macOS • Android
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from alijaddi import __version__ as ALIJADDI_VERSION
from ui.theme_qt import ThemeManager
from ui.main_window import MainWindow
from ui import i18n


def main():
    app = QApplication(sys.argv)
    i18n.apply_to_app(app)
    app.setApplicationName("AliJaddi")
    app.setOrganizationName("AliJaddi")
    app.setApplicationVersion(ALIJADDI_VERSION)

    icon_path = Path(__file__).resolve().parent / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    theme = ThemeManager()
    theme.apply(app)

    window = MainWindow(theme)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
