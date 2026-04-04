# -*- coding: utf-8 -*-
"""
Hassan12 — هندسة الخدمات و**مدير مسارات/ملفات** تطبيقات المتجر داخل مجلد ``12``.

- كثافة كلمات مفتاحية (خدمات مصغّرة، بوابات، وكذلك مجلدات/مسارات/تنزيلات).
- استعراض آمن لمجلدات التطبيقات تحت ``~/.alijaddi/downloads`` (مدير التنزيلات).
- صفوف تدريب موحّدة مع ``assistant_id=Hassan12``.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Final, Optional

HASSAN12_ASSISTANT_ID: Final = "Hassan12"
HASSAN12_ENGINE_VERSION: Final = "v1_files_services"
HASSAN12_DISPLAY_AR: Final = "حسن 12"

# مجال Hassan12: بنية + ملفات/مسارات (مدير الملفات على مستوى المنصّة)
HASSAN_KEYWORDS: Final[frozenset[str]] = frozenset(
    {
        "microservice",
        "microservices",
        "grpc",
        "gateway",
        "gin",
        "fastapi",
        "rest",
        "api",
        "go",
        "golang",
        "service",
        "services",
        "هيكلة",
        "خدمات",
        "مصغرة",
        "بوابة",
        "فصل",
        "معماري",
        "معمارية",
        "kafka",
        "rabbitmq",
        "spark",
        "authorization",
        "authentication",
        "scheduler",
        "distributed",
        "message",
        "queue",
        "folder",
        "directory",
        "file",
        "path",
        "explorer",
        "downloads",
        "filesystem",
        "مجلد",
        "ملف",
        "ملفات",
        "مسار",
        "مستكشف",
        "تنزيلات",
        "مدير",
    }
)


def _token_set(text: str) -> set[str]:
    if not text:
        return set()
    return set(re.findall(r"[\w\u0600-\u06FF]+", text.lower()))


def hassan_keyword_density(blob: str) -> float:
    words = _token_set(blob)
    if not words:
        return 0.0
    inter = words & HASSAN_KEYWORDS
    if not inter:
        return 0.0
    return len(inter) / len(words)


def apps_downloads_root() -> Path:
    """جذر مدير تنزيلات المتجر (نفس ``services.paths.apps_root``)."""
    from services.paths import apps_root

    return apps_root()


def list_store_app_folders(*, max_items: int = 200) -> list[dict[str, str]]:
    """
    قائمة مجلدات التطبيقات المثبّتة تحت مدير التنزيلات — للواجهات والتدريب (أسماء فقط، بدون حذف).
    """
    root = apps_downloads_root()
    if not root.is_dir():
        return []
    out: list[dict[str, str]] = []
    try:
        for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
            if p.is_dir():
                out.append({"name": p.name, "path": str(p.resolve())})
            if len(out) >= max_items:
                break
    except OSError:
        return out
    return out


def safe_folder_segment(name: str) -> str:
    """تصفية اسم مجلد لاستخدامه كجزء من مسار نسبي آمن."""
    s = (name or "").strip()
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", s)
    return s[:120] if s else "app"


def hassan12_domain_hint_ar(text: str) -> str:
    """إرشاد عربي لمجال Hassan12 (بوابات + هيكلة + ملفات التنزيلات)."""
    tl = (text or "").strip().lower()
    if "kafka" in tl or "rabbitmq" in tl or "grpc" in tl or "gateway" in tl:
        return (
            "للبنية: ضع الخدمات خلف بوابة API؛ استخدم gRPC أو REST للداخل؛ "
            "Kafka/RabbitMQ للفك غير المتزامن بين خدمات Go/Java وبايثون."
        )
    if any(k in tl for k in ("folder", "path", "file", "explorer", "download", "مجلد", "ملف", "مسار")):
        return (
            "لمدير الملفات على المنصّة: تطبيقات المتجر تحت مجلد المستخدم "
            "`.alijaddi/downloads` (أو ALIJADDI_APPS_ROOT). افتح المجلد من «تطبيقاتي» "
            "أو استخدم list_store_app_folders() للقائمة؛ التثبيت/التحديث عبر Ali12."
        )
    return (
        "للهندسة: اربط خدمات مصغّرة بعقود واضحة؛ اجعل الاستدلال خلف واجهة شبكة مستقلة عن عميل Qt."
    )


def hassan12_training_payload(
    *,
    event_kind: str,
    model_id: str,
    user_message_snippet: str,
    hint_ar: str,
    resolution_label: str = "",
    signals: Optional[dict[str, Any]] = None,
    rule_id: str = "",
    confidence: Optional[float] = None,
) -> dict[str, Any]:
    from Ali12 import training_payload_stub

    return training_payload_stub(
        event_kind=event_kind,
        model_id=model_id,
        user_message_snippet=user_message_snippet,
        ali12_hint_ar=hint_ar,
        resolution_label=resolution_label,
        ali12_signals=signals,
        ali12_rule_id=rule_id,
        ali12_confidence=confidence,
        assistant_id=HASSAN12_ASSISTANT_ID,
    )


def hassan12_meta() -> dict[str, str]:
    return {
        "id": HASSAN12_ASSISTANT_ID,
        "role_ar": "هندسة الخدمات، بوابات، ومدير مسارات/مجلدات تطبيقات المتجر",
        "focus": "FastAPI, gRPC, Kafka, store downloads layout, safe paths",
        "engine": HASSAN12_ENGINE_VERSION,
        "bundle_dir": "12",
    }
