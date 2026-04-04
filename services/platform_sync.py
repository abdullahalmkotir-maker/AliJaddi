# -*- coding: utf-8 -*-
"""
تزامن/تحقق موحّد لطبقات المنصّة: manifest السرب، وصف المساعدين، ومنطق التوجيه.

يُستدعى من الاختبارات أو سكربتات CI؛ لا يعتمد على شبكة.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from alijaddi.config import PLATFORM_ROOT

from services.assistants_squad import pick_assistant_id_for_context as squad_pick
from services.assistants_squad import squad_assistants_meta


def _manifest_path() -> Path:
    return PLATFORM_ROOT / "12" / "manifest.json"


def full_platform_sync() -> dict[str, Any]:
    """
    يتحقق من:
    - تطابق معرفات ``manifest.json`` مع ``squad_assistants_meta()``.
    - اتساق نتيجة التوجيه بين ``assistants_squad`` و ``bento_serving.routing`` لعيّنة نصوص.
    """
    out: dict[str, Any] = {
        "ok": True,
        "manifest_path": str(_manifest_path()),
        "errors": [],
        "manifest_assistant_ids": [],
        "squad_ids": [],
    }
    errs: list[str] = out["errors"]
    mp = _manifest_path()
    if not mp.is_file():
        errs.append(f"manifest_missing:{mp}")
        out["ok"] = False
        return out

    try:
        raw = json.loads(mp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errs.append(f"manifest_read_error:{e}")
        out["ok"] = False
        return out

    assistants = raw.get("assistants")
    if not isinstance(assistants, list):
        errs.append("manifest_assistants_not_list")
        out["ok"] = False
        return out

    manifest_ids: list[str] = []
    for a in assistants:
        if isinstance(a, dict) and a.get("id"):
            manifest_ids.append(str(a["id"]))
    out["manifest_assistant_ids"] = manifest_ids

    meta = squad_assistants_meta()
    squad_ids = [str(m.get("id", "")) for m in meta if m.get("id")]
    out["squad_ids"] = squad_ids

    if set(manifest_ids) != set(squad_ids):
        errs.append(
            f"id_mismatch manifest={sorted(set(manifest_ids))} squad={sorted(set(squad_ids))}"
        )
        out["ok"] = False

    # توجيه Bento يجب أن يطابق السرب (نفس العتبات والمعرفات)
    try:
        from bento_serving.routing import pick_assistant_id_for_context as bento_pick
    except ImportError as e:
        errs.append(f"bento_routing_import:{e}")
        out["ok"] = False
        return out

    samples = [
        "",
        "تثبيت zip inno متجر",
        "kafka rabbitmq بوابة api خدمات",
        "bentoml jsonl تدريب human_resolution",
        "asyncio pipeline training",
        "mixed kafka bentoml zip",
    ]
    for t in samples:
        a = squad_pick(t)
        b = bento_pick(t)
        if a != b:
            errs.append(f"routing_divergence text={t!r} squad={a} bento={b}")
            out["ok"] = False

    return out
