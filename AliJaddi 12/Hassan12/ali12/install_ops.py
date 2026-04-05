# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

APP_FOLDER_NAME = "Hassan12"
COPY_NAMES = (
    "hassan12",
    "ali12",
    "requirements.txt",
    "run_hassan12.py",
    "run_ali12.py",
    "Install-Ali12.ps1",
)


def default_install_root() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / APP_FOLDER_NAME
    return Path.home() / "AppData" / "Local" / APP_FOLDER_NAME


def _ignore_copy(d: str, names: list[str]) -> set[str]:
    skip = {"__pycache__", ".git", "venv", ".venv", "build", "dist", "مجلد_محمي"}
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


def create_venv_and_pip(install_root: Path, app_dir: Path) -> Path:
    vpy = Path(sys.executable)
    venv_dir = install_root / "venv"
    subprocess.run([str(vpy), "-m", "venv", str(venv_dir)], check=True, cwd=str(install_root))
    if os.name == "nt":
        pip = venv_dir / "Scripts" / "python.exe"
        pyw = venv_dir / "Scripts" / "pythonw.exe"
        if not pyw.is_file():
            pyw = pip
    else:
        pip = venv_dir / "bin" / "python"
        pyw = pip
    req = app_dir / "requirements.txt"
    if req.is_file():
        subprocess.run([str(pip), "-m", "pip", "install", "-q", "-r", str(req)], check=True)
    return pyw


def create_windows_shortcut(pyw: Path, script: Path, lnk_path: Path) -> None:
    if os.name != "nt":
        return
    lnk_path.parent.mkdir(parents=True, exist_ok=True)
    pyw = pyw.resolve()
    script = script.resolve()
    ps = (
        "$W = New-Object -ComObject WScript.Shell; "
        f"$S = $W.CreateShortcut({json.dumps(str(lnk_path.resolve()))}); "
        f"$S.TargetPath = {json.dumps(str(pyw))}; "
        f"$S.Arguments = {json.dumps(str(script))}; "
        f"$S.WorkingDirectory = {json.dumps(str(script.parent))}; "
        "$S.Save()"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        check=True,
        cwd=str(script.parent),
    )


def desktop_path() -> Path:
    one = Path.home() / "OneDrive" / "Desktop"
    if one.is_dir():
        return one
    return Path.home() / "Desktop"


def install(source_root: Path | None = None, install_root: Path | None = None) -> Path:
    if source_root is None:
        source_root = Path(__file__).resolve().parent.parent
    source_root = source_root.resolve()
    install_root = install_root or default_install_root()
    install_root = install_root.resolve()
    app_dir = install_root / "app"
    copy_application_files(source_root, app_dir)
    pyw = create_venv_and_pip(install_root, app_dir)
    launcher = app_dir / "run_hassan12.py"
    if os.name == "nt" and launcher.is_file():
        lnk = desktop_path() / "مدير الملفات Hassan12.lnk"
        create_windows_shortcut(pyw, launcher, lnk)
    return install_root
