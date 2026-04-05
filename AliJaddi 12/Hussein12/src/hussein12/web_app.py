"""تطبيق FastAPI للمنصة — وثائق OpenAPI مع عناوين ووسوم عربية."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from hussein12.ai.model import نموذج_ذكي
from hussein12.platform import بدء_المنصة
from hussein12.store import تطبيق, متجر


class جسم_تنبؤ(BaseModel):
    البيانات: Any = Field(description="مدخلات النموذج (أي JSON صالح)")


def انشاء_تطبيق_ويب(منصة: بدء_المنصة) -> FastAPI:
    اسم_المتجر = منصة.المتجر.اسم if منصة.المتجر else None

    app = FastAPI(
        title="منصة Hussein12",
        description=(
            "واجهة HTTP موحّدة للنماذج الذكية وكتالوج المتجر. "
            "استخدم `/docs` أو `/redoc` لاستكشاف المسارات."
        ),
        version="0.1.0",
        openapi_tags=[
            {"name": "عام", "description": "صحة الخدمة ومعلومات المنصة"},
            {"name": "المتجر", "description": "عرض التطبيقات المدرجة في المتجر"},
            {"name": "النماذج", "description": "تشغيل تنبؤ النماذج المحمّلة في الذاكرة"},
        ],
    )

    @app.get("/صحة", tags=["عام"], summary="فحص الصحة")
    def صحة() -> dict[str, str]:
        return {"الحالة": "يعمل", "المتجر": اسم_المتجر or ""}

    @app.get(
        "/api/متجر/تطبيقات",
        tags=["المتجر"],
        summary="قائمة تطبيقات المتجر",
    )
    def تطبيقات_المتجر() -> dict[str, Any]:
        if منصة.المتجر is None:
            return {"اسم_المتجر": None, "التطبيقات": []}
        م: متجر = منصة.المتجر
        return {
            "اسم_المتجر": م.اسم,
            "التطبيقات": [_تطبيق_كامل(ط) for ط in م.التطبيقات],
        }

    @app.post(
        "/api/نماذج/{model_index}/تنبؤ",
        tags=["النماذج"],
        summary="تنبؤ بنموذج حسب الترتيب في قائمة المنصة",
    )
    def تنبؤ_نموذج(model_index: int, جسم: جسم_تنبؤ) -> dict[str, Any]:
        if model_index < 0 or model_index >= len(منصة.النماذج):
            raise HTTPException(status_code=404, detail="لم يُعثر على النموذج بهذا الرقم")
        ن: نموذج_ذكي = منصة.النماذج[model_index]
        try:
            نتيجة = ن.تنبؤ(جسم.البيانات)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return {"النتيجة": نتيجة, "رقم_النموذج": model_index}

    return app


def _تطبيق_كامل(ط: تطبيق) -> dict[str, Any]:
    return {
        "الاسم": ط.الاسم,
        "الإصدار": ط.الإصدار,
        "السعر": ط.السعر,
    }
