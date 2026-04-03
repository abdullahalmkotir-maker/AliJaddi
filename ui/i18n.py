"""
ترجمة الواجهة — عربي، إنجليزي، كردي (سوراني)، فارسي.
"""
from __future__ import annotations

from PySide6.QtCore import QLocale, Qt
from PySide6.QtWidgets import QApplication

from services.local_store import get_setting, set_setting

# اللغات: ckb = کوردی (سورانی)
LANG_CODES = ("ar", "en", "ckb", "fa")
LANG_LABELS = {
    "ar": "العربية",
    "en": "English",
    "ckb": "کوردی",
    "fa": "فارسی",
}
RTL_LANGS = frozenset({"ar", "fa", "ckb"})

# مفاتيح مشتركة — القيمة الافتراضية العربية تُنسخ للغات الأخرى عند الحاجة
S: dict[str, dict[str, str]] = {
    "ar": {
        "app_tagline": "علي جدّي — منصة الذكاء الاصطناعي",
        "login": "تسجيل الدخول",
        "signup": "إنشاء حساب",
        "username": "المعرف",
        "username_hint": "حروف إنجليزية وأرقام و _ (٣–٢٤)",
        "full_name": "الاسم الكامل",
        "birth_date": "تاريخ الميلاد",
        "gender": "الجنس",
        "gender_male": "ذكر",
        "gender_female": "أنثى",
        "contact_email": "البريد لتأكيد الحساب",
        "contact_email_hint": "يُرسل إليه رمز التأكيد فقط — لا يُستخدم لتسجيل الدخول",
        "password": "كلمة المرور",
        "confirm_password": "تأكيد كلمة المرور",
        "login_sub": "أدخل المعرف وكلمة المرور.",
        "signup_sub": "أكمل بياناتك. التأكيد يصل إلى بريدك.",
        "processing": "جارٍ المعالجة…",
        "have_account": "لديك حساب؟ سجّل الدخول",
        "no_account": "ليس لديك حساب؟ أنشئ حساباً",
        "guest": "المتابعة كزائر",
        "or": "أو",
        "confirm_account": "تأكيد الحساب",
        "otp_sent": "أرسلنا رمزاً مكوّناً من ٦ أرقام إلى:\n{email}\nافتح بريدك وأدخل الرمز أدناه.",
        "enter_code": "أدخل الرمز",
        "verify": "تأكيد",
        "resend": "إعادة الإرسال",
        "no_message": "لم تصلك الرسالة؟",
        "back_login": "العودة لتسجيل الدخول",
        "check_spam": "تحقق أيضاً من مجلد الرسائل غير المرغوبة",
        "check_email_title": "تحقق من بريدك",
        "check_email_body": "أرسلنا رابطاً إلى:\n{email}\nبعد الضغط على الرابط اضغط «تم التأكيد».",
        "confirmed_try_login": "تم التأكيد — سجّل الدخول",
        "lang": "اللغة",
        "logout": "تسجيل الخروج",
        "profile_id": "المعرف",
        "tab_home": "تطبيقاتي",
        "tab_store": "متجر التطبيقات",
        "tab_rank": "المتصدرون",
        "tab_invite": "دعوة أصدقاء",
        "tab_profile": "حسابي",
        "header_sub": "تطبيقات ذكية في مكان واحد",
        "err_user_pass": "أدخل المعرف وكلمة المرور",
        "err_username_short": "المعرف قصير جداً (٣ أحرف على الأقل)",
        "err_username_chars": "المعرف: حروف إنجليزية وأرقام و _ فقط",
        "err_name": "أدخل الاسم الكامل",
        "err_contact_email": "أدخل بريداً صحيحاً لتأكيد الحساب",
        "err_confirm_pw": "أكد كلمة المرور",
        "err_pw_mismatch": "كلمتا المرور غير متطابقتين",
        "err_pw_short": "كلمة المرور قصيرة (٨ أحرف على الأقل)",
        "err_otp_short": "أدخل الرمز الستّي",
        "err_generic": "حدث خطأ — حاول مرة أخرى",
        "username_taken": "هذا المعرف مستخدم مسبقاً — اختر معرفاً آخر",
        "network_error": "لا يوجد اتصال — جرّب لاحقاً",
        "missing_key": "مفتاح الخادم غير مضبوط في الإعدادات",
        "login_success": "تم تسجيل الدخول",
        "signup_success": "تم إنشاء الحساب",
        "confirm_success": "تم تأكيد الحساب وتسجيل الدخول",
        "otp_resent": "أُعيد إرسال رمز التأكيد",
        "otp_invalid": "الرمز غير صحيح",
        "email_not_confirmed": "الحساب غير مؤكد — تحقق من بريدك",
    },
    "en": {
        "app_tagline": "AliJaddi — AI app hub",
        "login": "Log in",
        "signup": "Create account",
        "username": "Username",
        "username_hint": "Letters, numbers, _ (3–24)",
        "full_name": "Full name",
        "birth_date": "Date of birth",
        "gender": "Gender",
        "gender_male": "Male",
        "gender_female": "Female",
        "contact_email": "Email for verification",
        "contact_email_hint": "We send your confirmation code here only — not used to log in",
        "password": "Password",
        "confirm_password": "Confirm password",
        "login_sub": "Enter your username and password.",
        "signup_sub": "Fill in your profile. Confirmation is sent to your email.",
        "processing": "Processing…",
        "have_account": "Have an account? Log in",
        "no_account": "No account? Sign up",
        "guest": "Continue as guest",
        "or": "or",
        "confirm_account": "Confirm account",
        "otp_sent": "We sent a 6-digit code to:\n{email}\nCheck your inbox and enter it below.",
        "enter_code": "Enter code",
        "verify": "Verify",
        "resend": "Resend",
        "no_message": "Didn’t get it?",
        "back_login": "Back to log in",
        "check_spam": "Check your spam folder too",
        "check_email_title": "Check your email",
        "check_email_body": "We sent a link to:\n{email}\nAfter opening the link, tap “I confirmed”.",
        "confirmed_try_login": "Confirmed — log me in",
        "lang": "Language",
        "logout": "Log out",
        "profile_id": "Username",
        "tab_home": "My apps",
        "tab_store": "App Store",
        "tab_rank": "Leaderboard",
        "tab_invite": "Invite friends",
        "tab_profile": "Account",
        "header_sub": "Smart apps in one place",
        "err_user_pass": "Enter username and password",
        "err_username_short": "Username too short (min 3 characters)",
        "err_username_chars": "Username: letters, numbers, and _ only",
        "err_name": "Enter your full name",
        "err_contact_email": "Enter a valid email for verification",
        "err_confirm_pw": "Confirm your password",
        "err_pw_mismatch": "Passwords do not match",
        "err_pw_short": "Password too short (min 8 characters)",
        "err_otp_short": "Enter the 6-digit code",
        "err_generic": "Something went wrong — try again",
        "username_taken": "This username is taken — choose another",
        "network_error": "No connection — try again later",
        "missing_key": "Server key is not configured",
        "login_success": "Signed in successfully",
        "signup_success": "Account created",
        "confirm_success": "Verified and signed in",
        "otp_resent": "Verification code resent",
        "otp_invalid": "Invalid code",
        "email_not_confirmed": "Account not verified — check your email",
    },
    "fa": {
        "app_tagline": "علی جدی — مرکز برنامه‌های هوش مصنوعی",
        "login": "ورود",
        "signup": "ثبت‌نام",
        "username": "نام کاربری",
        "username_hint": "حروف انگلیسی، عدد و _ (۳–۲۴)",
        "full_name": "نام و نام خانوادگی",
        "birth_date": "تاریخ تولد",
        "gender": "جنسیت",
        "gender_male": "مرد",
        "gender_female": "زن",
        "contact_email": "ایمیل برای تأیید حساب",
        "contact_email_hint": "فقط برای ارسال کد تأیید — برای ورود استفاده نمی‌شود",
        "password": "رمز عبور",
        "confirm_password": "تکرار رمز عبور",
        "login_sub": "نام کاربری و رمز عبور را وارد کنید.",
        "signup_sub": "اطلاعات را تکمیل کنید. تأیید به ایمیل شما ارسال می‌شود.",
        "processing": "در حال پردازش…",
        "have_account": "حساب دارید؟ ورود",
        "no_account": "حساب ندارید؟ ثبت‌نام",
        "guest": "ادامه به‌عنوان مهمان",
        "or": "یا",
        "confirm_account": "تأیید حساب",
        "otp_sent": "کد ۶ رقمی به این آدرس ارسال شد:\n{email}\nکد را در زیر وارد کنید.",
        "enter_code": "کد را وارد کنید",
        "verify": "تأیید",
        "resend": "ارسال مجدد",
        "no_message": "پیام را نگرفتید؟",
        "back_login": "بازگشت به ورود",
        "check_spam": "پوشه هرزنامه را هم بررسی کنید",
        "check_email_title": "ایمیل خود را بررسی کنید",
        "check_email_body": "لینک به این آدرس ارسال شد:\n{email}\nپس از باز کردن لینک، «تأیید کردم» را بزنید.",
        "confirmed_try_login": "تأیید شد — وارد شوم",
        "lang": "زبان",
        "logout": "خروج",
        "profile_id": "نام کاربری",
        "tab_home": "برنامه‌های من",
        "tab_store": "فروشگاه برنامه",
        "tab_rank": "برترین‌ها",
        "tab_invite": "دعوت دوستان",
        "tab_profile": "حساب من",
        "header_sub": "همه برنامه‌های هوشمند در یکجا",
        "err_user_pass": "نام کاربری و رمز را وارد کنید",
        "err_username_short": "نام کاربری خیلی کوتاه است",
        "err_username_chars": "فقط حروف انگلیسی، عدد و _",
        "err_name": "نام کامل را وارد کنید",
        "err_contact_email": "ایمیل معتبر برای تأیید وارد کنید",
        "err_confirm_pw": "رمز را تکرار کنید",
        "err_pw_mismatch": "رمزها یکسان نیستند",
        "err_pw_short": "رمز کوتاه است (حداقل ۸)",
        "err_otp_short": "کد ۶ رقمی را وارد کنید",
        "err_generic": "خطایی رخ داد — دوباره تلاش کنید",
        "username_taken": "این نام کاربری گرفته شده است",
        "network_error": "اتصال برقرار نیست",
        "missing_key": "کلید سرور تنظیم نشده",
        "login_success": "با موفقیت وارد شدید",
        "signup_success": "حساب ایجاد شد",
        "confirm_success": "تأیید و ورود انجام شد",
        "otp_resent": "کد دوباره ارسال شد",
        "otp_invalid": "کد نادرست است",
        "email_not_confirmed": "حساب تأیید نشده",
    },
    "ckb": {
        "app_tagline": "عەلی جەدی — سەنتەری بەرنامەکانی زیرەکی دەستکرد",
        "login": "چوونەژوورەوە",
        "signup": "دروستکردنی هەژمار",
        "username": "ناسنامە",
        "username_hint": "پیت و ژمارە و _ (٣–٢٤)",
        "full_name": "ناوی تەواو",
        "birth_date": "ڕۆژی لەدایکبوون",
        "gender": "ڕەگەز",
        "gender_male": "نێر",
        "gender_female": "مێ",
        "contact_email": "ئیمەیڵ بۆ پشتڕاستکردنەوە",
        "contact_email_hint": "تەنها کۆدی پشتڕاستکردنەوە دەنێردرێت — بۆ چوونەژوورەوە بەکارناهێنرێت",
        "password": "وشەی نهێنی",
        "confirm_password": "دووبارەکردنەوەی وشەی نهێنی",
        "login_sub": "ناسنامە و وشەی نهێنی بنووسە.",
        "signup_sub": "زانیارییەکانت پڕبکەرەوە. پشتڕاستکردنەوە بۆ ئیمەیڵت دەنێردرێت.",
        "processing": "چاوەڕوانبە…",
        "have_account": "هەژمارت هەیە؟ بچۆ ژوورەوە",
        "no_account": "هەژمارت نییە؟ تۆماربە",
        "guest": "وەک میوان بەردەوامبە",
        "or": "یان",
        "confirm_account": "پشتڕاستکردنەوەی هەژمار",
        "otp_sent": "کۆدی ٦ ژمارەمان نارد بۆ:\n{email}\nکۆدەکە لێرە بنووسە.",
        "enter_code": "کۆد بنووسە",
        "verify": "پشتڕاستکردنەوە",
        "resend": "دووبارە بنێرە",
        "no_message": "نامەت نەگەیشت؟",
        "back_login": "گەڕانەوە بۆ چوونەژوورەوە",
        "check_spam": "بوخچەی سپام بپشکنە",
        "check_email_title": "ئیمەیڵەکەت بپشکنە",
        "check_email_body": "لینکێکمان نارد بۆ:\n{email}\nدوای کردنەوەی لینکەکە «پشتڕامکردەوە» دابگرە.",
        "confirmed_try_login": "پشتڕامکرد — بچمە ژوورەوە",
        "lang": "زمان",
        "logout": "دەرچوون",
        "profile_id": "ناسنامە",
        "tab_home": "بەرنامەکانم",
        "tab_store": "فرۆشگای بەرنامە",
        "tab_rank": "سەرەکییەکان",
        "tab_invite": "بانگهێشتکردن",
        "tab_profile": "هەژمار",
        "header_sub": "بەرنامە زیرەکان لە یەک شوێن",
        "err_user_pass": "ناسنامە و وشەی نهێنی بنووسە",
        "err_username_short": "ناسنامە کورتە",
        "err_username_chars": "تەنها پیت و ژمارە و _",
        "err_name": "ناوی تەواو بنووسە",
        "err_contact_email": "ئیمەیڵێکی دروست بنووسە",
        "err_confirm_pw": "وشەی نهێنی دووبارە بکەرەوە",
        "err_pw_mismatch": "وشەکان یەکناگرنەوە",
        "err_pw_short": "وشەی نهێنی کورتە (٨)",
        "err_otp_short": "کۆدی ٦ ژمارە بنووسە",
        "err_generic": "هەڵەیەک ڕوویدا",
        "username_taken": "ئەم ناسنامەیە بەکارهاتووە",
        "network_error": "پەیوەندی نییە",
        "missing_key": "کلیلی سێرڤەر دانەنراوە",
        "login_success": "بە سەرکەوتوویی چوویتە ژوورەوە",
        "signup_success": "هەژمار دروستکرا",
        "confirm_success": "پشتڕامکرا و چوویتە ژوورەوە",
        "otp_resent": "کۆد دووبارە نێردرا",
        "otp_invalid": "کۆد هەڵەیە",
        "email_not_confirmed": "هەژمار پشتڕانەکراوە",
    },
}


def current_lang() -> str:
    code = (get_setting("language", "ar") or "ar").lower()
    return code if code in LANG_CODES else "ar"


def set_language(code: str):
    if code in LANG_CODES:
        set_setting("language", code)


def tr(key: str, **kwargs) -> str:
    lang = current_lang()
    s = S.get(lang, S["ar"]).get(key)
    if s is None:
        s = S["ar"].get(key, key)
    return s.format(**kwargs) if kwargs else s


def is_rtl() -> bool:
    return current_lang() in RTL_LANGS


def layout_direction() -> Qt.LayoutDirection:
    return Qt.RightToLeft if is_rtl() else Qt.LeftToRight


def qlocale() -> QLocale:
    lang = current_lang()
    if lang == "en":
        return QLocale(QLocale.Language.English)
    if lang == "fa":
        return QLocale(QLocale.Language.Persian, QLocale.Country.Iran)
    if lang == "ckb":
        kur = getattr(QLocale.Language, "Kurdish", None)
        if kur is not None:
            return QLocale(kur, QLocale.Country.Iraq)
    return QLocale(QLocale.Language.Arabic, QLocale.Country.SaudiArabia)


def apply_to_app(app: QApplication | None):
    """اتجاه الواجهة + لغة النظام للأرقام والتواريخ."""
    if app is None:
        return
    QLocale.setDefault(qlocale())
    app.setLayoutDirection(layout_direction())


def tab_labels_list() -> list[str]:
    return [
        tr("tab_home"),
        tr("tab_store"),
        tr("tab_rank"),
        tr("tab_invite"),
        tr("tab_profile"),
    ]
