"""اكتشاف وتشغيل مشاريع النماذج من منصة AliJaddi."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import PLATFORM_ROOT
from .models import MODEL_REGISTRY, ModelInfo, get_ai_models


def _desktop() -> Path:
    return PLATFORM_ROOT.parent


def discover_models() -> Dict[str, Tuple[ModelInfo, Path, bool]]:
    """يكتشف أي نماذج موجودة فعلاً على سطح المكتب ومعها rabt_cloud_sync.py."""
    desktop = _desktop()
    result: Dict[str, Tuple[ModelInfo, Path, bool]] = {}
    for model_id, info in get_ai_models().items():
        folder = desktop / info["project_folder"]
        if folder.is_dir():
            has_sync = (folder / "rabt_cloud_sync.py").is_file()
            if model_id == "mudir":
                has_sync = (folder / "mudir_altawasul" / "integration" / "rabt_cloud.py").is_file()
            result[model_id] = (info, folder, has_sync)
    return result


def launch_model(model_id: str) -> Optional[subprocess.Popen]:
    """يشغّل مشروع النموذج في عملية منفصلة."""
    info = MODEL_REGISTRY.get(model_id)
    if not info or not info["project_folder"]:
        return None
    folder = _desktop() / info["project_folder"]
    if not folder.is_dir():
        return None
    cmd = info["launch_cmd"]
    if not cmd:
        return None
    return subprocess.Popen(
        cmd,
        cwd=str(folder),
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def status_report() -> str:
    models = discover_models()
    lines: List[str] = []
    lines.append("=" * 55)
    lines.append("  AliJaddi — AI Models Status")
    lines.append("=" * 55)
    if not models:
        lines.append("  (no model projects found on Desktop)")
    for mid, (info, path, has_sync) in models.items():
        sync_tag = "cloud OK" if has_sync else "NO cloud sync"
        lines.append(f"  {info['icon']} [{mid}] {info['name']}")
        lines.append(f"      {path}")
        lines.append(f"      launch: {info['launch_cmd']}  |  {sync_tag}")
        lines.append("")
    lines.append("=" * 55)
    return "\n".join(lines)
