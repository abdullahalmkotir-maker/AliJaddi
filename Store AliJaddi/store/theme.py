# -*- coding: utf-8 -*-
"""ثيم واجهة «متجر علي جدّي» (Streamlit + RTL)."""
from __future__ import annotations

import streamlit as st


def apply_store_theme() -> None:
    st.markdown(
        """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
  html, body, [class*="stApp"] {
    font-family: 'Tajawal', 'Segoe UI', sans-serif;
  }
  [data-testid="stAppViewContainer"] {
    direction: rtl;
    background: linear-gradient(165deg, #0f1419 0%, #1a2332 45%, #121820 100%);
  }
  [data-testid="stHeader"] { background: transparent; }
  [data-testid="stSidebar"] {
    direction: rtl;
    background: linear-gradient(180deg, #1e2a3a 0%, #152028 100%) !important;
    border-left: 1px solid rgba(255,255,255,0.08);
  }
  [data-testid="stSidebar"] [data-baseweb="radio"] label {
    font-size: 1rem;
  }
  div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,180,100,0.25);
    border-radius: 12px;
    padding: 0.75rem 1rem;
  }
  .store-hero {
    background: linear-gradient(120deg, rgba(249,115,22,0.15), rgba(59,130,246,0.12));
    border: 1px solid rgba(249,115,22,0.35);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
  }
  .store-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 1rem;
    min-height: 140px;
  }
  .stButton button[kind="primary"] {
    background: linear-gradient(90deg, #ea580c, #f97316);
    border: none;
  }
</style>
        """,
        unsafe_allow_html=True,
    )
