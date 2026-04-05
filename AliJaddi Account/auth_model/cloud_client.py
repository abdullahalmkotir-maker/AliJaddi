"""عميل REST لـ Supabase (PostgREST). لا يقرأ/يكتب مجلد AliJaddi Cloud — ذلك المجلد للهجرات فقط."""
from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests


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


def _headers(supabase_anon_key: str, access_token: str, prefer: Optional[str] = None) -> Dict[str, str]:
    h: Dict[str, str] = {
        "apikey": supabase_anon_key,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def fetch_user_stars_balance(
    supabase_url: str, supabase_anon_key: str, access_token: str, user_id: str
) -> Optional[int]:
    base = supabase_url.rstrip("/")
    r = requests.get(
        f"{base}/rest/v1/users",
        params={"id": f"eq.{user_id}", "select": "stars_balance"},
        headers=_headers(supabase_anon_key, access_token),
        timeout=30,
    )
    r.raise_for_status()
    rows = r.json()
    if not rows:
        return None
    return int(rows[0].get("stars_balance") or 0)


def fetch_user_models(
    supabase_url: str, supabase_anon_key: str, access_token: str, user_id: str
) -> List[Dict[str, Any]]:
    base = supabase_url.rstrip("/")
    r = requests.get(
        f"{base}/rest/v1/user_models",
        params={"user_id": f"eq.{user_id}", "select": "*", "order": "model_name.asc"},
        headers=_headers(supabase_anon_key, access_token),
        timeout=30,
    )
    r.raise_for_status()
    return list(r.json())


def fetch_model_catalog(
    supabase_url: str, supabase_anon_key: str, access_token: str
) -> List[Dict[str, Any]]:
    base = supabase_url.rstrip("/")
    r = requests.get(
        f"{base}/rest/v1/model_catalog",
        params={"select": "model_id,display_name_ar,description"},
        headers=_headers(supabase_anon_key, access_token),
        timeout=30,
    )
    r.raise_for_status()
    return list(r.json())


def fetch_all_model_user_data(
    supabase_url: str, supabase_anon_key: str, access_token: str
) -> List[Dict[str, Any]]:
    base = supabase_url.rstrip("/")
    uid = decode_jwt_sub(access_token)
    r = requests.get(
        f"{base}/rest/v1/model_user_data",
        params={"user_id": f"eq.{uid}", "select": "*", "order": "model_id.asc"},
        headers=_headers(supabase_anon_key, access_token),
        timeout=60,
    )
    r.raise_for_status()
    return list(r.json())


def upsert_model_user_payload(
    supabase_url: str,
    supabase_anon_key: str,
    access_token: str,
    model_id: str,
    payload: Dict[str, Any],
    schema_version: int = 1,
) -> List[Dict[str, Any]]:
    base = supabase_url.rstrip("/")
    uid = decode_jwt_sub(access_token)
    body = {
        "user_id": uid,
        "model_id": model_id,
        "payload": payload,
        "schema_version": schema_version,
        "client_updated_at": datetime.now(timezone.utc).isoformat(),
    }
    r = requests.post(
        f"{base}/rest/v1/model_user_data",
        params={"on_conflict": "user_id,model_id"},
        headers=_headers(
            supabase_anon_key,
            access_token,
            prefer="resolution=merge-duplicates,return=representation",
        ),
        json=body,
        timeout=60,
    )
    r.raise_for_status()
    if not r.text:
        return []
    data = r.json()
    return data if isinstance(data, list) else [data]
