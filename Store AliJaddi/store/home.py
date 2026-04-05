# -*- coding: utf-8 -*-
"""الصفحة الرئيسية للمتجر."""
from __future__ import annotations

import streamlit as st

from auth_model.auth import AuthManager


def show_home_page() -> None:
    user = st.session_state.user
    auth = AuthManager()
    linked = auth.get_user_models(user)
    u = auth.get_user_by_username_or_email(user)
    stars = (u or {}).get("stars", 0)

    st.markdown(
        '<div class="store-hero"><h2 style="margin:0 0 0.35rem 0;">🛒 مرحباً في متجر علي جدّي</h2>'
        "<p style='margin:0;opacity:0.9;'>ارتبِط بالتطبيقات، زامِن بياناتك مع السحابة، وتابع النجوم من مكان واحد.</p></div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("تطبيقاتي", len(linked))
    with c2:
        st.metric("النجوم", stars)
    with c3:
        st.metric("الحساب", user or "—")

    st.divider()
    st.markdown("**ابدأ من هنا**")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🛍️ تصفّح المتجر", use_container_width=True, type="primary"):
            st.session_state._store_nav = "store"
            st.rerun()
    with b2:
        if st.button("⚙️ الحساب والمزامنة", use_container_width=True):
            st.session_state._store_nav = "account"
            st.rerun()
