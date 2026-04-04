# -*- coding: utf-8 -*-
"""واجهة Streamlit — مساعد أحمد الياسري الذكي (عيادة أسنان + تكامل علي جدّي)."""
from __future__ import annotations

import streamlit as st

import database as db
from config import (
    MODEL_ID,
    MODEL_NAME,
    MODEL_VERSION,
    PRIMARY_COLOR,
    load_env_files,
)

load_env_files()


def _table_exists(conn, name: str) -> bool:
    r = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (name,)
    ).fetchone()
    return r is not None


st.set_page_config(page_title=MODEL_NAME, page_icon="🦷", layout="wide")

db.init_db()

st.markdown(
    f'<p style="color:{PRIMARY_COLOR};font-size:1.1rem;font-weight:600">{MODEL_NAME}</p>',
    unsafe_allow_html=True,
)
st.caption(f"المعرّف: `{MODEL_ID}` — إصدار {MODEL_VERSION} — أحمد الياسري — جاهز للتثبيت من متجر علي جدّي")

col1, col2, col3 = st.columns(3)
with col1:
    with db.get_db() as conn:
        n_pat = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    st.metric("المرضى", n_pat)
with col2:
    with db.get_db() as conn:
        n_sess = (
            conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            if _table_exists(conn, "sessions")
            else 0
        )
    st.metric("الجلسات", n_sess)
with col3:
    st.info("البيانات محلية في مجلد `data/`. للمزامنة استخدم تبويب السحابة إن وُجد JWT.")

st.divider()
st.subheader("آخر المرضى")
with db.get_db() as conn:
    rows = conn.execute(
        "SELECT id, full_name, phone, created_at FROM patients ORDER BY id DESC LIMIT 25"
    ).fetchall()
if rows:
    st.dataframe(
        [{"المعرف": r[0], "الاسم": r[1], "الهاتف": r[2], "أُنشئ": r[3]} for r in rows],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("لا مرضى بعد. شغّل `run_seed_156.bat` أو `python scripts/seed_156_patients.py` لإدراج بيانات تجريبية.")

with st.expander("عن التطبيق"):
    st.markdown(
        """
- **متجر علي جدّي:** تثبيت عبر Ali12 و`store_consent_v2` تحت `~/.alijaddi/downloads/AhmedYassiriSmartAssistant`.
- **تكامل السحابة:** عيّن `SUPABASE_URL` / `SUPABASE_ANON_KEY` و`ALIJADDI_SUPABASE_ACCESS_TOKEN` من المنصّة عند التشغيل المضمّن.
"""
    )
