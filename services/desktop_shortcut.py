"""
اختصارات سطح المكتب (ويندوز) لمجلدات التطبيقات التي يديرها **مدير تنزيلات** علي جدّي.
يُظهر للمستخدم أيقونة باسم عربي (مثل «عقد») بينما المجلد الفعلي قد يكون Latin (Euqid).
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from services.paths import user_desktop_dir

_INVALID_WIN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _sanitize_shortcut_base(name: str) -> str:
    s = (name or "").strip() or "تطبيق"
    s = _INVALID_WIN.sub("_", s)
    return s[:120]


def create_hosted_app_desktop_shortcut(display_name: str, installed_folder: Path) -> Path | None:
    """
    ينشئ ملف .lnk على سطح المكتب (OneDrive Desktop أو Desktop).
    الهدف: فتح مجلد التطبيق في مستكشف الملفات.
    """
    if os.name != "nt":
        return None
    folder = Path(installed_folder)
    if not folder.is_dir():
        return None
    desktop = user_desktop_dir()
    if desktop is None or not desktop.is_dir():
        return None
    base = _sanitize_shortcut_base(display_name)
    lnk = desktop / f"{base}.lnk"
    target = str(folder.resolve())
    l_esc = str(lnk.resolve()).replace("'", "''")
    t_esc = target.replace("'", "''")
    ps = f"$ws=New-Object -ComObject WScript.Shell;$s=$ws.CreateShortcut('{l_esc}');$s.TargetPath='{t_esc}';$s.Save()"
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            check=True,
            capture_output=True,
            timeout=20,
        )
        return lnk if lnk.is_file() else None
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def remove_desktop_shortcut(path: str | Path) -> None:
    p = Path(path) if path else None
    if not p:
        return
    try:
        if p.is_file():
            p.unlink()
    except OSError:
        pass
