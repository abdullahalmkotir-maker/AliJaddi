# -*- coding: utf-8 -*-
"""
مكافآت مساهمة المستخدم (نجوم) — تغذية البيانات وتصحيح الأخطاء للمساعدين Ali12 / Hassan12 / Hussein12.
محلياً: يزيد رصيد الجلسة؛ السحابة (Supabase) تُكمّل لاحقاً عبر ``profiles.stars_balance``.
لا يُستخدم لأغراض تجارية — بيانات المستخدم فقط كما في سياسة السحابة.
"""
from __future__ import annotations

import os
from typing import Any, Optional

import httpx

from services.local_store import add_session_stars, load_session

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# نقاط مقترحة لكل نوع مساهمة (قابلة للضبط لاحقاً من السحابة)
POINTS_TRAINING_EXPORT = 3
POINTS_HUMAN_RESOLUTION = 5


def record_contribution(
    kind: str,
    *,
    points: Optional[int] = None,
    meta: Optional[dict[str, Any]] = None,
) -> int:
    """
    يسجّل مساهمة ويضيف نجوماً للجلسة المحلية. يرجع الرصيد الجديد أو 0 إن لم توجد جلسة.
    """
    if points is None:
        if kind in ("training_export", "jsonl_seed"):
            points = POINTS_TRAINING_EXPORT
        elif kind in ("human_resolution", "correction"):
            points = POINTS_HUMAN_RESOLUTION
        else:
            points = 2

    new_total = add_session_stars(int(points))
    # محاولة خفيفة لتسجيل الحدث في REST (إن وُجد الجدول والـ RLS يسمحان)
    _try_post_contribution_event(kind, int(points), meta or {})
    return new_total


def _try_post_contribution_event(kind: str, points: int, meta: dict[str, Any]) -> None:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return
    sess = load_session()
    tok = (sess or {}).get("access_token") or ""
    if not tok:
        return
    body = {
        "kind": kind[:80],
        "points": points,
        "meta": meta,
    }
    try:
        r = httpx.post(
            f"{SUPABASE_URL}/rest/v1/user_contribution_events",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {tok}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            json=body,
            timeout=12,
        )
        if r.status_code in (404, 400):
            return
    except Exception:
        pass
