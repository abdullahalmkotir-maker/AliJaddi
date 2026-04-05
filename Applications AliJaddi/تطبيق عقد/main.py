# -*- coding: utf-8 -*-
"""واجهة مؤقتة لتطبيق عقد (Euqid) — يُستبدل بالمشروع الكامل."""
from __future__ import annotations

import webbrowser

import streamlit as st

REPO = "https://github.com/alijadditechnology/AliJaddi"
SUPABASE = "https://nzevwjghbvrrmmshnvem.supabase.co"

st.set_page_config(page_title="عقد — Euqid", layout="centered")
st.title("عقد (Euqid)")
st.info(
    "مدخل مؤقت داخل مستودع AliJaddi. لاستبداله بالتطبيق الكامل: "
    "شغّل `_move_euqid_here.ps1` أو انسخ ملفات المشروع هنا."
)
st.markdown(f"- [المستودع]({REPO})")
st.markdown(f"- [مشروع Supabase]({SUPABASE})")
if st.button("فتح المستودع في المتصفح"):
    webbrowser.open(REPO)
