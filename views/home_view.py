"""الشاشة الرئيسية — تعمل بدون إنترنت، تسجيل الدخول اختياري."""
from __future__ import annotations
import subprocess
import platform
from pathlib import Path
from typing import Callable
import flet as ft
import theme as T
from services.models_data import MODELS, LEADERBOARD, STORE_ITEMS
from services.local_store import (
    record_launch, toggle_favorite, is_favorite, get_last_model,
    get_all_stats, load_settings, set_setting, load_session,
)
from services.addon_manager import (
    is_installed, installed_version, check_update, get_registry,
    install_model, uninstall_model, fetch_manifest, load_installed,
)

IS_MOBILE = platform.system() not in ("Windows", "Darwin", "Linux")


def _desktop() -> Path:
    """مسار سطح المكتب — يعمل على Windows وعلى الموبايل (fallback)."""
    here = Path(__file__).resolve()
    for p in here.parents:
        if p.name == "AliJaddi":
            return p.parent
    home = Path.home()
    for candidate in [home / "OneDrive" / "Desktop", home / "Desktop", home]:
        if candidate.is_dir():
            return candidate
    return home


def _snack(page: ft.Page, text: str, color: str):
    """SnackBar آمن — يعمل مع Flet 0.84+."""
    try:
        sb = ft.SnackBar(content=ft.Text(text, color="#FFF"), bgcolor=color)
        page.overlay.append(sb)
        sb.open = True
        page.update()
    except Exception:
        pass


def _recent_models(limit: int = 3):
    stats = get_all_stats().get("models", {})
    rows = []
    for model_id, data in stats.items():
        last_used = data.get("last_used") or ""
        rows.append((model_id, last_used, data.get("launches", 0)))
    rows.sort(key=lambda item: item[1], reverse=True)
    return rows[:limit]


def _installed_models_count() -> int:
    desktop = _desktop()
    return sum(1 for model in MODELS if model.get("active") and (desktop / model["folder"]).is_dir())


def _summary_chip(page, icon, label: str, value: str, color: str):
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon, color=color, size=16),
                    width=30,
                    height=30,
                    border_radius=15,
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    [
                        ft.Text(value, size=14, weight=ft.FontWeight.W_700, color=T.tx(page)),
                        ft.Text(label, size=11, color=T.tx2(page)),
                    ],
                    spacing=1,
                    tight=True,
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_radius=14,
        border=ft.border.all(1, T.border(page)),
        bgcolor=ft.Colors.with_opacity(0.02, T.tx(page)),
    )


# ═══════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════
class AppHeader(ft.Container):
    def __init__(self, page, auth, on_toggle_theme, on_profile):
        logged_in = auth.is_logged_in
        offline = auth.offline_mode

        conn_color = T.SUCCESS if (logged_in and not offline) else ("#F59E0B" if offline else T.D_TEXT2)
        conn_tip = "متصل" if (logged_in and not offline) else ("أوفلاين" if offline else "زائر")
        status_dot = ft.Container(width=8, height=8, bgcolor=conn_color, border_radius=4, tooltip=conn_tip)

        email = auth.user.get("email", "")
        if logged_in and email:
            avatar_content = ft.Text(email[0].upper(), size=14, weight=ft.FontWeight.BOLD, color="#FFF")
            avatar_bg = T.PRIMARY
        else:
            avatar_content = ft.Icon(ft.Icons.PERSON_OUTLINED, size=18, color=T.tx2(page))
            avatar_bg = ft.Colors.with_opacity(0.1, T.tx(page))

        avatar = ft.Container(
            content=avatar_content, width=36, height=36, bgcolor=avatar_bg,
            border_radius=18, alignment=ft.Alignment(0, 0),
            on_click=lambda _: on_profile(), ink=True,
            tooltip="الملف الشخصي",
        )

        theme_icon = ft.Icons.DARK_MODE_ROUNDED if T.is_dark(page) else ft.Icons.LIGHT_MODE_ROUNDED
        theme_btn = ft.IconButton(
            icon=theme_icon, icon_color=T.tx2(page), icon_size=22,
            tooltip="تبديل المظهر", on_click=on_toggle_theme,
        )

        def _show_notifications(_):
            items = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.NEW_RELEASES_ROUNDED, color=T.PRIMARY),
                    title=ft.Text("أهلاً بك في AliJaddi"),
                    subtitle=ft.Text("ابدأ بتجربة النماذج أو سجّل الدخول للمزامنة."),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.STAR_ROUNDED, color=T.star(page)),
                    title=ft.Text("رصيد النجوم المحلي جاهز"),
                    subtitle=ft.Text("يمكنك استخدام التطبيق بالكامل بدون إنترنت."),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SMART_TOY_ROUNDED, color=T.ACCENT_CYAN),
                    title=ft.Text("اقتراح اليوم"),
                    subtitle=ft.Text("جرّب نموذج زخرفة أو Euqid من الشاشة الرئيسية."),
                ),
            ]
            sheet = ft.BottomSheet(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("الإشعارات", size=18, weight=ft.FontWeight.BOLD, color=T.tx(page)),
                            ft.Divider(color=T.border(page)),
                            *items,
                        ],
                        spacing=8,
                        tight=True,
                    ),
                    padding=ft.padding.all(20),
                )
            )
            page.overlay.append(sheet)
            sheet.open = True
            page.update()

        notif_stack = ft.Stack([
            ft.IconButton(icon=ft.Icons.NOTIFICATIONS_NONE_ROUNDED, icon_color=T.tx2(page), icon_size=22),
            ft.Container(
                content=ft.Text("3", size=9, color="#FFF", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                width=16, height=16, bgcolor=T.DANGER, border_radius=8,
                alignment=ft.Alignment(0, 0), right=4, top=4),
        ], width=40, height=40)
        notif_btn = ft.Container(content=notif_stack, on_click=_show_notifications, ink=True)

        logo = ft.Row([
            ft.Image(src="icon.png", width=32, height=32, fit=ft.BoxFit.CONTAIN),
            ft.Text("AliJaddi", size=20, weight=ft.FontWeight.BOLD, color=T.tx(page)),
            status_dot,
        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        super().__init__(
            content=ft.Row([logo, ft.Container(expand=True), theme_btn, notif_btn, avatar],
                           vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=T.header(page),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border=ft.border.only(bottom=ft.BorderSide(1, T.border(page))),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
            height=60,
        )


# ═══════════════════════════════════════════════════════
#  NAV TABS
# ═══════════════════════════════════════════════════════
class NavTabs(ft.Container):
    def __init__(self, page, selected, on_change):
        tabs = [
            (ft.Icons.SMART_TOY_ROUNDED, "النماذج"),
            (ft.Icons.EXTENSION_ROUNDED, "الإضافات"),
            (ft.Icons.STAR_ROUNDED, "المتصدرون"),
            (ft.Icons.PEOPLE_ROUNDED, "دعوة أصدقاء"),
            (ft.Icons.PERSON_ROUNDED, "حسابي"),
        ]
        btns = []
        for i, (icon, label) in enumerate(tabs):
            tab_idx = i if i < 4 else 99
            active = (tab_idx == selected) or (i == 4 and selected == 99)
            btns.append(ft.Container(
                content=ft.Row([
                    ft.Icon(icon, size=18, color=T.primary(page) if active else T.tx2(page)),
                    ft.Text(label, size=13, weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400,
                            color=T.primary(page) if active else T.tx2(page)),
                ], spacing=6),
                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                border=ft.border.only(bottom=ft.BorderSide(2.5, T.primary(page))) if active else None,
                on_click=lambda _, idx=tab_idx: on_change(idx), ink=True,
                border_radius=ft.border_radius.only(top_left=8, top_right=8),
            ))
        super().__init__(
            content=ft.Row(btns, spacing=2, scroll=ft.ScrollMode.AUTO),
            bgcolor=T.header(page),
            padding=ft.padding.symmetric(horizontal=12),
            border=ft.border.only(bottom=ft.BorderSide(1, T.border(page))),
        )


# ═══════════════════════════════════════════════════════
#  MODEL CARD
# ═══════════════════════════════════════════════════════
def _model_card(page, m, on_launch, on_like):
    active = m.get("active", True)
    desktop = _desktop()
    folder = desktop / m["folder"]
    exists = folder.is_dir()
    fav = is_favorite(m["id"])
    stats = get_all_stats().get("models", {}).get(m["id"], {})
    launches = stats.get("launches", 0)
    if not active:
        availability_label = "قريباً"
        availability_color = T.tx2(page)
        availability_icon = ft.Icons.SCHEDULE_ROUNDED
    elif exists:
        availability_label = "جاهز على جهازك"
        availability_color = T.SUCCESS
        availability_icon = ft.Icons.CHECK_CIRCLE_ROUNDED
    else:
        availability_label = "غير مثبت محلياً"
        availability_color = T.ACCENT_CYAN
        availability_icon = ft.Icons.DOWNLOAD_DONE_ROUNDED

    if active:
        stars_row = ft.Row([
            ft.Icon(ft.Icons.STAR_ROUNDED, color=T.star(page), size=16),
            ft.Text(str(m["rating"]), size=13, weight=ft.FontWeight.W_600, color=T.star(page)),
            ft.Text(f"  •  {m['users']} مستخدم", size=11, color=T.tx2(page)),
            ft.Container(expand=True),
            ft.Text(f"{launches} جلسة", size=11, color=T.tx2(page)) if launches > 0 else ft.Container(),
        ], spacing=4)
    else:
        stars_row = ft.Text("قريباً", size=13, color=T.tx2(page), italic=True)

    top_accent = ft.Container(height=3, bgcolor=m["color"],
                              border_radius=ft.border_radius.only(top_left=16, top_right=16))

    icon_box = ft.Container(
        content=ft.Icon(m["icon"], color="#FFF", size=28),
        width=50, height=50,
        bgcolor=m["color"] if active else ft.Colors.with_opacity(0.3, m["color"]),
        border_radius=14, alignment=ft.Alignment(0, 0),
    )

    status_chip = ft.Container(
        content=ft.Row(
            [
                ft.Icon(availability_icon, size=14, color=availability_color),
                ft.Text(availability_label, size=11, color=availability_color, weight=ft.FontWeight.W_600),
            ],
            spacing=4,
            tight=True,
        ),
        padding=ft.padding.symmetric(horizontal=10, vertical=6),
        border_radius=999,
        bgcolor=ft.Colors.with_opacity(0.08, availability_color),
        border=ft.border.all(1, ft.Colors.with_opacity(0.25, availability_color)),
    )

    if active and exists:
        launch_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color="#FFF", size=18),
                ft.Text("تشغيل", color="#FFF", size=13, weight=ft.FontWeight.W_600),
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=m["color"], border_radius=10,
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            on_click=lambda _, mid=m["id"]: on_launch(mid), ink=True,
        )
    elif active:
        launch_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, color=availability_color, size=18),
                ft.Text("غير مثبت", color=availability_color, size=13, weight=ft.FontWeight.W_600),
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            border=ft.border.all(1, ft.Colors.with_opacity(0.35, availability_color)),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            on_click=lambda _: _snack(page, f"النموذج {m['name']} غير متوفر محلياً حالياً", T.ACCENT_CYAN),
            ink=True,
            bgcolor=ft.Colors.with_opacity(0.06, availability_color),
        )
    else:
        launch_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE_ROUNDED, color=T.tx2(page), size=16),
                ft.Text("أذكرني", size=12, color=T.tx2(page)),
            ], spacing=4),
            border=ft.border.all(1, T.border(page)), border_radius=10,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            on_click=lambda _: _snack(page, "سيتم إشعارك عند إضافة النموذج", T.PRIMARY),
            ink=True,
        )

    actions = ft.Row([
        launch_btn,
        ft.Container(expand=True),
        ft.IconButton(
            icon=ft.Icons.FAVORITE_ROUNDED if fav else ft.Icons.FAVORITE_BORDER_ROUNDED,
            icon_color=T.DANGER, icon_size=20,
            tooltip="إزالة من المفضلة" if fav else "إعجاب",
            on_click=lambda _, mid=m["id"]: on_like(mid),
        ),
        ft.PopupMenuButton(
            icon=ft.Icons.MORE_VERT_ROUNDED, icon_color=T.tx2(page), icon_size=20,
            items=[
                ft.PopupMenuItem(content=ft.Row([ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=18), ft.Text("تفاصيل", size=14)], spacing=8)),
                ft.PopupMenuItem(content=ft.Row([ft.Icon(ft.Icons.SHARE_ROUNDED, size=18), ft.Text("مشاركة", size=14)], spacing=8)),
            ],
        ),
    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    return ft.Container(
        content=ft.Column([
            top_accent,
            ft.Container(
                content=ft.Column([
                    ft.Row([icon_box,
                            ft.Column([
                                ft.Text(m["name"], size=17, weight=ft.FontWeight.W_700, color=T.tx(page)),
                                ft.Text(m["desc"], size=12, color=T.tx2(page), max_lines=1,
                                         overflow=ft.TextOverflow.ELLIPSIS),
                            ], spacing=3, expand=True)], spacing=14),
                    status_chip,
                    stars_row,
                    ft.Divider(height=1, color=T.border(page)),
                    actions,
                ], spacing=10),
                padding=ft.padding.only(left=16, right=16, bottom=14, top=10),
            ),
        ], spacing=0),
        bgcolor=T.card(page), border_radius=16, border=ft.border.all(1, T.border(page)),
        opacity=1.0 if active else 0.65,
        col={"xs": 12, "sm": 12, "md": 6, "lg": 4},
    )


# ═══════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════
def _sidebar(page, auth):
    sess = load_session()
    stars = 0
    try:
        stars = auth.fetch_stars() if auth.is_logged_in else (sess.get("stars", 0) if sess else 0)
    except Exception:
        stars = sess.get("stars", 0) if sess else 0
    stats = get_all_stats()
    last = get_last_model()
    last_name = next((m["name"] for m in MODELS if m["id"] == last), None) if last else None

    stars_card = ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.STAR_ROUNDED, color=T.star(page), size=24),
                    ft.Text("رصيد النجوم", size=15, weight=ft.FontWeight.W_600, color=T.tx(page))], spacing=8),
            ft.Container(
                content=ft.Text(str(stars), size=36, weight=ft.FontWeight.BOLD, color=T.star(page),
                                text_align=ft.TextAlign.CENTER),
                alignment=ft.Alignment(0, 0), padding=ft.padding.symmetric(vertical=8)),
            ft.Text(f"إجمالي الجلسات: {stats.get('total_launches', 0)}", size=12, color=T.tx2(page),
                     text_align=ft.TextAlign.CENTER),
        ], spacing=8),
        bgcolor=T.card(page), border=ft.border.all(1, T.border(page)),
        border_radius=16, padding=ft.padding.all(18),
    )

    medals = ["🥇", "🥈", "🥉"]
    lb_items = []
    for u in LEADERBOARD[:5]:
        r = u["rank"]
        lb_items.append(ft.Row([
            ft.Text(medals[r - 1] if r <= 3 else f"#{r}", size=16),
            ft.Text(u["name"], size=14, weight=ft.FontWeight.W_500, color=T.tx(page), expand=True),
            ft.Text(f"{u['stars']}⭐", size=13, color=T.tx2(page)),
        ], spacing=8))

    lb_card = ft.Container(
        content=ft.Column([
            ft.Text("أفضل المستخدمين", size=15, weight=ft.FontWeight.W_600, color=T.tx(page)),
            ft.Divider(height=1, color=T.border(page)), *lb_items,
        ], spacing=8),
        bgcolor=T.card(page), border=ft.border.all(1, T.border(page)),
        border_radius=16, padding=ft.padding.all(18),
    )

    quick_card = ft.Container(
        content=ft.Column([
            ft.Text("الوصول السريع", size=15, weight=ft.FontWeight.W_600, color=T.tx(page)),
            ft.Divider(height=1, color=T.border(page)),
            ft.Text(f"آخر نموذج: {last_name or '—'}", size=13, color=T.tx2(page)),
            ft.Text(f"المفضلات: {len(stats.get('favorites', []))}", size=13, color=T.tx2(page)),
        ], spacing=8),
        bgcolor=T.card(page), border=ft.border.all(1, T.border(page)),
        border_radius=16, padding=ft.padding.all(18),
    )

    recent_items = []
    for model_id, _, launches in _recent_models(3):
        model = next((m for m in MODELS if m["id"] == model_id), None)
        if not model:
            continue
        recent_items.append(
            ft.Row(
                [
                    ft.Icon(model["icon"], color=model["color"], size=18),
                    ft.Text(model["name"], size=13, color=T.tx(page), expand=True),
                    ft.Text(f"{launches}x", size=12, color=T.tx2(page)),
                ],
                spacing=8,
            )
        )
    recent_card = ft.Container(
        content=ft.Column(
            [
                ft.Text("آخر ما استخدمته", size=15, weight=ft.FontWeight.W_600, color=T.tx(page)),
                ft.Divider(height=1, color=T.border(page)),
                *(recent_items or [ft.Text("لا يوجد استخدام سابق بعد", size=12, color=T.tx2(page))]),
            ],
            spacing=8,
        ),
        bgcolor=T.card(page), border=ft.border.all(1, T.border(page)),
        border_radius=16, padding=ft.padding.all(18),
    )

    return ft.Container(
        content=ft.Column([stars_card, lb_card, quick_card, recent_card], spacing=14, scroll=ft.ScrollMode.ADAPTIVE),
        width=280, padding=ft.padding.only(left=14),
    )


# ═══════════════════════════════════════════════════════
#  ADDONS STORE (متجر الإضافات)
# ═══════════════════════════════════════════════════════
def _addons_content(page, on_install, on_uninstall, on_update):
    """متجر الإضافات — تثبيت/تحديث/حذف النماذج."""
    desktop = _desktop()
    installed = load_installed()
    try:
        registry = get_registry()
    except Exception:
        registry = {"schema_version": 2, "models": []}
    reg_models = {e["id"]: e for e in registry.get("models", [])}

    total = len(MODELS)
    installed_count = sum(1 for m in MODELS if m.get("active") and (desktop / m["folder"]).is_dir())
    try:
        updatable = sum(1 for m in MODELS if check_update(m["id"], registry) is not None)
    except Exception:
        updatable = 0

    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.EXTENSION_ROUNDED, color=T.primary(page), size=28),
                ft.Column([
                    ft.Text("متجر الإضافات", size=22, weight=ft.FontWeight.BOLD, color=T.tx(page)),
                    ft.Text("ثبّت، حدّث أو احذف نماذج الذكاء الاصطناعي مباشرة.", size=13, color=T.tx2(page)),
                ], spacing=3, expand=True),
            ], spacing=12),
            ft.Container(height=8),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(total), size=20, weight=ft.FontWeight.BOLD, color=T.tx(page)),
                        ft.Text("متاح", size=11, color=T.tx2(page)),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=True, padding=ft.padding.all(10),
                    bgcolor=ft.Colors.with_opacity(0.06, T.primary(page)),
                    border_radius=12,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(installed_count), size=20, weight=ft.FontWeight.BOLD, color=T.SUCCESS),
                        ft.Text("مثبت", size=11, color=T.tx2(page)),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=True, padding=ft.padding.all(10),
                    bgcolor=ft.Colors.with_opacity(0.06, T.SUCCESS),
                    border_radius=12,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(updatable), size=20, weight=ft.FontWeight.BOLD, color=T.star(page)),
                        ft.Text("تحديث", size=11, color=T.tx2(page)),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=True, padding=ft.padding.all(10),
                    bgcolor=ft.Colors.with_opacity(0.06, T.star(page)),
                    border_radius=12,
                ),
            ], spacing=8),
        ], spacing=4),
        bgcolor=T.card(page), border=ft.border.all(1, T.border(page)),
        border_radius=20, padding=ft.padding.all(18),
    )

    cards = []
    for m in MODELS:
        exists = (desktop / m["folder"]).is_dir()
        model_installed = exists or is_installed(m["id"])
        local_ver = installed_version(m["id"]) or m.get("version", "")
        try:
            new_ver = check_update(m["id"], registry)
        except Exception:
            new_ver = None
        has_download = bool(m.get("download_url"))
        active = m.get("active", True)

        if model_installed and exists:
            status_text = f"مثبت — v{local_ver}"
            status_color = T.SUCCESS
            status_icon = ft.Icons.CHECK_CIRCLE_ROUNDED
        elif not active:
            status_text = "قريباً"
            status_color = T.tx2(page)
            status_icon = ft.Icons.SCHEDULE_ROUNDED
        else:
            status_text = f"غير مثبت — {m.get('size_mb', '?')} MB"
            status_color = T.ACCENT_CYAN
            status_icon = ft.Icons.CLOUD_DOWNLOAD_ROUNDED

        # أزرار الإجراء
        actions = []
        if model_installed and exists:
            if new_ver:
                actions.append(ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SYSTEM_UPDATE_ROUNDED, color="#FFF", size=16),
                        ft.Text(f"تحديث إلى v{new_ver}", color="#FFF", size=12, weight=ft.FontWeight.W_600),
                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=T.star(page), border_radius=10,
                    padding=ft.padding.symmetric(horizontal=14, vertical=8),
                    on_click=lambda _, mid=m["id"], url=m.get("download_url", ""), fld=m["folder"], v=new_ver: on_update(mid, url, fld, v),
                    ink=True,
                ))
            actions.append(ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DELETE_OUTLINE_ROUNDED, color=T.DANGER, size=16),
                    ft.Text("حذف", color=T.DANGER, size=12, weight=ft.FontWeight.W_600),
                ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                border=ft.border.all(1, ft.Colors.with_opacity(0.3, T.DANGER)),
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=14, vertical=8),
                on_click=lambda _, mid=m["id"], fld=m["folder"]: on_uninstall(mid, fld),
                ink=True,
            ))
        elif active and has_download:
            actions.append(ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, color="#FFF", size=16),
                    ft.Text("تثبيت", color="#FFF", size=12, weight=ft.FontWeight.W_600),
                ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=m["color"], border_radius=10,
                padding=ft.padding.symmetric(horizontal=14, vertical=8),
                on_click=lambda _, mid=m["id"], url=m.get("download_url", ""), fld=m["folder"], v=m.get("version", ""): on_install(mid, url, fld, v),
                ink=True,
            ))
        elif active:
            actions.append(ft.Container(
                content=ft.Text("رابط التحميل غير متوفر بعد", size=11, color=T.tx2(page)),
                padding=ft.padding.symmetric(horizontal=10, vertical=8),
            ))

        card = ft.Container(
            content=ft.Column([
                ft.Container(height=3, bgcolor=m["color"],
                             border_radius=ft.border_radius.only(top_left=16, top_right=16)),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(m["icon"], color="#FFF", size=24),
                                width=44, height=44,
                                bgcolor=m["color"] if active else ft.Colors.with_opacity(0.3, m["color"]),
                                border_radius=12, alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column([
                                ft.Text(m["name"], size=16, weight=ft.FontWeight.W_700, color=T.tx(page)),
                                ft.Text(m["desc"], size=12, color=T.tx2(page), max_lines=2,
                                         overflow=ft.TextOverflow.ELLIPSIS),
                            ], spacing=3, expand=True),
                        ], spacing=12),
                        ft.Row([
                            ft.Icon(status_icon, size=14, color=status_color),
                            ft.Text(status_text, size=12, color=status_color, weight=ft.FontWeight.W_600),
                            ft.Container(expand=True),
                            ft.Text(m.get("category", ""), size=10, color=T.tx2(page)),
                        ], spacing=6),
                        ft.Divider(height=1, color=T.border(page)),
                        ft.Row(actions, spacing=8) if actions else ft.Container(),
                    ], spacing=10),
                    padding=ft.padding.only(left=14, right=14, bottom=12, top=10),
                ),
            ], spacing=0),
            bgcolor=T.card(page), border_radius=16, border=ft.border.all(1, T.border(page)),
            opacity=1.0 if active else 0.6,
            col={"xs": 12, "sm": 12, "md": 6, "lg": 4},
        )
        cards.append(card)

    return ft.Column([
        ft.Container(content=header, padding=ft.padding.only(left=20, right=20, top=16, bottom=4)),
        ft.Container(
            content=ft.ResponsiveRow(cards, spacing=14, run_spacing=14),
            padding=ft.padding.symmetric(horizontal=16),
        ),
    ], spacing=10, scroll=ft.ScrollMode.ADAPTIVE, expand=True)


# ═══════════════════════════════════════════════════════
#  LEADERBOARD
# ═══════════════════════════════════════════════════════
def _leaderboard_content(page):
    medals = ["🥇", "🥈", "🥉"]
    items = []
    for u in LEADERBOARD:
        r = u["rank"]
        items.append(ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(medals[r - 1] if r <= 3 else f"#{r}", size=22 if r <= 3 else 16,
                                    text_align=ft.TextAlign.CENTER),
                    width=44, height=44, bgcolor=ft.Colors.with_opacity(0.1, T.tx(page)),
                    border_radius=12, alignment=ft.Alignment(0, 0)),
                ft.Column([
                    ft.Text(u["name"], size=16, weight=ft.FontWeight.W_600, color=T.tx(page)),
                    ft.Row([ft.Icon(ft.Icons.STAR_ROUNDED, color=T.star(page), size=14),
                            ft.Text(str(u["stars"]), size=13, color=T.star(page))], spacing=4),
                ], spacing=3, expand=True),
            ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=T.card(page), border=ft.border.all(1, T.border(page)),
            border_radius=16, padding=ft.padding.all(14),
        ))
    return ft.Column([
        ft.Container(content=ft.Text("المتصدرون", size=22, weight=ft.FontWeight.BOLD, color=T.tx(page)),
                     padding=ft.padding.all(20)),
        *items,
    ], spacing=10, scroll=ft.ScrollMode.ADAPTIVE, expand=True)


# ═══════════════════════════════════════════════════════
#  INVITE
# ═══════════════════════════════════════════════════════
def _invite_content(page):
    return ft.Column([
        ft.Container(height=40),
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.PEOPLE_ROUNDED, size=60, color=T.ACCENT_CYAN),
                ft.Text("دعوة أصدقاء", size=24, weight=ft.FontWeight.BOLD, color=T.tx(page)),
                ft.Text("شارك AliJaddi واحصل على 10 نجوم لكل صديق!",
                         size=14, color=T.tx2(page), text_align=ft.TextAlign.CENTER),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Row([
                        ft.Text("https://alijaddi.app/invite/CODE", size=12, color=T.tx2(page), expand=True, selectable=True),
                        ft.IconButton(icon=ft.Icons.CONTENT_COPY, icon_color=T.ACCENT_CYAN, icon_size=20,
                                      on_click=lambda _: _snack(page, "تم نسخ الرابط!", T.SUCCESS)),
                    ]),
                    bgcolor=ft.Colors.with_opacity(0.06, T.tx(page)),
                    border_radius=12, padding=ft.padding.symmetric(horizontal=16, vertical=8),
                ),
                ft.Container(height=14),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.SHARE_ROUNDED, icon_color="#25D366", icon_size=30, tooltip="WhatsApp"),
                    ft.IconButton(icon=ft.Icons.TELEGRAM, icon_color="#0088CC", icon_size=30, tooltip="Telegram"),
                    ft.IconButton(icon=ft.Icons.EMAIL_ROUNDED, icon_color=T.PRIMARY, icon_size=30, tooltip="Email"),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=16),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            bgcolor=T.card(page), border=ft.border.all(1, T.border(page)),
            border_radius=22, padding=ft.padding.all(30), width=400,
        ),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, scroll=ft.ScrollMode.ADAPTIVE)


# ═══════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════
def _footer(page):
    return ft.Container(
        content=ft.Row([
            ft.Text("© 2026 AliJaddi", size=12, color=T.tx2(page)),
            ft.Container(expand=True),
            ft.TextButton("حول", style=ft.ButtonStyle(color=T.tx2(page))),
            ft.TextButton("الخصوصية", style=ft.ButtonStyle(color=T.tx2(page))),
            ft.TextButton("تواصل", style=ft.ButtonStyle(color=T.tx2(page))),
        ]),
        bgcolor=T.header(page),
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
        border=ft.border.only(top=ft.BorderSide(1, T.border(page))),
    )


# ═══════════════════════════════════════════════════════
#  HOME VIEW
# ═══════════════════════════════════════════════════════
class HomeView(ft.View):
    def __init__(self, page: ft.Page, auth, on_rebuild: Callable):
        self.pg = page
        self.auth = auth
        self.on_rebuild = on_rebuild
        self._tab = 0
        self._search_query = ""
        self._favorites_only = False
        self._installed_only = False

        self.content_area = ft.Container(expand=True)
        self.sidebar_area = ft.Container()
        self._build_tab(0)

        self._header = AppHeader(page, auth, self._toggle_theme, self._show_profile)
        self._nav = NavTabs(page, 0, self._switch_tab)

        body = ft.Row([self.content_area, self.sidebar_area],
                       expand=True, spacing=0, vertical_alignment=ft.CrossAxisAlignment.START)

        fab = ft.FloatingActionButton(
            icon=ft.Icons.ROCKET_LAUNCH_ROUNDED, bgcolor=T.primary(page),
            mini=True, on_click=self._fab_click, tooltip="إجراءات سريعة",
        )

        super().__init__(
            route="/home", controls=[self._header, self._nav, body, _footer(page)],
            padding=0, spacing=0, floating_action_button=fab,
            floating_action_button_location=ft.FloatingActionButtonLocation.START_FLOAT,
            bgcolor=T.bg(page),
        )

    def _build_tab(self, idx):
        if idx == 0:
            settings = load_settings()
            stats = get_all_stats()
            query = self._search_query.strip().lower()
            filtered = []
            for m in MODELS:
                matches_query = not query or query in m["name"].lower() or query in m["desc"].lower()
                matches_fav = (not self._favorites_only) or is_favorite(m["id"])
                matches_installed = (not self._installed_only) or ((_desktop() / m["folder"]).is_dir())
                if matches_query and matches_fav and matches_installed:
                    filtered.append(m)

            total_models = len([m for m in MODELS if m.get("active")])
            installed_models = _installed_models_count()
            favorite_count = len(stats.get("favorites", []))
            has_filters = bool(query) or self._favorites_only or self._installed_only

            guest_banner = None
            if self.auth.is_guest:
                guest_banner = ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CLOUD_OFF_ROUNDED, color=T.ACCENT_CYAN, size=20),
                            ft.Column(
                                [
                                    ft.Text("أنت تستخدم التطبيق كزائر", size=14, weight=ft.FontWeight.W_600, color=T.tx(self.pg)),
                                    ft.Text("سجّل الدخول من تبويب حسابي لمزامنة النجوم والمفضلات على السحابة.", size=12, color=T.tx2(self.pg)),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor=T.card(self.pg),
                    border=ft.border.all(1, T.border(self.pg)),
                    border_radius=16,
                    padding=ft.padding.all(16),
                )

            hero_card = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("ابدأ من النموذج المناسب بسرعة", size=24, weight=ft.FontWeight.BOLD, color=T.tx(self.pg)),
                                        ft.Text(
                                            "رتّبنا الشاشة لتصل إلى النماذج المثبتة، المفضلة، وآخر استخداماتك بخطوات أقل.",
                                            size=13,
                                            color=T.tx2(self.pg),
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color="#FFF", size=22),
                                    width=44,
                                    height=44,
                                    border_radius=14,
                                    alignment=ft.Alignment(0, 0),
                                    bgcolor=T.primary(self.pg),
                                ),
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.ResponsiveRow(
                            [
                                _summary_chip(self.pg, ft.Icons.GRID_VIEW_ROUNDED, "نماذج نشطة", str(total_models), T.primary(self.pg)),
                                _summary_chip(self.pg, ft.Icons.DOWNLOAD_DONE_ROUNDED, "جاهزة محلياً", str(installed_models), T.SUCCESS),
                                _summary_chip(self.pg, ft.Icons.FAVORITE_ROUNDED, "المفضلة", str(favorite_count), T.DANGER),
                            ],
                            spacing=10,
                            run_spacing=10,
                        ),
                    ],
                    spacing=14,
                ),
                padding=ft.padding.all(18),
                border_radius=20,
                bgcolor=T.card(self.pg),
                border=ft.border.all(1, T.border(self.pg)),
            )

            onboarding = None
            if not settings.get("onboarding_dismissed", False):
                onboarding = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.WAVING_HAND_ROUNDED, color=T.star(self.pg), size=22),
                                    ft.Text("جولة سريعة", size=16, weight=ft.FontWeight.BOLD, color=T.tx(self.pg)),
                                    ft.Container(expand=True),
                                    ft.TextButton("إخفاء", on_click=lambda _: self._dismiss_onboarding(), style=ft.ButtonStyle(color=T.tx2(self.pg))),
                                ]
                            ),
                            ft.Text("1. ابحث عن أي نموذج.  2. أضفه للمفضلة.  3. شغّله مباشرة.  4. سجّل الدخول لاحقاً إذا أردت المزامنة.", size=13, color=T.tx2(self.pg)),
                        ],
                        spacing=8,
                    ),
                    bgcolor=T.card(self.pg),
                    border=ft.border.all(1, T.border(self.pg)),
                    border_radius=16,
                    padding=ft.padding.all(16),
                )

            search_bar = ft.Column(
                [
                    ft.Row(
                        [
                            ft.TextField(
                                value=self._search_query,
                                hint_text="ابحث عن نموذج، مثل: زخرفة أو عقد",
                                prefix_icon=ft.Icons.SEARCH_ROUNDED,
                                on_change=self._on_search_change,
                                border_radius=14,
                                expand=True,
                                height=48,
                            ),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(
                                            ft.Icons.FAVORITE_ROUNDED if self._favorites_only else ft.Icons.FAVORITE_BORDER_ROUNDED,
                                            color=T.DANGER,
                                            size=18,
                                        ),
                                        ft.Text("المفضلة", size=12, color=T.tx(self.pg)),
                                    ],
                                    spacing=6,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                on_click=lambda _: self._toggle_favorites_only(),
                                ink=True,
                                padding=ft.padding.symmetric(horizontal=12, vertical=10),
                                border=ft.border.all(1, T.border(self.pg)),
                                border_radius=14,
                                bgcolor=ft.Colors.with_opacity(0.06, T.DANGER) if self._favorites_only else T.card(self.pg),
                            ),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(
                                            ft.Icons.DOWNLOAD_DONE_ROUNDED if self._installed_only else ft.Icons.DOWNLOAD_ROUNDED,
                                            color=T.SUCCESS,
                                            size=18,
                                        ),
                                        ft.Text("جاهز محلياً", size=12, color=T.tx(self.pg)),
                                    ],
                                    spacing=6,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                on_click=lambda _: self._toggle_installed_only(),
                                ink=True,
                                padding=ft.padding.symmetric(horizontal=12, vertical=10),
                                border=ft.border.all(1, T.border(self.pg)),
                                border_radius=14,
                                bgcolor=ft.Colors.with_opacity(0.06, T.SUCCESS) if self._installed_only else T.card(self.pg),
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                f"{len(filtered)} نتيجة"
                                + (" من النماذج المتاحة" if not has_filters else " بعد تطبيق الفلاتر"),
                                size=12,
                                color=T.tx2(self.pg),
                            ),
                            ft.Container(expand=True),
                            ft.TextButton(
                                "مسح الفلاتر",
                                visible=has_filters,
                                on_click=lambda _: self._clear_filters(),
                                style=ft.ButtonStyle(color=T.primary(self.pg)),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
            )

            recent_row = []
            for model_id, _, launches in _recent_models(3):
                model = next((m for m in MODELS if m["id"] == model_id), None)
                if not model:
                    continue
                recent_row.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(model["icon"], color=model["color"], size=16),
                                ft.Text(model["name"], size=12, color=T.tx(self.pg)),
                            ],
                            spacing=6,
                        ),
                        padding=ft.padding.symmetric(horizontal=10, vertical=8),
                        border=ft.border.all(1, T.border(self.pg)),
                        border_radius=12,
                        on_click=lambda _, mid=model["id"]: self._launch(mid),
                        ink=True,
                        tooltip=f"تشغيل ({launches} جلسة)",
                    )
                )

            cards = ft.ResponsiveRow(
                [_model_card(self.pg, m, self._launch, self._like) for m in filtered],
                spacing=14,
                run_spacing=14,
            )
            empty_state = None
            if not filtered:
                empty_state = ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, color=T.tx2(self.pg), size=42),
                            ft.Text("لا توجد نتائج مطابقة", size=15, weight=ft.FontWeight.W_600, color=T.tx(self.pg)),
                            ft.Text("جرّب إزالة الفلترة أو البحث بكلمة أخرى.", size=12, color=T.tx2(self.pg)),
                        ],
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(24),
                    bgcolor=T.card(self.pg),
                    border=ft.border.all(1, T.border(self.pg)),
                    border_radius=16,
                )

            top_controls = [
                hero_card,
            ]
            if guest_banner:
                top_controls.append(guest_banner)
            if onboarding:
                top_controls.append(onboarding)
            top_controls.append(search_bar)
            if recent_row:
                top_controls.append(
                    ft.Column(
                        [
                            ft.Text("حديثاً", size=13, weight=ft.FontWeight.W_600, color=T.tx(self.pg)),
                            ft.Row(recent_row, spacing=8, scroll=ft.ScrollMode.AUTO),
                        ],
                        spacing=8,
                    )
                )
            top_controls.append(empty_state or cards)

            self.content_area.content = ft.Container(
                content=ft.Column(top_controls, spacing=14, scroll=ft.ScrollMode.ADAPTIVE),
                padding=ft.padding.all(16),
                expand=True,
            )
            self.sidebar_area.content = _sidebar(self.pg, self.auth)
            self.sidebar_area.visible = True
        elif idx == 1:
            try:
                addons_ui = _addons_content(
                    self.pg,
                    on_install=self._install_addon,
                    on_uninstall=self._uninstall_addon,
                    on_update=self._install_addon,
                )
            except Exception as exc:
                addons_ui = ft.Column([
                    ft.Container(height=40),
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color=T.DANGER, size=48),
                            ft.Text("تعذّر تحميل متجر الإضافات", size=18,
                                    weight=ft.FontWeight.BOLD, color=T.tx(self.pg)),
                            ft.Text(str(exc), size=12, color=T.tx2(self.pg),
                                    text_align=ft.TextAlign.CENTER),
                            ft.Container(height=10),
                            ft.Container(
                                content=ft.Text("إعادة المحاولة", color="#FFF", size=14,
                                                weight=ft.FontWeight.W_600),
                                bgcolor=T.primary(self.pg), border_radius=12,
                                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                on_click=lambda _: self._switch_tab(1), ink=True,
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=ft.padding.all(30),
                        bgcolor=T.card(self.pg), border_radius=20,
                        border=ft.border.all(1, T.border(self.pg)),
                        width=400,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
            self.content_area.content = ft.Container(
                content=addons_ui,
                padding=ft.padding.symmetric(horizontal=0), expand=True,
            )
            self.sidebar_area.visible = False
        elif idx == 2:
            self.content_area.content = ft.Container(content=_leaderboard_content(self.pg),
                                                      padding=ft.padding.symmetric(horizontal=16), expand=True)
            self.sidebar_area.visible = False
        elif idx == 3:
            self.content_area.content = ft.Container(content=_invite_content(self.pg),
                                                      padding=ft.padding.symmetric(horizontal=16), expand=True)
            self.sidebar_area.visible = False
        elif idx == 99:
            from views.profile_view import build_profile_content
            self.content_area.content = ft.Container(
                content=build_profile_content(self.pg, self.auth, self._on_login_done, self._logout),
                padding=ft.padding.symmetric(horizontal=0), expand=True)
            self.sidebar_area.visible = False

    def _switch_tab(self, idx):
        self._tab = idx
        self._nav = NavTabs(self.pg, idx, self._switch_tab)
        self._build_tab(idx)
        self.controls[1] = self._nav
        self.pg.update()

    def _toggle_theme(self, _):
        dark = not T.is_dark(self.pg)
        set_setting("theme", "dark" if dark else "light")
        T.apply_theme(self.pg, dark)
        self.on_rebuild()

    def _show_profile(self):
        self._switch_tab(99)

    def _on_login_done(self):
        self.on_rebuild()

    def _logout(self):
        self.auth.sign_out()
        self.on_rebuild()

    def _launch(self, model_id):
        model = next((m for m in MODELS if m["id"] == model_id), None)
        if not model or not model.get("active"):
            return
        desktop = _desktop()
        folder = desktop / model["folder"]
        if not folder.is_dir():
            _snack(self.pg, f"مجلد {model['folder']} غير موجود", T.DANGER)
            return
        try:
            subprocess.Popen(model["launch"], cwd=str(folder), shell=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            record_launch(model_id)
            _snack(self.pg, f"✓ تم تشغيل {model['name']}", T.SUCCESS)
        except Exception as e:
            _snack(self.pg, f"خطأ: {e}", T.DANGER)

    def _like(self, model_id):
        now_fav = toggle_favorite(model_id)
        _snack(self.pg,
               "❤ تمت الإضافة للمفضلة" if now_fav else "تمت الإزالة من المفضلة",
               T.DANGER if now_fav else T.D_BORDER)
        self._build_tab(self._tab)
        self.pg.update()

    def _on_search_change(self, e):
        self._search_query = e.control.value or ""
        self._build_tab(self._tab)
        self.pg.update()

    def _toggle_favorites_only(self):
        self._favorites_only = not self._favorites_only
        self._build_tab(self._tab)
        self.pg.update()

    def _toggle_installed_only(self):
        self._installed_only = not self._installed_only
        self._build_tab(self._tab)
        self.pg.update()

    def _clear_filters(self):
        self._search_query = ""
        self._favorites_only = False
        self._installed_only = False
        self._build_tab(self._tab)
        self.pg.update()

    def _install_addon(self, model_id, download_url, folder, version):
        _snack(self.pg, f"جارٍ تحميل {model_id}...", T.PRIMARY)

        def _on_progress(msg):
            _snack(self.pg, msg, T.PRIMARY)

        def _on_done(ok, msg):
            if ok:
                _snack(self.pg, msg, T.SUCCESS)
            else:
                _snack(self.pg, msg, T.DANGER)
            self._build_tab(self._tab)
            self.pg.update()

        install_model(model_id, download_url, folder, version,
                      on_progress=_on_progress, on_done=_on_done)

    def _uninstall_addon(self, model_id, folder):
        dlg = ft.AlertDialog(
            title=ft.Text("تأكيد الحذف", weight=ft.FontWeight.BOLD),
            content=ft.Text(f"هل تريد حذف {folder} من جهازك؟\nيمكنك إعادة تثبيته لاحقاً من متجر الإضافات."),
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def _close_dlg(_=None):
            dlg.open = False
            self.pg.update()

        def _do_uninstall(_):
            _close_dlg()
            ok, msg = uninstall_model(model_id, folder)
            _snack(self.pg, msg, T.SUCCESS if ok else T.DANGER)
            self._build_tab(self._tab)
            self.pg.update()

        dlg.actions = [
            ft.TextButton("إلغاء", on_click=_close_dlg),
            ft.TextButton("حذف", on_click=_do_uninstall,
                          style=ft.ButtonStyle(color=T.DANGER)),
        ]
        self.pg.overlay.append(dlg)
        dlg.open = True
        self.pg.update()

    def _dismiss_onboarding(self):
        set_setting("onboarding_dismissed", True)
        self._build_tab(self._tab)
        self.pg.update()

    def _fab_click(self, _):
        last = get_last_model()
        last_name = next((m["name"] for m in MODELS if m["id"] == last), "—") if last else "—"

        def close_bs(_):
            self.pg.pop_dialog()

        bs = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("إجراءات سريعة", size=18, weight=ft.FontWeight.BOLD, color=T.tx(self.pg)),
                    ft.Divider(color=T.border(self.pg)),
                    ft.ListTile(leading=ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=T.SUCCESS),
                                title=ft.Text(f"تشغيل: {last_name}"),
                                on_click=lambda _: (_close_bs(), self._launch(last) if last else None)),
                    ft.ListTile(leading=ft.Icon(ft.Icons.STOREFRONT_ROUNDED, color=T.PRIMARY),
                                title=ft.Text("المتجر"),
                                on_click=lambda _: (_close_bs(), self._switch_tab(1))),
                    ft.ListTile(leading=ft.Icon(ft.Icons.PERSON_ROUNDED, color=T.ACCENT_CYAN),
                                title=ft.Text("الملف الشخصي"),
                                on_click=lambda _: (_close_bs(), self._show_profile())),
                ], spacing=6, tight=True), padding=ft.padding.all(20),
            ),
        )

        def _close_bs():
            bs.open = False
            self.pg.update()

        self.pg.overlay.append(bs)
        bs.open = True
        self.pg.update()
