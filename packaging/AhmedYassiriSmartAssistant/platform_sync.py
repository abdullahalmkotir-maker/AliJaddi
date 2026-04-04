"""
تكامل موحّد مع منظومة علي جدّي
══════════════════════════════════
متوافق مع:
  • AliJaddi — alijaddi/supabase_client.py (نفس عناوين REST والرؤوس)
  • AliJaddi Cloud — python/integration/model_data_rest.py + model_ids.py
  • AliJaddiAccount — auth_model/cloud_client.py

يمكن تمرير JWT عبر البيئة من المشغّل:
  ALIJADDI_SUPABASE_ACCESS_TOKEN أو SUPABASE_ACCESS_TOKEN
"""
from __future__ import annotations

import base64
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

from config import (
    MODEL_ID,
    MODEL_NAME,
    MODEL_VERSION,
    MODEL_USER_DATA_SCHEMA_VERSION,
    SUPABASE_URL,
    SUPABASE_ANON_KEY,
    DATA_DIR,
    alijaddi_cloud_root,
)

_TIMEOUT_SHORT = 30
_TIMEOUT_LONG = 60

# ─── اختياري: استيراد معرّفات AliJaddi Cloud من المستودع الشقيق ───
_CANONICAL_IDS: Optional[frozenset] = None
_INTEGRATION_PATH_TRIED = False


def _ensure_cloud_python_on_path() -> None:
    """يضيف AliJaddi Cloud/python إلى sys.path ويحمّل CANONICAL_MODEL_IDS إن وُجد."""
    global _CANONICAL_IDS, _INTEGRATION_PATH_TRIED
    if _INTEGRATION_PATH_TRIED:
        return
    _INTEGRATION_PATH_TRIED = True
    py_root = alijaddi_cloud_root() / "python"
    integ = py_root / "integration"
    if integ.is_dir() and str(py_root) not in sys.path:
        sys.path.insert(0, str(py_root))
    try:
        from integration.model_ids import CANONICAL_MODEL_IDS  # type: ignore

        _CANONICAL_IDS = CANONICAL_MODEL_IDS
    except Exception:
        _CANONICAL_IDS = None


def is_canonical_model_id(model_id: str) -> bool:
    _ensure_cloud_python_on_path()
    if _CANONICAL_IDS is None:
        return True
    return model_id in _CANONICAL_IDS


# ═══════════════════════════ JWT (مثل cloud_client / rest_sync) ═══════════════════════════

def decode_jwt_sub(access_token: str) -> str:
    parts = access_token.strip().split(".")
    if len(parts) != 3:
        raise ValueError("رمز وصول JWT غير صالح")
    payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
    payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode("ascii")))
    sub = payload.get("sub")
    if not sub:
        raise ValueError("لا يوجد sub في الرمز")
    return str(sub)


def decode_jwt_email(access_token: str) -> str:
    try:
        parts = access_token.strip().split(".")
        if len(parts) != 3:
            return ""
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode("ascii")))
        return str(payload.get("email", "") or "")
    except Exception:
        return ""


def _headers(access_token: str, prefer: Optional[str] = None) -> Dict[str, str]:
    h: Dict[str, str] = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


# ═══════════════════════════ جلسة محلية ═══════════════════════════

_SESSION_FILE = DATA_DIR / "platform_session.json"


def save_platform_session(access_token: str, email: str = "", stars: int = 0) -> None:
    try:
        uid = decode_jwt_sub(access_token)
    except Exception:
        uid = ""
    if not email:
        email = decode_jwt_email(access_token)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _SESSION_FILE.write_text(
        json.dumps(
            {
                "access_token": access_token,
                "user_id": uid,
                "email": email,
                "stars": stars,
                "saved_at": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def load_platform_session() -> Optional[Dict[str, Any]]:
    if not _SESSION_FILE.is_file():
        return None
    try:
        data = json.loads(_SESSION_FILE.read_text(encoding="utf-8"))
        if data.get("access_token"):
            return data
    except Exception:
        pass
    return None


def clear_platform_session() -> None:
    try:
        if _SESSION_FILE.is_file():
            _SESSION_FILE.unlink()
    except OSError:
        pass


def access_token_from_environment() -> str:
    """رمز يمرره مشغّل AliJaddi أو سكربت خارجي."""
    for key in (
        "ALIJADDI_SUPABASE_ACCESS_TOKEN",
        "SUPABASE_ACCESS_TOKEN",
        "ALI_JADDI_ACCESS_TOKEN",
    ):
        v = os.getenv(key, "").strip()
        if v:
            return v
    return ""


# ═══════════════════════════ REST — مطابق لـ upsert_model_user_payload (AliJaddi) ═══════════════════════════

def upsert_model_user_payload_raw(
    access_token: str,
    model_id: str,
    payload: Dict[str, Any],
    *,
    schema_version: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """يرفع مثل AliJaddi.supabase_client.upsert_model_user_payload — يرفع استثناء عند فشل HTTP."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise RuntimeError("SUPABASE_URL أو SUPABASE_ANON_KEY غير معرّفين")
    base = SUPABASE_URL.rstrip("/")
    uid = decode_jwt_sub(access_token)
    sv = schema_version if schema_version is not None else MODEL_USER_DATA_SCHEMA_VERSION
    body = {
        "user_id": uid,
        "model_id": model_id,
        "payload": payload,
        "schema_version": sv,
        "client_updated_at": datetime.now(timezone.utc).isoformat(),
    }
    r = requests.post(
        f"{base}/rest/v1/model_user_data",
        params={"on_conflict": "user_id,model_id"},
        headers=_headers(
            access_token,
            prefer="resolution=merge-duplicates,return=representation",
        ),
        json=body,
        timeout=_TIMEOUT_LONG,
    )
    r.raise_for_status()
    if not r.text:
        return []
    data = r.json()
    return data if isinstance(data, list) else [data]


def sync_payload_to_cloud(access_token: str, payload: dict) -> Tuple[bool, str]:
    """واجهة Streamlit: (نجاح، رسالة)."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return False, "أكمل إعدادات Supabase (SUPABASE_ANON_KEY) أو انسخ .env من AliJaddi / AliJaddiAccount"
    _ensure_cloud_python_on_path()
    try:
        upsert_model_user_payload_raw(access_token, MODEL_ID, payload)
        return True, "تمت المزامنة بنجاح ☁️"
    except requests.HTTPError as e:
        txt = e.response.text[:400] if e.response is not None else str(e)
        return False, f"HTTP: {txt}"
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"خطأ: {e}"


def fetch_model_row(access_token: str, model_id: str = MODEL_ID) -> Optional[Dict[str, Any]]:
    """صف كامل من model_user_data (مثل fetch_model_payload في Cloud مع select=*)."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None
    base = SUPABASE_URL.rstrip("/")
    try:
        uid = decode_jwt_sub(access_token)
    except Exception:
        return None
    try:
        r = requests.get(
            f"{base}/rest/v1/model_user_data",
            params={
                "user_id": f"eq.{uid}",
                "model_id": f"eq.{model_id}",
                "select": "*",
            },
            headers=_headers(access_token),
            timeout=_TIMEOUT_LONG,
        )
        r.raise_for_status()
        rows = r.json()
        return rows[0] if rows else None
    except Exception:
        return None


def fetch_payload_from_cloud(access_token: str) -> Optional[Dict[str, Any]]:
    """للتوافقية: يعيد الصف الكامل (يحتوي payload و updated_at)."""
    return fetch_model_row(access_token, MODEL_ID)


def fetch_all_model_user_data(access_token: str) -> List[Dict[str, Any]]:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return []
    base = SUPABASE_URL.rstrip("/")
    try:
        uid = decode_jwt_sub(access_token)
    except Exception:
        return []
    try:
        r = requests.get(
            f"{base}/rest/v1/model_user_data",
            params={"user_id": f"eq.{uid}", "select": "*", "order": "model_id.asc"},
            headers=_headers(access_token),
            timeout=_TIMEOUT_LONG,
        )
        r.raise_for_status()
        return list(r.json())
    except Exception:
        return []


def fetch_user_stars_balance(access_token: str, user_id: str) -> Optional[int]:
    """توقيع مطابق لـ AliJaddi supabase_client.fetch_user_stars_balance."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None
    base = SUPABASE_URL.rstrip("/")
    try:
        r = requests.get(
            f"{base}/rest/v1/users",
            params={"id": f"eq.{user_id}", "select": "stars_balance"},
            headers=_headers(access_token),
            timeout=_TIMEOUT_SHORT,
        )
        r.raise_for_status()
        rows = r.json()
        if not rows:
            return None
        return int(rows[0].get("stars_balance") or 0)
    except Exception:
        return None


def fetch_user_stars(access_token: str) -> Optional[int]:
    uid = decode_jwt_sub(access_token)
    return fetch_user_stars_balance(access_token, uid)


def fetch_user_models(access_token: str) -> List[Dict[str, Any]]:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return []
    base = SUPABASE_URL.rstrip("/")
    try:
        uid = decode_jwt_sub(access_token)
    except Exception:
        return []
    try:
        r = requests.get(
            f"{base}/rest/v1/user_models",
            params={
                "user_id": f"eq.{uid}",
                "select": "*",
                "order": "model_name.asc",
            },
            headers=_headers(access_token),
            timeout=_TIMEOUT_SHORT,
        )
        r.raise_for_status()
        return list(r.json())
    except Exception:
        return []


def fetch_model_catalog(access_token: str) -> List[Dict[str, Any]]:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return []
    base = SUPABASE_URL.rstrip("/")
    try:
        r = requests.get(
            f"{base}/rest/v1/model_catalog",
            params={"select": "model_id,display_name_ar,description"},
            headers=_headers(access_token),
            timeout=_TIMEOUT_SHORT,
        )
        r.raise_for_status()
        return list(r.json())
    except Exception:
        return []


def check_model_linked(access_token: str) -> bool:
    for m in fetch_user_models(access_token):
        if m.get("model_name") == MODEL_ID:
            return True
    return False


# ═══════════════════════════ بناء الحمولة (إصدار 2) ═══════════════════════════

def build_sync_payload(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    حمولة غنية لـ AliJaddiAccount.merge_model_payloads_from_cloud ولوحات المنصة.
    stats: مخرجات database.get_stats()
    """
    proc = stats.get("procedure_counts") or {}
    top_procedures = dict(
        sorted(proc.items(), key=lambda x: x[1], reverse=True)[:12]
    )
    session_types = {
        row["session_type"]: row["cnt"]
        for row in (stats.get("session_type_stats") or [])
    }
    return {
        "canonical_model_id": MODEL_ID,
        "display_name_ar": MODEL_NAME,
        "app_version": MODEL_VERSION,
        "payload_schema": 2,
        "clinic_stats": {
            "total_patients": stats.get("total_patients", 0),
            "total_sessions": stats.get("total_sessions", 0),
            "today_sessions": stats.get("today_sessions", 0),
            "today_appointments": stats.get("today_appointments", 0),
            "total_revenue": stats.get("total_revenue", 0),
            "total_paid": stats.get("total_paid", 0),
            "outstanding": stats.get("outstanding", 0),
            "month_sessions": stats.get("month_sessions", 0),
            "month_revenue": stats.get("month_revenue", 0),
            "pending_lab": stats.get("pending_lab", 0),
        },
        "top_procedures": top_procedures,
        "session_types_breakdown": session_types,
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "client": {
            "name": "dental_assistant_streamlit",
            "version": MODEL_VERSION,
        },
    }


def bootstrap_session_from_env() -> Optional[Dict[str, Any]]:
    """
    للاستدعاء من main عند الإقلاع: إن وُجد رمز في البيئة احفظه وارجع ملخص الجلسة.
    """
    tok = access_token_from_environment()
    if not tok:
        return None
    stars = fetch_user_stars(tok)
    if stars is None:
        stars = 0
    email = decode_jwt_email(tok)
    save_platform_session(tok, email, stars)
    return {
        "access_token": tok,
        "email": email,
        "stars": stars,
        "user_id": decode_jwt_sub(tok),
    }


def init_streamlit_platform_session(st: Any) -> None:
    """
    ربط جلسة Streamlit بالمنصة: أولوية لرمز البيئة (من مشغّل AliJaddi) ثم الملف المحلي.
    يتوقع مفاتيح: platform_jwt, platform_email, platform_stars, platform_connected
    """
    ss = st.session_state
    if ss.get("platform_connected") and (ss.get("platform_jwt") or "").strip():
        return
    tok = access_token_from_environment().strip()
    if not tok:
        saved = load_platform_session()
        if saved and saved.get("access_token"):
            tok = saved["access_token"].strip()
            ss["platform_jwt"] = tok
            ss["platform_email"] = saved.get("email", "")
            ss["platform_stars"] = int(saved.get("stars") or 0)
            ss["platform_connected"] = True
        return
    try:
        decode_jwt_sub(tok)
        stars = fetch_user_stars(tok)
        if stars is None:
            stars = 0
        email = decode_jwt_email(tok)
        ss["platform_jwt"] = tok
        ss["platform_email"] = email
        ss["platform_stars"] = stars
        ss["platform_connected"] = True
        save_platform_session(tok, email, stars)
    except Exception:
        ss["platform_connected"] = False
