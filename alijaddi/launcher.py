"""اكتشاف وتشغيل مشاريع النماذج من منصة AliJaddi."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import PLATFORM_ROOT
from .models import MODEL_REGISTRY, ModelInfo, get_ai_models

try:
    from services.paths import app_dir as _app_dir
except ImportError:
    _app_dir = None


def _has_cloud_sync(folder: Path, model_id: str) -> bool:
    """يتعرّف على سكربت مزامنة علي جدي سحابة."""
    if model_id == "mudir":
        return (folder / "mudir_altawasul" / "integration" / "alijaddi_cloud.py").is_file()
    return (folder / "alijaddi_cloud_sync.py").is_file()


def discover_models() -> Dict[str, Tuple[ModelInfo, Path, bool]]:
    """يكتشف النماذج على سطح المكتب وما إذا كانت تتضمّن مزامنة علي جدي سحابة."""
    result: Dict[str, Tuple[ModelInfo, Path, bool]] = {}
    for model_id, info in get_ai_models().items():
        pf = (info.get("project_folder") or "").strip()
        if not pf:
            continue
        if _app_dir is not None:
            folder = _app_dir(pf)
        else:
            folder = PLATFORM_ROOT.parent / pf
        if folder.is_dir():
            result[model_id] = (info, folder, _has_cloud_sync(folder, model_id))
    return result


def launch_model(model_id: str) -> Optional[subprocess.Popen]:
    """يشغّل مشروع النموذج في عملية منفصلة."""
    info = MODEL_REGISTRY.get(model_id)
    if not info or not info["project_folder"]:
        return None
    pf = (info.get("project_folder") or "").strip()
    if _app_dir is not None:
        folder = _app_dir(pf)
    else:
        folder = PLATFORM_ROOT.parent / pf
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
