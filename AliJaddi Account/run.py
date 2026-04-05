"""AliJaddi Account — Streamlit."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from auth_model.app import (
    init_session_state,
    apply_theme,
    show_auth_ui,
    show_account_center,
)
from platform_linking.app import show_linking_ui


def main():
    st.set_page_config(page_title="AliJaddi Account", layout="wide")
    init_session_state()
    apply_theme()

    if not st.session_state.logged_in:
        show_auth_ui()
        return

    with st.sidebar:
        st.write(f"**{st.session_state.user}** — ⭐ {st.session_state.stars}")
        page = st.radio("القائمة", ["الحساب", "منصة الربط", "خروج"])
        if page == "خروج":
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.role = "user"
            st.session_state.stars = 0
            st.rerun()

    if page == "خروج":
        st.stop()

    if page == "الحساب":
        show_account_center()
    elif page == "منصة الربط":
        show_linking_ui()


if __name__ == "__main__":
    main()
