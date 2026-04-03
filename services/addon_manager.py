"""
مدير الإضافات — تحميل، تثبيت، تحديث، حذف النماذج.
• يجلب السجل من GitHub أولاً، ثم Supabase كمرآة
• يدعم العمل بدون إنترنت (كاش محلي)
• التثبيت: تحميل zip → فك الضغط → تسجيل محلي
"""
from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import time
import uuid
import zipfile
from pathlib import Path
from threading import Event, Thread
from typing import Callable, Optional

import httpx

from services.desktop_shortcut import create_hosted_app_desktop_shortcut
from services.local_store import cache_get, cache_set, _read, _write, _DIR
from services.install_telemetry import emit_install_event
from services.paths import app_dir, apps_root, bundle_root

_GITHUB_REPO = "abdullahalmkotir-maker/AliJaddi"
_GITHUB_BRANCH = "main"
_REGISTRY_PATH = "addons/registry.json"
_MANIFEST_DIR = "addons/manifests"
_RAW_BASE = f"https://raw.githubusercontent.com/{_GITHUB_REPO}/{_GITHUB_BRANCH}"

_INSTALLED_FILE = _DIR / "installed_addons.json"
_REGISTRY_CACHE_KEY = "addon_registry"
_TIMEOUT = 20


def version_sort_tuple(v: str) -> tuple[int, ...]:
    """جزء صحيح من semver للفرز والمقارنة (0.3.10 > 0.3.9)."""
    s = re.sub(r"^v", "", (v or "").strip(), flags=re.I)
    parts = [int(x) for x in re.findall(r"\d+", s)]
    return tuple(parts) if parts else (0,)


def is_remote_version_newer(remote_ver: str, local_ver: str) -> bool:
    r = (remote_ver or "").strip()
    l = (local_ver or "").strip()
    if not r or not l:
        return False
    if r == l:
        return False
    return version_sort_tuple(r) > version_sort_tuple(l)


def _safe_extractall(zf: zipfile.ZipFile, dest: Path) -> None:
    """فك ضغط آمن — رفض مسارات Zip Slip (.. أو جذر مطلق)."""
    dest_abs = dest.resolve()
    for info in zf.infolist():
        name = info.filename
        if not name or name.startswith(("/", "\\")):
            raise ValueError(f"مسار غير آمن في الأرشيف: {name!r}")
        parts = Path(name).parts
        if ".." in parts:
            raise ValueError(f"مسار غير آمن في الأرشيف: {name!r}")
        target = (dest_abs / name).resolve()
        if dest_abs != target and dest_abs not in target.parents:
            raise ValueError(f"مسار يخرج عن مجلد الاستخراج: {name!r}")
    zf.extractall(dest_abs)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mfhtnfxdfpelrgzonxov.supabase.co").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


def _local_registry_path() -> Path:
    """مسار موحّد يعمل مع التطوير و‎PyInstaller‎ (‎bundle_root‎)."""
    return bundle_root() / "addons" / "registry.json"


# ═══════════════════════ INSTALLED TRACKING ═══════════════════════

def load_installed() -> dict:
    return _read(_INSTALLED_FILE, {})


def _save_installed(data: dict):
    _write(_INSTALLED_FILE, data)


def mark_installed(
    model_id: str,
    version: str,
    folder: str,
    *,
    desktop_lnk: str = "",
    apps_parent: str = "",
):
    inst = load_installed()
    row = {
        "version": version,
        "folder": folder,
        "installed_at": __import__("datetime").datetime.now().isoformat(),
    }
    if desktop_lnk:
        row["desktop_lnk"] = desktop_lnk
    ap = (apps_parent or "").strip()
    if ap:
        row["apps_parent"] = ap
    inst[model_id] = row
    _save_installed(inst)


def mark_uninstalled(model_id: str):
    inst = load_installed()
    inst.pop(model_id, None)
    _save_installed(inst)


def installed_app_path(model_id: str, folder: str) -> Path:
    """مسار التطبيق المثبّت: `apps_parent` من السجل إن وُجد، وإلا جذر مدير التنزيلات الافتراضي."""
    row = load_installed().get(model_id) or {}
    parent = (row.get("apps_parent") or "").strip()
    name = (folder or "").strip()
    if not name:
        return app_dir(name)
    if parent:
        return (Path(parent).expanduser() / name).resolve()
    return app_dir(name)


def is_installed(model_id: str) -> bool:
    inst = load_installed()
    if model_id not in inst:
        return False
    folder = inst[model_id].get("folder", "")
    return bool(folder and installed_app_path(model_id, folder).is_dir())


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


def get_registry_offline_first() -> dict:
    """فوري للواجهة: محلي → كاش — بدون انتظار الشبكة (مناسب لتجربة أوفلاين)."""
    local = fetch_registry_local()
    cached = cache_get(_REGISTRY_CACHE_KEY)

    def _nonempty_models(d: Optional[dict]) -> bool:
        return bool(
            isinstance(d, dict)
            and isinstance(d.get("models"), list)
            and len(d["models"]) > 0
        )

    if local and isinstance(local, dict) and _nonempty_models(local):
        return local
    if cached and isinstance(cached, dict) and _nonempty_models(cached):
        return cached
    if local and isinstance(local, dict):
        return local
    if cached and isinstance(cached, dict):
        return cached
    return {"schema_version": 2, "models": []}


def refresh_registry_background(
    on_complete: Callable[[dict, bool], None],
) -> None:
    """مزامنة السجل في خيط خلفي. on_complete(reg, reached_remote) — استخدم QTimer على الخيط الرئيسي."""

    def _work():
        reg = fetch_registry_github()
        remote = bool(reg)
        if not reg:
            reg = fetch_registry_supabase()
            remote = bool(reg)
            if reg:
                cache_set(_REGISTRY_CACHE_KEY, reg)
        final = reg if reg else get_registry_offline_first()
        on_complete(final, remote)

    Thread(target=_work, daemon=True).start()


def get_registry() -> dict:
    """يحاول: GitHub → Supabase → كاش → محلي (قد يبطئ الواجهة — للمسارات غير التفاعلية)."""
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
    *,
    display_name: str = "",
    apps_parent: Optional[Path] = None,
    install_contract: str = "",
):
    """تحميل وتثبيت نموذج (في thread منفصل).

    تطبيقات **المتجر** تمرّ من ``store_install_standard.run_store_install_consent`` ثم تُمرَّر
    ``apps_parent`` و``install_contract`` (مثل ``store_consent_v2``).

    on_detail(pct, downloaded_bytes, total_bytes, speed_bps, phase)
    provides structured progress for rich UI (progress bars, speed display).
    """
    import time as _time

    def _work():
        if apps_parent is not None:
            ap = apps_parent.expanduser().resolve()
            ap.mkdir(parents=True, exist_ok=True)
            target = ap / folder
            apps_parent_str = str(ap)
        else:
            target = apps_root() / folder
            apps_parent_str = ""
        try:
            if on_progress:
                on_progress("جارٍ التحميل...")
            if on_detail:
                on_detail(0, 0, 0, 0, "connecting")

            if not download_url:
                emit_install_event(
                    "install_no_url",
                    model_id=model_id,
                    success=False,
                    detail={"folder": folder, "version": version},
                )
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
                    extract_dir.mkdir(parents=True, exist_ok=True)
                    _safe_extractall(zf, extract_dir)

                    contents = list(extract_dir.iterdir())
                    if len(contents) == 1 and contents[0].is_dir():
                        source = contents[0]
                    else:
                        source = extract_dir

                    # استبدال المجلد بأمان على ويندوز (OneDrive / ملفات مقفلة → WinError 183)
                    tmp_target = target.parent / f"{target.name}.__new_{uuid.uuid4().hex[:10]}"
                    shutil.copytree(source, tmp_target)
                    if target.exists():
                        for _ in range(8):
                            shutil.rmtree(target, ignore_errors=True)
                            if not target.exists():
                                break
                            time.sleep(0.2)
                        if target.exists():
                            legacy = target.parent / f"{target.name}.__old_{uuid.uuid4().hex[:8]}"
                            try:
                                target.rename(legacy)
                                shutil.rmtree(legacy, ignore_errors=True)
                            except OSError:
                                shutil.rmtree(target, ignore_errors=True)
                    tmp_target.rename(target)

                lnk_record = ""
                label = (display_name or "").strip()
                if label:
                    sp = create_hosted_app_desktop_shortcut(label, target)
                    if sp is not None:
                        lnk_record = str(sp)
                mark_installed(
                    model_id,
                    version,
                    folder,
                    desktop_lnk=lnk_record,
                    apps_parent=apps_parent_str,
                )

                ok_detail: dict = {
                    "folder": folder,
                    "version": version,
                    "install_flow": "store_folder_picker"
                    if apps_parent_str
                    else "default_incubator",
                    **({"apps_parent": apps_parent_str} if apps_parent_str else {}),
                }
                ic = (install_contract or "").strip()
                if ic:
                    ok_detail["install_contract"] = ic
                emit_install_event(
                    "install_ok",
                    model_id=model_id,
                    success=True,
                    detail=ok_detail,
                )
                if on_detail:
                    on_detail(100, downloaded, total, 0, "done")
                if on_progress:
                    on_progress("تم التثبيت بنجاح")
                if on_done:
                    on_done(True, f"تم تثبيت {folder} بنجاح")

        except httpx.HTTPStatusError as e:
            msg = f"فشل التحميل: HTTP {e.response.status_code}"
            emit_install_event(
                "install_fail",
                model_id=model_id,
                success=False,
                detail={
                    "folder": folder,
                    "version": version,
                    "http_status": e.response.status_code,
                    "phase": "download",
                },
            )
            if on_detail:
                on_detail(0, 0, 0, 0, "error")
            if on_done:
                on_done(False, msg)
        except Exception as e:
            emit_install_event(
                "install_fail",
                model_id=model_id,
                success=False,
                detail={
                    "folder": folder,
                    "version": version,
                    "error": str(e),
                    "phase": "install",
                },
            )
            if on_detail:
                on_detail(0, 0, 0, 0, "error")
            if on_done:
                on_done(False, f"خطأ في التثبيت: {e}")

    Thread(target=_work, daemon=True).start()


def install_model_sync(
    model_id: str,
    download_url: str,
    folder: str,
    version: str,
    *,
    display_name: str = "",
    apps_parent: Optional[Path] = None,
    install_contract: str = "",
    timeout_sec: float = 900.0,
    on_progress: Optional[Callable[[str], None]] = None,
) -> tuple[bool, str]:
    """مثل ``install_model`` لكن يُنتظر اكتمال التحميل — للسكربتات وCLI."""
    done = Event()
    result: list[bool | str] = [False, ""]

    def _on_done(ok: bool, msg: str) -> None:
        result[0] = ok
        result[1] = msg
        done.set()

    install_model(
        model_id,
        download_url,
        folder,
        version,
        on_progress=on_progress,
        on_done=_on_done,
        display_name=display_name,
        apps_parent=apps_parent,
        install_contract=install_contract,
    )
    if not done.wait(timeout=timeout_sec):
        return False, f"انتهت مهلة التثبيت ({int(timeout_sec)} ثانية)"
    return bool(result[0]), str(result[1])


def uninstall_model(model_id: str, folder: str) -> tuple[bool, str]:
    """حذف نموذج من القرص وإزالة التسجيل."""
    target = installed_app_path(model_id, folder)
    try:
        prev = load_installed().get(model_id) or {}
        lnk = (prev.get("desktop_lnk") or "").strip()
        if lnk:
            try:
                Path(lnk).unlink(missing_ok=True)
            except OSError:
                pass
        if target.is_dir():
            shutil.rmtree(target)
        mark_uninstalled(model_id)
        emit_install_event(
            "uninstall_ok",
            model_id=model_id,
            success=True,
            detail={"folder": folder},
        )
        return True, f"تم حذف {folder}"
    except Exception as e:
        emit_install_event(
            "uninstall_fail",
            model_id=model_id,
            success=False,
            detail={"folder": folder, "error": str(e)},
        )
        return False, f"خطأ في الحذف: {e}"


def check_update(model_id: str, registry: Optional[dict] = None) -> Optional[str]:
    """يرجع رقم الإصدار في المتجر إن كان أحدث من المثبّت حسب سجل المتجر."""
    reg = registry if registry is not None else get_registry_offline_first()
    local_ver = installed_version(model_id)
    if not local_ver:
        return None
    for entry in reg.get("models", []):
        if not isinstance(entry, dict) or entry.get("id") != model_id:
            continue
        remote_ver = str(entry.get("version", "") or "").strip()
        if remote_ver and is_remote_version_newer(remote_ver, local_ver):
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
