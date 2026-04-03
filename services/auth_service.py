"""
خدمة المصادقة — Supabase Auth + وضع أوفلاين.
- تسجيل الدخول اختياري — التطبيق يعمل بدون حساب
- حفظ الجلسة محلياً + استعادة تلقائية
- retry مع exponential backoff عند فشل الشبكة
"""
from __future__ import annotations

import os
import time
from typing import Optional

import httpx

from services.local_store import (
    save_session, load_session, clear_session, cache_set, cache_get,
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mfhtnfxdfpelrgzonxov.supabase.co").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

_MAX_RETRIES = 3
_TIMEOUT = 15

_MISSING_KEY_MSG = (
    "مفتاح Supabase غير مضبوط.\n"
    "انسخ .env.example إلى .env في مجلد المشروع "
    "والصق SUPABASE_ANON_KEY من لوحة Supabase ثم أعد تشغيل التطبيق."
)


def _retry_request(fn, retries=_MAX_RETRIES):
    """Exponential backoff: 1s → 2s → 4s."""
    last_err = None
    for attempt in range(retries):
        try:
            return fn()
        except (httpx.ConnectError, httpx.TimeoutException, httpx.ConnectTimeout, OSError) as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(min(2 ** attempt, 8))
    raise last_err  # type: ignore[misc]


def _safe_error(r) -> str:
    """استخلاص رسالة خطأ مفهومة من استجابة Supabase."""
    try:
        body = r.json()
        return str(
            body.get("error_description")
            or body.get("msg")
            or body.get("message")
            or body.get("error")
            or r.text
        )
    except Exception:
        return r.text or f"خطأ HTTP {r.status_code}"


class AuthService:
    def __init__(self):
        self.access_token: str = ""
        self.refresh_token: str = ""
        self.user: dict = {}
        self.offline_mode: bool = False
        self._url = SUPABASE_URL
        self._key = SUPABASE_ANON_KEY
        self._try_restore_session()

    @property
    def is_logged_in(self) -> bool:
        return bool(self.access_token)

    @property
    def is_guest(self) -> bool:
        return not self.access_token

    def _auth_headers(self) -> dict[str, str]:
        return {"apikey": self._key, "Content-Type": "application/json"}

    def _bearer_headers(self) -> dict[str, str]:
        h = self._auth_headers()
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    def _try_restore_session(self):
        """استعادة الجلسة المحفوظة محلياً عند فتح التطبيق."""
        sess = load_session()
        if sess:
            self.access_token = sess.get("access_token", "")
            self.refresh_token = sess.get("refresh_token", "")
            self.user = {
                "id": sess.get("user_id", ""),
                "email": sess.get("email", ""),
            }

    def _persist(self, stars: int = 0):
        save_session(
            email=self.user.get("email", ""),
            user_id=self.user.get("id", ""),
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            stars=stars,
        )

    def sign_up(self, email: str, password: str) -> tuple[bool, str]:
        if not (self._key or "").strip():
            return False, _MISSING_KEY_MSG

        # Strategy: create a pre-confirmed user via admin API, then sign in
        if SUPABASE_SERVICE_KEY:
            try:
                ok, msg = self._admin_create_user(email, password)
                if ok:
                    return self.sign_in(email, password)
                if "already been registered" in msg.lower() or "already_exists" in msg.lower():
                    return False, "هذا البريد مسجّل مسبقاً — جرّب تسجيل الدخول"
                return False, msg
            except Exception:
                pass

        # Fallback: normal signup (requires email confirmation)
        def _do():
            return httpx.post(
                f"{self._url}/auth/v1/signup",
                headers=self._auth_headers(),
                json={"email": email, "password": password},
                timeout=_TIMEOUT,
            )
        try:
            r = _retry_request(_do)
            if r.status_code in (200, 201):
                body = r.json()
                if body.get("access_token"):
                    self._apply(body)
                    self._persist()
                    self.offline_mode = False
                    return True, "تم إنشاء الحساب بنجاح"
                return True, "تم إنشاء الحساب — تحقّق من بريدك لتأكيد الحساب ثم سجّل الدخول"
            return False, _safe_error(r)
        except Exception:
            self.offline_mode = True
            return False, "لا يوجد اتصال — جرّب لاحقاً"

    def _admin_create_user(self, email: str, password: str) -> tuple[bool, str]:
        """Create a pre-confirmed user via service role key."""
        r = httpx.post(
            f"{self._url}/auth/v1/admin/users",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json",
            },
            json={"email": email, "password": password, "email_confirm": True},
            timeout=_TIMEOUT,
        )
        if r.status_code in (200, 201):
            return True, ""
        return False, _safe_error(r)

    def sign_in(self, email: str, password: str) -> tuple[bool, str]:
        if not (self._key or "").strip():
            return False, _MISSING_KEY_MSG

        def _do():
            return httpx.post(
                f"{self._url}/auth/v1/token?grant_type=password",
                headers=self._auth_headers(),
                json={"email": email, "password": password},
                timeout=_TIMEOUT,
            )
        try:
            r = _retry_request(_do)
            if r.status_code == 200:
                self._apply(r.json())
                stars = self.fetch_stars() or 0
                self._persist(stars)
                self.offline_mode = False
                self._sync_addons_background()
                return True, "تم تسجيل الدخول"
            return False, _safe_error(r)
        except Exception:
            self.offline_mode = True
            return False, "لا يوجد اتصال — جرّب لاحقاً"

    def sign_out(self):
        if self.access_token:
            try:
                httpx.post(f"{self._url}/auth/v1/logout", headers=self._bearer_headers(), timeout=5)
            except Exception:
                pass
        self.access_token = ""
        self.refresh_token = ""
        self.user = {}
        clear_session()

    def _apply(self, data: dict):
        self.access_token = data.get("access_token", "")
        self.refresh_token = data.get("refresh_token", "")
        self.user = data.get("user", {})

    def fetch_stars(self) -> int:
        cached = cache_get("stars")
        if cached is not None:
            return int(cached)
        if not self.access_token:
            sess = load_session()
            return sess.get("stars", 0) if sess else 0
        uid = self.user.get("id", "")
        try:
            r = httpx.get(
                f"{self._url}/rest/v1/users",
                params={"id": f"eq.{uid}", "select": "stars_balance"},
                headers=self._bearer_headers(),
                timeout=10,
            )
            r.raise_for_status()
            rows = r.json()
            val = int(rows[0].get("stars_balance", 0)) if rows else 0
            cache_set("stars", val)
            return val
        except Exception:
            sess = load_session()
            return sess.get("stars", 0) if sess else 0

    def fetch_model_catalog(self) -> list[dict]:
        cached = cache_get("model_catalog")
        if cached is not None:
            return cached
        try:
            r = httpx.get(
                f"{self._url}/rest/v1/model_catalog",
                params={"select": "*"},
                headers=self._bearer_headers(),
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            cache_set("model_catalog", data)
            return data
        except Exception:
            return []

    def _sync_addons_background(self):
        """مزامنة الإضافات المثبتة مع السحابة في الخلفية."""
        from threading import Thread

        def _work():
            try:
                from services.addon_manager import sync_installed_to_cloud
                sync_installed_to_cloud(self.access_token)
            except Exception:
                pass

        Thread(target=_work, daemon=True).start()

    def check_connection(self) -> bool:
        try:
            httpx.head(self._url, timeout=5)
            self.offline_mode = False
            return True
        except Exception:
            self.offline_mode = True
            return False
