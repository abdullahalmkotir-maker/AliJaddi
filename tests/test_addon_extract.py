"""أمان فك ضغط أرشيفات التثبيت."""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from services.addon_manager import _safe_extractall


def test_safe_extractall_normal(tmp_path: Path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("ok/hello.txt", b"hi")
    buf.seek(0)
    dest = tmp_path / "out"
    dest.mkdir()
    with zipfile.ZipFile(buf, "r") as zf:
        _safe_extractall(zf, dest)
    assert (dest / "ok" / "hello.txt").read_bytes() == b"hi"


def test_safe_extractall_rejects_zip_slip(tmp_path: Path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("../evil.txt", b"x")
    buf.seek(0)
    dest = tmp_path / "out"
    dest.mkdir()
    with zipfile.ZipFile(buf, "r") as zf:
        with pytest.raises(ValueError):
            _safe_extractall(zf, dest)
