"""النافذة الرئيسية — PySide6: تطبيقاتي، متجر التطبيقات، تجربة قريبة من متاجر الأنظمة."""
from __future__ import annotations

import os
import subprocess
import platform
from pathlib import Path
from functools import partial

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QGridLayout, QStackedWidget,
    QTabBar, QSizePolicy, QCheckBox, QMessageBox, QSpacerItem,
    QToolButton, QApplication, QComboBox,
)
from PySide6.QtCore import Qt, QSize, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor, QPainter, QCursor

from ui.theme_qt import (
    ThemeManager, create_model_icon,
    PRIMARY, DANGER, SUCCESS, STAR, ACCENT_CYAN,
)
from ui.login_dialog import LoginDialog
from ui import i18n
from services.auth_service import AuthService
from services.local_store import (
    record_launch, toggle_favorite, is_favorite, get_last_model,
    get_all_stats, load_settings, set_setting, load_session,
)
from services.addon_manager import (
    is_installed, installed_version, check_update, get_registry,
    install_model, uninstall_model, load_installed,
)
from alijaddi import __version__ as ALIJADDI_VERSION

IS_MOBILE = platform.system() not in ("Windows", "Darwin", "Linux")

LEADERBOARD = [
    {"name": "أحمد", "stars": 520, "rank": 1},
    {"name": "فاطمة", "stars": 480, "rank": 2},
    {"name": "محمد", "stars": 390, "rank": 3},
    {"name": "زينب", "stars": 310, "rank": 4},
    {"name": "علي", "stars": 275, "rank": 5},
    {"name": "نور", "stars": 210, "rank": 6},
    {"name": "حسن", "stars": 185, "rank": 7},
]



def _get_models():
    """Load models without Flet dependency."""
    import json
    here = Path(__file__).resolve()
    manifests_dir = None
    for p in here.parents:
        if p.name == "AliJaddi":
            manifests_dir = p / "addons" / "manifests"
            break
    models = []
    seen = set()
    if manifests_dir and manifests_dir.is_dir():
        for f in sorted(manifests_dir.glob("*.json")):
            try:
                d = json.loads(f.read_text("utf-8"))
                mid = d.get("id", f.stem)
                if mid not in seen:
                    seen.add(mid)
                    models.append(d)
            except Exception:
                continue
    if not models:
        models = _FALLBACK_MODELS[:]
    return models


_FALLBACK_MODELS = [
    {"id": "zakhrafatan", "name": "زخرفة", "desc": "توليد وتصنيف الزخارف العربية بالذكاء الاصطناعي",
     "color": "#8B5CF6", "folder": "Zakhrafatan", "launch": "streamlit run main.py",
     "rating": 4.8, "users": 142, "active": True, "version": "1.0.0", "size_mb": 85,
     "download_url": "", "category": "ai-art"},
    {"id": "euqid", "name": "عقد", "desc": "إدارة وتحليل العقود الذكية",
     "color": "#F97316", "folder": "Euqid", "launch": "python main.py",
     "rating": 4.9, "users": 208, "active": True, "version": "1.0.0", "size_mb": 45,
     "download_url": "", "category": "productivity"},
    {"id": "tahlil", "name": "تحليل", "desc": "تحليل بيانات واستبيانات ذكي",
     "color": "#3B82F6", "folder": "statistics", "launch": "streamlit run app.py",
     "rating": 4.7, "users": 95, "active": True, "version": "1.0.0", "size_mb": 60,
     "download_url": "", "category": "data-analysis"},
    {"id": "mudir", "name": "مدير التواصل", "desc": "جدولة ونشر المحتوى على المنصات الاجتماعية",
     "color": "#06B6D4", "folder": "Mudir Altawasul", "launch": "python run_desktop.py",
     "rating": 4.6, "users": 73, "active": True, "version": "0.2.0-beta", "size_mb": 35,
     "download_url": "", "category": "social-media"},
    {"id": "sniper_perspective", "name": "منظور القناص", "desc": "تتبع الأهداف بـ YOLO وكاميرا الويب",
     "color": "#EF4444", "folder": "SniperPerspective_Project",
     "launch": "python SniperPerspective.py", "rating": 0, "users": 0,
     "active": False, "version": "0.2.0-beta", "size_mb": 120, "download_url": "",
     "category": "computer-vision"},
    {"id": "dental_assistant", "name": "مساعد طبيب الأسنان",
     "desc": "إدارة عيادة الأسنان والمرضى بالذكاء الاصطناعي",
     "color": "#0D9488", "folder": "Ahmed Al-Yassiri's Smart Assistant",
     "launch": "streamlit run main.py", "rating": 4.5, "users": 60,
     "active": True, "version": "1.2.0", "size_mb": 50, "download_url": "",
     "category": "medical"},
]


def _desktop() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if p.name == "AliJaddi":
            return p.parent
    home = Path.home()
    for c in [home / "OneDrive" / "Desktop", home / "Desktop", home]:
        if c.is_dir():
            return c
    return home


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
        self.setMinimumWidth(300)
        self.setMaximumWidth(520)

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        main_lay.addWidget(AccentLine(model.get("color", PRIMARY)))

        body = QVBoxLayout()
        body.setContentsMargins(16, 12, 16, 16)
        body.setSpacing(12)

        active = model.get("active", True)
        desktop = _desktop()
        exists = (desktop / model.get("folder", "")).is_dir()
        color = model.get("color", PRIMARY)
        name = model.get("name", model["id"])

        hdr = QHBoxLayout()
        hdr.setSpacing(12)
        icon_lbl = QLabel()
        letter = name[0] if name else "?"
        icon_lbl.setPixmap(create_model_icon(letter, color, 48))
        icon_lbl.setFixedSize(48, 48)
        hdr.addWidget(icon_lbl)

        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_col.addWidget(_label(name, 16, bold=True, color=theme.text))
        desc = model.get("desc", "")
        desc_lbl = _label(desc, 12, color=theme.text2)
        desc_lbl.setWordWrap(True)
        desc_lbl.setMaximumHeight(72)
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
        mid = model["id"]
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
        self.setMinimumWidth(300)
        self.setMaximumWidth(520)

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        color = model.get("color", PRIMARY)
        main_lay.addWidget(AccentLine(color))

        body = QVBoxLayout()
        body.setContentsMargins(16, 12, 16, 16)
        body.setSpacing(12)

        active = model.get("active", True)
        desktop = _desktop()
        exists = (desktop / model.get("folder", "")).is_dir()
        model_installed = exists or is_installed(model["id"])
        local_ver = installed_version(model["id"]) or model.get("version", "")
        try:
            new_ver = check_update(model["id"], registry)
        except Exception:
            new_ver = None

        name = model.get("name", model["id"])
        letter = name[0] if name else "?"

        hdr = QHBoxLayout()
        hdr.setSpacing(12)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(create_model_icon(letter, color, 48))
        icon_lbl.setFixedSize(48, 48)
        hdr.addWidget(icon_lbl)

        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_col.addWidget(_label(name, 16, bold=True, color=theme.text))
        d_lbl = _label(model.get("desc", ""), 12, color=theme.text2)
        d_lbl.setWordWrap(True)
        d_lbl.setMaximumHeight(72)
        name_col.addWidget(d_lbl)
        hdr.addLayout(name_col, 1)
        body.addLayout(hdr)

        if model_installed and exists:
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
        mid = model["id"]
        folder = model.get("folder", "")
        dl = model.get("download_url", "")
        ver = model.get("version", "")

        if model_installed and exists:
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
        self._favorites_only = False
        self._installed_only = False

        self.setWindowTitle("AliJaddi — علي جدّي")
        self.setMinimumSize(960, 680)
        self.resize(1180, 780)
        self.setLayoutDirection(i18n.layout_direction())

        icon_path = Path(__file__).resolve().parent.parent / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        self.tab_bar = QTabBar()
        self.tab_bar.setExpanding(False)
        for label in i18n.tab_labels_list():
            self.tab_bar.addTab(label)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        tab_wrap = QWidget()
        tw_lay = QHBoxLayout(tab_wrap)
        tw_lay.setContentsMargins(16, 6, 16, 0)
        tw_lay.addWidget(self.tab_bar)
        tw_lay.addStretch()
        tab_wrap.setStyleSheet(
            f"background: {theme.header}; border-bottom: 1px solid {theme.border};"
        )
        root.addWidget(tab_wrap)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        root.addWidget(self._build_footer())

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

        icon_path = Path(__file__).resolve().parent.parent / "icon.png"
        if icon_path.exists():
            logo_img = QLabel()
            pm = QPixmap(str(icon_path)).scaled(
                28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation
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
        avatar.clicked.connect(lambda: self.tab_bar.setCurrentIndex(4))
        lay.addWidget(avatar)

        return bar

    # ─── Footer ───
    def _build_footer(self):
        bar = QFrame()
        bar.setObjectName("footerBar")
        bar.setFixedHeight(40)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.addWidget(_label("© 2026 AliJaddi · بيتا 0.1 · تطبيقات ذكية", 11, color=self.theme.text2))
        lay.addStretch()
        for txt in ["حول", "الخصوصية", "تواصل"]:
            btn = QPushButton(txt)
            btn.setObjectName("outline")
            btn.setStyleSheet(
                f"color: {self.theme.text2}; font-size: 11px; "
                f"background: transparent; border: none; padding: 4px 8px;"
            )
            btn.setCursor(Qt.PointingHandCursor)
            lay.addWidget(btn)
        return bar

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

    # ─── Tab switching ───
    def _on_tab_changed(self, idx):
        self._rebuild_current_tab()

    def _rebuild_current_tab(self):
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()

        idx = self.tab_bar.currentIndex()
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
        self._full_rebuild()

    def _full_rebuild(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())

        cur = self.tab_bar.currentIndex()
        self.tab_bar = QTabBar()
        self.tab_bar.setExpanding(False)
        for label in i18n.tab_labels_list():
            self.tab_bar.addTab(label)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        tab_wrap = QWidget()
        tw_lay = QHBoxLayout(tab_wrap)
        tw_lay.setContentsMargins(16, 6, 16, 0)
        tw_lay.addWidget(self.tab_bar)
        tw_lay.addStretch()
        tab_wrap.setStyleSheet(
            f"background: {self.theme.header}; "
            f"border-bottom: 1px solid {self.theme.border};"
        )
        root.addWidget(tab_wrap)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)
        root.addWidget(self._build_footer())

        self.tab_bar.setCurrentIndex(cur)

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
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget()
        col = QVBoxLayout(content)
        col.setContentsMargins(20, 20, 24, 24)
        col.setSpacing(16)

        # Hero
        hero = CardFrame()
        h_lay = QVBoxLayout(hero)
        h_lay.setContentsMargins(18, 18, 18, 18)
        h_lay.setSpacing(10)
        h_lay.addWidget(_label("تطبيقاتك في لمحة", 22, bold=True, color=t.text))
        h_lay.addWidget(_label(
            "شغّل ما هو مثبّت، تصفّح المفضلة، أو انتقل بضغطة إلى متجر التطبيقات — "
            "تجربة قريبة من ما تعرفه على هاتفك.",
            13, color=t.text2, wrap=True,
        ))

        stats = get_all_stats()
        total = len([m for m in self.models if m.get("active", True)])
        inst_c = sum(
            1 for m in self.models
            if m.get("active", True) and (_desktop() / m.get("folder", "")).is_dir()
        )
        fav_c = len(stats.get("favorites", []))
        chips_row = QHBoxLayout()
        for lbl, val, clr in [
            ("تطبيقات متاحة", str(total), t.primary),
            ("مثبّتة لديك", str(inst_c), SUCCESS),
            ("في المفضلة", str(fav_c), DANGER),
        ]:
            chip = CardFrame()
            cl = QVBoxLayout(chip)
            cl.setAlignment(Qt.AlignCenter)
            cl.setSpacing(2)
            cl.addWidget(_label(val, 18, bold=True, color=t.text), alignment=Qt.AlignCenter)
            cl.addWidget(_label(lbl, 11, color=t.text2), alignment=Qt.AlignCenter)
            chip.setStyleSheet(
                f"QFrame#card {{ background: rgba({QColor(clr).red()},"
                f"{QColor(clr).green()},{QColor(clr).blue()},0.08); "
                f"border: 1px solid {t.border}; border-radius: 12px; }}"
            )
            chip.setMinimumHeight(60)
            chips_row.addWidget(chip)
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

        # Search + filters
        search_row = QHBoxLayout()
        self._search_field = QLineEdit()
        self._search_field.setPlaceholderText("ابحث عن تطبيق بالاسم أو الوصف…")
        self._search_field.setMinimumHeight(46)
        self._search_field.textChanged.connect(self._on_search)
        self._search_field.setText(self._search_query)
        search_row.addWidget(self._search_field, 1)

        fav_filter = QPushButton("♥ المفضلة فقط")
        fav_filter.setObjectName("outline")
        fav_filter.setCursor(Qt.PointingHandCursor)
        if self._favorites_only:
            fav_filter.setStyleSheet(
                f"background: rgba(239,68,68,0.1); color: {DANGER}; "
                f"border: 1px solid {DANGER}; border-radius: 12px; padding: 8px 14px;"
            )
        fav_filter.clicked.connect(self._toggle_fav_filter)
        search_row.addWidget(fav_filter)

        inst_filter = QPushButton("✓ المثبّتة فقط")
        inst_filter.setObjectName("outline")
        inst_filter.setCursor(Qt.PointingHandCursor)
        if self._installed_only:
            inst_filter.setStyleSheet(
                f"background: rgba(34,197,94,0.1); color: {SUCCESS}; "
                f"border: 1px solid {SUCCESS}; border-radius: 12px; padding: 8px 14px;"
            )
        inst_filter.clicked.connect(self._toggle_inst_filter)
        search_row.addWidget(inst_filter)
        col.addLayout(search_row)

        # Filter results
        query = self._search_query.strip().lower()
        filtered = []
        for m in self.models:
            if query and query not in m.get("name", "").lower() and query not in m.get("desc", "").lower():
                continue
            if self._favorites_only and not is_favorite(m["id"]):
                continue
            if self._installed_only and not (_desktop() / m.get("folder", "")).is_dir():
                continue
            filtered.append(m)

        filt_note = ""
        if query or self._favorites_only or self._installed_only:
            filt_note = " — مع تطبيق الفلاتر"
        col.addWidget(_label(f"{len(filtered)} تطبيق{filt_note}", 12, color=t.text2))

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)
        cols = 2
        for i, m in enumerate(filtered):
            card = ModelCard(m, t)
            card.launch_requested.connect(self._launch_model)
            card.like_requested.connect(self._like_model)
            card.store_requested.connect(self._open_app_store)
            grid.addWidget(card, i // cols, i % cols)

        if not filtered:
            empty = _label("لا يوجد تطبيق مطابق — جرّب تعديل البحث أو إيقاف الفلاتر.", 14, color=t.text2)
            empty.setAlignment(Qt.AlignCenter)
            grid.addWidget(empty, 0, 0, 1, cols)

        col.addLayout(grid)
        col.addStretch()
        scroll.setWidget(content)
        main_h.addWidget(scroll, 1)

        # --- sidebar ---
        sidebar = self._build_sidebar()
        main_h.addWidget(sidebar)

        return wrapper

    def _build_sidebar(self):
        t = self.theme
        sb = QWidget()
        sb.setFixedWidth(288)
        sb_lay = QVBoxLayout(sb)
        sb_lay.setContentsMargins(12, 20, 18, 20)
        sb_lay.setSpacing(14)

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
        ll.addWidget(_label("أفضل المستخدمين", 14, bold=True, color=t.text))
        medals = ["🥇", "🥈", "🥉"]
        for u in LEADERBOARD[:5]:
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
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget()
        col = QVBoxLayout(content)
        col.setContentsMargins(24, 20, 24, 24)
        col.setSpacing(16)

        try:
            registry = get_registry()
        except Exception:
            registry = {"schema_version": 2, "models": []}

        desktop = _desktop()
        total = len(self.models)
        inst_c = sum(1 for m in self.models if m.get("active", True) and (desktop / m.get("folder", "")).is_dir())
        try:
            upd_c = sum(1 for m in self.models if check_update(m["id"], registry) is not None)
        except Exception:
            upd_c = 0

        # Header
        hdr = CardFrame()
        hl = QVBoxLayout(hdr)
        hl.setContentsMargins(18, 18, 18, 18)
        hl.setSpacing(8)
        hl.addWidget(_label("متجر التطبيقات", 22, bold=True, color=t.text))
        hl.addWidget(_label(
            "تصفّح، ثبّت، حدّث أو أزل التطبيقات — كما في متاجر الأنظمة الشهيرة.",
            13, color=t.text2, wrap=True,
        ))

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

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)
        cols = 2
        for i, m in enumerate(self.models):
            card = AddonCard(m, t, registry)
            card.install_requested.connect(self._do_install)
            card.uninstall_requested.connect(self._do_uninstall)
            card.update_requested.connect(self._do_install)
            grid.addWidget(card, i // cols, i % cols)

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
        content = QWidget()
        col = QVBoxLayout(content)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(10)
        col.addWidget(_label("المتصدرون", 22, bold=True, color=t.text))
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
        content = QWidget()
        col = QVBoxLayout(content)
        col.setContentsMargins(0, 20, 0, 20)
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
            if not m.get("active", True):
                continue
            ms = all_stats.get("models", {}).get(m["id"], {})
            launches = ms.get("launches", 0)
            last = ms.get("last_used", "—")
            if last and last != "—":
                last = last[:10]
            row = QHBoxLayout()
            icon_lbl = QLabel()
            icon_lbl.setPixmap(create_model_icon(
                m.get("name", "?")[0], m.get("color", PRIMARY), 32
            ))
            icon_lbl.setFixedSize(32, 32)
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
    def _on_search(self, text):
        self._search_query = text
        self._rebuild_current_tab()

    def _toggle_fav_filter(self):
        self._favorites_only = not self._favorites_only
        self._rebuild_current_tab()

    def _toggle_inst_filter(self):
        self._installed_only = not self._installed_only
        self._rebuild_current_tab()

    def _open_app_store(self, _model_id: str = ""):
        """ينتقل إلى تبويب متجر التطبيقات (مثل «احصل» في المتاجر الشهيرة)."""
        self.tab_bar.setCurrentIndex(1)

    def _launch_model(self, model_id):
        from ui.toast import show_toast
        model = next((m for m in self.models if m["id"] == model_id), None)
        if not model or not model.get("active", True):
            return
        desktop = _desktop()
        folder = desktop / model.get("folder", "")
        if not folder.is_dir():
            show_toast(
                self,
                f"التطبيق غير مثبّت على الجهاز. افتح «متجر التطبيقات» للتنزيل.",
                "warning",
            )
            return
        try:
            env = os.environ.copy()
            sess = load_session() or {}
            tok = (sess.get("access_token") or "").strip()
            if tok:
                env["ALIJADDI_JWT"] = tok
            subprocess.Popen(
                model.get("launch", ""), cwd=str(folder), shell=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                env=env,
            )
            record_launch(model_id)
            show_toast(self, f"✓ جارٍ فتح {model.get('name', model_id)}", "success")
        except Exception as e:
            show_toast(self, str(e), "error")

    def _like_model(self, model_id):
        toggle_favorite(model_id)
        self._rebuild_current_tab()

    def _do_install(self, mid, url, folder, ver):
        from ui.download_dialog import DownloadDialog
        from ui.toast import show_toast

        model = next((m for m in self.models if m["id"] == mid), {})
        name = model.get("name", mid)
        color = model.get("color", PRIMARY)

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
                QTimer.singleShot(500, lambda: show_toast(self, f"✓ تم تثبيت التطبيق «{name}»", "success"))
                QTimer.singleShot(1000, self._rebuild_current_tab)
            else:
                QTimer.singleShot(500, lambda: show_toast(self, f"تعذّر تنزيل «{name}»: {msg}", "error"))

        install_model(mid, url, folder, ver, on_progress=_progress, on_done=_done, on_detail=_detail)

    def _do_uninstall(self, mid, folder):
        from ui.toast import show_toast
        reply = QMessageBox.question(
            self, "إزالة التطبيق",
            f"سيتم حذف التطبيق من جهازك (المجلد: {folder}).\n"
            "يمكنك تنزيله مجدداً من متجر التطبيقات في أي وقت.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            ok, msg = uninstall_model(mid, folder)
            show_toast(self, msg, "success" if ok else "error")
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
