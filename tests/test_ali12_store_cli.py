"""تشغيل خفيف لسطر أوامر تثبيت المتجر (Ali12)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_ali12_store_cli_list():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "ali12_store_install.py"
    assert script.is_file()
    r = subprocess.run(
        [sys.executable, str(script), "list"],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=120,
        encoding="utf-8",
        errors="replace",
    )
    assert r.returncode == 0
    out = (r.stdout or "").lower()
    assert "dental_assistant" in out or "euqid" in out
