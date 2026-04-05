# -*- coding: utf-8 -*-
"""تثبيت متجر علي جدّي تحت %%LOCALAPPDATA%%\\AliJaddiStore (نمط Ali12)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from store12 import VERSION

APP_FOLDER_NAME = "AliJaddiStore"

COPY_NAMES = (
    "auth_model",
    "store",
    "platform_linking",
    "alijaddi_platform",
    "store12",
    "requirements-desktop.txt",
    "requirements.txt",
    "run.py",
    "run_desktop.py",
    "config.py",
    ".env.example",
    "README.md",
    "VERSION.txt",
    "run_store12.py",
    "Install-StoreAliJaddi.ps1",
)


def default_install_root() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / APP_FOLDER_NAME
    return Path.home() / "AppData" / "Local" / APP_FOLDER_NAME


def _ignore_copy(_d: str, names: list[str]) -> set[str]:
    skip = {"__pycache__", ".git", "venv", ".venv", "build", "dist", "releases", ".pytest_cache"}
    return {n for n in names if n in skip or n.endswith(".pyc")}


def copy_application_files(source_root: Path, app_dir: Path) -> None:
    app_dir.mkdir(parents=True, exist_ok=True)
    for name in COPY_NAMES:
        src = source_root / name
        if not src.exists():
            continue
        dst = app_dir / name
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, ignore=_ignore_copy)
        else:
            shutil.copy2(src, dst)
    data_dir = app_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)


def create_venv_and_pip(install_root: Path, app_dir: Path) -> Path:
    vpy = Path(sys.executable)
    venv_dir = install_root / "venv"
    subprocess.run([str(vpy), "-m", "venv", str(venv_dir)], check=True, cwd=str(install_root))
    if os.name == "nt":
        pip = venv_dir / "Scripts" / "python.exe"
    else:
        pip = venv_dir / "bin" / "python"
    req = app_dir / "requirements-desktop.txt"
    if not req.is_file():
        req = app_dir / "requirements.txt"
    subprocess.run([str(pip), "-m", "pip", "install", "-q", "-r", str(req)], check=True)
    return pip


def create_windows_shortcut(py_exe: Path, work_dir: Path, lnk_path: Path) -> None:
    if os.name != "nt":
        return
    lnk_path.parent.mkdir(parents=True, exist_ok=True)
    py_exe = py_exe.resolve()
    work_dir = work_dir.resolve()
    args = "-m streamlit run run.py --server.headless true --browser.gatherUsageStats false"
    ps = (
        "$W = New-Object -ComObject WScript.Shell; "
        f"$S = $W.CreateShortcut({json.dumps(str(lnk_path.resolve()))}); "
        f"$S.TargetPath = {json.dumps(str(py_exe))}; "
        f"$S.Arguments = {json.dumps(args)}; "
        f"$S.WorkingDirectory = {json.dumps(str(work_dir))}; "
        f"$S.Description = {json.dumps(f'متجر علي جدّي {VERSION}')}; "
        "$S.Save()"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        check=True,
        cwd=str(work_dir),
    )


def desktop_path() -> Path:
    one = Path.home() / "OneDrive" / "Desktop"
    if one.is_dir():
        return one
    return Path.home() / "Desktop"


def install(source_root: Path | None = None, install_root: Path | None = None) -> Path:
    """
    ينسخ التطبيق إلى LOCALAPPDATA\\AliJaddiStore\\app، ينشئ venv،
    يثبّت المتطلبات، ويضع اختصاراً على سطح المكتب (ويندوز).
    """
    if source_root is None:
        source_root = Path(__file__).resolve().parent.parent
    source_root = source_root.resolve()
    install_root = install_root or default_install_root()
    install_root = install_root.resolve()
    app_dir = install_root / "app"
    copy_application_files(source_root, app_dir)
    py_exe = create_venv_and_pip(install_root, app_dir)
    if os.name == "nt":
        lnk = desktop_path() / "متجر علي جدّي — بيتا.lnk"
        create_windows_shortcut(py_exe, app_dir, lnk)
    return install_root
