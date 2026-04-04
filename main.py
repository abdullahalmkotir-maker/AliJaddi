# -*- coding: utf-8 -*-
"""
لوحة متجر علي جدّي (Streamlit) — صفحة واحدة بارتفاع نافذة المتصفح دون تمرير عمودي للصفحة.

تشغيل من جذر المستودع::

    pip install streamlit httpx
    streamlit run main.py --server.headless true --browser.gatherUsageStats false

كلمة مرور الدخول: store_consent_v2
"""
from __future__ import annotations

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
        f"""
<style>
  html, body, .stApp {{
    background-color: #1e1e1e !important;
    color: #e8e8e8 !important;
    overflow: hidden !important;
    height: 100vh !important;
    max-height: 100vh !important;
  }}
  [data-testid="stAppViewContainer"] {{
    overflow: hidden !important;
    height: 100vh !important;
  }}
  [data-testid="stAppViewContainer"] > .main {{
    overflow: hidden !important;
    height: 100vh !important;
  }}
  section.main > div.block-container {{
    padding: 0.35rem 0.75rem 0.25rem 0.75rem !important;
    max-width: 100% !important;
    height: calc(100vh - 0px) !important;
    overflow: hidden !important;
    display: flex;
    flex-direction: column;
  }}
  #alijaddi-dashboard {{
    direction: rtl;
    flex: 1;
    min-height: 0;
    display: grid;
    grid-template-rows: minmax(72px, auto) minmax(0, 1fr) minmax(56px, auto);
    gap: 0.35rem;
    height: 100%;
    max-height: calc(100vh - 1rem);
  }}
  /* تطبيقات يسار، ليدر بورد يمين — ترتيب أعمدة Streamlit يبقى LTR */
  #alijaddi-dashboard .aj-row2 {{
    direction: ltr;
  }}
  #alijaddi-dashboard .aj-row2 .aj-panel,
  #alijaddi-dashboard .aj-row1,
  #alijaddi-dashboard .aj-row3 {{
    direction: rtl;
  }}
  .aj-row1 {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.4rem;
    align-items: stretch;
  }}
  .aj-metric-card {{
    background: rgba(45, 45, 45, 0.92);
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    padding: 0.35rem 0.5rem;
    text-align: center;
    font-size: clamp(0.72rem, 1.1vw, 0.88rem);
  }}
  .aj-metric-card strong {{
    display: block;
    font-size: clamp(1rem, 2vw, 1.35rem);
    color: #fff;
    margin-top: 0.15rem;
  }}
  .aj-row2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.45rem;
    min-height: 0;
  }}
  .aj-panel {{
    background: rgba(45, 45, 45, 0.88);
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    padding: 0.35rem 0.45rem;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }}
  .aj-panel h4 {{
    margin: 0 0 0.25rem 0;
    font-size: clamp(0.75rem, 1.2vw, 0.9rem);
    color: #ccc;
    flex-shrink: 0;
  }}
  .aj-scroll-y {{
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
  }}
  .aj-scroll-x {{
    flex: 1;
    min-height: 0;
    overflow-x: auto;
    overflow-y: hidden;
    display: flex;
    flex-direction: row;
    gap: 0.35rem;
    align-items: stretch;
    padding-bottom: 0.2rem;
  }}
  .aj-app-card {{
    flex: 0 0 140px;
    background: #252525;
    border: 1px solid #444;
    border-radius: 8px;
    padding: 0.35rem;
    font-size: 0.78rem;
  }}
  .aj-row3 {{
    display: grid;
    grid-template-columns: 1fr auto auto auto;
    gap: 0.4rem;
    align-items: center;
    background: rgba(40, 40, 40, 0.95);
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    padding: 0.3rem 0.5rem;
    font-size: clamp(0.68rem, 1vw, 0.82rem);
  }}
  div[data-testid="stVerticalBlockBorderWrapper"] {{
    border: none !important;
  }}
  .stButton > button {{
    background-color: #0078d4 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600;
    padding: 0.25rem 0.65rem !important;
    font-size: 0.78rem !important;
  }}
  .stButton > button:hover {{
    background-color: #1084d8 !important;
    box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.35);
  }}
  [data-testid="stHeader"] {{
    background: rgba(30, 30, 30, 0.95);
  }}
  [data-testid="stDecoration"] {{
    display: none;
  }}
  section[data-testid="stSidebar"] {{
    display: none !important;
  }}
  [data-testid="collapsedControl"] {{
    display: none !important;
  }}
  footer {{ visibility: hidden; height: 0; }}
  .aj-login-box {{
    max-width: 360px;
    margin: 2rem auto;
    padding: 1rem;
    background: #2d2d2d;
    border-radius: 10px;
    border: 1px solid #444;
  }}
  /* جداول مضغوطة داخل اللوحة */
  .aj-scroll-y [data-testid="stDataFrame"] {{
    max-height: 100% !important;
  }}
</style>
""",
        unsafe_allow_html=True,
    )


def _render_login() -> None:
    st.markdown('<div class="aj-login-box">', unsafe_allow_html=True)
    st.markdown("### 🔐 دخول مدير المتجر")
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

    reg = get_registry_offline_first()
    xp = get_store_experience_offline_first()
    installed = load_installed()
    stats = _load_local_stats()
    manifests = _manifest_rows(reg)
    n_ok, n_stars, n_hinges, n_apps = _stats_four(reg, xp, installed)
    status_emoji, status_detail = _ping_registry()

    logo_path = primary_icon_path()
    header_l, header_m, header_r = st.columns([1, 5, 1])
    with header_l:
        if logo_path.is_file():
            st.image(str(logo_path), width=44)
        else:
            st.markdown("#### 🛒")
    with header_m:
        st.markdown(
            "<div style='text-align:center;font-size:clamp(1rem,2vw,1.25rem);margin:0;padding:0.1rem 0'>"
            "<strong>علي جدّي — لوحة المتجر</strong></div>",
            unsafe_allow_html=True,
        )
    with header_r:
        if st.button("خروج", key="logout"):
            st.session_state["store_authed"] = False
            st.rerun()

    st.markdown('<div id="alijaddi-dashboard">', unsafe_allow_html=True)

    # —— الصف 1: إحصائيات ——
    st.markdown('<div class="aj-row1">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="aj-metric-card">✅ مرات النجاح<br><strong>{n_ok}</strong></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="aj-metric-card">⭐ التحصيلات (نجوم)<br><strong>{n_stars}</strong></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="aj-metric-card">🔗 المفصلات (اختصارات)<br><strong>{n_hinges}</strong></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="aj-metric-card">📱 التطبيقات المتاحة<br><strong>{n_apps}</strong></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # —— الصف 2 ——
    st.markdown('<div class="aj-row2">', unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="aj-panel"><h4>📲 التطبيقات المتاحة</h4>', unsafe_allow_html=True)
        cards_html = "".join(
            f'<div class="aj-app-card"><b>{html.escape(m["name"])}</b><br>v{html.escape(m["version"])}<br>'
            f"<small>{html.escape(m['id'])}</small></div>"
            for m in manifests
        )
        empty_apps = '<span style="opacity:0.6">—</span>'
        st.markdown(
            f'<div class="aj-scroll-x">{cards_html or empty_apps}</div>',
            unsafe_allow_html=True,
        )

        pick_ids = [m["id"] for m in manifests]
        pick_labels = [f"{m['name']} ({m['version']})" for m in manifests]
        if pick_ids:
            idx = st.selectbox("اختر تطبيقاً للتثبيت على سطح المكتب (.url)", range(len(pick_ids)), format_func=lambda i: pick_labels[i], label_visibility="visible")
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
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="aj-panel" style="height:48%;margin-bottom:0.35rem"><h4>🏆 أفضل المستخدمين</h4><div class="aj-scroll-y">', unsafe_allow_html=True)
        lb = _contributors(xp)
        if lb:
            st.dataframe(
                [{"الترتيب": c.get("rank", i + 1), "الاسم": c.get("name", ""), "النجوم": c.get("stars", 0)} for i, c in enumerate(lb)],
                hide_index=True,
                use_container_width=True,
                height=min(220, 38 * (len(lb) + 1)),
            )
        else:
            st.caption("لا بيانات.")
        st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown('<div class="aj-panel" style="flex:1;min-height:120px"><h4>📜 سجل الاستخدام</h4><div class="aj-scroll-y">', unsafe_allow_html=True)
        ur = _usage_table_rows(stats)
        if ur:
            st.dataframe(ur, hide_index=True, use_container_width=True, height=min(200, 36 * (len(ur) + 1)))
        else:
            st.caption("لا سجل محلي بعد.")
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # —— الصف 3 ——
    st.markdown('<div class="aj-row3">', unsafe_allow_html=True)
    u1, u2, u3, u4 = st.columns([3, 1, 1, 1])
    with u1:
        st.markdown(
            f"<div style='line-height:1.25'><b>📰 التحديثات</b><br><small>{_updates_snippet_html(reg, manifests)}</small><br>"
            f"<b>حالة الخادم:</b> {html.escape(status_emoji)} — <small>{html.escape(status_detail)}</small> — "
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
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
