"""واجهة Streamlit مبسّطة."""
from __future__ import annotations

import streamlit as st

from .auth import AuthManager


def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "role" not in st.session_state:
        st.session_state.role = "user"
    if "stars" not in st.session_state:
        st.session_state.stars = 0


def apply_theme():
    """يُستدعى من `run.py` عبر `store.theme`؛ تبقى للتوافق مع استيراد قديم."""
    pass


def show_auth_ui():
    auth = AuthManager()
    st.title("🔐 متجر علي جدّي")
    st.caption("سجّل الدخول أو أنشئ حساباً للوصول إلى الكتالوج والمزامنة مع السحابة.")
    t1, t2 = st.tabs(["دخول", "تسجيل"])
    with t1:
        u = st.text_input("المستخدم أو البريد", key="l_u")
        p = st.text_input("كلمة المرور", type="password", key="l_p")
        if st.button("دخول", key="l_b"):
            ok, msg = auth.login(u, p)
            if ok:
                info = auth.get_user_by_username_or_email(u)
                st.session_state.logged_in = True
                st.session_state.user = info["username"]
                st.session_state.role = info.get("role", "user")
                st.session_state.stars = info.get("stars", 0)
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    with t2:
        nu = st.text_input("اسم المستخدم", key="r_u")
        em = st.text_input("البريد", key="r_e")
        p1 = st.text_input("كلمة المرور", type="password", key="r_p")
        if st.button("تسجيل", key="r_b"):
            ok, msg = auth.register(nu, p1, em)
            if ok:
                st.success(msg)
            else:
                st.error(msg)


def show_cloud_sync_tab(auth: AuthManager, username: str):
    st.subheader("☁️ مزامنة السحابة (Supabase)")
    try:
        from config import SUPABASE_URL, SUPABASE_ANON_KEY, CLOUD_SYNC_APPLY_STARS
    except ImportError:
        SUPABASE_URL = SUPABASE_ANON_KEY = ""
        CLOUD_SYNC_APPLY_STARS = True
    c1, c2 = st.columns(2)
    with c1:
        url_in = st.text_input("SUPABASE_URL", value=SUPABASE_URL or "", key="cu")
    with c2:
        key_in = st.text_input("SUPABASE_ANON_KEY", value=SUPABASE_ANON_KEY or "", type="password", key="ck")
    apply = st.checkbox("تحديث النجوم من السحابة", value=CLOUD_SYNC_APPLY_STARS, key="ca")
    prune = st.checkbox("حذف الروابط غير الموجودة في السحابة", value=False, key="cp")
    token = st.text_area("JWT", height=100, key="cj")
    if st.button("🔄 مزامنة الآن", type="primary"):
        if not token.strip():
            st.error("أدخل JWT")
        else:
            ok, msg = auth.sync_from_alijaddi_cloud(
                username,
                token.strip(),
                supabase_url=url_in.strip() or None,
                supabase_anon_key=key_in.strip() or None,
                apply_stars=apply,
                prune_not_in_cloud=prune,
            )
            if ok:
                st.success(msg)
                u = auth.get_user_by_username_or_email(username)
                if u:
                    st.session_state.stars = u.get("stars", 0)
                st.rerun()
            else:
                st.error(msg)
    if st.button("⬇️ دمج حمولات model_user_data"):
        if not token.strip():
            st.error("أدخل JWT")
        else:
            ok, msg = auth.merge_model_payloads_from_cloud(
                username,
                token.strip(),
                supabase_url=url_in.strip() or None,
                supabase_anon_key=key_in.strip() or None,
            )
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


def show_account_center_content(auth: AuthManager, username: str):
    st.subheader("مركز الحساب")
    u = auth.get_user_by_username_or_email(username)
    if u:
        st.metric("النجوم", u.get("stars", 0))
    t1, t2, t3 = st.tabs(["مزامنة السحابة", "النماذج", "ربط سريع"])
    with t1:
        show_cloud_sync_tab(auth, username)
    with t2:
        from config import AVAILABLE_MODELS

        linked = auth.get_user_models(username)
        st.write(f"مرتبط: **{len(linked)}**")
        mid = st.selectbox("نموذج", list(AVAILABLE_MODELS.keys()))
        if st.button("ربط"):
            meta = AVAILABLE_MODELS[mid]
            ok, msg = auth.link_model(username, mid, meta["name"])
            st.success(msg) if ok else st.error(msg)
    with t3:
        st.info("استخدم تبويب «النماذج» أعلاه، أو افتح «🛒 المتجر» من الشريط الجانبي لاستكشاف الكتالوج.")


def show_account_center(user_only: bool = True):
    show_account_center_content(AuthManager(), st.session_state.user)
