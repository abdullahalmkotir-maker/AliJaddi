"""تسجيل الدخول بالمعرف — إنشاء حساب (اسم، ميلاد، جنس، بريد تأكيد فقط) — PySide6."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QWidget, QScrollArea,
    QDateEdit, QComboBox,
)
from PySide6.QtCore import Qt, Signal, QTimer, QDate
from PySide6.QtGui import QFont, QGuiApplication

from services.local_store import get_setting
from ui.theme_qt import PRIMARY, DANGER, SUCCESS, ACCENT_CYAN
from ui import i18n

_LOGIN = 0
_SIGNUP = 1
_CONFIRM_OTP = 2


def _auth_err_msg(code: str) -> str:
    key_map = {
        "USERNAME_TAKEN": "username_taken",
        "MISSING_KEY": "missing_key",
        "NETWORK_ERROR": "network_error",
        "OTP_INVALID": "otp_invalid",
        "EMAIL_NOT_CONFIRMED": "email_not_confirmed",
        "TOO_SHORT": "err_username_short",
        "TOO_LONG": "err_username_chars",
        "BAD_NAME": "err_name",
        "BAD_CONTACT_EMAIL": "err_contact_email",
        "WEAK_PASSWORD": "err_pw_short",
        "NO_PENDING": "err_generic",
        "NO_SMTP": "err_generic",
    }
    k = key_map.get(code, "")
    if k:
        return i18n.tr(k)
    if code and not code.isascii():
        return code
    return i18n.tr("err_generic")


class LoginDialog(QDialog):
    login_done = Signal()

    def __init__(self, theme, auth, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.auth = auth
        self._state = _LOGIN
        self._pending_contact_email = ""
        self._locale = get_setting("language", "ar") or "ar"

        self.setWindowTitle("AliJaddi")
        scr = QGuiApplication.primaryScreen()
        if scr:
            aw = scr.availableGeometry().width()
            self.setMinimumWidth(max(280, min(440, aw - 32)))
            self.setMaximumWidth(min(540, aw - 16))
        else:
            self.setMinimumWidth(440)
            self.setMaximumWidth(520)
        self._apply_direction()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.root = QVBoxLayout(self)
        self.root.setSpacing(0)
        self.root.setContentsMargins(0, 0, 0, 0)
        self._build()

    def _apply_direction(self):
        self.setLayoutDirection(i18n.layout_direction())
        if i18n.is_rtl():
            self.setLocale(i18n.qlocale())

    def _build(self):
        while self.root.count():
            item = self.root.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        t = self.theme
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setSpacing(14)
        lay.setContentsMargins(24, 20, 24, 20)

        brand = QFrame()
        brand.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #6D28D9, stop:1 #4F46E5); border-radius: 14px;"
        )
        bl = QVBoxLayout(brand)
        bl.setAlignment(Qt.AlignCenter)
        bl.setContentsMargins(20, 20, 20, 20)
        bl.setSpacing(4)
        n = QLabel("AliJaddi")
        n.setFont(QFont("Segoe UI", 22, QFont.Bold))
        n.setStyleSheet("color:#FFF;background:transparent;")
        n.setAlignment(Qt.AlignCenter)
        bl.addWidget(n)
        s = QLabel(i18n.tr("app_tagline"))
        s.setStyleSheet("color:rgba(255,255,255,0.85);font-size:12px;background:transparent;")
        s.setAlignment(Qt.AlignCenter)
        s.setWordWrap(True)
        bl.addWidget(s)
        lay.addWidget(brand)

        if self._state in (_LOGIN, _SIGNUP):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setFrameShape(QFrame.NoFrame)
            inner = QWidget()
            inner_lay = QVBoxLayout(inner)
            inner_lay.setContentsMargins(0, 0, 4, 0)
            inner_lay.setSpacing(12)
            self._build_auth(inner_lay, t)
            scroll.setWidget(inner)
            lay.addWidget(scroll, 1)
        elif self._state == _CONFIRM_OTP:
            self._build_otp(lay, t)

        self.root.addWidget(container)

    def _build_auth(self, lay, t):
        signup = self._state == _SIGNUP

        title = QLabel(i18n.tr("signup") if signup else i18n.tr("login"))
        title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        sub = QLabel(i18n.tr("signup_sub") if signup else i18n.tr("login_sub"))
        sub.setStyleSheet(f"color:{t.text2};font-size:12px;")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        lay.addWidget(sub)

        self.user_in = QLineEdit()
        self.user_in.setPlaceholderText(i18n.tr("username_hint"))
        self.user_in.setMinimumHeight(44)
        lay.addWidget(self.user_in)

        if signup:
            self.name_in = QLineEdit()
            self.name_in.setPlaceholderText(i18n.tr("full_name"))
            self.name_in.setMinimumHeight(44)
            lay.addWidget(self.name_in)

            dob_row = QHBoxLayout()
            dob_lbl = QLabel(i18n.tr("birth_date"))
            dob_lbl.setStyleSheet(f"color:{t.text2};min-width:100px;")
            self.dob_in = QDateEdit()
            self.dob_in.setCalendarPopup(True)
            self.dob_in.setDisplayFormat("yyyy-MM-dd")
            self.dob_in.setMaximumDate(QDate.currentDate())
            self.dob_in.setDate(QDate.currentDate().addYears(-18))
            self.dob_in.setMinimumHeight(44)
            dob_row.addWidget(dob_lbl)
            dob_row.addWidget(self.dob_in, 1)
            lay.addLayout(dob_row)

            gen_row = QHBoxLayout()
            gen_lbl = QLabel(i18n.tr("gender"))
            gen_lbl.setStyleSheet(f"color:{t.text2};min-width:100px;")
            self.gender_in = QComboBox()
            self.gender_in.setMinimumHeight(44)
            self.gender_in.addItem(i18n.tr("gender_male"), "male")
            self.gender_in.addItem(i18n.tr("gender_female"), "female")
            gen_row.addWidget(gen_lbl)
            gen_row.addWidget(self.gender_in, 1)
            lay.addLayout(gen_row)

            self.contact_in = QLineEdit()
            self.contact_in.setPlaceholderText(i18n.tr("contact_email"))
            self.contact_in.setMinimumHeight(44)
            lay.addWidget(self.contact_in)
            hint = QLabel(i18n.tr("contact_email_hint"))
            hint.setStyleSheet(f"color:{ACCENT_CYAN};font-size:11px;")
            hint.setWordWrap(True)
            lay.addWidget(hint)

        self.pw_in = QLineEdit()
        self.pw_in.setPlaceholderText(i18n.tr("password"))
        self.pw_in.setEchoMode(QLineEdit.Password)
        self.pw_in.setMinimumHeight(44)
        self.pw_in.returnPressed.connect(self._submit)
        lay.addWidget(self.pw_in)

        if signup:
            self.pw2_in = QLineEdit()
            self.pw2_in.setPlaceholderText(i18n.tr("confirm_password"))
            self.pw2_in.setEchoMode(QLineEdit.Password)
            self.pw2_in.setMinimumHeight(44)
            self.pw2_in.returnPressed.connect(self._submit)
            lay.addWidget(self.pw2_in)

        self.msg_lbl = QLabel("")
        self.msg_lbl.setAlignment(Qt.AlignCenter)
        self.msg_lbl.setWordWrap(True)
        self.msg_lbl.setVisible(False)
        lay.addWidget(self.msg_lbl)

        self.action_btn = QPushButton(i18n.tr("signup") if signup else i18n.tr("login"))
        self.action_btn.setObjectName("primary")
        self.action_btn.setMinimumHeight(46)
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.clicked.connect(self._submit)
        lay.addWidget(self.action_btn)

        dr = QHBoxLayout()
        for i in range(2):
            ln = QFrame()
            ln.setFrameShape(QFrame.HLine)
            ln.setStyleSheet(f"color:{t.border};")
            dr.addWidget(ln)
            if i == 0:
                ol = QLabel(i18n.tr("or"))
                ol.setStyleSheet(f"color:{t.text2};font-size:11px;padding:0 8px;")
                dr.addWidget(ol)
        lay.addLayout(dr)

        tog = QPushButton(i18n.tr("have_account") if signup else i18n.tr("no_account"))
        tog.setObjectName("outline")
        tog.setCursor(Qt.PointingHandCursor)
        tog.setMinimumHeight(40)
        tog.clicked.connect(self._toggle)
        lay.addWidget(tog)

        skip = QPushButton(i18n.tr("guest"))
        skip.setStyleSheet(f"color:{t.text2};background:transparent;border:none;font-size:12px;padding:8px;")
        skip.setCursor(Qt.PointingHandCursor)
        skip.clicked.connect(self.reject)
        lay.addWidget(skip, alignment=Qt.AlignCenter)

    def _build_otp(self, lay, t):
        ico = QLabel("📧")
        ico.setFont(QFont("Segoe UI", 36))
        ico.setAlignment(Qt.AlignCenter)
        lay.addWidget(ico)

        lay.addWidget(self._cl("confirm_account", 17, True, t.text))
        lay.addWidget(self._cl(
            i18n.tr("otp_sent", email=self._pending_contact_email),
            13, False, t.text2, True,
        ))

        self.otp_in = QLineEdit()
        self.otp_in.setPlaceholderText(i18n.tr("enter_code"))
        self.otp_in.setMinimumHeight(50)
        self.otp_in.setMaxLength(6)
        self.otp_in.setAlignment(Qt.AlignCenter)
        self.otp_in.setFont(QFont("Consolas", 20, QFont.Bold))
        self.otp_in.setStyleSheet(
            f"letter-spacing:8px;border:2px solid {t.border};border-radius:12px;padding:8px;font-size:22px;"
        )
        self.otp_in.returnPressed.connect(self._verify_otp)
        lay.addWidget(self.otp_in)

        self.msg_lbl = QLabel("")
        self.msg_lbl.setAlignment(Qt.AlignCenter)
        self.msg_lbl.setWordWrap(True)
        self.msg_lbl.setVisible(False)
        lay.addWidget(self.msg_lbl)

        self.verify_btn = QPushButton(i18n.tr("verify"))
        self.verify_btn.setObjectName("primary")
        self.verify_btn.setMinimumHeight(46)
        self.verify_btn.setCursor(Qt.PointingHandCursor)
        self.verify_btn.clicked.connect(self._verify_otp)
        lay.addWidget(self.verify_btn)

        rr = QHBoxLayout()
        rr.addWidget(QLabel(i18n.tr("no_message")))
        rb = QPushButton(i18n.tr("resend"))
        rb.setStyleSheet(
            f"color:{ACCENT_CYAN};background:transparent;border:none;font-size:12px;font-weight:600;"
        )
        rb.setCursor(Qt.PointingHandCursor)
        rb.clicked.connect(self._resend)
        rr.addWidget(rb)
        rr.addStretch()
        lay.addLayout(rr)

        tip = QLabel(i18n.tr("check_spam"))
        tip.setStyleSheet(f"color:{t.text2};font-size:11px;")
        tip.setWordWrap(True)
        lay.addWidget(tip)

        bk = QPushButton(i18n.tr("back_login"))
        bk.setStyleSheet(f"color:{t.text2};background:transparent;border:none;font-size:12px;")
        bk.setCursor(Qt.PointingHandCursor)
        bk.clicked.connect(self._back)
        lay.addWidget(bk, alignment=Qt.AlignCenter)

    @staticmethod
    def _cl(text, size, bold, color, wrap=False):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", size, QFont.Bold if bold else QFont.Normal))
        lbl.setStyleSheet(f"color:{color};")
        lbl.setAlignment(Qt.AlignCenter)
        if wrap:
            lbl.setWordWrap(True)
        return lbl

    def _show_msg(self, text, is_error=True):
        self.msg_lbl.setText(text)
        self.msg_lbl.setStyleSheet(f"color:{DANGER if is_error else SUCCESS};font-size:13px;")
        self.msg_lbl.setVisible(True)

    def _toggle(self):
        self._state = _SIGNUP if self._state == _LOGIN else _LOGIN
        self._build()

    def _back(self):
        self._state = _LOGIN
        self._build()

    def _submit(self):
        un = self.user_in.text().strip()
        pw = self.pw_in.text().strip()

        if not un or not pw:
            self._show_msg(i18n.tr("err_user_pass"))
            return

        signup = self._state == _SIGNUP
        if signup:
            fn = self.name_in.text().strip()
            if len(fn) < 2:
                self._show_msg(i18n.tr("err_name"))
                return
            ce = self.contact_in.text().strip().lower()
            if "@" not in ce or "." not in ce.split("@")[-1]:
                self._show_msg(i18n.tr("err_contact_email"))
                return
            pw2 = self.pw2_in.text().strip()
            if not pw2:
                self._show_msg(i18n.tr("err_confirm_pw"))
                return
            if pw != pw2:
                self._show_msg(i18n.tr("err_pw_mismatch"))
                return
            if len(pw) < 8:
                self._show_msg(i18n.tr("err_pw_short"))
                return
            dob = self.dob_in.date().toString("yyyy-MM-dd")
            gender = self.gender_in.currentData()

        self.action_btn.setEnabled(False)
        self.action_btn.setText(i18n.tr("processing"))

        if signup:
            ok, result = self.auth.sign_up_with_profile(
                un, pw, fn, dob, gender, ce, self._locale,
            )
        else:
            ok, result = self.auth.sign_in_with_username(un, pw)

        self.action_btn.setEnabled(True)
        self.action_btn.setText(i18n.tr("signup") if signup else i18n.tr("login"))

        if ok and result == "CONFIRM_OTP":
            self._pending_contact_email = self.contact_in.text().strip().lower()
            self._state = _CONFIRM_OTP
            self._build()
        elif ok:
            self.login_done.emit()
            self.accept()
        elif result == "EMAIL_NOT_CONFIRMED":
            self._show_msg(i18n.tr("email_not_confirmed"))
        else:
            self._show_msg(_auth_err_msg(result))

    def _verify_otp(self):
        code = self.otp_in.text().strip()
        if len(code) < 6:
            self._show_msg(i18n.tr("err_otp_short"))
            return

        self.verify_btn.setEnabled(False)
        self.verify_btn.setText(i18n.tr("processing"))
        ok, result = self.auth.verify_registration_otp(self._pending_contact_email, code)
        self.verify_btn.setEnabled(True)
        self.verify_btn.setText(i18n.tr("verify"))

        if ok:
            self._show_msg(i18n.tr("confirm_success"), is_error=False)
            QTimer.singleShot(800, self._finish_ok)
        else:
            self._show_msg(_auth_err_msg(result))

    def _finish_ok(self):
        if self.auth.is_logged_in:
            self.login_done.emit()
            self.accept()

    def _resend(self):
        ok, msg = self.auth.resend_registration_otp(self._pending_contact_email, self._locale)
        if ok:
            self._show_msg(i18n.tr("otp_resent"), is_error=False)
        else:
            self._show_msg(_auth_err_msg(msg) if isinstance(msg, str) and msg.isupper() else i18n.tr("err_generic"))
