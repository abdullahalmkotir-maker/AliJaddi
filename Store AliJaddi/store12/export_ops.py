# -*- coding: utf-8 -*-
"""تصدير أرشيف ZIP لتوزيع متجر علي جدّي (نمط Ali12)."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from store12 import VERSION

EXCLUDE_DIR_NAMES = frozenset({
    ".git",
    "__pycache__",
    ".pytest_cache",
    "venv",
    ".venv",
    "releases",
    "dist",
    "build",
    ".streamlit",
    "node_modules",
    "tests",
})
EXCLUDE_FILE_NAMES = frozenset({".env"})
SKIP_SUFFIXES = (".pyc", ".db")


def _should_skip(rel: Path) -> bool:
    for p in rel.parts:
        if p in EXCLUDE_DIR_NAMES:
            return True
    if rel.name in EXCLUDE_FILE_NAMES:
        return True
    if rel.suffix.lower() in SKIP_SUFFIXES:
        return True
    return False


def build_release_zip(source_root: Path, dest_zip: Path, version: str | None = None) -> Path:
    """ZIP للتنزيل؛ جذر الأرشيف = AliJaddiStore-{version}/"""
    version = version or VERSION
    source_root = source_root.resolve()
    dest_zip = Path(dest_zip).resolve()
    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    arc_prefix = f"AliJaddiStore-{version}"

    manifest = {
        "app": "متجر علي جدّي",
        "version": version,
        "standard": "Ali12-style bundle",
        "entry_install": "Install-StoreAliJaddi.ps1",
        "entry_cli": "run_store12.py install",
    }

    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            f"{arc_prefix}/MANIFEST.json",
            json.dumps(manifest, ensure_ascii=False, indent=2),
        )
        for path in source_root.rglob("*"):
            if path.is_dir():
                continue
            if path.resolve() == dest_zip.resolve():
                continue
            try:
                rel = path.relative_to(source_root)
            except ValueError:
                continue
            if _should_skip(rel):
                continue
            zf.write(path, arcname=f"{arc_prefix}/{rel.as_posix()}")

    return dest_zip
