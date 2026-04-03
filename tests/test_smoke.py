"""اختبارات دخان خفيفة — تشغيل من جذر المشروع: pytest -q"""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_version_matches_beta():
    from alijaddi import __version__

    assert __version__ == "0.4.1-beta"


def test_local_registry_platform():
    from services.addon_manager import fetch_registry_local

    reg = fetch_registry_local()
    assert reg is not None
    assert reg.get("platform") == "0.4.1-beta"
    models = reg.get("models", [])
    assert len(models) >= 1


def test_apps_paths_resolve():
    from services.paths import bundle_root, primary_icon_path, apps_root

    assert bundle_root().is_dir()
    assert primary_icon_path().name.endswith(".png")
    ar = apps_root()
    assert ar.name == "downloads"
    assert ar.parent.name == ".alijaddi"


def test_main_window_constructible():
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    from ui.theme_qt import ThemeManager
    from ui.main_window import MainWindow

    w = MainWindow(ThemeManager())
    w.close()
    app.quit()
