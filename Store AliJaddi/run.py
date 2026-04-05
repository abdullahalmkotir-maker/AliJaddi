"""متجر علي جدّي — واجهة Streamlit (حساب، متجر، مزامنة)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

from auth_model.app import (
    init_session_state,
    show_auth_ui,
)
from store import apply_store_theme, render_store_app


def main() -> None:
    st.set_page_config(
        page_title="متجر علي جدّي",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_session_state()
    apply_store_theme()

    if not st.session_state.logged_in:
        show_auth_ui()
        return

    render_store_app()


if __name__ == "__main__":
    main()
