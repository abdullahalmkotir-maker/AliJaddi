"""تجميع مكوّنات المنصة وتشغيلها عبر FastAPI/uvicorn."""

from __future__ import annotations

from typing import Any

from hussein12.ai.model import نموذج_ذكي
from hussein12.store import متجر


class بدء_المنصة:
    """
    يجمع النماذج والمتجر ليبني كائن تشغيل موحّد.
    `تشغيل()` يشغّل خادم uvicorn افتراضياً؛ استخدم `ملخص_فقط=True` للاختبار دون حظر.
    """

    def __init__(
        self,
        *,
        النماذج: list[نموذج_ذكي] | None = None,
        المتجر: متجر | None = None,
    ) -> None:
        self.النماذج = list(النماذج or [])
        self.المتجر = المتجر

    def تشغيل(
        self,
        *,
        المضيف: str = "127.0.0.1",
        المنفذ: int = 8000,
        ملخص_فقط: bool = False,
    ) -> dict[str, Any] | None:
        """
        يشغّل خادم الويب على العنوان والمنفذ المحددين.
        إذا `ملخص_فقط=True` يعيد ملخصاً دون تشغيل الخادم (مناسب للاختبارات).
        """
        ملخص = {
            "المضيف": المضيف,
            "المنفذ": المنفذ,
            "عدد_النماذج": len(self.النماذج),
            "المتجر": self.المتجر.اسم if self.المتجر else None,
            "الرسالة": "خادم FastAPI — وثائق على /docs و /redoc",
        }
        if ملخص_فقط:
            return ملخص

        import uvicorn

        from hussein12.web_app import انشاء_تطبيق_ويب

        تطبيق_فاست = انشاء_تطبيق_ويب(self)
        uvicorn.run(تطبيق_فاست, host=المضيف, port=المنفذ, log_level="info")
        return None
