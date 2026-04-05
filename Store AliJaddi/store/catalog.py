# -*- coding: utf-8 -*-
"""كتالوج المتجر — استكشاف التطبيقات وربطها وإدارة المرتبطة."""
from __future__ import annotations

import streamlit as st

from auth_model.auth import AuthManager


def _catalog_entries():
    from config import AVAILABLE_MODELS

    return sorted(
        AVAILABLE_MODELS.items(),
        key=lambda x: x[1].get("name", x[0]),
    )


def show_catalog_page() -> None:
    if not st.session_state.get("logged_in"):
        st.warning("سجّل الدخول أولاً")
        return

    auth = AuthManager()
    user = st.session_state.user
    linked = auth.get_user_models(user)

    st.title("🛒 المتجر")
    st.caption("استكشف التطبيقات المتاحة وأضِفها إلى حسابك، أو أدِر ما اخترته مسبقاً.")

    tab_browse, tab_mine = st.tabs(["استكشف التطبيقات", "تطبيقاتي"])

    with tab_browse:
        st.subheader("الكتالوج")
        entries = _catalog_entries()
        for row_start in range(0, len(entries), 3):
            cols = st.columns(3)
            for col, (mid, meta) in zip(cols, entries[row_start : row_start + 3]):
                with col:
                    icon = meta.get("icon", "📦")
                    name = meta.get("name", mid)
                    desc = meta.get("description", "")
                    st.markdown(
                        f'<div class="store-card"><div style="font-size:1.75rem;">{icon}</div>'
                        f"<strong>{name}</strong><br/><small style='opacity:0.85'>{desc}</small></div>",
                        unsafe_allow_html=True,
                    )
                    is_linked = mid in linked
                    if is_linked:
                        st.success("✓ مرتبط")
                    else:
                        if st.button("إضافة", key=f"add_{mid}", use_container_width=True):
                            ok, msg = auth.link_model(user, mid, name)
                            if ok:
                                st.toast(msg)
                                st.rerun()
                            else:
                                st.error(msg)

    with tab_mine:
        st.subheader("تطبيقاتي")
        if not linked:
            st.info("لم تربط أي تطبيق بعد. انتقل إلى «استكشف التطبيقات» واضغط «إضافة».")
            return

        for mid, info in sorted(linked.items(), key=lambda x: x[1].get("name", x[0])):
            title = f"{info.get('name', mid)} — `{mid}`"
            with st.expander(title, expanded=False):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.json(info)
                with c2:
                    if st.button("إلغاء الربط", key=f"unlink_{mid}", type="secondary"):
                        ok, msg = auth.unlink_model(user, mid)
                        if ok:
                            st.toast(msg)
                            st.rerun()
                        else:
                            st.error(msg)
