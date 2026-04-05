"""اختبارات واجهة FastAPI."""

from __future__ import annotations

import pickle
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from hussein12 import انشاء_تطبيق_ويب
from hussein12.ai import نموذج_ذكي
from hussein12.platform import بدء_المنصة
from hussein12.store import تطبيق, متجر


class _M:
    def predict(self, x):
        return x + 1


def test_صحة_ومتجر_ونموذج() -> None:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "m.pkl"
        with p.open("wb") as f:
            pickle.dump(_M(), f)
        ن = نموذج_ذكي.تحميل(p)
    متجر_ = متجر(اسم="متجري")
    متجر_.أضف_تطبيق(تطبيق(الاسم="تطبيق1", السعر=5.0))
    منصة = بدء_المنصة(النماذج=[ن], المتجر=متجر_)
    app = انشاء_تطبيق_ويب(منصة)
    عميل = TestClient(app)

    ح = عميل.get("/صحة")
    assert ح.status_code == 200
    assert ح.json()["الحالة"] == "يعمل"

    ت = عميل.get("/api/متجر/تطبيقات")
    assert ت.status_code == 200
    ج = ت.json()
    assert ج["اسم_المتجر"] == "متجري"
    assert len(ج["التطبيقات"]) == 1
    assert ج["التطبيقات"][0]["الاسم"] == "تطبيق1"

    نت = عميل.post("/api/نماذج/0/تنبؤ", json={"البيانات": 10})
    assert نت.status_code == 200
    assert نت.json()["النتيجة"] == 11


def test_متجر_فارغ() -> None:
    منصة = بدء_المنصة(النماذج=[], المتجر=None)
    عميل = TestClient(انشاء_تطبيق_ويب(منصة))
    ت = عميل.get("/api/متجر/تطبيقات")
    assert ت.json()["التطبيقات"] == []


def test_نموذج_غير_موجود() -> None:
    منصة = بدء_المنصة(النماذج=[], المتجر=None)
    عميل = TestClient(انشاء_تطبيق_ويب(منصة))
    نت = عميل.post("/api/نماذج/0/تنبؤ", json={"البيانات": 1})
    assert نت.status_code == 404
