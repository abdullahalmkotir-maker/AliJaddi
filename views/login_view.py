"""شاشة تسجيل الدخول — تُعرض من الملف الشخصي (اختياري، ليس إجبارياً)."""
from __future__ import annotations
from typing import Callable
import flet as ft
import theme as T


def _field_fill(page: ft.Page) -> str:
    # اجعل خلفية الحقول متلائمة مع الفاتح والداكن بدون إبهار بصري مزعج
    return ft.Colors.with_opacity(0.06, ft.Colors.WHITE) if T.is_dark(page) else ft.Colors.with_opacity(0.04, ft.Colors.BLACK)


class LoginSheet(ft.BottomSheet):
    """نافذة تسجيل دخول / تسجيل — تُفتح من الملف الشخصي."""

    def __init__(self, page: ft.Page, auth, on_done: Callable):
        self.pg = page
        self.auth = auth
        self.on_done = on_done
        self._signup = False

        fill = _field_fill(page)

        self.email = ft.TextField(
            label="البريد الإلكتروني",
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
            keyboard_type=ft.KeyboardType.EMAIL,
            text_align=ft.TextAlign.RIGHT,
            border_radius=14,
            border_color=T.border(page),
            focused_border_color=T.primary(page),
            filled=True,
            fill_color=fill,
            text_size=15,
            height=56,
            width=float("inf"),
            on_change=lambda _: self._clear_msg(),
        )
        self.password = ft.TextField(
            label="كلمة المرور",
            prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
            password=True,
            can_reveal_password=True,
            text_align=ft.TextAlign.RIGHT,
            border_radius=14,
            border_color=T.border(page),
            focused_border_color=T.primary(page),
            filled=True,
            fill_color=fill,
            text_size=15,
            height=56,
            width=float("inf"),
            on_change=lambda _: self._clear_msg(),
            on_submit=lambda _: self._submit(None),
        )
        self.confirm_password = ft.TextField(
            label="تأكيد كلمة المرور",
            prefix_icon=ft.Icons.LOCK_RESET_ROUNDED,
            password=True,
            can_reveal_password=True,
            text_align=ft.TextAlign.RIGHT,
            border_radius=14,
            border_color=T.border(page),
            focused_border_color=T.primary(page),
            filled=True,
            fill_color=fill,
            text_size=15,
            height=56,
            width=float("inf"),
            visible=False,
            on_change=lambda _: self._clear_msg(),
            on_submit=lambda _: self._submit(None),
        )

        self.hint = ft.Text(
            "",
            size=11,
            color=T.tx2(page),
            text_align=ft.TextAlign.CENTER,
            visible=False,
        )
        self.msg = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)
        self.spinner = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2.5, color=T.primary(page))

        self.title = ft.Text("تسجيل الدخول", size=20, weight=ft.FontWeight.BOLD, color=T.tx(page), text_align=ft.TextAlign.CENTER)
        self.subtitle = ft.Text(
            "سجّل الدخول بشكل اختياري لمزامنة النجوم والحد الأدنى من البيانات على السحابة.",
            size=12,
            color=T.tx2(page),
            text_align=ft.TextAlign.CENTER,
        )

        self.action_text = ft.Text("تسجيل الدخول", color="#FFF", size=15, weight=ft.FontWeight.W_600)
        self.action_icon = ft.Icon(ft.Icons.LOGIN_ROUNDED, color="#FFF", size=20)

        action_btn = ft.Container(
            content=ft.Row([self.action_icon, self.action_text], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor=T.primary(page),
            border_radius=14,
            height=52,
            width=float("inf"),
            alignment=ft.Alignment(0, 0),
            on_click=self._submit,
            ink=True,
        )

        self.toggle_text = ft.TextButton(
            "ليس لديك حساب؟ سجّل الآن",
            on_click=self._toggle,
            style=ft.ButtonStyle(color=T.ACCENT_CYAN, text_style=ft.TextStyle(size=13)),
        )

        super().__init__(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(width=40, height=4, bgcolor=T.border(page), border_radius=2, alignment=ft.Alignment(0, 0)),
                        ft.Row(
                            [
                                ft.Container(expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE_ROUNDED,
                                    icon_color=T.tx2(page),
                                    tooltip="إغلاق",
                                    on_click=lambda _: self._close(),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        self.title,
                        self.subtitle,
                        ft.Container(height=6),
                        self.email,
                        self.password,
                        self.confirm_password,
                        self.hint,
                        self.msg,
                        ft.Row([self.spinner], alignment=ft.MainAxisAlignment.CENTER),
                        action_btn,
                        ft.Row([self.toggle_text], alignment=ft.MainAxisAlignment.CENTER),
                    ],
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.all(22),
                width=float("inf"),
            )
        )

    def _close(self):
        try:
            self.open = False
            self.pg.update()
        except Exception:
            try:
                self.pg.pop_dialog()
            except Exception:
                pass

    def _clear_msg(self):
        self.msg.value = ""
        self.pg.update()

    def _busy(self, on: bool):
        self.spinner.visible = bool(on)

    def _set_mode_ui(self):
        if self._signup:
            self.title.value = "إنشاء حساب"
            self.subtitle.value = "أنشئ حساباً، ثم يمكنك مزامنة نجومك واستخدام التطبيق بدون إنترنت أيضاً."
            self.action_text.value = "إنشاء الحساب"
            self.action_icon.name = ft.Icons.PERSON_ADD_ROUNDED
            self.toggle_text.text = "لديك حساب؟ سجّل الدخول"
            self.confirm_password.visible = True
            self.hint.visible = True
            self.hint.value = "نصيحة: استخدم 8 أحرف على الأقل مع مزيج من الأرقام والرموز في كلمة المرور."
            self.password.hint_text = "8+ أحرف موصى بها"
        else:
            self.title.value = "تسجيل الدخول"
            self.subtitle.value = "سجّل الدخول بشكل اختياري لمزامنة النجوم والحد الأدنى من البيانات على السحابة."
            self.action_text.value = "تسجيل الدخول"
            self.action_icon.name = ft.Icons.LOGIN_ROUNDED
            self.toggle_text.text = "ليس لديك حساب؟ سجّل الآن"
            self.confirm_password.visible = False
            self.confirm_password.value = ""
            self.hint.visible = False
            self.password.hint_text = None

    def _toggle(self, _):
        self._signup = not self._signup
        self._set_mode_ui()
        self.msg.value = ""
        self.pg.update()

    @staticmethod
    def _basic_email_ok(email: str) -> bool:
        e = email.lower()
        return ("@" in e) and ("." in e.split("@")[-1]) and (len(e) >= 6)

    @staticmethod
    def _password_ok_for_signup(password: str) -> tuple[bool, str]:
        if len(password) < 8:
            return False, "كلمة المرور قصيرة جداً (الحد الأدنى 8 أحرف)."
        if password.isdigit() or password.isalpha():
            return False, "أضف مزيجاً من الأحرف والأرقام لتكون أقوى."
        return True, ""

    def _submit(self, _):
        em = (self.email.value or "").strip()
        pw = (self.password.value or "").strip()

        if not em or not pw:
            self.msg.value = "أدخل البريد وكلمة المرور"
            self.msg.color = T.DANGER
            self.pg.update()
            return

        if not self._basic_email_ok(em):
            self.msg.value = "صيغة البريد غير واضحة — تأكد من وجود @ والنطاق"
            self.msg.color = T.DANGER
            self.pg.update()
            return

        if self._signup:
            pw2 = (self.confirm_password.value or "").strip()
            if not pw2:
                self.msg.value = "أكد كلمة المرور"
                self.msg.color = T.DANGER
                self.pg.update()
                return
            if pw != pw2:
                self.msg.value = "كلمتا المرور غير متطابقتين"
                self.msg.color = T.DANGER
                self.pg.update()
                return
            ok_pw, pw_msg = self._password_ok_for_signup(pw)
            if not ok_pw:
                self.msg.value = pw_msg
                self.msg.color = T.DANGER
                self.pg.update()
                return

        self._busy(True)
        self.msg.value = ""
        self.pg.update()

        ok, txt = self.auth.sign_up(em, pw) if self._signup else self.auth.sign_in(em, pw)
        self._busy(False)
        if ok:
            self._close()
            self.on_done()
            return

        self.msg.value = txt
        self.msg.color = T.DANGER
        self.pg.update()
