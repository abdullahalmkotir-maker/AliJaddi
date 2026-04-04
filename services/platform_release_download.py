# -*- coding: utf-8 -*-
"""
تنزيل حزمة المنصّة من GitHub Releases — لمسار **Ali12** (`ali12_store_install.py platform`).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Optional

import httpx

_GITHUB_API_LATEST = (
    "https://api.github.com/repos/abdullahalmkotir-maker/AliJaddi/releases/latest"
)
_GITHUB_API_RELEASES = (
    "https://api.github.com/repos/abdullahalmkotir-maker/AliJaddi/releases"
)
_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "AliJaddi-Ali12-platform-download/1.0",
}


def fetch_latest_release_json() -> Optional[dict[str, Any]]:
    try:
        r = httpx.get(_GITHUB_API_LATEST, timeout=30, headers=_HEADERS)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def fetch_recent_releases(*, per_page: int = 30) -> list[dict[str, Any]]:
    """قائمة إصدارات حديثة (الأحدث أولاً) — لاختيار إصدار فيه حزمة منصّة وليس مجرد نماذج."""
    try:
        r = httpx.get(
            _GITHUB_API_RELEASES,
            params={"per_page": per_page},
            timeout=30,
            headers=_HEADERS,
        )
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
    except Exception:
        pass
    return []


def find_release_with_platform_asset(
    *,
    prefer: str,
    is_windows: bool,
) -> tuple[Optional[dict[str, Any]], Optional[tuple[str, str]]]:
    """
    يمرّ على الإصدارات حتى يجد أصول Setup/ZIP للمنصّة.
    يُرجع (release_dict, (اسم_الملف, url)) أو (None, None).
    """
    for rel in fetch_recent_releases():
        raw_assets = rel.get("assets")
        assets = raw_assets if isinstance(raw_assets, list) else []
        picked = pick_platform_asset(assets, prefer=prefer, is_windows=is_windows)
        if picked:
            return rel, picked
    return None, None


def _asset_name(a: dict[str, Any]) -> str:
    return str(a.get("name") or "").strip()


def _asset_url(a: dict[str, Any]) -> str:
    return str(a.get("browser_download_url") or "").strip()


def pick_platform_asset(
    assets: list[dict[str, Any]],
    *,
    prefer: str,
    is_windows: bool,
) -> Optional[tuple[str, str]]:
    """
    يختار أصل الإصدار: (اسم الملف, browser_download_url).
    ``prefer``: auto | setup | zip
    """
    if not assets:
        return None

    def candidates() -> list[dict[str, Any]]:
        return [a for a in assets if isinstance(a, dict) and _asset_url(a)]

    rows = candidates()
    if not rows:
        return None

    setup_re = re.compile(r"AliJaddi.*Setup\.exe$", re.I)
    zip_re = re.compile(r"AliJaddi.*Windows\.zip$", re.I)

    setups = [a for a in rows if setup_re.search(_asset_name(a))]
    zips = [a for a in rows if zip_re.search(_asset_name(a))]

    if prefer == "setup" and setups:
        a = setups[0]
        return _asset_name(a), _asset_url(a)
    if prefer == "zip" and zips:
        a = zips[0]
        return _asset_name(a), _asset_url(a)

    if prefer == "auto":
        if is_windows and setups:
            a = setups[0]
            return _asset_name(a), _asset_url(a)
        if zips:
            a = zips[0]
            return _asset_name(a), _asset_url(a)
        if setups:
            a = setups[0]
            return _asset_name(a), _asset_url(a)
        # أي ‎.exe / ‎.zip يحمل AliJaddi في الاسم
        for a in rows:
            n = _asset_name(a)
            if "alijaddi" in n.lower() and n.lower().endswith(".exe"):
                return n, _asset_url(a)
        for a in rows:
            n = _asset_name(a)
            if "alijaddi" in n.lower() and n.lower().endswith(".zip"):
                return n, _asset_url(a)
        # أسماء قديمة / يدوية: أي Setup.exe أو ‎*Windows*.zip
        for a in rows:
            n = _asset_name(a).lower()
            if n.endswith(".exe") and "setup" in n:
                return _asset_name(a), _asset_url(a)
        for a in rows:
            n = _asset_name(a).lower()
            if n.endswith(".zip") and ("windows" in n or "win64" in n or "portable" in n):
                return _asset_name(a), _asset_url(a)

    return None


def stream_download_to_file(
    url: str,
    dest: Path,
    *,
    on_progress: Optional[Callable[[str], None]] = None,
) -> Path:
    """تنزيل إلى ``dest`` (ملف كامل)."""
    import time as _time

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with httpx.stream(
            "GET",
            url,
            timeout=120,
            follow_redirects=True,
            headers=_HEADERS,
        ) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            t0 = _time.monotonic()
            last = 0.0
            with open(tmp, "wb") as f:
                for chunk in resp.iter_bytes(chunk_size=65536):
                    f.write(chunk)
                    downloaded += len(chunk)
                    now = _time.monotonic()
                    if on_progress and total and now - last >= 0.25:
                        last = now
                        pct = int(downloaded / total * 100)
                        on_progress(f"جارٍ التحميل... {pct}% ({downloaded // 1024 // 1024} ميجابايت)")
        tmp.replace(dest)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    return dest


def default_platform_download_dir() -> Path:
    from services.paths import apps_root

    d = apps_root() / "platform_update"
    d.mkdir(parents=True, exist_ok=True)
    return d.resolve()


def run_windows_setup(setup_path: Path) -> bool:
    """تشغيل المثبّت (المستخدم يتحمّل UAC)."""
    if sys.platform != "win32":
        return False
    try:
        subprocess.Popen(
            [str(setup_path)],
            cwd=str(setup_path.parent),
            shell=False,
        )
        return True
    except OSError:
        return False
