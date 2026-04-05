"""مصادقة محلية (SQLite) + مزامنة اختيارية إلى Supabase عبر REST. بيانات المستخدم على القرص هنا فقط — ليس في مجلد AliJaddi Cloud."""
from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import bcrypt
import requests

from . import cloud_client
from .utils import validate_email, validate_password

logger = logging.getLogger(__name__)


class AuthManager:
    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self) -> None:
        with self._conn() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    stars INTEGER DEFAULT 0,
                    linked_models TEXT DEFAULT '{}',
                    supabase_user_id TEXT,
                    created_at TEXT
                )
                """
            )

    def _hash(self, p: str) -> str:
        return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

    def _verify(self, p: str, h: str) -> bool:
        try:
            return bcrypt.checkpw(p.encode(), h.encode())
        except Exception:
            return False

    def register(self, username: str, password: str, email: str, role: str = "user") -> Tuple[bool, str]:
        if not username or not password:
            return False, "أكمل الحقول"
        if not validate_email(email):
            return False, "صيغة البريد غير صحيحة"
        ok, msg = validate_password(password)
        if not ok:
            return False, msg
        try:
            with self._lock:
                with self._conn() as c:
                    c.execute(
                        """INSERT INTO users (username,email,password_hash,role,stars,linked_models,created_at)
                           VALUES (?,?,?,?,0,?,?)""",
                        (
                            username,
                            email,
                            self._hash(password),
                            role,
                            "{}",
                            datetime.now().isoformat(),
                        ),
                    )
            return True, "تم التسجيل"
        except sqlite3.IntegrityError:
            return False, "اسم المستخدم موجود"
        except Exception as e:
            logger.exception("register")
            return False, str(e)

    def login(self, username_or_email: str, password: str) -> Tuple[bool, str]:
        u = self.get_user_by_username_or_email(username_or_email)
        if not u:
            return False, "بيانات غير صحيحة"
        if not self._verify(password, u["password_hash"]):
            return False, "بيانات غير صحيحة"
        return True, "مرحباً"

    def get_user_by_username_or_email(self, key: str) -> Optional[Dict[str, Any]]:
        key = (key or "").strip()
        if not key:
            return None
        with self._conn() as c:
            c.row_factory = sqlite3.Row
            r = c.execute(
                "SELECT * FROM users WHERE username=? OR email=? LIMIT 1", (key, key)
            ).fetchone()
            if not r:
                return None
            d = dict(r)
            d.pop("password_hash", None)
            return d

    def _row_with_hash(self, key: str) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            c.row_factory = sqlite3.Row
            r = c.execute(
                "SELECT * FROM users WHERE username=? OR email=? LIMIT 1", (key, key)
            ).fetchone()
            return dict(r) if r else None

    def get_user_models(self, username: str) -> Dict[str, Any]:
        row = self._row_with_hash(username)
        if not row:
            return {}
        try:
            return json.loads(row.get("linked_models") or "{}")
        except json.JSONDecodeError:
            return {}

    def _persist_linked_models(self, username: str, linked: Dict[str, Any]) -> None:
        with self._lock:
            with self._conn() as c:
                c.execute(
                    "UPDATE users SET linked_models=? WHERE username=? OR email=?",
                    (json.dumps(linked, ensure_ascii=False), username, username),
                )

    def _update_user_field(self, username: str, field: str, value: Any) -> None:
        if field not in ("supabase_user_id", "stars"):
            return
        with self._lock:
            with self._conn() as c:
                c.execute(
                    f"UPDATE users SET {field}=? WHERE username=? OR email=?",
                    (value, username, username),
                )

    def link_model(self, username: str, model_id: str, name: str) -> Tuple[bool, str]:
        linked = self.get_user_models(username)
        linked[model_id] = {
            "name": name,
            "config": {},
            "enabled": True,
            "last_used": None,
            "stars_earned": 0,
            "added_at": datetime.now().isoformat(),
        }
        self._persist_linked_models(username, linked)
        return True, "تم الربط"

    def unlink_model(self, username: str, model_id: str) -> Tuple[bool, str]:
        linked = self.get_user_models(username)
        if model_id not in linked:
            return False, "النموذج غير مرتبط"
        del linked[model_id]
        self._persist_linked_models(username, linked)
        return True, "أُلغي الربط"

    def set_stars(self, username: str, stars: int, reason: str, source: str) -> Tuple[bool, str]:
        with self._lock:
            with self._conn() as c:
                c.execute(
                    "UPDATE users SET stars=? WHERE username=? OR email=?",
                    (int(stars), username, username),
                )
        return True, "تم التحديث"

    def sync_from_alijaddi_cloud(
        self,
        username: str,
        access_token: str,
        supabase_url: Optional[str] = None,
        supabase_anon_key: Optional[str] = None,
        apply_stars: Optional[bool] = None,
        prune_not_in_cloud: bool = False,
    ) -> Tuple[bool, str]:
        try:
            base_url = (supabase_url or os.getenv("SUPABASE_URL", "")).strip()
            anon = (supabase_anon_key or os.getenv("SUPABASE_ANON_KEY", "")).strip()
            if not base_url or not anon:
                return False, "عرّف SUPABASE_URL و SUPABASE_ANON_KEY"

            uid = cloud_client.decode_jwt_sub(access_token)

            try:
                cat_rows = cloud_client.fetch_model_catalog(base_url, anon, access_token)
                cat_map = {r.get("model_id"): r.get("display_name_ar") for r in cat_rows if r.get("model_id")}
            except Exception as e:
                logger.warning("model_catalog: %s", e)
                cat_map = {}

            try:
                from config import AVAILABLE_MODELS
            except ImportError:
                AVAILABLE_MODELS = {}

            rows = cloud_client.fetch_user_models(base_url, anon, access_token, uid)
            user = self.get_user_by_username_or_email(username)
            if not user:
                return False, "المستخدم المحلي غير موجود"

            linked = self.get_user_models(username)
            by_mid: Dict[str, Any] = {}
            for row in rows:
                mid = (row.get("model_id") or row.get("model_name") or "").strip()
                if mid:
                    by_mid[mid] = row

            for mid, row in by_mid.items():
                display = cat_map.get(mid) or AVAILABLE_MODELS.get(mid, {}).get("name", mid)
                active = bool(row.get("is_active", True))
                if mid not in linked:
                    linked[mid] = {
                        "name": display,
                        "config": {},
                        "enabled": active,
                        "last_used": None,
                        "stars_earned": 0,
                        "added_at": datetime.now().isoformat(),
                    }
                linked[mid]["name"] = display
                linked[mid]["enabled"] = active
                se = row.get("stars_earned_from_model")
                if se is not None:
                    linked[mid]["stars_earned"] = int(se)
                lu = row.get("last_used")
                if lu:
                    linked[mid]["last_used"] = lu if isinstance(lu, str) else str(lu)

            if prune_not_in_cloud and rows:
                for k in list(linked.keys()):
                    if k not in by_mid:
                        del linked[k]

            self._persist_linked_models(username, linked)
            self._update_user_field(username, "supabase_user_id", uid)

            if apply_stars is None:
                apply_stars = os.getenv("CLOUD_SYNC_APPLY_STARS", "true").lower() in ("1", "true", "yes")
            if apply_stars:
                bal = cloud_client.fetch_user_stars_balance(base_url, anon, access_token, uid)
                if bal is not None:
                    self.set_stars(username, bal, "مزامنة سحابة", "cloud")

            return True, "تمت المزامنة مع السحابة (Supabase)."
        except requests.RequestException as e:
            resp = getattr(e, "response", None)
            msg = (resp.text if resp is not None else str(e)) if resp else str(e)
            logger.error("sync HTTP: %s", msg)
            return False, f"فشل الطلب: {msg[:400]}"
        except Exception as e:
            logger.exception("sync")
            return False, str(e)

    def merge_model_payloads_from_cloud(
        self,
        username: str,
        access_token: str,
        supabase_url: Optional[str] = None,
        supabase_anon_key: Optional[str] = None,
    ) -> Tuple[bool, str]:
        try:
            base = (supabase_url or os.getenv("SUPABASE_URL", "")).strip()
            anon = (supabase_anon_key or os.getenv("SUPABASE_ANON_KEY", "")).strip()
            if not base or not anon:
                return False, "عرّف SUPABASE_URL و SUPABASE_ANON_KEY"
            rows = cloud_client.fetch_all_model_user_data(base, anon, access_token)
            linked = self.get_user_models(username)
            n = 0
            for row in rows:
                mid = row.get("model_id")
                if not mid or mid not in linked:
                    continue
                cfg = linked[mid].get("config")
                if not isinstance(cfg, dict):
                    cfg = {}
                else:
                    cfg = dict(cfg)
                cfg["cloud_payload"] = row.get("payload")
                linked[mid]["config"] = cfg
                n += 1
            self._persist_linked_models(username, linked)
            return True, f"دمج {n} حمولة."
        except Exception as e:
            logger.exception("merge")
            return False, str(e)
