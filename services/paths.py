"""
مسارات وقت التشغيل — حزمة PyInstaller، **مدير تنزيلات** علي جدّي (مجلدات التطبيقات المستخرجة)، الأيقونة الموحّدة.

التطبيقات المُنزَّلة من المتجر تُفكّ افتراضياً تحت ``~/.alijaddi/downloads/<folder>``.
التثبيتات القديمة تُحلّ عبر ``services.legacy_data`` (حاضنة سطح المكتب وغيرها).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from services.legacy_data import LEGACY_DESKTOP_HOST_DIR_NAME

# مجلد بيانات المنصّة (موحّد مع local_store)
_ALIJADDI_DATA = Path.home() / ".alijaddi"

# جذر «مدير التنزيلات»: أب مجلدات النماذج (اسم المجلد من manifest.folder)
STORE_DOWNLOADS_DIR_NAME = "downloads"

# توافق اختبارات/شيفرة قديمة: كان يشير لاسم مجلد الحاضنة
APPS_HOST_DIR_NAME = LEGACY_DESKTOP_HOST_DIR_NAME


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


def apps_root() -> Path:
    """
    جذر تنزيلات متجر علي جدّي (مدير التنزيلات): ``~/.alijaddi/downloads`` افتراضياً.
    يُنشأ تلقائياً. يمكن تجاوزه بـ ``ALIJADDI_APPS_ROOT`` (مسار أب لمجلدات التطبيقات).
    """
    override = (os.environ.get("ALIJADDI_APPS_ROOT") or "").strip()
    if override:
        p = Path(override).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()
    root = _ALIJADDI_DATA / STORE_DOWNLOADS_DIR_NAME
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


def app_dir(folder_name: str) -> Path:
    """
    مسار تطبيق مثبّت: مدير التنزيلات الحالي أولاً، ثم بيانات **قديمة** عبر ``legacy_data``.
    """
    from services.legacy_data import resolve_app_path_with_source

    path, _src = resolve_app_path_with_source(folder_name, apps_root())
    return path


def user_desktop_dir() -> Path | None:
    """أول سطح مكتب متاح (OneDrive أو Desktop) — لاختصارات .lnk."""
    from services.legacy_data import desktop_candidates

    for d in desktop_candidates():
        if d.is_dir():
            return d
    return None


def primary_icon_path() -> Path:
    """أيقونة الهوية: رندر Blender → assets/branding/app_icon.png، أو icon.png الاحتياطي."""
    root = bundle_root()
    branded = root / "assets" / "branding" / "app_icon.png"
    if branded.is_file():
        return branded
    return root / "icon.png"
