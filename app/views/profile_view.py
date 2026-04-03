"""الملف الشخصي — تسجيل الدخول الاختياري + إحصائيات + إعدادات."""
from __future__ import annotations
from typing import Callable
import flet as ft
import theme as T
from alijaddi import __version__ as ALIJADDI_VERSION
from services.models_data import MODELS
from services.local_store import (
    get_all_stats, load_settings, set_setting, load_session,
)


def build_profile_content(page: ft.Page, auth, on_login_done: Callable, on_logout: Callable) -> ft.Column:
    stats = get_all_stats()
    settings = load_settings()
    sess = load_session()
    logged_in = auth.is_logged_in

    email = auth.user.get("email", "") if logged_in else (sess.get("email", "") if sess else "")
    try:
        stars = auth.fetch_stars() if logged_in else (sess.get("stars", 0) if sess else 0)
    except Exception:
        stars = sess.get("stars", 0) if sess else 0

    # ─── Avatar + Status ───
    if logged_in or email:
        avatar_letter = email[0].upper() if email else "U"
        avatar = ft.Container(
            content=ft.Text(avatar_letter, size=26, weight=ft.FontWeight.BOLD, color="#FFF"),
            width=80, height=80, bgcolor=T.PRIMARY, border_radius=40, alignment=ft.Alignment(0, 0),
        )
        user_label = ft.Text(email, size=15, weight=ft.FontWeight.W_500, color=T.tx(page))
        status_chip = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CLOUD_DONE_ROUNDED, color="#FFF", size=14),
                ft.Text("متصل" if logged_in and not auth.offline_mode else "غير متصل", size=12, color="#FFF"),
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=T.SUCCESS if (logged_in and not auth.offline_mode) else T.D_TEXT2,
            border_radius=12, padding=ft.padding.symmetric(horizontal=12, vertical=4),
        )
    else:
        avatar = ft.Container(
            content=ft.Icon(ft.Icons.PERSON_ROUNDED, size=36, color=T.tx2(page)),
            width=80, height=80,
            bgcolor=ft.Colors.with_opacity(0.08, T.tx(page)),
            border_radius=40, alignment=ft.Alignment(0, 0),
        )
        user_label = ft.Text("زائر", size=15, weight=ft.FontWeight.W_500, color=T.tx(page))
        status_chip = ft.Container(
            content=ft.Text("وضع بدون حساب", size=12, color=T.tx2(page)),
            border=ft.border.all(1, T.border(page)),
            border_radius=12, padding=ft.padding.symmetric(horizontal=12, vertical=4),
        )

    # ─── Login / Logout Button ───
    if logged_in:
        auth_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOGOUT_ROUNDED, color="#FFF", size=18),
                ft.Text("تسجيل الخروج", color="#FFF", size=14, weight=ft.FontWeight.W_600),
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=T.DANGER,
            border_radius=14, height=48, alignment=ft.Alignment(0, 0),
            on_click=lambda _: on_logout(), ink=True,
        )
    else:
        def _open_login(_):
            from views.login_view import LoginSheet
            sheet = LoginSheet(page, auth, on_login_done)
            page.show_dialog(sheet)

        auth_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOGIN_ROUNDED, color="#FFF", size=18),
                ft.Text("تسجيل الدخول", color="#FFF", size=14, weight=ft.FontWeight.W_600),
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=T.primary(page),
            border_radius=14, height=48, alignment=ft.Alignment(0, 0),
            on_click=_open_login, ink=True,
        )

    # ─── Stats Cards ───
    total_launches = stats.get("total_launches", 0)
    fav_count = len(stats.get("favorites", []))
    models_used = len(stats.get("models", {}))

    stats_row = ft.Row([
        _mini_stat(page, "الجلسات", str(total_launches), ft.Icons.PLAY_CIRCLE_ROUNDED, T.SUCCESS),
        _mini_stat(page, "النجوم", str(stars), ft.Icons.STAR_ROUNDED, T.star(page)),
        _mini_stat(page, "المفضلات", str(fav_count), ft.Icons.FAVORITE_ROUNDED, T.DANGER),
        _mini_stat(page, "نماذج", str(models_used), ft.Icons.SMART_TOY_ROUNDED, T.PRIMARY),
    ], spacing=8)

    # ─── Model usage breakdown ───
    model_items = []
    for m in MODELS:
        if not m.get("active"):
            continue
        ms = stats.get("models", {}).get(m["id"], {})
        launches = ms.get("launches", 0)
        last = ms.get("last_used", "—")
        if last and last != "—":
            last = last[:10]
        model_items.append(
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(m["icon"], color="#FFF", size=18),
                        width=36, height=36, bgcolor=m["color"], border_radius=10, alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(m["name"], size=14, weight=ft.FontWeight.W_600, color=T.tx(page)),
                        ft.Text(f"{launches} جلسة  •  آخر: {last}", size=11, color=T.tx2(page)),
                    ], spacing=2, expand=True),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=6),
            )
        )

    usage_card = ft.Container(
        content=ft.Column([
            ft.Text("إحصائيات الاستخدام", size=16, weight=ft.FontWeight.W_600, color=T.tx(page)),
            ft.Divider(height=1, color=T.border(page)),
            *model_items,
        ], spacing=8),
        bgcolor=T.card(page), border=ft.border.all(1, T.border(page)),
        border_radius=16, padding=ft.padding.all(18),
    )

    # ─── Settings ───
    dark = T.is_dark(page)
    settings_card = ft.Container(
        content=ft.Column([
            ft.Text("الإعدادات", size=16, weight=ft.FontWeight.W_600, color=T.tx(page)),
            ft.Divider(height=1, color=T.border(page)),
            _switch(page, "الوضع الليلي", dark, ft.Icons.DARK_MODE_ROUNDED, "theme"),
            _switch(page, "الإشعارات", settings.get("notifications", True), ft.Icons.NOTIFICATIONS_ROUNDED, "notifications"),
            _switch(page, "مزامنة تلقائية", settings.get("auto_sync", True), ft.Icons.CLOUD_SYNC_ROUNDED, "auto_sync"),
        ], spacing=10),
        bgcolor=T.card(page), border=ft.border.all(1, T.border(page)),
        border_radius=16, padding=ft.padding.all(18),
    )

    # ─── About ───
    about_card = ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.INFO_ROUNDED, color=T.primary(page), size=18),
                    ft.Text("حول التطبيق", size=16, weight=ft.FontWeight.W_600, color=T.tx(page))], spacing=8),
            ft.Divider(height=1, color=T.border(page)),
            _info_row(page, "الإصدار", ALIJADDI_VERSION),
            _info_row(page, "الإطار", "Flet (Flutter + Python)"),
            _info_row(page, "المنصات", "Windows • Android • iOS"),
            _info_row(page, "وضع الشبكة", "متصل" if not auth.offline_mode else "غير متصل (أوفلاين)"),
        ], spacing=8),
        bgcolor=T.card(page), border=ft.border.all(1, T.border(page)),
        border_radius=16, padding=ft.padding.all(18),
    )

    return ft.Column([
        ft.Container(height=20),
        ft.Container(content=avatar, alignment=ft.Alignment(0, 0)),
        ft.Container(content=user_label, alignment=ft.Alignment(0, 0), padding=ft.padding.only(top=10)),
        ft.Container(content=status_chip, alignment=ft.Alignment(0, 0), padding=ft.padding.only(top=4, bottom=6)),
        ft.Container(content=auth_btn, padding=ft.padding.symmetric(horizontal=40), alignment=ft.Alignment(0, 0)),
        ft.Container(content=stats_row, padding=ft.padding.symmetric(horizontal=16, vertical=8)),
        ft.Container(content=usage_card, padding=ft.padding.symmetric(horizontal=16)),
        ft.Container(content=settings_card, padding=ft.padding.symmetric(horizontal=16)),
        ft.Container(content=about_card, padding=ft.padding.symmetric(horizontal=16)),
        ft.Container(height=20),
    ], spacing=10, expand=True, scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)


def _mini_stat(page, label, value, icon, color):
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, color=color, size=20),
            ft.Text(value, size=17, weight=ft.FontWeight.BOLD, color=T.tx(page)),
            ft.Text(label, size=10, color=T.tx2(page)),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
        bgcolor=ft.Colors.with_opacity(0.06, color),
        border_radius=14,
        padding=ft.padding.symmetric(vertical=10, horizontal=6),
        expand=True,
    )


def _switch(page, label, value, icon, key):
    def _on(e):
        set_setting(key, e.control.value)
    return ft.Row([
        ft.Icon(icon, size=18, color=T.tx2(page)),
        ft.Text(label, size=14, color=T.tx(page), expand=True),
        ft.Switch(value=value, on_change=_on, active_color=T.primary(page)),
    ], spacing=8)


def _info_row(page, label, value):
    return ft.Row([
        ft.Text(label, size=13, color=T.tx2(page), expand=True),
        ft.Text(value, size=13, color=T.tx(page)),
    ])
