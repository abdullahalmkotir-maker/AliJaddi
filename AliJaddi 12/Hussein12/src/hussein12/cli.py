"""أدوات سطر أوامر Hussein12."""

from __future__ import annotations

import textwrap
from pathlib import Path

import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """مكتبة Hussein12 — أوامر عربية."""
    pass


@main.command("بدء_مشروع")
@click.argument("اسم_المشروع")
def بدء_مشروع(اسم_المشروع: str) -> None:
    """ينشئ مجلداً بملف main.py أولي."""
    الجذر = Path(اسم_المشروع).resolve()
    if الجذر.exists() and any(الجذر.iterdir()):
        raise click.ClickException(f"المجلد غير فارغ أو موجود: {الجذر}")
    الجذر.mkdir(parents=True, exist_ok=True)
    (الجذر / "main.py").write_text(
        textwrap.dedent(
            '''
            """مشروع منشأ بـ hussein12 بدء_مشروع."""

            import hussein12
            from hussein12 import بدء_المنصة
            from hussein12.ai import نموذج_ذكي
            from hussein12.store import متجر, تطبيق

            def الرئيسية() -> None:
                print(hussein12.مرحباً())
                متجر_المنصة = متجر(اسم="متجري")
                متجر_المنصة.أضف_تطبيق(تطبيق(الاسم="تطبيق_تجريبي", السعر=0))
                # مثال نموذج: ضع ملف model.pkl ثم فعّل السطر التالي
                # نموذج = نموذج_ذكي.تحميل("model.pkl")
                نماذج = []  # type: list[نموذج_ذكي]
                المنصة = بدء_المنصة(النماذج=نماذج, المتجر=متجر_المنصة)
                # يشغّل FastAPI — الوثائق: http://127.0.0.1:8000/docs
                المنصة.تشغيل(المضيف="0.0.0.0", المنفذ=8000)

            if __name__ == "__main__":
                الرئيسية()
            '''
        ).lstrip(),
        encoding="utf-8",
    )
    click.echo(f"تم إنشاء المشروع في: {الجذر}")


if __name__ == "__main__":
    main()
