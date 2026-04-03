"""
AliJaddi — تطبيق متعدد المنصات (Windows / Android / iOS)
• تسجيل الدخول اختياري (من الملف الشخصي)
• يعمل بدون إنترنت
• تخزين محلي + كاش + حفظ جلسة تلقائي
"""
from __future__ import annotations
from pathlib import Path

from dotenv import load_dotenv

# تحميل SUPABASE_* وغيرها من ملف .env بجانب هذا الملف (قبل استيراد AuthService)
load_dotenv(Path(__file__).resolve().parent / ".env")

import flet as ft

from views.home_view import HomeView
from services.auth_service import AuthService
from services.local_store import load_settings
from theme import apply_theme


class AliJaddiApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.auth = AuthService()
        self._setup()
        self._show_home()

    def _setup(self):
        settings = load_settings()
        dark = settings.get("theme", "dark") == "dark"
        apply_theme(self.page, dark=dark)
        self.page.title = "AliJaddi — علي جدّي"
        self.page.window.min_width = 360
        self.page.window.min_height = 640
        self.page.window.width = 1100
        self.page.window.height = 750
        self.page.padding = 0

    def _show_home(self):
        self.page.views.clear()
        self.page.views.append(
            HomeView(self.page, self.auth, on_rebuild=self._show_home)
        )
        self.page.update()


def main(page: ft.Page):
    AliJaddiApp(page)


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")

# flet build entry point
app = main
