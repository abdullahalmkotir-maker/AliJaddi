"""مسارات التشغيل — حزمة وجذر التطبيقات."""
from __future__ import annotations

from services.paths import (
    STORE_DOWNLOADS_DIR_NAME,
    app_dir,
    apps_root,
    bundle_root,
    primary_icon_path,
)


def test_bundle_root_exists():
    br = bundle_root()
    assert br.is_dir()
    assert (br / "addons" / "manifests").is_dir() or (br / "main_qt.py").is_file()


def test_primary_icon_exists():
    p = primary_icon_path()
    assert p.suffix.lower() in (".png", ".ico")


def test_apps_root_name():
    root = apps_root()
    assert root.name == STORE_DOWNLOADS_DIR_NAME
    assert root.is_dir()


def test_app_dir_returns_path_under_host():
    p = app_dir("NonexistentFolderXYZ123")
    assert p.name == "NonexistentFolderXYZ123"
    assert p.parent == apps_root()
