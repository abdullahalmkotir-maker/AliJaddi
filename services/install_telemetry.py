"""
أحداث تثبيت/فك التطبيقات الفرعية — سجل محلي + إرسال اختياري إلى Supabase.
يهدف لتجميع إحصاءات الأعطال لتحسين المنصّة ولاحقاً تدريب نماذج مساعدة (بعد ترشيح/تعليم بشري).
لا تُرسل كلمات مرور أو JWT في detail؛ اقتصر على رموز أخطاء ونصوص مقتطفة.
"""
from __future__ import annotations

import json
import os
import platform
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from alijaddi import __version__ as PLATFORM_VERSION
from Ali12 import ALI12_ASSISTANT_ID, resolve_ali12
from services.local_store import _DIR, load_session

_TELEMETRY_FILE = _DIR / "telemetry_install_events.jsonl"
_MAX_LOCAL_BYTES = 2_000_000

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


def _truncate(s: str, n: int = 2000) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[: n - 3] + "..."


def _append_local(record: dict[str, Any]) -> None:
    line = json.dumps(record, ensure_ascii=False) + "\n"
    try:
        _TELEMETRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_TELEMETRY_FILE, "a", encoding="utf-8") as f:
            f.write(line)
        if _TELEMETRY_FILE.stat().st_size > _MAX_LOCAL_BYTES:
            _trim_local_log()
    except OSError:
        pass


def _trim_local_log() -> None:
    try:
        raw = _TELEMETRY_FILE.read_text(encoding="utf-8")
        lines = raw.splitlines()
        keep = lines[-8000:]
        _TELEMETRY_FILE.write_text("\n".join(keep) + ("\n" if keep else ""), encoding="utf-8")
    except OSError:
        pass


def emit_install_event(
    event_kind: str,
    *,
    model_id: str = "",
    success: Optional[bool] = None,
    detail: Optional[dict[str, Any]] = None,
    access_token: Optional[str] = None,
) -> None:
    """
    event_kind: install_ok | install_fail | install_no_url | uninstall_ok | uninstall_fail
        | launch_fail (فشل تشغيل تطبيق فرعي من لوحة المنصّة)
    """
    safe_detail: dict[str, Any] = {}
    if detail:
        for k, v in detail.items():
            if isinstance(v, str):
                safe_detail[str(k)[:80]] = _truncate(v, 500)
            elif isinstance(v, (bool, int, float)) or v is None:
                safe_detail[str(k)[:80]] = v
            elif isinstance(v, dict):
                safe_detail[str(k)[:80]] = _truncate(json.dumps(v, ensure_ascii=False), 500)

    if success is False or event_kind in (
        "install_fail",
        "install_no_url",
        "uninstall_fail",
        "launch_fail",
    ):
        mid = (model_id or "").strip()
        if mid and "model_id" not in safe_detail:
            safe_detail["model_id"] = mid[:80]
        meta = resolve_ali12(event_kind=event_kind, message="", detail=safe_detail)
        ha = meta.get("hint_ar") or ""
        if ha:
            safe_detail["ali12_hint"] = _truncate(ha, 2000)
        safe_detail["ali12_rule_id"] = meta.get("rule_id")
        safe_detail["ali12_confidence"] = meta.get("confidence")
        safe_detail["ali12_signals"] = meta.get("signals")

    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "assistant_model": ALI12_ASSISTANT_ID,
        "event_kind": event_kind,
        "model_id": model_id,
        "platform_app_version": PLATFORM_VERSION,
        "client_os": _truncate(platform.platform(), 300),
        "success": success,
        "detail": safe_detail,
    }
    _append_local(record)

    tok = (access_token or "").strip()
    if not tok:
        sess = load_session() or {}
        tok = (sess.get("access_token") or "").strip()
    if not tok or not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return

    body = {
        "event_kind": event_kind,
        "model_id": model_id or None,
        "platform_app_version": PLATFORM_VERSION,
        "client_os": record["client_os"],
        "success": success,
        "assistant_model": ALI12_ASSISTANT_ID,
        "detail": safe_detail,
    }
    try:
        r = httpx.post(
            f"{SUPABASE_URL}/rest/v1/platform_install_events",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {tok}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            json=body,
            timeout=12,
        )
        r.raise_for_status()
    except Exception:
        pass
