# -*- coding: utf-8 -*-
"""مستشار آلي: قواعد محلية + اختياري مفتاح API لنموذج خارجي."""

from __future__ import annotations

import os
import urllib.error
import urllib.request
from typing import Any

from hassan12.security_kb import PROMPTS_AR, RULES_AR, advice_for_operation, training_snippets


def local_advise(user_text: str) -> str:
    t = user_text.strip().lower()
    lines: list[str] = []
    if "حذف" in user_text or "delete" in t:
        lines.append(RULES_AR["delete"])
    if "نقل" in user_text or "move" in t:
        lines.append(RULES_AR["move"])
    if "إرسال" in user_text or "ارسال" in user_text or "send" in t:
        lines.append(RULES_AR["send"])
    if "مزامن" in user_text or "sync" in t:
        lines.append(RULES_AR["sync"])
    if not lines:
        lines.extend(PROMPTS_AR[:3])
    lines.append("\n— مقتطفات تدريب مكتبة سد الثغرات —")
    for s in training_snippets()[:2]:
        lines.append(f"• {s['content']}")
    return "\n".join(lines)


def maybe_openai_compatible(user_message: str) -> str | None:
    base = os.environ.get("HASSAN12_AI_BASE", "").strip().rstrip("/")
    key = os.environ.get("HASSAN12_AI_KEY", "").strip()
    model = os.environ.get("HASSAN12_AI_MODEL", "gpt-4o-mini")
    if not base or not key:
        return None
    url = base + "/v1/chat/completions"
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "أنت مستشار أمن بيانات وإدارة ملفات لبرنامج «مدير الملفات Hassan12». "
                    "أجب بالعربية بإيجاز. لا تقترح تجاوز موافقة المستخدم أو إرسال بيانات دون موافقة."
                ),
            },
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
    }
    import json

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
        choices = payload.get("choices") or []
        if not choices:
            return None
        msg = choices[0].get("message") or {}
        content = msg.get("content")
        return str(content).strip() if content else None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
        return None


def advise(user_text: str, prefer_network: bool = False) -> str:
    if prefer_network:
        remote = maybe_openai_compatible(user_text)
        if remote:
            return remote
    local = local_advise(user_text)
    if prefer_network:
        return local + "\n\n(لم يتصل بخادم الذكاء الاصطناعي؛ عرض الإرشادات المحلية.)"
    return local


def advise_operation(op: str, path: str = "") -> str:
    return advice_for_operation(op, path)
