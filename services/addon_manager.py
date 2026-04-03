"""
مدير الإضافات — تحميل، تثبيت، تحديث، حذف النماذج.
• يجلب السجل من GitHub أولاً، ثم Supabase كمرآة
• يدعم العمل بدون إنترنت (كاش محلي)
• التثبيت: تحميل zip → فك الضغط → تسجيل محلي
"""
from __future__ import annotations

import json
import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from threading import Thread
from typing import Callable, Optional

import httpx

from services.local_store import cache_get, cache_set, _read, _write, _DIR

_GITHUB_REPO = "abdullahalmkotir-maker/AliJaddi"
_GITHUB_BRANCH = "main"
_REGISTRY_PATH = "addons/registry.json"
_MANIFEST_DIR = "addons/manifests"
_RAW_BASE = f"https://raw.githubusercontent.com/{_GITHUB_REPO}/{_GITHUB_BRANCH}"

_INSTALLED_FILE = _DIR / "installed_addons.json"
_REGISTRY_CACHE_KEY = "addon_registry"
_TIMEOUT = 20

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mfhtnfxdfpelrgzonxov.supabase.co").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


def _desktop() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if p.name == "AliJaddi":
            return p.parent
    home = Path.home()
    for candidate in [home / "OneDrive" / "Desktop", home / "Desktop", home]:
        if candidate.is_dir():
            return candidate
    return home


def _local_registry_path() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if p.name == "AliJaddi":
            return p / "addons" / "registry.json"
    return Path("addons/registry.json")


# ═══════════════════════ INSTALLED TRACKING ═══════════════════════

def load_installed() -> dict:
    return _read(_INSTALLED_FILE, {})


def _save_installed(data: dict):
    _write(_INSTALLED_FILE, data)


def mark_installed(model_id: str, version: str, folder: str):
    inst = load_installed()
    inst[model_id] = {
        "version": version,
        "folder": folder,
        "installed_at": __import__("datetime").datetime.now().isoformat(),
    }
    _save_installed(inst)


def mark_uninstalled(model_id: str):
    inst = load_installed()
    inst.pop(model_id, None)
    _save_installed(inst)


def is_installed(model_id: str) -> bool:
    inst = load_installed()
    if model_id in inst:
        folder = inst[model_id].get("folder", "")
        if folder and (_desktop() / folder).is_dir():
            return True
    return False


def installed_version(model_id: str) -> Optional[str]:
    return load_installed().get(model_id, {}).get("version")


# ═══════════════════════ REGISTRY FETCH ═══════════════════════

def fetch_registry_github() -> Optional[dict]:
    """جلب السجل من GitHub raw content."""
    try:
        r = httpx.get(f"{_RAW_BASE}/{_REGISTRY_PATH}", timeout=_TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            cache_set(_REGISTRY_CACHE_KEY, data)
            return data
    except Exception:
        pass
    return None


def fetch_registry_supabase() -> Optional[dict]:
    """جلب السجل من Supabase كمرآة."""
    if not SUPABASE_ANON_KEY:
        return None
    try:
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/addon_registry",
            params={"select": "*", "id": "eq.main"},
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            timeout=_TIMEOUT,
        )
        if r.status_code == 200:
            rows = r.json()
            if rows:
                return rows[0].get("data", {})
    except Exception:
        pass
    return None


def fetch_registry_local() -> Optional[dict]:
    """قراءة السجل المحلي من ملفات المشروع."""
    reg_path = _local_registry_path()
    if reg_path.is_file():
        try:
            return json.loads(reg_path.read_text("utf-8"))
        except Exception:
            pass
    return None


def get_registry() -> dict:
    """يحاول: GitHub → Supabase → كاش → محلي."""
    cached = cache_get(_REGISTRY_CACHE_KEY)

    reg = fetch_registry_github()
    if reg:
        return reg

    reg = fetch_registry_supabase()
    if reg:
        cache_set(_REGISTRY_CACHE_KEY, reg)
        return reg

    if cached:
        return cached

    return fetch_registry_local() or {"schema_version": 2, "models": []}


# ═══════════════════════ MANIFEST FETCH ═══════════════════════

def fetch_manifest(model_id: str) -> Optional[dict]:
    """جلب manifest نموذج من GitHub أو محلياً."""
    manifest_url = f"{_RAW_BASE}/{_MANIFEST_DIR}/{model_id}.json"
    try:
        r = httpx.get(manifest_url, timeout=_TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass

    local_path = _local_registry_path().parent / "manifests" / f"{model_id}.json"
    if local_path.is_file():
        try:
            return json.loads(local_path.read_text("utf-8"))
        except Exception:
            pass
    return None


# ═══════════════════════ INSTALL / UNINSTALL ═══════════════════════

def install_model(
    model_id: str,
    download_url: str,
    folder: str,
    version: str,
    on_progress: Optional[Callable[[str], None]] = None,
    on_done: Optional[Callable[[bool, str], None]] = None,
    on_detail: Optional[Callable] = None,
):
    """تحميل وتثبيت نموذج (في thread منفصل).

    on_detail(pct, downloaded_bytes, total_bytes, speed_bps, phase)
    provides structured progress for rich UI (progress bars, speed display).
    """
    import time as _time

    def _work():
        target = _desktop() / folder
        try:
            if on_progress:
                on_progress("جارٍ التحميل...")
            if on_detail:
                on_detail(0, 0, 0, 0, "connecting")

            if not download_url:
                if on_done:
                    on_done(False, "رابط التنزيل غير متوفر لهذا التطبيق")
                return

            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                zip_path = tmp_path / f"{model_id}.zip"

                with httpx.stream("GET", download_url, timeout=120, follow_redirects=True) as resp:
                    resp.raise_for_status()
                    total = int(resp.headers.get("content-length", 0))
                    downloaded = 0
                    t_start = _time.monotonic()
                    last_report = 0.0
                    with open(zip_path, "wb") as f:
                        for chunk in resp.iter_bytes(chunk_size=65536):
                            f.write(chunk)
                            downloaded += len(chunk)
                            now = _time.monotonic()
                            elapsed = now - t_start
                            speed = int(downloaded / elapsed) if elapsed > 0.1 else 0
                            pct = int(downloaded / total * 100) if total else 0

                            if now - last_report >= 0.25:
                                last_report = now
                                if on_progress and total:
                                    on_progress(f"جارٍ التحميل... {pct}%")
                                if on_detail:
                                    on_detail(pct, downloaded, total, speed, "downloading")

                if on_progress:
                    on_progress("جارٍ فك الضغط...")
                if on_detail:
                    on_detail(100, downloaded, total, 0, "extracting")

                with zipfile.ZipFile(zip_path, "r") as zf:
                    extract_dir = tmp_path / "extracted"
                    zf.extractall(extract_dir)

                    contents = list(extract_dir.iterdir())
                    if len(contents) == 1 and contents[0].is_dir():
                        source = contents[0]
                    else:
                        source = extract_dir

                    if target.exists():
                        shutil.rmtree(target, ignore_errors=True)
                    shutil.copytree(source, target)

                mark_installed(model_id, version, folder)

                if on_detail:
                    on_detail(100, downloaded, total, 0, "done")
                if on_progress:
                    on_progress("تم التثبيت بنجاح")
                if on_done:
                    on_done(True, f"تم تثبيت {folder} بنجاح")

        except httpx.HTTPStatusError as e:
            msg = f"فشل التحميل: HTTP {e.response.status_code}"
            if on_detail:
                on_detail(0, 0, 0, 0, "error")
            if on_done:
                on_done(False, msg)
        except Exception as e:
            if on_detail:
                on_detail(0, 0, 0, 0, "error")
            if on_done:
                on_done(False, f"خطأ في التثبيت: {e}")

    Thread(target=_work, daemon=True).start()


def uninstall_model(model_id: str, folder: str) -> tuple[bool, str]:
    """حذف نموذج من القرص وإزالة التسجيل."""
    target = _desktop() / folder
    try:
        if target.is_dir():
            shutil.rmtree(target)
        mark_uninstalled(model_id)
        return True, f"تم حذف {folder}"
    except Exception as e:
        return False, f"خطأ في الحذف: {e}"


def check_update(model_id: str, registry: Optional[dict] = None) -> Optional[str]:
    """يرجع رقم الإصدار الجديد إذا يوجد تحديث، None إذا محدّث."""
    reg = registry or get_registry()
    local_ver = installed_version(model_id)
    if not local_ver:
        return None
    for entry in reg.get("models", []):
        if entry["id"] == model_id:
            remote_ver = entry.get("version", "")
            if remote_ver and remote_ver != local_ver:
                return remote_ver
    return None


# ═══════════════════════ SYNC TO SUPABASE ═══════════════════════

def sync_installed_to_cloud(access_token: str):
    """رفع قائمة النماذج المثبتة إلى Supabase للمزامنة بين الأجهزة."""
    if not SUPABASE_ANON_KEY or not access_token:
        return
    inst = load_installed()
    try:
        httpx.post(
            f"{SUPABASE_URL}/rest/v1/user_addons",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates",
            },
            json={"installed": inst},
            timeout=10,
        )
    except Exception:
        pass


def fetch_cloud_installed(access_token: str) -> dict:
    """جلب قائمة النماذج المثبتة من السحابة."""
    if not SUPABASE_ANON_KEY or not access_token:
        return {}
    try:
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/user_addons",
            params={"select": "installed"},
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10,
        )
        if r.status_code == 200:
            rows = r.json()
            if rows:
                return rows[0].get("installed", {})
    except Exception:
        pass
    return {}
