"""النافذة الرئيسية — PySide6: تطبيقاتي، متجر التطبيقات، تجربة قريبة من متاجر الأنظمة."""
from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from functools import partial

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QGridLayout, QStackedWidget,
    QSizePolicy, QCheckBox, QMessageBox, QSpacerItem,
    QToolButton, QApplication, QComboBox, QButtonGroup,
)
from PySide6.QtCore import Qt, QSize, Signal, QTimer, QUrl
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor, QPainter, QCursor, QGuiApplication, QDesktopServices

from ui.theme_qt import (
    ThemeManager, create_model_icon, MODEL_CARD_ICON_PX,
    PRIMARY, DANGER, SUCCESS, STAR, ACCENT_CYAN,
)
from ui.login_dialog import LoginDialog
from ui.hosted_app_dock import HostedAppDock
from ui import i18n
from services.auth_service import AuthService
from services.local_store import (
    record_launch, toggle_favorite, is_favorite, get_last_model,
    get_all_stats, load_settings, set_setting, load_session,
)
from services.addon_manager import (
    is_installed,
    installed_version,
    check_update,
    get_registry_offline_first,
    refresh_registry_background,
    install_model,
    uninstall_model,
    installed_app_path,
)
from services.paths import primary_icon_path, apps_root
from services.store_install_standard import (
    STORE_INSTALL_CONTRACT_VERSION,
    run_store_install_consent,
)
from services.model_catalog import load_qt_models
from services.platform_data import LEADERBOARD
from services.platform_store import (
    PLATFORM_STORE_ID,
    platform_releases_open_url,
    platform_store_local_version,
    platform_store_update_version,
    registry_platform_version,
)
from alijaddi import __version__ as ALIJADDI_VERSION

IS_MOBILE = platform.system() not in ("Windows", "Darwin", "Linux")


def _get_models():
    """قائمة التطبيقات لـ Qt — من الكتالوج الموحّد (manifests)."""
    return load_qt_models()


def _layout_width_bucket(cw: int) -> int:
    """تغيير تخطيط الشبكة عند عتبات العرض (أعمدة + الشريط الجانبي)."""
    if cw < 900:
        return 0
    if cw < 1180:
        return 1
    if cw < 1420:
        return 2
    return 3


def _grid_columns_for_bucket(bucket: int) -> int:
    return 1 if bucket <= 0 else (2 if bucket <= 2 else 3)


# ═══════════════════════════════════════════════════════════
#  REUSABLE WIDGETS
# ═══════════════════════════════════════════════════════════

class CardFrame(QFrame):
    """Styled card container."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")


class AccentLine(QFrame):
    """3px color accent at card top."""
    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(3)
        self.setStyleSheet(
            f"background: {color}; border: none; "
            f"border-top-left-radius: 16px; border-top-right-radius: 16px;"
        )


def _label(text, size=13, bold=False, color=None, wrap=False):
    lbl = QLabel(text)
    weight = QFont.Bold if bold else QFont.Normal
    lbl.setFont(QFont("Segoe UI", size // 1.33 + 1, weight))
    if color:
        lbl.setStyleSheet(f"color: {color}; background: transparent;")
    if wrap:
        lbl.setWordWrap(True)
    return lbl


def _icon_btn(text, color, callback, min_h=36):
    btn = QPushButton(text)
    btn.setStyleSheet(
        f"background: {color}; color: #FFF; border-radius: 10px; "
        f"padding: 6px 14px; font-weight: 600; font-size: 12px;"
    )
    btn.setMinimumHeight(min_h)
    btn.setCursor(Qt.PointingHandCursor)
    btn.clicked.connect(callback)
    return btn


def _outline_btn(text, color, callback):
    btn = QPushButton(text)
    btn.setStyleSheet(
        f"background: transparent; color: {color}; "
        f"border: 1px solid {color}; border-radius: 10px; "
        f"padding: 6px 14px; font-weight: 600; font-size: 12px;"
    )
    btn.setMinimumHeight(36)
    btn.setCursor(Qt.PointingHandCursor)
    btn.clicked.connect(callback)
    return btn


# ═══════════════════════════════════════════════════════════
#  MODEL CARD
# ═══════════════════════════════════════════════════════════

class ModelCard(CardFrame):
    launch_requested = Signal(str)
    like_requested = Signal(str)
    store_requested = Signal(str)

    def __init__(self, model: dict, theme: ThemeManager, parent=None):
        super().__init__(parent)
        self.model = model
        self.theme = theme
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.setMinimumWidth(260)
        self.setMaximumWidth(520)

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        main_lay.addWidget(AccentLine(model.get("color", PRIMARY)))

        body = QVBoxLayout()
        body.setContentsMargins(14, 10, 14, 12)
        body.setSpacing(8)

        active = model.get("active", True)
        mid = model["id"]
        exists = installed_app_path(mid, model.get("folder", "")).is_dir()
        color = model.get("color", PRIMARY)
        name = model.get("name", mid)

        hdr = QHBoxLayout()
        hdr.setSpacing(10)
        icon_lbl = QLabel()
        letter = name[0] if name else "?"
        icon_lbl.setPixmap(create_model_icon(letter, color, MODEL_CARD_ICON_PX))
        icon_lbl.setFixedSize(MODEL_CARD_ICON_PX, MODEL_CARD_ICON_PX)
        hdr.addWidget(icon_lbl)

        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_col.addWidget(_label(name, 15, bold=True, color=theme.text))
        desc = model.get("desc", "")
        desc_lbl = _label(desc, 11, color=theme.text2)
        desc_lbl.setWordWrap(True)
        desc_lbl.setMaximumHeight(52)
        name_col.addWidget(desc_lbl)
        hdr.addLayout(name_col, 1)
        body.addLayout(hdr)

        if not active:
            st_text, st_color = "قريباً في المتجر", theme.text2
        elif exists:
            st_text, st_color = "مثبّت وجاهز", SUCCESS
        else:
            st_text, st_color = "غير مثبّت — من المتجر", ACCENT_CYAN

        chip = QLabel(f"  {st_text}  ")
        chip.setStyleSheet(
            f"background: rgba({QColor(st_color).red()},{QColor(st_color).green()},"
            f"{QColor(st_color).blue()},0.12); color: {st_color}; "
            f"border-radius: 10px; padding: 5px 12px; font-size: 11px; font-weight: 600;"
        )
        chip.setFixedHeight(26)
        body.addWidget(chip, alignment=Qt.AlignRight)

        if active:
            rating = model.get("rating", 0)
            users = model.get("users", 0)
            stats_all = get_all_stats().get("models", {}).get(model["id"], {})
            launches = stats_all.get("launches", 0)
            r_text = f"⭐ {rating}  ·  {users} مستخدم"
            if launches:
                r_text += f"  ·  فُتح {launches} مرة"
            body.addWidget(_label(r_text, 12, color=theme.text2))
        else:
            body.addWidget(_label("سيتوفر قريباً", 12, color=theme.text2))

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color: {theme.border}; max-height: 1px;")
        body.addWidget(div)

        acts = QHBoxLayout()
        acts.setSpacing(10)
        if active and exists:
            run = _icon_btn("فتح التطبيق", color, partial(self._on_launch, mid), min_h=40)
            run.setToolTip("تشغيل التطبيق على جهازك")
            acts.addWidget(run)
        elif active:
            get_btn = _icon_btn("الحصول من المتجر", ACCENT_CYAN, partial(self._on_store, mid), min_h=40)
            get_btn.setToolTip("الانتقال إلى متجر التطبيقات للتنزيل")
            acts.addWidget(get_btn)
        else:
            acts.addWidget(_outline_btn("إشعاري عند الإطلاق", theme.text2, lambda: None))

        acts.addStretch()
        fav = is_favorite(mid)
        fav_btn = QPushButton("♥" if fav else "♡")
        fav_btn.setStyleSheet(
            f"color: {DANGER}; font-size: 20px; background: transparent; border: none;"
        )
        fav_btn.setCursor(Qt.PointingHandCursor)
        fav_btn.setToolTip("إزالة من المفضلة" if fav else "إضافة للمفضلة")
        fav_btn.clicked.connect(partial(self._on_like, mid))
        acts.addWidget(fav_btn)
        body.addLayout(acts)

        body_w = QWidget()
        body_w.setLayout(body)
        main_lay.addWidget(body_w)

        if not active:
            self.setStyleSheet(self.styleSheet() + "QFrame#card { opacity: 0.7; }")

    def _on_launch(self, mid):
        self.launch_requested.emit(mid)

    def _on_store(self, mid):
        self.store_requested.emit(mid)

    def _on_like(self, mid):
        self.like_requested.emit(mid)


# ═══════════════════════════════════════════════════════════
#  ADDON CARD
# ═══════════════════════════════════════════════════════════

class AddonCard(CardFrame):
    install_requested = Signal(str, str, str, str)
    uninstall_requested = Signal(str, str)
    update_requested = Signal(str, str, str, str)

    def __init__(self, model: dict, theme: ThemeManager, registry: dict, parent=None):
        super().__init__(parent)
        self.model = model
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.setMinimumWidth(260)
        self.setMaximumWidth(520)

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        color = model.get("color", PRIMARY)
        main_lay.addWidget(AccentLine(color))

        body = QVBoxLayout()
        body.setContentsMargins(14, 10, 14, 12)
        body.setSpacing(8)

        active = model.get("active", True)
        mid = model["id"]
        is_host_platform = mid == PLATFORM_STORE_ID

        if is_host_platform:
            exists = True
            model_installed = True
            local_ver = platform_store_local_version()
            try:
                new_ver = platform_store_update_version(registry)
            except Exception:
                new_ver = None
        else:
            exists = installed_app_path(mid, model.get("folder", "")).is_dir()
            model_installed = exists or is_installed(mid)
            local_ver = installed_version(model["id"]) or model.get("version", "")
            try:
                new_ver = check_update(model["id"], registry)
            except Exception:
                new_ver = None

        name = model.get("name", model["id"])
        letter = name[0] if name else "?"

        hdr = QHBoxLayout()
        hdr.setSpacing(10)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(create_model_icon(letter, color, MODEL_CARD_ICON_PX))
        icon_lbl.setFixedSize(MODEL_CARD_ICON_PX, MODEL_CARD_ICON_PX)
        hdr.addWidget(icon_lbl)

        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_col.addWidget(_label(name, 15, bold=True, color=theme.text))
        d_lbl = _label(model.get("desc", ""), 11, color=theme.text2)
        d_lbl.setWordWrap(True)
        d_lbl.setMaximumHeight(52)
        name_col.addWidget(d_lbl)
        hdr.addLayout(name_col, 1)
        body.addLayout(hdr)

        if is_host_platform:
            cat_ver = registry_platform_version(registry)
            if cat_ver and cat_ver != local_ver:
                st = f"المنصّة قيد التشغيل · لديك {local_ver} · سجل المتجر {cat_ver}"
            else:
                st = f"المنصّة قيد التشغيل · الإصدار {local_ver}"
            sc = SUCCESS
        elif model_installed and exists:
            st = f"مثبّت · الإصدار {local_ver}"
            sc = SUCCESS
        elif not active:
            st, sc = "قريباً في المتجر", theme.text2
        else:
            st = f"غير مثبّت · ≈ {model.get('size_mb', '?')} ميجابايت"
            sc = ACCENT_CYAN

        status = _label(st, 12, bold=True, color=sc)
        body.addWidget(status)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color: {theme.border};")
        body.addWidget(div)

        acts = QHBoxLayout()
        acts.setSpacing(8)
        folder = model.get("folder", "")
        dl = model.get("download_url", "")
        ver = model.get("version", "")

        if is_host_platform:
            if new_ver:
                acts.addWidget(
                    _icon_btn(
                        f"تحديث المنصّة إلى {new_ver}", STAR,
                        partial(self._emit_update, mid, "", folder, new_ver),
                        min_h=40,
                    )
                )
            acts.addWidget(
                _outline_btn(
                    "صفحة إصدارات GitHub",
                    theme.primary,
                    partial(self._emit_update, mid, "", folder, new_ver or local_ver),
                )
            )
        elif model_installed and exists:
            if new_ver:
                acts.addWidget(
                    _icon_btn(
                        f"تحديث إلى {new_ver}", STAR,
                        partial(self._emit_update, mid, dl, folder, new_ver),
                        min_h=40,
                    )
                )
            acts.addWidget(
                _outline_btn(
                    "إزالة التطبيق", DANGER,
                    partial(self._emit_uninstall, mid, folder),
                )
            )
        elif active and dl:
            acts.addWidget(
                _icon_btn(
                    "تنزيل وتثبيت", color,
                    partial(self._emit_install, mid, dl, folder, ver),
                    min_h=40,
                )
            )
        elif active:
            acts.addWidget(_label("التنزيل غير متاح حالياً", 11, color=theme.text2))

        body.addLayout(acts)

        body_w = QWidget()
        body_w.setLayout(body)
        main_lay.addWidget(body_w)

    def _emit_install(self, mid, url, folder, ver):
        self.install_requested.emit(mid, url, folder, ver)

    def _emit_uninstall(self, mid, folder):
        self.uninstall_requested.emit(mid, folder)

    def _emit_update(self, mid, url, folder, ver):
        self.update_requested.emit(mid, url, folder, ver)


# ═══════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self, theme: ThemeManager, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.auth = AuthService()
        self.models = _get_models()
        self._search_query = ""
        self._store_search_query = ""
        self._favorites_only = False
        self._installed_only = False
        self._section_index = 0
        self._registry = get_registry_offline_first()
        self._patch_platform_model_version_from_registry()
        self._activity_group = QButtonGroup(self)
        self._activity_group.setExclusive(True)
        self._status_label = None

        self.setWindowTitle("AliJaddi — علي جدّي")
        scr = QGuiApplication.primaryScreen()
        self.setMinimumSize(960, 600)
        if scr:
            ag = scr.availableGeometry()
            self.resize(
                min(1520, max(960, int(ag.width() * 0.92))),
                min(920, max(620, int(ag.height() * 0.9))),
            )
        else:
            self.resize(1320, 820)
        self.setLayoutDirection(i18n.layout_direction())
        self._width_bucket = -1
        self._shown_once = False

        icon_path = primary_icon_path()
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        body_wrap = QWidget()
        body_lay = QHBoxLayout(body_wrap)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)
        body_lay.addWidget(self._build_activity_rail())
        self.stack = QStackedWidget()
        body_lay.addWidget(self.stack, 1)
        root.addWidget(body_wrap, 1)

        self._hosted_dock = HostedAppDock(self.theme, self)
        self._hosted_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        # افتراضياً على اليمين لعرض المزيد من البطاقات دون تقليل ارتفاع المنطقة الرئيسية
        self.addDockWidget(Qt.RightDockWidgetArea, self._hosted_dock)
        self._hosted_dock.hide()

        root.addWidget(self._build_status_bar())

        self._activity_group.idClicked.connect(self._on_activity_clicked)
        self._rebuild_current_tab()
        self._width_bucket = _layout_width_bucket(max(self.width(), 360))

        self._set_status_text(i18n.tr("status_syncing_registry"))

        def _on_reg_done(reg: dict, reached_remote: bool):
            QTimer.singleShot(0, lambda: self._apply_registry_refresh(reg, reached_remote))

        refresh_registry_background(_on_reg_done)

    def _patch_platform_model_version_from_registry(self) -> None:
        """مزامنة رقم إصدار بطاقة المنصّة مع حقل ``platform`` في سجل المتجر."""
        pv = registry_platform_version(self._registry)
        if not pv:
            return
        for m in self.models:
            if m.get("id") == PLATFORM_STORE_ID:
                m["version"] = pv
                break

    def showEvent(self, event):
        super().showEvent(event)
        if not self._shown_once:
            self._shown_once = True
        QTimer.singleShot(0, self._maybe_relayout_for_width)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._shown_once:
            self._maybe_relayout_for_width()

    def _maybe_relayout_for_width(self):
        cw = max(self.width(), 360)
        bucket = _layout_width_bucket(cw)
        if bucket == self._width_bucket:
            return
        self._width_bucket = bucket
        if self.stack.count():
            self._rebuild_current_tab()

    # ─── Header ───
    def _build_header(self):
        t = self.theme
        bar = QFrame()
        bar.setObjectName("headerBar")
        bar.setFixedHeight(60)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(22, 6, 22, 6)
        lay.setSpacing(12)

        icon_path = primary_icon_path()
        if icon_path.exists():
            logo_img = QLabel()
            pm = QPixmap(str(icon_path)).scaled(
                22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            logo_img.setPixmap(pm)
            lay.addWidget(logo_img)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title_col.addWidget(_label("AliJaddi", 17, bold=True, color=t.text))
        title_col.addWidget(_label(i18n.tr("header_sub"), 10, color=t.text2))
        lay.addLayout(title_col)

        logged = self.auth.is_logged_in
        offline = self.auth.offline_mode
        dot_color = SUCCESS if (logged and not offline) else (STAR if offline else t.text2)
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {dot_color}; font-size: 10px;")
        dot.setToolTip("متصل" if (logged and not offline) else ("أوفلاين" if offline else "زائر"))
        lay.addWidget(dot)

        lay.addStretch()

        lang_lbl = QLabel(i18n.tr("lang"))
        lang_lbl.setStyleSheet(f"color:{t.text2};font-size:11px;")
        lay.addWidget(lang_lbl)
        lang_combo = QComboBox()
        lang_combo.setMinimumWidth(110)
        for code in i18n.LANG_CODES:
            lang_combo.addItem(i18n.LANG_LABELS[code], code)
        cur = i18n.current_lang()
        lang_combo.blockSignals(True)
        if cur in i18n.LANG_CODES:
            lang_combo.setCurrentIndex(i18n.LANG_CODES.index(cur))
        lang_combo.blockSignals(False)
        lang_combo.currentIndexChanged.connect(self._on_language_changed)
        lay.addWidget(lang_combo)

        theme_btn = QPushButton("🌙" if t.is_dark else "☀")
        theme_btn.setStyleSheet("font-size: 18px; background: transparent; border: none;")
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.setToolTip("تبديل المظهر")
        theme_btn.clicked.connect(self._toggle_theme)
        lay.addWidget(theme_btn)

        disp = self.auth.display_identity() if logged else ""
        if logged and disp and disp != "User":
            avatar_text = disp[0].upper()
            avatar_bg = PRIMARY
        else:
            avatar_text = "👤"
            avatar_bg = "transparent"

        avatar = QPushButton(avatar_text)
        avatar.setFixedSize(36, 36)
        avatar.setStyleSheet(
            f"background: {avatar_bg}; color: #FFF; border-radius: 18px; "
            f"font-size: 14px; font-weight: bold; border: none;"
        )
        avatar.setCursor(Qt.PointingHandCursor)
        avatar.setToolTip("الملف الشخصي")
        avatar.clicked.connect(lambda: self._set_section(4))
        lay.addWidget(avatar)

        return bar

    def _build_activity_rail(self):
        """شريط نشاط عمودي — أسلوب قريب من VS Code."""
        t = self.theme
        rail = QFrame()
        rail.setObjectName("actRail")
        edge = "border-left" if i18n.is_rtl() else "border-right"
        rail.setStyleSheet(
            f"QFrame#actRail {{ background: {t.bg}; {edge}: 1px solid {t.border}; }}"
        )
        rail.setFixedWidth(48)
        vl = QVBoxLayout(rail)
        vl.setContentsMargins(4, 14, 4, 10)
        vl.setSpacing(3)
        pc = QColor(t.primary)
        tip_keys = (
            "activity_tip_home",
            "activity_tip_store",
            "activity_tip_rank",
            "activity_tip_invite",
            "activity_tip_profile",
        )
        emojis = ("🏠", "🛒", "🏆", "👥", "👤")
        for idx, (emoji, tip_key) in enumerate(zip(emojis, tip_keys)):
            btn = QToolButton()
            btn.setCheckable(True)
            btn.setText(emoji)
            btn.setToolTip(i18n.tr(tip_key))
            btn.setFixedSize(38, 38)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                f"QToolButton {{ background: transparent; border: none; border-radius: 8px; "
                f"font-size: 17px; color: {t.text}; }}"
                f"QToolButton:hover {{ background: rgba(128,128,128,0.12); }}"
                f"QToolButton:checked {{ background: rgba({pc.red()},{pc.green()},{pc.blue()},0.25); }}"
            )
            self._activity_group.addButton(btn, idx)
            if idx == self._section_index:
                btn.setChecked(True)
            vl.addWidget(btn, alignment=Qt.AlignHCenter)
        vl.addStretch()
        return rail

    def _sync_activity_checks(self):
        for i in range(5):
            b = self._activity_group.button(i)
            if b:
                b.blockSignals(True)
                b.setChecked(i == self._section_index)
                b.blockSignals(False)

    def _build_status_bar(self):
        t = self.theme
        bar = QFrame()
        bar.setObjectName("statusBar")
        bar.setFixedHeight(28)
        bar.setStyleSheet(
            f"QFrame#statusBar {{ background: {t.header}; border-top: 1px solid {t.border}; }}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 3, 12, 3)
        self._status_label = QLabel(i18n.tr("status_catalog_local"))
        self._status_label.setStyleSheet(f"color: {t.text2}; font-size: 11px;")
        self._status_label.setWordWrap(False)
        lay.addWidget(self._status_label, 1)
        ver = QLabel(f"AliJaddi {ALIJADDI_VERSION}")
        ver.setStyleSheet(f"color: {t.text2}; font-size: 11px;")
        lay.addWidget(ver)
        return bar

    def _set_status_text(self, s: str):
        if self._status_label is not None:
            self._status_label.setText(s)

    def _apply_registry_refresh(self, reg: dict, reached_remote: bool):
        self._registry = reg
        self._patch_platform_model_version_from_registry()
        self._set_status_text(
            i18n.tr("status_catalog_online")
            if reached_remote
            else i18n.tr("status_catalog_local")
        )
        # إعادة بناء التبويب الحالي لتحديث عدّاد «تحديث متوفر» وأزرار الإصدار من سجل المتجر
        self._rebuild_current_tab()

    def _on_language_changed(self, idx: int):
        if idx < 0:
            return
        code = i18n.LANG_CODES[idx]
        if code == i18n.current_lang():
            return
        i18n.set_language(code)
        i18n.apply_to_app(QApplication.instance())
        self.setLayoutDirection(i18n.layout_direction())
        self._full_rebuild()

    def _on_activity_clicked(self, idx: int):
        if idx == self._section_index:
            return
        self._section_index = idx
        self._rebuild_current_tab()

    def _set_section(self, idx: int):
        if idx < 0 or idx > 4:
            return
        self._section_index = idx
        btn = self._activity_group.button(idx)
        if btn:
            btn.blockSignals(True)
            btn.setChecked(True)
            btn.blockSignals(False)
        self._rebuild_current_tab()

    def _rebuild_current_tab(self):
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()

        idx = self._section_index
        if idx == 0:
            self.stack.addWidget(self._build_models_tab())
        elif idx == 1:
            self.stack.addWidget(self._build_addons_tab())
        elif idx == 2:
            self.stack.addWidget(self._build_leaderboard_tab())
        elif idx == 3:
            self.stack.addWidget(self._build_invite_tab())
        elif idx == 4:
            self.stack.addWidget(self._build_profile_tab())
        self.stack.setCurrentIndex(0)

    # ─── Theme ───
    def _toggle_theme(self, _=None):
        self.theme.toggle()
        self.theme.apply(QApplication.instance())
        self._hosted_dock.refresh_theme(self.theme)
        self._full_rebuild()

    def _full_rebuild(self):
        cur = self._section_index
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())

        self._activity_group = QButtonGroup(self)
        self._activity_group.setExclusive(True)
        body_wrap = QWidget()
        body_lay = QHBoxLayout(body_wrap)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)
        body_lay.addWidget(self._build_activity_rail())
        self.stack = QStackedWidget()
        body_lay.addWidget(self.stack, 1)
        root.addWidget(body_wrap, 1)
        root.addWidget(self._build_status_bar())
        self._activity_group.idClicked.connect(self._on_activity_clicked)
        self._section_index = cur
        self._sync_activity_checks()
        self._rebuild_current_tab()
        self._hosted_dock.refresh_theme(self.theme)

    # ═══════════════════════════════════════
    #  TAB 0 — MODELS
    # ═══════════════════════════════════════
    def _build_models_tab(self):
        t = self.theme
        wrapper = QWidget()
        main_h = QHBoxLayout(wrapper)
        main_h.setContentsMargins(0, 0, 0, 0)
        main_h.setSpacing(0)

        # --- content ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget()
        col = QVBoxLayout(content)
        col.setContentsMargins(16, 14, 18, 14)
        col.setSpacing(12)

        # Hero — صف مدمج: عنوان + إحصاءات بجانب النص حيث يتسع الشاشة
        hero = CardFrame()
        h_lay = QVBoxLayout(hero)
        h_lay.setContentsMargins(14, 12, 14, 12)
        h_lay.setSpacing(8)
        hero_title = _label("تطبيقاتك في لمحة", 17, bold=True, color=t.text)
        hero_sub = _label(
            "تثبيت شبيه بمتاجر النظام: موافقة ثم اختيار مجلد الأب — يُنشأ مجلد التطبيق تلقائياً (المقترح: «تطبيقات علي جدي»). **Ali12** يفسّر الأخطاء عند الفشل.",
            12, color=t.text2, wrap=True,
        )
        hero_sub.setMaximumHeight(44)

        stats = get_all_stats()
        visible = [m for m in self.models if not m.get("store_only")]
        total_n = len([m for m in visible if m.get("active", True)])
        inst_c = sum(
            1
            for m in visible
            if m.get("active", True)
            and installed_app_path(m["id"], m.get("folder", "")).is_dir()
        )
        fav_c = len(stats.get("favorites", []))
        chips_row = QHBoxLayout()
        chips_row.setSpacing(8)
        for lbl, val, clr in [
            ("متاحة", str(total_n), t.primary),
            ("مثبّتة", str(inst_c), SUCCESS),
            ("مفضلة", str(fav_c), DANGER),
        ]:
            chip = CardFrame()
            cl = QVBoxLayout(chip)
            cl.setAlignment(Qt.AlignCenter)
            cl.setSpacing(0)
            cl.setContentsMargins(6, 6, 6, 6)
            cl.addWidget(_label(val, 15, bold=True, color=t.text), alignment=Qt.AlignCenter)
            cl.addWidget(_label(lbl, 10, color=t.text2), alignment=Qt.AlignCenter)
            chip.setStyleSheet(
                f"QFrame#card {{ background: rgba({QColor(clr).red()},"
                f"{QColor(clr).green()},{QColor(clr).blue()},0.08); "
                f"border: 1px solid {t.border}; border-radius: 10px; }}"
            )
            chip.setMinimumHeight(52)
            chips_row.addWidget(chip)

        cw_hero = max(self.width(), 360)
        if cw_hero >= 900:
            hero_top = QHBoxLayout()
            hero_top.setSpacing(16)
            left_col = QVBoxLayout()
            left_col.setSpacing(4)
            left_col.addWidget(hero_title)
            left_col.addWidget(hero_sub)
            hero_top.addLayout(left_col, 1)
            hero_top.addLayout(chips_row, 0)
            h_lay.addLayout(hero_top)
        else:
            h_lay.addWidget(hero_title)
            h_lay.addWidget(hero_sub)
            h_lay.addLayout(chips_row)
        col.addWidget(hero)

        # Guest banner
        if self.auth.is_guest:
            banner = CardFrame()
            bl = QHBoxLayout(banner)
            bl.setContentsMargins(16, 12, 16, 12)
            bl.addWidget(_label("☁", 18))
            bc = QVBoxLayout()
            bc.setSpacing(2)
            bc.addWidget(_label("أنت تتصفّح كزائر", 14, bold=True, color=t.text))
            bc.addWidget(_label(
                "من «حسابي» يمكنك تسجيل الدخول لمزامنة النجوم والمفضلة بين أجهزتك.",
                12, color=t.text2, wrap=True,
            ))
            bl.addLayout(bc, 1)
            col.addWidget(banner)

        cw = max(self.width(), 360)
        bucket = _layout_width_bucket(cw)
        cols = _grid_columns_for_bucket(bucket)
        show_sidebar = bucket >= 2

        # Search + filters (صف ثانٍ للشاشات الضيقة — أقرب لتطبيقات مثل فيسبوك)
        self._search_field = QLineEdit()
        self._search_field.setPlaceholderText("ابحث عن تطبيق بالاسم أو الوصف…")
        self._search_field.setMinimumHeight(40)
        self._search_field.textChanged.connect(self._on_search)
        self._search_field.setText(self._search_query)

        fav_filter = QPushButton("♥ المفضلة فقط")
        fav_filter.setObjectName("outline")
        fav_filter.setCursor(Qt.PointingHandCursor)
        if self._favorites_only:
            fav_filter.setStyleSheet(
                f"background: rgba(239,68,68,0.1); color: {DANGER}; "
                f"border: 1px solid {DANGER}; border-radius: 12px; padding: 8px 14px;"
            )
        fav_filter.clicked.connect(self._toggle_fav_filter)

        inst_filter = QPushButton("✓ المثبّتة فقط")
        inst_filter.setObjectName("outline")
        inst_filter.setCursor(Qt.PointingHandCursor)
        if self._installed_only:
            inst_filter.setStyleSheet(
                f"background: rgba(34,197,94,0.1); color: {SUCCESS}; "
                f"border: 1px solid {SUCCESS}; border-radius: 12px; padding: 8px 14px;"
            )
        inst_filter.clicked.connect(self._toggle_inst_filter)

        if cw < 720:
            col.addWidget(self._search_field)
            filt_row = QHBoxLayout()
            filt_row.addWidget(fav_filter)
            filt_row.addWidget(inst_filter)
            col.addLayout(filt_row)
        else:
            search_row = QHBoxLayout()
            search_row.addWidget(self._search_field, 1)
            search_row.addWidget(fav_filter)
            search_row.addWidget(inst_filter)
            col.addLayout(search_row)

        # Filter results
        query = self._search_query.strip().lower()
        filtered = []
        for m in self.models:
            if m.get("store_only"):
                continue
            if query and query not in m.get("name", "").lower() and query not in m.get("desc", "").lower():
                continue
            if self._favorites_only and not is_favorite(m["id"]):
                continue
            if self._installed_only and not installed_app_path(
                m["id"], m.get("folder", "")
            ).is_dir():
                continue
            filtered.append(m)

        filt_note = ""
        if query or self._favorites_only or self._installed_only:
            filt_note = " — مع تطبيق الفلاتر"
        col.addWidget(_label(f"{len(filtered)} تطبيق{filt_note}", 12, color=t.text2))

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        for i, m in enumerate(filtered):
            card = ModelCard(m, t)
            card.launch_requested.connect(self._launch_model)
            card.like_requested.connect(self._like_model)
            card.store_requested.connect(self._open_app_store)
            if cols == 1:
                card.setMaximumWidth(16777215)
                card.setMinimumWidth(max(260, min(420, cw - 40)))
            else:
                card.setMaximumWidth(480 if cols >= 3 else 520)
            grid.addWidget(card, i // cols, i % cols)

        if not filtered:
            empty = _label("لا يوجد تطبيق مطابق — جرّب تعديل البحث أو إيقاف الفلاتر.", 14, color=t.text2)
            empty.setAlignment(Qt.AlignCenter)
            grid.addWidget(empty, 0, 0, 1, cols)

        col.addLayout(grid)
        col.addStretch()
        scroll.setWidget(content)
        main_h.addWidget(scroll, 1)

        if show_sidebar:
            main_h.addWidget(self._build_sidebar())

        return wrapper

    def _build_sidebar(self):
        t = self.theme
        sb = QWidget()
        sb.setFixedWidth(268)
        sb_lay = QVBoxLayout(sb)
        sb_lay.setContentsMargins(10, 14, 14, 14)
        sb_lay.setSpacing(10)

        sess = load_session()
        try:
            stars = self.auth.fetch_stars() if self.auth.is_logged_in else (sess.get("stars", 0) if sess else 0)
        except Exception:
            stars = sess.get("stars", 0) if sess else 0

        # Stars card
        sc = CardFrame()
        sl = QVBoxLayout(sc)
        sl.setContentsMargins(16, 14, 16, 14)
        sl.setSpacing(6)
        sl.addWidget(_label("⭐ رصيد النجوم", 14, bold=True, color=t.text))
        sl.addWidget(_label(str(stars), 32, bold=True, color=t.star_color), alignment=Qt.AlignCenter)
        stats = get_all_stats()
        sl.addWidget(
            _label(f"مرات فتح التطبيقات: {stats.get('total_launches', 0)}", 12, color=t.text2),
            alignment=Qt.AlignCenter,
        )
        sb_lay.addWidget(sc)

        # Leaderboard
        lb = CardFrame()
        ll = QVBoxLayout(lb)
        ll.setContentsMargins(16, 14, 16, 14)
        ll.setSpacing(6)
        ll.addWidget(_label("أفضل المستخدمين", 13, bold=True, color=t.text))
        medals = ["🥇", "🥈", "🥉"]
        for u in LEADERBOARD[:4]:
            r = u["rank"]
            row = QHBoxLayout()
            row.addWidget(_label(medals[r - 1] if r <= 3 else f"#{r}", 14))
            row.addWidget(_label(u["name"], 13, color=t.text), 1)
            row.addWidget(_label(f"{u['stars']}⭐", 12, color=t.text2))
            ll.addLayout(row)
        sb_lay.addWidget(lb)

        # Quick access
        qa = CardFrame()
        ql = QVBoxLayout(qa)
        ql.setContentsMargins(16, 14, 16, 14)
        ql.setSpacing(6)
        ql.addWidget(_label("الوصول السريع", 14, bold=True, color=t.text))
        last = get_last_model()
        last_name = next((m.get("name", m["id"]) for m in self.models if m["id"] == last), "—") if last else "—"
        ql.addWidget(_label(f"آخر تطبيق: {last_name}", 12, color=t.text2))
        ql.addWidget(_label(f"المفضلات: {len(stats.get('favorites', []))}", 12, color=t.text2))
        sb_lay.addWidget(qa)

        sb_lay.addStretch()
        return sb

    # ═══════════════════════════════════════
    #  TAB 1 — ADDONS STORE
    # ═══════════════════════════════════════
    def _build_addons_tab(self):
        t = self.theme
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget()
        col = QVBoxLayout(content)
        col.setContentsMargins(16, 14, 18, 14)
        col.setSpacing(12)

        registry = self._registry if isinstance(self._registry, dict) else {"schema_version": 2, "models": []}

        cw = max(self.width(), 360)
        grid_cols = _grid_columns_for_bucket(_layout_width_bucket(cw))
        total = len(self.models)
        inst_c = sum(
            1
            for m in self.models
            if m.get("active", True)
            and (
                m.get("id") == PLATFORM_STORE_ID
                or installed_app_path(m["id"], m.get("folder", "")).is_dir()
            )
        )
        try:
            upd_c = sum(
                1
                for m in self.models
                if not m.get("store_only") and check_update(m["id"], registry) is not None
            )
            if platform_store_update_version(registry):
                upd_c += 1
        except Exception:
            upd_c = 0

        q_store = self._store_search_query.strip().lower()
        filtered_store = []
        for m in self.models:
            if q_store and q_store not in m.get("name", "").lower() and q_store not in m.get("desc", "").lower():
                continue
            filtered_store.append(m)

        # Header
        hdr = CardFrame()
        hl = QVBoxLayout(hdr)
        hl.setContentsMargins(14, 12, 14, 12)
        hl.setSpacing(6)
        hl.addWidget(_label("متجر التطبيقات", 17, bold=True, color=t.text))
        st_hint = _label(
            "**علي جدي (المنصّة):** بطاقة مثبّتة أولاً — يقرأ إصدارها من سجل المستودع (`platform`) بعد المزامنة، ثم زر تحديث أو صفحة GitHub. "
            "**تطبيقات المتجر:** تثبيت تلقائي في «تطبيقات علي جدي»؛ التحديثات من السجل عند ارتفاع رقم الإصدار في `registry.json`.",
            12, color=t.text2, wrap=True,
        )
        st_hint.setMaximumHeight(40)
        hl.addWidget(st_hint)
        hl.addWidget(_label(i18n.tr("store_offline_hint"), 11, color=t.text2, wrap=True))

        stats_row = QHBoxLayout()
        for lbl, val, clr in [
            ("في المتجر", str(total), t.primary),
            ("مثبّتة", str(inst_c), SUCCESS),
            ("تحديث متوفر", str(upd_c), t.star_color),
        ]:
            chip = QWidget()
            cl = QVBoxLayout(chip)
            cl.setAlignment(Qt.AlignCenter)
            cl.addWidget(_label(val, 18, bold=True, color=clr), alignment=Qt.AlignCenter)
            cl.addWidget(_label(lbl, 11, color=t.text2), alignment=Qt.AlignCenter)
            chip.setStyleSheet(
                f"background: rgba({QColor(clr).red()},{QColor(clr).green()},"
                f"{QColor(clr).blue()},0.08); border-radius: 12px; padding: 8px;"
            )
            stats_row.addWidget(chip)
        hl.addLayout(stats_row)
        col.addWidget(hdr)

        store_search = QLineEdit()
        store_search.setPlaceholderText(i18n.tr("store_search_ph"))
        store_search.setMinimumHeight(40)
        store_search.setText(self._store_search_query)
        store_search.textChanged.connect(self._on_store_search)
        col.addWidget(store_search)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        if not filtered_store:
            empty = _label(i18n.tr("store_empty"), 14, color=t.text2)
            empty.setAlignment(Qt.AlignCenter)
            grid.addWidget(empty, 0, 0, 1, max(1, grid_cols))
        for i, m in enumerate(filtered_store):
            card = AddonCard(m, t, registry)
            card.install_requested.connect(self._do_install)
            card.uninstall_requested.connect(self._do_uninstall)
            card.update_requested.connect(self._do_install)
            if grid_cols == 1:
                card.setMaximumWidth(16777215)
                card.setMinimumWidth(max(260, min(420, cw - 40)))
            else:
                card.setMaximumWidth(480 if grid_cols >= 3 else 520)
            grid.addWidget(card, i // grid_cols, i % grid_cols)

        col.addLayout(grid)
        col.addStretch()
        scroll.setWidget(content)
        return scroll

    # ═══════════════════════════════════════
    #  TAB 2 — LEADERBOARD
    # ═══════════════════════════════════════
    def _build_leaderboard_tab(self):
        t = self.theme
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        col = QVBoxLayout(content)
        col.setContentsMargins(16, 12, 16, 12)
        col.setSpacing(8)
        col.addWidget(_label("المتصدرون", 17, bold=True, color=t.text))
        col.addWidget(_label(
            "ترتيب حسب رصيد النجوم — شارك التطبيق لترتفع في القائمة.",
            12, color=t.text2, wrap=True,
        ))

        medals = ["🥇", "🥈", "🥉"]
        for u in LEADERBOARD:
            r = u["rank"]
            card = CardFrame()
            row = QHBoxLayout(card)
            row.setContentsMargins(14, 12, 14, 12)
            medal_text = medals[r - 1] if r <= 3 else f"#{r}"
            ml = QLabel(medal_text)
            ml.setFixedWidth(40)
            ml.setAlignment(Qt.AlignCenter)
            ml.setFont(QFont("Segoe UI", 16 if r <= 3 else 12))
            row.addWidget(ml)
            row.addWidget(_label(u["name"], 15, bold=True, color=t.text), 1)
            row.addWidget(_label(f"{u['stars']} ⭐", 14, color=t.star_color))
            col.addWidget(card)

        col.addStretch()
        scroll.setWidget(content)
        return scroll

    # ═══════════════════════════════════════
    #  TAB 3 — INVITE
    # ═══════════════════════════════════════
    def _build_invite_tab(self):
        t = self.theme
        wrapper = QWidget()
        lay = QVBoxLayout(wrapper)
        lay.setAlignment(Qt.AlignCenter)

        card = CardFrame()
        card.setMaximumWidth(420)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(30, 30, 30, 30)
        cl.setSpacing(12)
        cl.setAlignment(Qt.AlignCenter)

        cl.addWidget(_label("👥", 48), alignment=Qt.AlignCenter)
        cl.addWidget(_label("دعوة أصدقاء", 22, bold=True, color=t.text), alignment=Qt.AlignCenter)
        cl.addWidget(
            _label("ادعُ أصدقاءك واحصل على نجوم إضافية عند انضمامهم.", 14, color=t.text2, wrap=True),
            alignment=Qt.AlignCenter,
        )

        link_row = QHBoxLayout()
        link_input = QLineEdit("https://alijaddi.app/invite/CODE")
        link_input.setReadOnly(True)
        link_row.addWidget(link_input, 1)
        copy_btn = QPushButton("نسخ")
        copy_btn.setObjectName("primary")
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(
            lambda: QApplication.clipboard().setText("https://alijaddi.app/invite/CODE")
        )
        link_row.addWidget(copy_btn)
        cl.addLayout(link_row)

        lay.addWidget(card)
        return wrapper

    # ═══════════════════════════════════════
    #  TAB 4 — PROFILE
    # ═══════════════════════════════════════
    def _build_profile_tab(self):
        t = self.theme
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        col = QVBoxLayout(content)
        col.setContentsMargins(0, 14, 0, 14)
        col.setSpacing(12)
        col.setAlignment(Qt.AlignHCenter)

        logged = self.auth.is_logged_in
        sess = load_session()
        display = self.auth.display_identity() if logged else ""
        meta = (self.auth.user.get("user_metadata") or {}) if logged else {}
        username = (meta.get("username") or (sess.get("username", "") if sess else "")).strip()
        try:
            stars = self.auth.fetch_stars() if logged else (sess.get("stars", 0) if sess else 0)
        except Exception:
            stars = sess.get("stars", 0) if sess else 0

        show_name = display if (logged and display and display != "User") else ""
        if logged and show_name:
            avatar = QPushButton(show_name[0].upper())
            avatar.setFixedSize(72, 72)
            avatar.setStyleSheet(
                f"background: {PRIMARY}; color: #FFF; border-radius: 36px; "
                f"font-size: 28px; font-weight: bold; border: none;"
            )
        else:
            avatar = QLabel("👤")
            avatar.setFixedSize(72, 72)
            avatar.setAlignment(Qt.AlignCenter)
            avatar.setFont(QFont("Segoe UI", 32))
        col.addWidget(avatar, alignment=Qt.AlignCenter)

        col.addWidget(
            _label(show_name or i18n.tr("guest"), 15, bold=True, color=t.text), alignment=Qt.AlignCenter
        )
        if logged and username:
            col.addWidget(
                _label(f"{i18n.tr('profile_id')}: @{username}", 12, color=t.text2), alignment=Qt.AlignCenter
            )

        status_text = "متصل" if (logged and not self.auth.offline_mode) else "غير متصل"
        status_color = SUCCESS if (logged and not self.auth.offline_mode) else t.text2
        st_lbl = QLabel(f"  {status_text}  ")
        st_lbl.setStyleSheet(
            f"background: rgba({QColor(status_color).red()},{QColor(status_color).green()},"
            f"{QColor(status_color).blue()},0.15); color: {status_color}; "
            f"border-radius: 10px; padding: 4px 12px; font-size: 12px;"
        )
        col.addWidget(st_lbl, alignment=Qt.AlignCenter)

        # Auth button
        if logged:
            auth_btn = _icon_btn(i18n.tr("logout"), DANGER, self._do_logout, 44)
        else:
            auth_btn = _icon_btn(i18n.tr("login"), t.primary, self._do_login, 44)
        auth_btn.setMaximumWidth(300)
        col.addWidget(auth_btn, alignment=Qt.AlignCenter)

        # Stats
        all_stats = get_all_stats()
        stats_card = CardFrame()
        stats_card.setMaximumWidth(500)
        sc_lay = QHBoxLayout(stats_card)
        sc_lay.setContentsMargins(12, 12, 12, 12)
        for lbl, val, clr in [
            ("مرات الفتح", str(all_stats.get("total_launches", 0)), SUCCESS),
            ("النجوم", str(stars), t.star_color),
            ("المفضلات", str(len(all_stats.get("favorites", []))), DANGER),
            ("تطبيقات", str(len(all_stats.get("models", {}))), PRIMARY),
        ]:
            w = QWidget()
            wl = QVBoxLayout(w)
            wl.setAlignment(Qt.AlignCenter)
            wl.setSpacing(2)
            wl.addWidget(_label(val, 16, bold=True, color=t.text), alignment=Qt.AlignCenter)
            wl.addWidget(_label(lbl, 10, color=t.text2), alignment=Qt.AlignCenter)
            w.setStyleSheet(
                f"background: rgba({QColor(clr).red()},{QColor(clr).green()},"
                f"{QColor(clr).blue()},0.08); border-radius: 12px; padding: 8px;"
            )
            sc_lay.addWidget(w)
        col.addWidget(stats_card, alignment=Qt.AlignCenter)

        # Usage
        usage = CardFrame()
        usage.setMaximumWidth(500)
        ul = QVBoxLayout(usage)
        ul.setContentsMargins(18, 14, 18, 14)
        ul.setSpacing(8)
        ul.addWidget(_label("استخدام التطبيقات", 15, bold=True, color=t.text))
        for m in self.models:
            if m.get("store_only") or not m.get("active", True):
                continue
            ms = all_stats.get("models", {}).get(m["id"], {})
            launches = ms.get("launches", 0)
            last = ms.get("last_used", "—")
            if last and last != "—":
                last = last[:10]
            row = QHBoxLayout()
            icon_lbl = QLabel()
            icon_lbl.setPixmap(create_model_icon(
                m.get("name", "?")[0], m.get("color", PRIMARY), 28
            ))
            icon_lbl.setFixedSize(28, 28)
            row.addWidget(icon_lbl)
            rc = QVBoxLayout()
            rc.setSpacing(0)
            rc.addWidget(_label(m.get("name", m["id"]), 13, bold=True, color=t.text))
            rc.addWidget(_label(f"فُتح {launches} مرة  ·  آخر استخدام: {last}", 11, color=t.text2))
            row.addLayout(rc, 1)
            ul.addLayout(row)
        col.addWidget(usage, alignment=Qt.AlignCenter)

        # Settings
        settings_card = CardFrame()
        settings_card.setMaximumWidth(500)
        stl = QVBoxLayout(settings_card)
        stl.setContentsMargins(18, 14, 18, 14)
        stl.setSpacing(10)
        stl.addWidget(_label("الإعدادات", 15, bold=True, color=t.text))
        s = load_settings()
        for key, label in [
            ("notifications", "الإشعارات"),
            ("auto_sync", "مزامنة تلقائية"),
        ]:
            row = QHBoxLayout()
            row.addWidget(_label(label, 13, color=t.text), 1)
            cb = QCheckBox()
            cb.setChecked(s.get(key, True))
            cb.stateChanged.connect(partial(self._on_setting, key))
            row.addWidget(cb)
            stl.addLayout(row)
        col.addWidget(settings_card, alignment=Qt.AlignCenter)

        # تحديث المنصّة (GitHub Releases — التنزيل يدوي اختياري)
        upd_card = CardFrame()
        upd_card.setMaximumWidth(500)
        u_lay = QVBoxLayout(upd_card)
        u_lay.setContentsMargins(18, 14, 18, 14)
        u_lay.setSpacing(10)
        u_lay.addWidget(_label(i18n.tr("update_section"), 15, bold=True, color=t.text))
        uh = _label(i18n.tr("update_addon_hint"), 11, color=t.text2, wrap=True)
        u_lay.addWidget(uh)
        chk_btn = QPushButton(i18n.tr("update_check_btn"))
        chk_btn.setObjectName("primary")
        chk_btn.setCursor(Qt.PointingHandCursor)
        chk_btn.clicked.connect(self._check_platform_update)
        u_lay.addWidget(chk_btn, alignment=Qt.AlignCenter)
        col.addWidget(upd_card, alignment=Qt.AlignCenter)

        # About
        about = CardFrame()
        about.setMaximumWidth(500)
        al = QVBoxLayout(about)
        al.setContentsMargins(18, 14, 18, 14)
        al.setSpacing(6)
        al.addWidget(_label("حول التطبيق", 15, bold=True, color=t.text))
        for k, v in [
            ("الإصدار", ALIJADDI_VERSION),
            ("الإطار", "Qt for Python (PySide6)"),
            ("المنصات", "Windows • macOS • Android"),
            ("وضع الشبكة", "متصل" if not self.auth.offline_mode else "غير متصل"),
        ]:
            row = QHBoxLayout()
            row.addWidget(_label(k, 12, color=t.text2), 1)
            row.addWidget(_label(v, 12, color=t.text))
            al.addLayout(row)
        col.addWidget(about, alignment=Qt.AlignCenter)

        col.addStretch()
        scroll.setWidget(content)
        return scroll

    # ─── Actions ───
    def _check_platform_update(self):
        from services.platform_update import check_platform_update

        info = check_platform_update()
        if not info.ok:
            QMessageBox.warning(self, i18n.tr("update_section"), info.message)
            return
        if info.has_newer and info.html_url:
            r = QMessageBox.question(
                self,
                i18n.tr("update_section"),
                info.message + "\n\n" + i18n.tr("update_open_release") + "?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if r == QMessageBox.Yes:
                QDesktopServices.openUrl(QUrl(info.html_url))
        else:
            QMessageBox.information(self, i18n.tr("update_section"), info.message)

    def _on_search(self, text):
        self._search_query = text
        self._rebuild_current_tab()

    def _on_store_search(self, text):
        self._store_search_query = text
        self._rebuild_current_tab()

    def _toggle_fav_filter(self):
        self._favorites_only = not self._favorites_only
        self._rebuild_current_tab()

    def _toggle_inst_filter(self):
        self._installed_only = not self._installed_only
        self._rebuild_current_tab()

    def _open_app_store(self, _model_id: str = ""):
        """ينتقل إلى تبويب متجر التطبيقات (مثل «احصل» في المتاجر الشهيرة)."""
        self._set_section(1)

    def _launch_model(self, model_id):
        from ui.toast import show_toast
        model = next((m for m in self.models if m["id"] == model_id), None)
        if not model or not model.get("active", True):
            return
        launch_cmd = (model.get("launch") or "").strip()
        if not launch_cmd:
            show_toast(self, "لا يوجد أمر تشغيل مضبوط لهذا التطبيق.", "warning")
            return
        folder = installed_app_path(model_id, model.get("folder", ""))
        if not folder.is_dir():
            show_toast(
                self,
                f"التطبيق غير مثبّت. افتح «متجر التطبيقات» لاختيار مجلد التثبيت ثم التنزيل.",
                "warning",
            )
            return
        try:
            env = os.environ.copy()
            sess = load_session() or {}
            tok = (sess.get("access_token") or "").strip()
            if tok:
                env["ALIJADDI_JWT"] = tok
            env["ALIJADDI_PLATFORM_HOST"] = "1"
            env["ALIJADDI_THEME"] = "dark" if self.theme.is_dark else "light"
            env["ALIJADDI_APPS_ROOT"] = str(folder.parent.resolve())
            if sys.platform == "win32":
                env.setdefault("PYTHONUTF8", "1")
            self._hosted_dock.start_app(
                model.get("name", model_id),
                launch_cmd,
                folder,
                env,
                model_id=model_id,
            )
            record_launch(model_id)
            show_toast(
                self,
                f"✓ جارٍ تشغيل {model.get('name', model_id)} — راقب لوحة «تشغيل داخل المنصّة»",
                "success",
            )
        except Exception as e:
            show_toast(self, str(e), "error")

    def _like_model(self, model_id):
        toggle_favorite(model_id)
        self._rebuild_current_tab()

    def _open_platform_update_from_store(self, registry_hint_ver: str = "") -> None:
        """تحديث المنصّة من المتجر — يفتح صفحة الإصدارات (Setup / ZIP)؛ لا يمر عبر تثبيت ZIP للمتجر."""
        from services.platform_update import check_platform_update

        info = check_platform_update()
        url = (
            (info.html_url if info.ok and info.html_url else None)
            or platform_releases_open_url()
        )
        reg_ver = registry_platform_version(self._registry)
        body = (
            f"إصدار المنصّة عندك الآن: {platform_store_local_version()}\n"
            f"سجل المتجر (بعد آخر مزامنة): {reg_ver or '—'}\n\n"
            "نزّل **Setup.exe** الرسمي أو **ZIP** من GitHub، ثم أغلق علي جدي وثبّت التحديث."
        )
        if registry_hint_ver:
            body = f"في السجل يظهر إصدار: {registry_hint_ver}\n\n" + body

        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("تحديث علي جدي من المتجر")
        box.setText(body)
        open_btn = box.addButton("فتح صفحة الإصدارات", QMessageBox.ButtonRole.AcceptRole)
        box.addButton("لاحقاً", QMessageBox.ButtonRole.RejectRole)
        box.exec()
        if box.clickedButton() == open_btn:
            QDesktopServices.openUrl(QUrl(url))

    def _do_install(self, mid, url, folder, ver):
        from ui.download_dialog import DownloadDialog
        from ui.toast import show_toast

        if mid == PLATFORM_STORE_ID:
            self._open_platform_update_from_store(registry_hint_ver=str(ver or ""))
            return

        model = next((m for m in self.models if m["id"] == mid), {})
        name = model.get("name", mid)
        color = model.get("color", PRIMARY)

        prep = run_store_install_consent(
            self,
            model_id=mid,
            manifest_folder=folder,
            version=ver,
            display_name=name,
        )
        if prep.apps_parent is None:
            if prep.cancel_phase == "folder":
                show_toast(
                    self,
                    "أُلغي اختيار المجلد. اضغط «تنزيل وتثبيت» مجدداً لإكمال التثبيت.",
                    "warning",
                    4500,
                )
            elif prep.cancel_phase == "consent":
                show_toast(
                    self,
                    "أُلغي التثبيت من نافذة الموافقة.",
                    "info",
                    3500,
                )
            return

        chosen_path = prep.apps_parent

        dlg = DownloadDialog(name, color, self.theme, self)
        dlg.show()

        def _progress(msg):
            pass

        def _detail(pct, downloaded, total, speed, phase):
            dlg.emit_progress(pct, downloaded, total, speed, phase)

        def _done(ok, msg):
            QTimer.singleShot(0, lambda: dlg.emit_progress(
                100, 0, 0, 0, "done" if ok else "error"
            ))
            if ok:
                final_path = chosen_path / folder
                QTimer.singleShot(
                    500,
                    lambda: show_toast(
                        self,
                        f"✓ تم تثبيت «{name}» — المجلد: {final_path} "
                        f"واختصار على سطح المكتب إن نجح إنشاؤه.",
                        "success",
                        7000,
                    ),
                )
                QTimer.singleShot(1000, self._rebuild_current_tab)
            else:
                from Ali12 import (
                    ALI12_ASSISTANT_ID,
                    infer_install_event_kind_from_message,
                    suggest_after_install_failure,
                )

                ek = infer_install_event_kind_from_message(msg, ok=False)
                hint = suggest_after_install_failure(event_kind=ek, message=msg, detail={})

                def _show_err():
                    show_toast(self, f"تعذّر تنزيل «{name}»: {msg}", "error")

                def _show_ali12():
                    if hint:
                        show_toast(
                            self,
                            f"{ALI12_ASSISTANT_ID} — {hint}",
                            "info",
                            5500,
                        )

                QTimer.singleShot(400, _show_err)
                QTimer.singleShot(900, _show_ali12)

        install_model(
            mid,
            url,
            folder,
            ver,
            on_progress=_progress,
            on_done=_done,
            on_detail=_detail,
            display_name=name,
            apps_parent=chosen_path,
            install_contract=STORE_INSTALL_CONTRACT_VERSION,
        )

    def _do_uninstall(self, mid, folder):
        from ui.toast import show_toast

        if mid == PLATFORM_STORE_ID:
            QMessageBox.information(
                self,
                "متجر التطبيقات",
                "منصّة علي جدي لا تُزال من بطاقة المتجر.\n"
                "لإزالة التطبيق المثبّت من النظام: «إعدادات Windows» ← «التطبيقات» (إن استخدمت Setup Inno).",
            )
            return

        target_path = installed_app_path(mid, folder)
        reply = QMessageBox.question(
            self, "إزالة التطبيق",
            f"سيتم حذف التطبيق من جهازك.\nالمجلد: {target_path}\n"
            "يمكنك تنزيله مجدداً من متجر التطبيقات في أي وقت.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            ok, msg = uninstall_model(mid, folder)
            if ok:
                show_toast(self, msg, "success")
            else:
                from Ali12 import ALI12_ASSISTANT_ID, suggest_after_install_failure

                hint = suggest_after_install_failure(
                    event_kind="uninstall_fail", message=msg, detail={}
                )
                show_toast(self, msg, "error")

                def _uh():
                    if hint:
                        show_toast(
                            self,
                            f"{ALI12_ASSISTANT_ID} — {hint}",
                            "info",
                            5500,
                        )

                QTimer.singleShot(600, _uh)
            self._rebuild_current_tab()

    def _do_login(self):
        dlg = LoginDialog(self.theme, self.auth, self)
        dlg.login_done.connect(self._full_rebuild)
        dlg.exec()

    def _do_logout(self):
        self.auth.sign_out()
        self._full_rebuild()

    def _on_setting(self, key, state):
        set_setting(key, bool(state))
