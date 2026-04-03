"""تنقل الواجهة الرئيسية Qt — شريط النشاط."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ui.theme_qt import ThemeManager
from ui.main_window import MainWindow


def test_main_window_sections_switch():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    theme = ThemeManager()
    w = MainWindow(theme)
    for idx in range(5):
        w._set_section(idx)
        assert w._section_index == idx
    w.close()
    app.quit()


def test_activity_rail_has_five_buttons():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    w = MainWindow(ThemeManager())
    assert len(w._activity_group.buttons()) == 5
    w.close()
    app.quit()
