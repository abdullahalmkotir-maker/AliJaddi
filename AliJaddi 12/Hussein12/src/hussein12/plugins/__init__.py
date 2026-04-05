"""نظام إضافات بخطافات بسيطة (v0.1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class إضافة:
    المصدر: str


خطاف = Callable[..., Any]


@dataclass
class نظام_الإضافات:
    اسم_المنصة: str
    _خطافات: dict[str, list[خطاف]] = field(default_factory=dict)

    def تثبيت(self, إضافة_جديدة: إضافة) -> None:
        """placeholder — في المستقبل: تحميل من المصدر."""
        _ = إضافة_جديدة

    def تسجيل_خطاف(self, الاسم: str, دالة: خطاف) -> None:
        self._خطافات.setdefault(الاسم, []).append(دالة)

    def تنفيذ_الخطاف(self, الاسم: str, *args: Any, **kwargs: Any) -> list[Any]:
        نتائج = []
        for دالة in self._خطافات.get(الاسم, []):
            نتائج.append(دالة(*args, **kwargs))
        return نتائج
