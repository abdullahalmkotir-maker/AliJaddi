# -*- coding: utf-8 -*-
"""تنقّل المتجر والشريط الجانبي."""
from __future__ import annotations

import streamlit as st

from auth_model.app import show_account_center

from .catalog import show_catalog_page
from .home import show_home_page

_NAV = (
    ("home", "🏠 الرئيسية"),
    ("account", "👤 الحساب والمزامنة"),
    ("store", "🛒 المتجر"),
)


def render_store_app() -> None:
    pending = st.session_state.pop("_store_nav", None)
    if pending in ("home", "account", "store"):
        st.session_state.store_page = pending
    if "store_page" not in st.session_state:
        st.session_state.store_page = "home"

    with st.sidebar:
        st.markdown("### متجر علي جدّي")
        st.caption(f"**{st.session_state.user}** · ⭐ {st.session_state.stars}")
        st.divider()
        for key, label in _NAV:
            is_here = st.session_state.store_page == key
            if st.button(
                label,
                key=f"nav_btn_{key}",
                use_container_width=True,
                type="primary" if is_here else "secondary",
            ):
                st.session_state.store_page = key
                st.rerun()
        st.divider()
        if st.button("🚪 خروج", key="nav_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.role = "user"
            st.session_state.stars = 0
            if "store_page" in st.session_state:
                del st.session_state.store_page
            st.rerun()
            return

    page = st.session_state.store_page
    if page == "home":
        show_home_page()
    elif page == "account":
        show_account_center()
    elif page == "store":
        show_catalog_page()
