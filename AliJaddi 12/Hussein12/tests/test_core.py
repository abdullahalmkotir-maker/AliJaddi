"""اختبارات أساسية لـ v0.1."""

from __future__ import annotations

import pickle
import tempfile
from pathlib import Path

import pytest

import hussein12
from hussein12 import بدء_المنصة
from hussein12.ai import نموذج_ذكي
from hussein12.plugins import إضافة, نظام_الإضافات
from hussein12.store import تطبيق, متجر, مستخدم
from hussein12.utils import معالجة_البيانات


class _DummyPredictor:
    def predict(self, x):
        return x * 2


def _هوية(z):
    return z


def test_مرحبا() -> None:
    assert "Hussein12" in hussein12.مرحباً()


def test_مستخدم_تسجيل() -> None:
    م = مستخدم.تسجيل("أحمد", "ahmed@example.com")
    assert م.الاسم == "أحمد"


def test_متجر() -> None:
    م = متجر(اسم="متجر")
    م.رفع(تطبيق(الاسم="x", السعر=1))
    assert len(م.التطبيقات) == 1


def test_نموذج_ذكي_pickle() -> None:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "m.pkl"
        with p.open("wb") as f:
            pickle.dump(_DummyPredictor(), f)
        ن = نموذج_ذكي.تحميل(p)
        assert ن.تنبؤ(3) == 6


def test_خطافات() -> None:
    نظام = نظام_الإضافات(اسم_المنصة="t")
    نظام.تسجيل_خطاف("hook", lambda x: x + 1)
    assert نظام.تنفيذ_الخطاف("hook", 1) == [2]
    نظام.تثبيت(إضافة(المصدر="https://example.com"))


def test_معالجة_البيانات() -> None:
    assert معالجة_البيانات.تنظيف({"a": 1, "b": None}) == {"a": 1}


def test_بدء_المنصة() -> None:
    م = متجر(اسم="m")
    ب = بدء_المنصة(النماذج=[], المتجر=م)
    ح = ب.تشغيل(ملخص_فقط=True)
    assert ح["عدد_النماذج"] == 0
    assert ح["المتجر"] == "m"


def test_خدمة_النموذج_نشر_بدون_bentoml() -> None:
    from hussein12.ai import خدمة_النموذج

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "m.pkl"
        with p.open("wb") as f:
            pickle.dump(_هوية, f)
        ن = نموذج_ذكي.تحميل(p)
    with pytest.raises(ImportError):
        خدمة_النموذج.نشر(ن, اسم_الخدمة="x")
