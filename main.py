# -*- coding: utf-8 -*-
"""
لوحة متجر علي جدّي (Streamlit) — صفحة واحدة بارتفاع نافذة المتصفح (100vh) دون تمرير عمودي للصفحة.
المحتوى الداخلي للبطاقات يستخدم overflow-y: auto عند الحاجة.

تشغيل من جذر المستودع::

    pip install streamlit httpx
    streamlit run main.py --server.headless true --browser.gatherUsageStats false

كلمة مرور الدخول: store_consent_v2
"""
from __future__ import annotations

import base64
import html
import os
import sys
from datetime import datetime
from pathlib import Path

# جذر المشروع على مسار الاستيراد
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import httpx
import streamlit as st

from services.addon_manager import fetch_manifest, get_registry_offline_first, load_installed
from services.paths import apps_root, primary_icon_path, user_desktop_dir
from services.store_experience import get_store_experience_offline_first

STORE_PASSWORD = "store_consent_v2"
_MIN_VIEWPORT = (1366, 768)


def _logo_data_uri() -> str:
    p = primary_icon_path()
    if not p.is_file():
        return ""
    try:
        raw = p.read_bytes()
        b64 = base64.b64encode(raw).decode("ascii")
        ext = p.suffix.lower()
        mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".ico": "image/x-icon"}.get(
            ext, "image/png"
        )
        return f"data:{mime};base64,{b64}"
    except OSError:
        return ""


def _load_local_stats() -> dict:
    try:
        from services import local_store as ls

        return ls.get_all_stats()
    except Exception:
        return {"models": {}, "favorites": [], "total_launches": 0, "last_model": None}


def _registry_models(reg: dict) -> list[dict]:
    models = reg.get("models") if isinstance(reg, dict) else None
    if not isinstance(models, list):
        return []
    out = []
    for m in models:
        if isinstance(m, dict) and m.get("id"):
            out.append(m)
    return out


def _manifest_rows(reg: dict) -> list[dict]:
    rows = []
    for m in _registry_models(reg):
        mid = str(m.get("id", ""))
        if mid == "alijaddi_platform":
            continue
        man = fetch_manifest(mid) or {}
        rows.append(
            {
                "id": mid,
                "name": str(man.get("name") or mid),
                "version": str(m.get("version", man.get("version", ""))),
                "folder": str(man.get("folder") or mid),
                "launch": str(man.get("launch", "")),
                "active": bool(man.get("active", True)),
            }
        )
    return rows


def _contributors(xp: dict) -> list[dict]:
    c = xp.get("contributors") if isinstance(xp, dict) else None
    if not isinstance(c, list):
        return []
    return [x for x in c if isinstance(x, dict) and x.get("name")]


def _usage_table_rows(stats: dict) -> list[dict]:
    models = stats.get("models") if isinstance(stats, dict) else {}
    if not isinstance(models, dict):
        return []
    rows = []
    for mid, v in models.items():
        if not isinstance(v, dict):
            continue
        rows.append(
            {
                "التطبيق": mid,
                "إطلاقات": int(v.get("launches", 0) or 0),
                "آخر استخدام": str(v.get("last_used") or "—"),
            }
        )
    rows.sort(key=lambda r: r["إطلاقات"], reverse=True)
    return rows[:12]


def _stats_four(reg: dict, xp: dict, installed: dict) -> tuple[int, int, int, int]:
    models = _registry_models(reg)
    app_count = len([m for m in models if str(m.get("id", "")) != "alijaddi_platform"])
    success = len(installed) if isinstance(installed, dict) else 0
    contrib = _contributors(xp)
    stars_sum = sum(int(c.get("stars", 0) or 0) for c in contrib)
    hinges = 0
    if isinstance(installed, dict):
        for _k, v in installed.items():
            if isinstance(v, dict) and (v.get("desktop_lnk") or "").strip():
                hinges += 1
    return success, stars_sum, hinges, app_count


def _updates_snippet_html(reg: dict, manifests: list[dict]) -> str:
    parts: list[str] = []
    if isinstance(reg, dict) and reg.get("updated_at"):
        parts.append(f"📅 سجل المتجر: {reg.get('updated_at')} — منصّة {reg.get('platform', '')}")
    for m in manifests[:5]:
        parts.append(f"• {m['name']} ({m['id']}) v{m['version']}")
    if not parts:
        return html.escape("—")
    return "<br/>".join(html.escape(p) for p in parts)


def _ping_registry() -> tuple[str, str]:
    url = "https://raw.githubusercontent.com/abdullahalmkotir-maker/AliJaddi/main/addons/registry.json"
    try:
        r = httpx.get(url, timeout=5.0)
        if r.status_code == 200:
            return "🟢 متصل", "GitHub (السجل)"
    except Exception as e:
        return "🟡 محلي", str(e)[:40]
    return "🟡 محلي", "لا استجابة"


def _create_desktop_url(display_name: str, folder_name: str) -> Path | None:
    """ينشئ ملف .url على سطح المكتب يشير إلى مجلد التطبيق (بعد الموافقة)."""
    if os.name != "nt":
        return None
    desktop = user_desktop_dir()
    if desktop is None or not desktop.is_dir():
        return None
    target = apps_root() / folder_name
    if not target.is_dir():
        target = Path(folder_name)
    try:
        uri = target.resolve().as_uri()
    except Exception:
        uri = f"file:///{target.as_posix()}"
    safe = "".join(c if c not in '<>:"/\\|?*' else "_" for c in display_name.strip())[:100] or "app"
    url_path = desktop / f"{safe}.url"
    body = f"[InternetShortcut]\nURL={uri}\nIconIndex=0\n"
    try:
        url_path.write_text(body, encoding="utf-8")
        return url_path
    except OSError:
        return None


def _inject_css() -> None:
    st.markdown(
        """
<style>
  :root {
    --aj-bg: #1e1e1e;
    --aj-card: rgba(45, 45, 45, 0.92);
    --aj-border: #3d3d3d;
    --aj-blue: #0078d4;
    --aj-blue-hover: #1084d8;
    --aj-mid-h: calc(100vh - 46px - 76px - 58px - 18px);
  }
  html, body {
    margin: 0 !important;
    padding: 0 !important;
    height: 100% !important;
    max-height: 100vh !important;
    background: var(--aj-bg) !important;
  }
  .stApp {
    background-color: var(--aj-bg) !important;
    color: #e8e8e8 !important;
    margin: 0 !important;
    padding: 0 !important;
    min-height: 100vh !important;
    max-height: 100vh !important;
  }
  /* لوحة التحكم: لا تمرير للصفحة */
  .stApp:has(#aj-dash-marker) {
    overflow: hidden !important;
  }
  /* شاشة الدخول: اسمح بالتمرير عند الضيق */
  .stApp:not(:has(#aj-dash-marker)) {
    overflow-y: auto !important;
  }
  [data-testid="stAppViewContainer"] {
    margin: 0 !important;
    padding: 0 !important;
  }
  .stApp:has(#aj-dash-marker) [data-testid="stAppViewContainer"] {
    overflow: hidden !important;
    max-height: 100vh !important;
    height: 100vh !important;
  }
  .stApp:has(#aj-dash-marker) [data-testid="stAppViewContainer"] > .main {
    overflow: hidden !important;
    max-height: 100vh !important;
    height: 100vh !important;
  }
  /* إخفاء شريط Streamlit العلوي لتوفير المسافة (1366×768) */
  .stApp:has(#aj-dash-marker) header[data-testid="stHeader"] {
    display: none !important;
  }
  .stApp:has(#aj-dash-marker) [data-testid="stToolbar"] {
    display: none !important;
  }
  .stApp:has(#aj-dash-marker) [data-testid="stDecoration"] {
    display: none !important;
  }
  section[data-testid="stSidebar"] {
    display: none !important;
  }
  [data-testid="collapsedControl"] {
    display: none !important;
  }
  footer { visibility: hidden !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }
  .stApp:has(#aj-dash-marker) section.main > div.block-container {
    padding: 0.2rem 0.45rem 0.15rem 0.45rem !important;
    margin: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
  }
  .stApp:has(#aj-dash-marker) section.main div[data-testid="stVerticalBlock"] {
    gap: 0.3rem !important;
    height: 100% !important;
    max-height: 100vh !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
  }
  .stApp:has(#aj-dash-marker) .element-container:has(#aj-dash-marker) {
    flex: 0 0 0 !important;
    min-height: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
  }
  .stApp:has(#aj-dash-marker) .element-container:has(.aj-row1-grid) {
    flex: 0 0 auto !important;
  }
  /* توسيط الصف ذي العمودين: الحاوية الأب تمتد داخل العمود الرأسي الرئيسي */
  .stApp:has(#aj-dash-marker) section.main div[data-testid="stVerticalBlock"] > div {
    min-height: 0 !important;
  }
  .stApp:has(#aj-dash-marker) section.main div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child)) {
    flex: 1 1 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
  }
  .stApp:has(#aj-dash-marker) section.main div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3):last-child)) {
    flex: 0 0 auto !important;
  }
  .stApp:has(#aj-dash-marker) section.main div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4):last-child)) {
    flex: 0 0 auto !important;
  }
  /* صف الأعمدة المكوّن من عمودين فقط = المنطقة الوسطى */
  .stApp:has(#aj-dash-marker) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child) {
    flex: 1 1 0 !important;
    min-height: 0 !important;
    height: var(--aj-mid-h) !important;
    max-height: var(--aj-mid-h) !important;
    overflow: hidden !important;
    align-items: stretch !important;
    display: flex !important;
  }
  .stApp:has(#aj-dash-marker) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child) > div[data-testid="column"] {
    min-height: 0 !important;
    max-height: 100% !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
  }
  .stApp:has(#aj-dash-marker) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child) > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
    flex: 1 1 0 !important;
    min-height: 0 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    gap: 0.25rem !important;
  }
  /* صف التطبيقات: أعمدة ثلاثة (شعار / عنوان / خروج) */
  .stApp:has(#aj-dash-marker) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3):last-child) {
    flex: 0 0 auto !important;
    min-height: 42px !important;
    max-height: 46px !important;
    align-items: center !important;
  }
  /* صف الأسفل: أربعة أعمدة */
  .stApp:has(#aj-dash-marker) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4):last-child) {
    flex: 0 0 auto !important;
    min-height: 52px !important;
    max-height: 58px !important;
    align-items: center !important;
    overflow: hidden !important;
  }
  .aj-row1-grid {
    direction: rtl;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.35rem;
    flex: 0 0 auto !important;
    min-height: 68px !important;
    max-height: 76px !important;
    align-items: stretch;
  }
  .aj-metric-card {
    background: var(--aj-card);
    border: 1px solid var(--aj-border);
    border-radius: 8px;
    padding: 0.3rem 0.4rem;
    text-align: center;
    font-size: clamp(0.68rem, 1vw, 0.82rem);
    line-height: 1.2;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .aj-metric-card strong {
    font-size: clamp(0.95rem, 1.85vw, 1.2rem);
    color: #fff;
    margin-top: 0.12rem;
    font-weight: 700;
  }
  .aj-panel-title {
    margin: 0 0 0.2rem 0;
    font-size: clamp(0.72rem, 1.1vw, 0.86rem);
    color: #c8c8c8;
    font-weight: 600;
    flex-shrink: 0;
  }
  .aj-scroll-x-apps {
    direction: rtl;
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    gap: 0.35rem;
    overflow-x: auto;
    overflow-y: hidden;
    min-height: 0;
    max-height: clamp(72px, 14vh, 100px);
    padding-bottom: 0.15rem;
    flex-shrink: 0;
  }
  .aj-app-card {
    flex: 0 0 auto;
    min-width: 118px;
    max-width: 140px;
    background: rgba(37, 37, 37, 0.95);
    border: 1px solid #4a4a4a;
    border-radius: 8px;
    padding: 0.3rem 0.35rem;
    font-size: 0.72rem;
    line-height: 1.25;
  }
  .aj-updates-line {
    line-height: 1.22;
    font-size: clamp(0.65rem, 0.95vw, 0.78rem);
    direction: rtl;
    text-align: right;
    overflow: hidden;
    max-height: 52px;
  }
  .stButton > button {
    background-color: var(--aj-blue) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 0.22rem 0.55rem !important;
    font-size: clamp(0.68rem, 0.95vw, 0.78rem) !important;
  }
  .stButton > button:hover {
    background-color: var(--aj-blue-hover) !important;
    box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.35);
  }
  div[data-testid="stVerticalBlockBorderWrapper"] {
    border: none !important;
  }
  .aj-login-wrap {
    direction: rtl;
    max-width: 380px;
    margin: 0.75rem auto;
    padding: 0.85rem;
    background: #2d2d2d;
    border-radius: 10px;
    border: 1px solid #444;
  }
  .aj-login-topbar {
    direction: rtl;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.35rem 0.5rem 0.5rem 0.5rem;
    margin-bottom: 0.25rem;
  }
  .aj-login-topbar img {
    width: 40px;
    height: 40px;
    object-fit: contain;
    border-radius: 6px;
  }
  /* جداول مضغوطة */
  [data-testid="stDataFrame"] {
    border-radius: 6px;
  }
</style>
""",
        unsafe_allow_html=True,
    )


def _render_login() -> None:
    logo = _logo_data_uri()
    left_logo = f'<img src="{logo}" alt=""/>' if logo else "<span style='font-size:1.6rem'>🛒</span>"
    st.markdown(
        f"""
<div class="aj-login-topbar">
  <div style="display:flex;align-items:center;gap:0.35rem">{left_logo}<span style="font-weight:700;font-size:clamp(0.85rem,2vw,1rem)">علي جدّي</span></div>
  <span style="opacity:0.75;font-size:0.78rem">🔐 دخول</span>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="aj-login-wrap">', unsafe_allow_html=True)
    st.markdown("#### 🔐 دخول مدير المتجر")
    pw = st.text_input("كلمة المرور", type="password", label_visibility="collapsed", placeholder="كلمة المرور")
    if st.button("تسجيل الدخول", type="primary", use_container_width=True):
        if pw == STORE_PASSWORD:
            st.session_state["store_authed"] = True
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة.")
    st.caption(f"الحد الأدنى للعرض الموصى به: {_MIN_VIEWPORT[0]}×{_MIN_VIEWPORT[1]}")
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="AliJaddi Store",
        layout="wide",
        initial_sidebar_state="collapsed",
        page_icon="🛒",
    )
    _inject_css()

    if not st.session_state.get("store_authed"):
        _render_login()
        return

    st.markdown(
        '<div id="aj-dash-marker" aria-hidden="true" style="height:0;margin:0;padding:0;line-height:0;overflow:hidden"></div>',
        unsafe_allow_html=True,
    )

    reg = get_registry_offline_first()
    xp = get_store_experience_offline_first()
    installed = load_installed()
    stats = _load_local_stats()
    manifests = _manifest_rows(reg)
    n_ok, n_stars, n_hinges, n_apps = _stats_four(reg, xp, installed)
    status_emoji, status_detail = _ping_registry()

    logo_uri = _logo_data_uri()
    img_html = f'<img src="{logo_uri}" style="width:40px;height:40px;object-fit:contain;border-radius:6px" alt=""/>' if logo_uri else "🛒"

    # —— شريط علوي رفيع: شعار يسار، عنوان، خروج يمين (RTL) ——
    hb1_l, hb1_m, hb1_r = st.columns([1, 6, 1])
    with hb1_l:
        st.markdown(f'<div style="text-align:right;padding:2px 0">{img_html}</div>', unsafe_allow_html=True)
    with hb1_m:
        st.markdown(
            "<div style='text-align:center;font-weight:700;font-size:clamp(0.88rem,1.6vw,1.05rem);padding:4px 0'>"
            "🛒 علي جدّي — لوحة المتجر</div>",
            unsafe_allow_html=True,
        )
    with hb1_r:
        if st.button("خروج", key="logout"):
            st.session_state["store_authed"] = False
            st.rerun()

    # —— الصف 1: أربع بطاقات (HTML grid، بدون أعمدة Streamlit) ——
    st.markdown(
        f"""
<div class="aj-row1-grid">
  <div class="aj-metric-card">✅ مرات النجاح<strong>{n_ok}</strong></div>
  <div class="aj-metric-card">⭐ التحصيلات (نجوم)<strong>{n_stars}</strong></div>
  <div class="aj-metric-card">🔗 المفصلات (اختصارات)<strong>{n_hinges}</strong></div>
  <div class="aj-metric-card">📱 التطبيقات المتاحة<strong>{n_apps}</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )

    # —— الصف 2: عمودان — تطبيقات يسار | ليدر بورد + سجل يمين (LTR داخل الصف ليبقى التطبيقات يسار) ——
    left, right = st.columns(2, gap="small")

    with left:
        st.markdown('<p class="aj-panel-title">📲 التطبيقات المتاحة</p>', unsafe_allow_html=True)
        cards_html = "".join(
            f'<div class="aj-app-card"><b>{html.escape(m["name"])}</b><br>v{html.escape(m["version"])}<br>'
            f"<small>{html.escape(m['id'])}</small></div>"
            for m in manifests
        )
        empty_apps = '<span style="opacity:0.55;padding:0.5rem">—</span>'
        st.markdown(
            f'<div class="aj-scroll-x-apps">{cards_html or empty_apps}</div>',
            unsafe_allow_html=True,
        )
        pick_ids = [m["id"] for m in manifests]
        pick_labels = [f"{m['name']} ({m['version']})" for m in manifests]
        if pick_ids:
            idx = st.selectbox(
                "اختر تطبيقاً للتثبيت على سطح المكتب (.url)",
                range(len(pick_ids)),
                format_func=lambda i: pick_labels[i],
                label_visibility="visible",
            )
            consent = st.checkbox(
                "أوافق على إنشاء اختصار .url وفق معيار المتجر **store_consent_v2**",
                value=False,
                key="consent_v2",
            )
            if st.button("⬇ تثبيت اختصار سطح المكتب (.url)", key="install_url"):
                if not consent:
                    st.warning("فعّل الموافقة على المعيار أولاً.")
                else:
                    sel = manifests[idx]
                    p = _create_desktop_url(sel["name"], sel["folder"])
                    if p:
                        st.success(f"تم الإنشاء: {p}")
                    else:
                        st.error("تعذّر إنشاء الملف — تحقق من سطح المكتب أو نظام التشغيل.")

    with right:
        st.markdown('<p class="aj-panel-title">🏆 أفضل المستخدمين</p>', unsafe_allow_html=True)
        lb = _contributors(xp)
        if lb:
            st.dataframe(
                [
                    {"الترتيب": c.get("rank", i + 1), "الاسم": c.get("name", ""), "النجوم": c.get("stars", 0)}
                    for i, c in enumerate(lb)
                ],
                hide_index=True,
                use_container_width=True,
                height=min(200, 28 + 32 * min(len(lb) + 1, 8)),
            )
        else:
            st.caption("لا بيانات.")

        st.markdown('<p class="aj-panel-title">📜 سجل الاستخدام</p>', unsafe_allow_html=True)
        ur = _usage_table_rows(stats)
        if ur:
            st.dataframe(
                ur,
                hide_index=True,
                use_container_width=True,
                height=min(180, 28 + 30 * min(len(ur) + 1, 7)),
            )
        else:
            st.caption("لا سجل محلي بعد.")

    # —— الصف 3: تحديثات + حالة خادم + أزرار ——
    u1, u2, u3, u4 = st.columns([3.2, 1, 1, 1], gap="small")
    with u1:
        st.markdown(
            f"<div class='aj-updates-line'><b>📰 التحديثات</b><br><small>{_updates_snippet_html(reg, manifests)}</small><br>"
            f"<b>🖥 حالة الخادم:</b> {html.escape(status_emoji)} — <small>{html.escape(status_detail)}</small> — "
            f"{html.escape(datetime.now().strftime('%H:%M:%S'))}</div>",
            unsafe_allow_html=True,
        )
    with u2:
        if st.button("🔄 تحديث اللوحة"):
            st.rerun()
    with u3:
        if st.button("🔁 إعادة تشغيل الجلسة"):
            st.rerun()
    with u4:
        if st.button("⏹ إيقاف"):
            st.session_state["_stop_ok"] = st.session_state.get("_stop_ok", 0) + 1
            if st.session_state["_stop_ok"] >= 2:
                os._exit(0)
            st.warning("اضغط «إيقاف» مرة ثانية للخروج من العملية.")


if __name__ == "__main__":
    main()
