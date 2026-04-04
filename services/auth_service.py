"""
خدمة المصادقة — Supabase Auth.
- تسجيل الدخول بالمعرف + كلمة المرور (البريد الداخلي فقط للربط مع Supabase)
- إنشاء حساب: الاسم، المعرف، الميلاد، الجنس، وبريد لتأكيد الحساب فقط
- تأكيد عبر رمز يُرسل إلى بريد التأكيد
"""
from __future__ import annotations

import hashlib
import os
import re
import secrets
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread
from typing import Any, Optional

import httpx

from alijaddi.config import SUPABASE_ANON_KEY, SUPABASE_URL
from services.local_store import (
    save_session, load_session, clear_session, cache_set, cache_get,
)
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

SMTP_EMAIL = os.getenv("SMTP_EMAIL", "alijadditechnology@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

USER_EMAIL_DOMAIN = "user.alijaddi.app"
SMTP_READY = bool(SMTP_PASSWORD)

_MAX_RETRIES = 3
_TIMEOUT = 15

_pending_otps: dict[str, str] = {}
# بريد التأكيد (صغير) → { synthetic_email, password }
_pending_signup: dict[str, dict[str, str]] = {}


def _retry_request(fn, retries=_MAX_RETRIES):
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
    try:
        body = r.json()
        msg = str(
            body.get("error_description")
            or body.get("msg")
            or body.get("message")
            or body.get("error")
            or r.text
        )
        if "email not confirmed" in msg.lower():
            return "EMAIL_NOT_CONFIRMED"
        return msg
    except Exception:
        return r.text or f"خطأ HTTP {r.status_code}"


def validate_username(username: str) -> tuple[bool, str]:
    """المعرف: ٣–٣٢ حرفاً؛ إن كان لاتينياً فقط يُقبل نمط a-z0-9_."""
    raw = (username or "").strip()
    if len(raw) < 3:
        return False, "TOO_SHORT"
    if len(raw) > 32:
        return False, "TOO_LONG"
    slug = re.sub(r"[^a-z0-9_]", "", raw.lower())
    if len(slug) >= 3:
        if len(slug) > 24:
            return False, "TOO_LONG"
        return True, ""
    return True, ""


def username_to_auth_email(username: str) -> str:
    """بريد داخلي فريد لـ Supabase — نفس الدالة للتسجيل وللدخول."""
    raw = username.strip()
    slug = re.sub(r"[^a-z0-9_]", "", raw.lower())
    if len(slug) >= 3:
        return f"{slug}@{USER_EMAIL_DOMAIN}"
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"u{h}@{USER_EMAIL_DOMAIN}"


def _send_otp_email(to_email: str, otp: str, lang_hint: str = "ar") -> tuple[bool, str]:
    if not SMTP_PASSWORD:
        return False, "NO_SMTP"

    subj = {
        "ar": f"رمز تأكيد AliJaddi: {otp}",
        "en": f"AliJaddi verification code: {otp}",
        "fa": f"کد تأیید AliJaddi: {otp}",
        "ckb": f"کۆدی پشتڕاستکردنەوەی AliJaddi: {otp}",
    }.get(lang_hint[:2] if lang_hint else "ar", f"AliJaddi code: {otp}")

    msg = MIMEMultipart("alternative")
    msg["From"] = f"AliJaddi <{SMTP_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subj

    html = _CONFIRM_EMAIL_HTML.replace("{{OTP}}", otp).replace("{{EMAIL}}", to_email)
    text = f"Your AliJaddi verification code: {otp}\nرمز التأكيد: {otp}"

    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        return True, ""
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP_AUTH"
    except Exception as e:
        return False, str(e)


class AuthService:
    def __init__(self):
        self.access_token: str = ""
        self.refresh_token: str = ""
        self.user: dict = {}
        self.offline_mode: bool = False
        self._url = SUPABASE_URL
        self._key = SUPABASE_ANON_KEY
        self._last_pw: str = ""
        self._try_restore_session()

    @property
    def is_logged_in(self) -> bool:
        return bool(self.access_token)

    @property
    def is_guest(self) -> bool:
        return not self.access_token

    def display_identity(self) -> str:
        """اسم للعرض في الواجهة (ليس بريد الدخول الداخلي)."""
        meta = self.user.get("user_metadata") or {}
        name = (meta.get("full_name") or "").strip()
        un = (meta.get("username") or "").strip()
        if name:
            return name
        if un:
            return un
        em = (self.user.get("email") or "").strip()
        if em and not em.endswith(f"@{USER_EMAIL_DOMAIN}"):
            return em
        sess = load_session()
        if sess:
            dn = (sess.get("display_name") or sess.get("username") or "").strip()
            if dn:
                return dn
            sem = (sess.get("email") or "").strip()
            if sem and not sem.endswith(f"@{USER_EMAIL_DOMAIN}"):
                return sem
        return "User"

    def _auth_headers(self) -> dict[str, str]:
        return {"apikey": self._key, "Content-Type": "application/json"}

    def _bearer_headers(self) -> dict[str, str]:
        h = self._auth_headers()
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    def _service_headers(self) -> dict[str, str]:
        return {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json",
        }

    def _try_restore_session(self):
        sess = load_session()
        if sess:
            self.access_token = sess.get("access_token", "")
            self.refresh_token = sess.get("refresh_token", "")
            self.user = {
                "id": sess.get("user_id", ""),
                "email": sess.get("email", ""),
                "user_metadata": {
                    "username": sess.get("username", ""),
                    "full_name": sess.get("display_name", ""),
                },
            }

    def _persist(self, stars: int = 0):
        meta = self.user.get("user_metadata") or {}
        save_session(
            email=self.user.get("email", ""),
            user_id=self.user.get("id", ""),
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            stars=stars,
            username=str(meta.get("username", "") or ""),
            display_name=str(meta.get("full_name", "") or ""),
        )

    def _admin_create_user(
        self,
        email: str,
        password: str,
        confirm: bool = False,
        user_metadata: Optional[dict[str, Any]] = None,
    ) -> tuple[bool, str]:
        body: dict[str, Any] = {
            "email": email,
            "password": password,
            "email_confirm": confirm,
        }
        if user_metadata:
            body["user_metadata"] = user_metadata
        r = httpx.post(
            f"{self._url}/auth/v1/admin/users",
            headers=self._service_headers(),
            json=body,
            timeout=_TIMEOUT,
        )
        if r.status_code in (200, 201):
            return True, ""
        return False, _safe_error(r)

    def _admin_confirm_user(self, email: str):
        r = httpx.get(
            f"{self._url}/auth/v1/admin/users",
            headers=self._service_headers(),
            timeout=_TIMEOUT,
        )
        if r.status_code != 200:
            return
        users = r.json().get("users", [])
        uid = None
        for u in users:
            if (u.get("email") or "").lower() == email.lower():
                uid = u.get("id")
                break
        if not uid:
            return
        httpx.put(
            f"{self._url}/auth/v1/admin/users/{uid}",
            headers=self._service_headers(),
            json={"email_confirm": True},
            timeout=_TIMEOUT,
        )

    # ═══════════════════════ تسجيل حساب (معرف + ملف شخصي + بريد تأكيد) ═══════════════════════

    def sign_up_with_profile(
        self,
        username: str,
        password: str,
        full_name: str,
        birth_date: str,
        gender: str,
        contact_email: str,
        locale: str = "ar",
    ) -> tuple[bool, str]:
        if not (self._key or "").strip():
            return False, "MISSING_KEY"

        ok_u, err_u = validate_username(username)
        if not ok_u:
            return False, err_u

        fn = (full_name or "").strip()
        if len(fn) < 2:
            return False, "BAD_NAME"

        em = contact_email.strip().lower()
        if "@" not in em or "." not in em.split("@")[-1]:
            return False, "BAD_CONTACT_EMAIL"

        if len(password) < 8:
            return False, "WEAK_PASSWORD"

        synthetic = username_to_auth_email(username)
        self._last_pw = password

        meta = {
            "username": username.strip(),
            "full_name": fn,
            "birth_date": birth_date,
            "gender": gender,
            "contact_email": em,
            "locale": locale,
        }

        if not SUPABASE_SERVICE_KEY:
            return False, "MISSING_KEY"

        ok, msg = self._admin_create_user(synthetic, password, confirm=False, user_metadata=meta)
        if not ok:
            low = msg.lower()
            if "already" in low or "exists" in low or "registered" in low:
                return False, "USERNAME_TAKEN"
            return False, msg

        otp = secrets.token_hex(3).upper()[:6]
        _pending_otps[em] = otp
        _pending_signup[em] = {"synthetic_email": synthetic, "password": password}

        if SMTP_READY:
            ok_mail, _ = _send_otp_email(em, otp, locale)
            if ok_mail:
                return True, "CONFIRM_OTP"
            try:
                self._admin_confirm_user(synthetic)
            except Exception:
                pass
            _pending_otps.pop(em, None)
            _pending_signup.pop(em, None)
            return self.sign_in_with_credentials(synthetic, password)

        try:
            self._admin_confirm_user(synthetic)
        except Exception:
            pass
        _pending_otps.pop(em, None)
        _pending_signup.pop(em, None)
        return self.sign_in_with_credentials(synthetic, password)

    def verify_registration_otp(self, contact_email: str, code: str) -> tuple[bool, str]:
        key = contact_email.strip().lower()
        expected = _pending_otps.get(key, "")
        if not expected or code.strip().upper() != expected.upper():
            return False, "OTP_INVALID"

        meta = _pending_signup.get(key)
        if not meta:
            return False, "OTP_INVALID"

        _pending_otps.pop(key, None)
        _pending_signup.pop(key, None)

        synthetic = meta["synthetic_email"]
        password = meta["password"]

        try:
            self._admin_confirm_user(synthetic)
        except Exception:
            pass

        ok, msg = self.sign_in_with_credentials(synthetic, password)
        if ok:
            return True, "OK"
        return False, msg

    def resend_registration_otp(self, contact_email: str, locale: str = "ar") -> tuple[bool, str]:
        key = contact_email.strip().lower()
        if key not in _pending_signup:
            return False, "NO_PENDING"
        otp = secrets.token_hex(3).upper()[:6]
        _pending_otps[key] = otp
        if not SMTP_READY:
            return False, "NO_SMTP"
        ok, err = _send_otp_email(key, otp, locale)
        if ok:
            return True, "RESENT"
        return False, err

    # ═══════════════════════ تسجيل الدخول ═══════════════════════

    def sign_in_with_credentials(self, email: str, password: str) -> tuple[bool, str]:
        if not (self._key or "").strip():
            return False, "MISSING_KEY"

        self._last_pw = password

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
                return True, "OK"
            err = _safe_error(r)
            if err == "EMAIL_NOT_CONFIRMED":
                return False, "EMAIL_NOT_CONFIRMED"
            return False, err
        except Exception:
            self.offline_mode = True
            return False, "NETWORK_ERROR"

    def sign_in_with_username(self, username: str, password: str) -> tuple[bool, str]:
        ok_u, err_u = validate_username(username)
        if not ok_u:
            return False, err_u
        synthetic = username_to_auth_email(username)
        return self.sign_in_with_credentials(synthetic, password)

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


_CONFIRM_EMAIL_HTML = """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
<body style="margin:0;padding:0;background:#0F172A;font-family:'Segoe UI',Tahoma,sans-serif;">
<div style="max-width:480px;margin:30px auto;background:#1E293B;border-radius:16px;overflow:hidden;">
  <div style="background:linear-gradient(135deg,#6D28D9,#4F46E5);padding:30px 24px;text-align:center;">
    <h1 style="color:#FFF;margin:0;font-size:28px;">AliJaddi</h1>
    <p style="color:rgba(255,255,255,0.8);margin:8px 0 0;font-size:14px;">علي جدّي</p>
  </div>
  <div style="padding:30px 24px;text-align:center;">
    <h2 style="color:#F1F5F9;font-size:20px;margin:0 0 12px;">تأكيد الحساب</h2>
    <p style="color:#94A3B8;font-size:14px;line-height:1.7;margin:0 0 20px;">
      أدخل الرمز في التطبيق
    </p>
    <div style="background:#0F172A;border-radius:12px;padding:20px;margin:0 auto;display:inline-block;">
      <span style="color:#A78BFA;font-size:36px;font-weight:bold;letter-spacing:8px;">{{OTP}}</span>
    </div>
    <p style="color:#64748B;font-size:12px;margin:20px 0 0;">Enter this code in the app / أدخل الرمز في التطبيق</p>
  </div>
</div>
</body></html>"""
