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


def list_store_app_folders(*, max_items: int = 200, include_legacy: bool = True) -> list[dict[str, str]]:
    """
    قائمة مجلدات التطبيقات: مدير التنزيلات ``.alijaddi/downloads`` + اختيارياً **حاضنة قديمة**
    ``سطح المكتب/تطبيقات علي جدي`` (انظر ``services.legacy_data``).
    """
    from pathlib import Path

    from services.legacy_data import SOURCE_STORE_DOWNLOADS, iter_legacy_install_entries

    root = apps_downloads_root()
    seen: set[str] = set()
    out: list[dict[str, str]] = []

    def add_row(name: str, path: Path, source: str) -> None:
        key = str(path.resolve())
        if key in seen:
            return
        seen.add(key)
        row = {"name": name, "path": key, "source": source}
        out.append(row)

    if root.is_dir():
        try:
            for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
                if p.is_dir():
                    add_row(p.name, p, SOURCE_STORE_DOWNLOADS)
                if len(out) >= max_items:
                    return out
        except OSError:
            pass

    if include_legacy and len(out) < max_items:
        for row in iter_legacy_install_entries():
            if len(out) >= max_items:
                break
            add_row(row["name"], Path(row["path"]), row.get("source", ""))

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
            "لمدير الملفات: التثبيت الحالي تحت `.alijaddi/downloads`؛ تثبيتات **قديمة** قد تظهر "
            "تحت `تطبيقات علي جدي` على سطح المكتب — `list_store_app_folders(include_legacy=True)` "
            "يجمع المصدرين؛ راجع `services/legacy_data.py`."
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
