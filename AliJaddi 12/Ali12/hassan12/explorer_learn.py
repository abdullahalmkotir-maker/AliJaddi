# -*- coding: utf-8 -*-
"""تعلم أنماط التنظيم من مستكشف الملفات ومجلدات المستخدم في ويندوز."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def open_in_explorer(path: Path, select: bool = False) -> None:
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(str(path))
    if select and path.is_file():
        subprocess.Popen(  # noqa: S603
            ["explorer.exe", "/select,", str(path)],
            shell=False,
        )
    else:
        subprocess.Popen(["explorer.exe", str(path)], shell=False)  # noqa: S603


def known_profile_folders() -> dict[str, str]:
    """مسارات شائعة كما يعرضها مستكشف الملفات (أسماء عربية للمعرّف فقط)."""
    home = Path.home()
    out: dict[str, str] = {}
    mapping = {
        "سطح_المكتب": home / "OneDrive" / "Desktop",
        "سطح_المكتب_بديل": home / "Desktop",
        "المستندات": home / "OneDrive" / "Documents",
        "المستندات_بديل": home / "Documents",
        "التنزيلات": home / "Downloads",
        "الصور": home / "OneDrive" / "Pictures",
        "الصور_بديل": home / "Pictures",
        "الموسيقى": home / "Music",
        "الفيديو": home / "Videos",
    }
    for label, p in mapping.items():
        try:
            if p.is_dir():
                out[label] = str(p.resolve())
        except OSError:
            continue
    return out


def snapshot_tree(
    root: Path,
    max_depth: int = 2,
    max_nodes: int = 200,
) -> dict[str, Any]:
    """لقطة هيكلية (أسماء فقط) للمقارنة والاقتراح — لا يُرفع محتوى الملفات."""
    root = root.resolve()
    top: list[dict[str, Any]] = []

    def one_entry(ch: Path, depth: int) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "name": ch.name,
            "type": "dir" if ch.is_dir() else "file",
        }
        if ch.is_dir() and depth < max_depth:
            sub: list[dict[str, Any]] = []
            try:
                for ch2 in sorted(ch.iterdir(), key=lambda x: x.name.lower())[:40]:
                    sub.append(
                        {
                            "name": ch2.name,
                            "type": "dir" if ch2.is_dir() else "file",
                        }
                    )
            except OSError:
                pass
            entry["children"] = sub
        return entry

    count = 0
    try:
        for ch in sorted(root.iterdir(), key=lambda x: x.name.lower()):
            if count >= max_nodes:
                break
            if ch.name.startswith(".hassan12"):
                continue
            count += 1
            top.append(one_entry(ch, 1))
    except OSError:
        pass
    return {
        "root": str(root),
        "scanned_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "max_depth": max_depth,
        "top_level": top,
    }


def read_lnk_target(lnk_path: Path) -> str | None:
    """يقرأ هدف اختصار .lnk عبر PowerShell (بدون مكتبات إضافية)."""
    p = str(lnk_path.resolve())
    if "'" in p:
        p = p.replace("'", "''")
    script = (
        "$sh = New-Object -ComObject WScript.Shell; "
        f"$l = $sh.CreateShortcut([string](Convert-Path -LiteralPath '{p}')); "
        "$l.TargetPath"
    )
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-NoLogo", "-Command", script],
            capture_output=True,
            text=True,
            timeout=20,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    out = (r.stdout or "").strip()
    if not out or r.returncode != 0:
        return None
    candidate = Path(out)
    return str(candidate) if candidate.exists() else out


def save_learned_bundle(
    policy_dir: Path,
    label: str,
    payload: dict[str, Any],
) -> Path:
    policy_dir = Path(policy_dir)
    policy_dir.mkdir(parents=True, exist_ok=True)
    path = policy_dir / "learned_from_explorer.json"
    bundle: dict[str, Any]
    if path.is_file():
        try:
            bundle = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            bundle = {"sessions": []}
    else:
        bundle = {"sessions": []}
    if "sessions" not in bundle or not isinstance(bundle["sessions"], list):
        bundle["sessions"] = []
    bundle["sessions"].append(
        {
            "label": label,
            "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": payload,
        }
    )
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def learned_to_training_entries(policy_dir: Path) -> list[dict[str, str]]:
    """يحوّل آخر الجلسات المخزّنة إلى مقتطفات تدريب."""
    path = Path(policy_dir) / "learned_from_explorer.json"
    if not path.is_file():
        return []
    try:
        bundle = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    sessions = bundle.get("sessions") or []
    if not sessions:
        return []
    last = sessions[-1]
    data = last.get("data") or {}
    label = last.get("label", "")
    lines: list[str] = []
    if isinstance(data.get("top_level"), list):
        names = [n.get("name", "") for n in data["top_level"] if isinstance(n, dict)]
        lines.append("أمثلة مجلدات/ملفات في الجذر: " + ", ".join(names[:40]))
    kf = data.get("known_folders_snapshot")
    if isinstance(kf, dict):
        lines.append("مجلدات ملف تعريف ويندوز المستخدمة كمرجع: " + ", ".join(kf.keys()))
    text = "\n".join(lines) if lines else json.dumps(data, ensure_ascii=False)[:2000]
    return [
        {
            "role": "تنظيم_من_المستكشف",
            "content": f"{label}\n{text}",
        }
    ]
