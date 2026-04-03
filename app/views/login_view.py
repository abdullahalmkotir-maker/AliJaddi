"""شاشة تسجيل الدخول — تُعرض من الملف الشخصي (اختياري، ليس إجبارياً)."""
from __future__ import annotations
from typing import Callable
import flet as ft
import theme as T


class LoginSheet(ft.BottomSheet):
    """نافذة تسجيل دخول / تسجيل — تُفتح من الملف الشخصي."""

    def __init__(self, page: ft.Page, auth, on_done: Callable):
        self.pg = page
        self.auth = auth
        self.on_done = on_done
        self._signup = False

        self.email = ft.TextField(
            label="البريد الإلكتروني",
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
            keyboard_type=ft.KeyboardType.EMAIL,
            text_align=ft.TextAlign.RIGHT,
            border_radius=14,
            border_color=T.border(page),
            focused_border_color=T.primary(page),
            filled=True,
            fill_color=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            text_size=15, height=56,
        )
        self.password = ft.TextField(
            label="كلمة المرور",
            prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
            password=True, can_reveal_password=True,
            text_align=ft.TextAlign.RIGHT,
            border_radius=14,
            border_color=T.border(page),
            focused_border_color=T.primary(page),
            filled=True,
            fill_color=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            text_size=15, height=56,
        )
        self.msg = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)
        self.spinner = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2.5, color=T.primary(page))

        self.action_text = ft.Text("تسجيل الدخول", color="#FFF", size=15, weight=ft.FontWeight.W_600)
        self.action_icon = ft.Icon(ft.Icons.LOGIN_ROUNDED, color="#FFF", size=20)

        action_btn = ft.Container(
            content=ft.Row([self.action_icon, self.action_text], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor=T.primary(page), border_radius=14, height=52,
            alignment=ft.Alignment(0, 0), on_click=self._submit, ink=True,
        )

        self.toggle_text = ft.TextButton(
            "ليس لديك حساب؟ سجّل الآن",
            on_click=self._toggle,
            style=ft.ButtonStyle(color=T.ACCENT_CYAN, text_style=ft.TextStyle(size=13)),
        )

        super().__init__(
            content=ft.Container(
                content=ft.Column([
                    ft.Container(width=40, height=4, bgcolor=T.border(page), border_radius=2,
                                 alignment=ft.Alignment(0, 0)),
                    ft.Text("تسجيل الدخول", size=20, weight=ft.FontWeight.BOLD, color=T.tx(page),
                             text_align=ft.TextAlign.CENTER),
                    ft.Text("سجّل للمزامنة مع السحابة والحصول على النجوم",
                             size=12, color=T.tx2(page), text_align=ft.TextAlign.CENTER),
                    ft.Container(height=8),
                    self.email, self.password,
                    self.msg,
                    ft.Row([self.spinner], alignment=ft.MainAxisAlignment.CENTER),
                    action_btn,
                    ft.Row([self.toggle_text], alignment=ft.MainAxisAlignment.CENTER),
                ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(28),
            )
        )

    def _toggle(self, _):
        self._signup = not self._signup
        self.action_text.value = "إنشاء حساب" if self._signup else "تسجيل الدخول"
        self.action_icon.name = ft.Icons.PERSON_ADD_ROUNDED if self._signup else ft.Icons.LOGIN_ROUNDED
        self.toggle_text.text = "لديك حساب؟ سجّل الدخول" if self._signup else "ليس لديك حساب؟ سجّل الآن"
        self.msg.value = ""
        self.pg.update()

    def _submit(self, _):
        em = (self.email.value or "").strip()
        pw = (self.password.value or "").strip()
        if not em or not pw:
            self.msg.value = "أدخل البريد وكلمة المرور"
            self.msg.color = T.DANGER
            self.pg.update()
            return

        self.spinner.visible = True
        self.msg.value = ""
        self.pg.update()

        ok, txt = self.auth.sign_up(em, pw) if self._signup else self.auth.sign_in(em, pw)
        self.spinner.visible = False
        if ok:
            self.msg.value = txt
            self.msg.color = T.SUCCESS
            self.pg.update()
            self.pg.pop_dialog()
            self.on_done()
        else:
            self.msg.value = txt
            self.msg.color = T.DANGER
            self.pg.update()
