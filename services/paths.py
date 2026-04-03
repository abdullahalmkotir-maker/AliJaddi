"""
مسارات وقت التشغيل — حزمة PyInstaller، حاضنة التطبيقات «تطبيقات علي جدي»، الأيقونة الموحّدة.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# اسم مجلد الحاضنة على سطح المكتب (ثقافيًا كما طلب المشروع)
APPS_HOST_DIR_NAME = "تطبيقات علي جدي"


def bundle_root() -> Path:
    """جذر موارد التطبيق: ‎_internal‎ بعد التجميع، أو جذر المستودع أثناء التطوير."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "addons" / "registry.json").is_file():
            return p
    for p in here.parents:
        if p.name == "AliJaddi":
            return p
    return here.parent.parent


def _desktop_candidates() -> list[Path]:
    home = Path.home()
    out: list[Path] = []
    for d in (home / "OneDrive" / "Desktop", home / "Desktop"):
        if d.is_dir():
            try:
                out.append(d.resolve())
            except Exception:
                out.append(d)
    return out


def apps_root() -> Path:
    """
    مجلد الحاضنة: يُنشأ تلقائياً إن لزم.
    يمكن تجاوزه بـ ALIJADDI_APPS_ROOT.
    """
    override = (os.environ.get("ALIJADDI_APPS_ROOT") or "").strip()
    if override:
        p = Path(override).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()
    for d in _desktop_candidates():
        root = d / APPS_HOST_DIR_NAME
        root.mkdir(parents=True, exist_ok=True)
        return root.resolve()
    p = (Path.home() / APPS_HOST_DIR_NAME)
    p.mkdir(parents=True, exist_ok=True)
    return p.resolve()


def app_dir(folder_name: str) -> Path:
    """
    مسار تطبيق مثبّت: داخل الحاضنة أولاً، ثم البحث في سطح المكتب (تثبيتات قديمة).
    """
    name = (folder_name or "").strip()
    primary = apps_root() / name
    if primary.is_dir():
        return primary
    for d in _desktop_candidates():
        legacy = d / name
        if legacy.is_dir():
            return legacy
    return primary


def primary_icon_path() -> Path:
    """أيقونة الهوية: رندر Blender → assets/branding/app_icon.png، أو icon.png الاحتياطي."""
    root = bundle_root()
    branded = root / "assets" / "branding" / "app_icon.png"
    if branded.is_file():
        return branded
    return root / "icon.png"
