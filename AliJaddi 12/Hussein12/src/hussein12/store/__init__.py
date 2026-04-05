"""متجر التطبيقات وإدارة التطبيقات والمستخدمين (هيكل v0.1)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class تطبيق:
    الاسم: str
    الإصدار: str = "1.0"
    السعر: float = 0.0


@dataclass
class مستخدم:
    الاسم: str
    البريد: str

    @classmethod
    def تسجيل(cls, الاسم: str, البريد: str) -> "مستخدم":
        return cls(الاسم=الاسم, البريد=البريد)


@dataclass
class متجر:
    """المتجر يأخذ `اسم` كما في أمثلة الوثائق."""

    اسم: str
    التطبيقات: list[تطبيق] = field(default_factory=list)

    def رفع(self, تطبيق_جديد: تطبيق) -> None:
        self.التطبيقات.append(تطبيق_جديد)

    def أضف_تطبيق(self, تطبيق_جديد: تطبيق) -> None:
        """مرادف لـ `رفع` يطابق مثال الوثائق."""
        self.رفع(تطبيق_جديد)
