# -*- coding: utf-8 -*-
"""دمج مقتطفات المعرفة مع عينات JSONL (اصطناعية أو خارجية) في ملف تدريب موحّد."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def _snippet_to_record(idx: int, item: dict[str, str]) -> dict[str, Any]:
    role = item.get("role", "سياسة")
    content = (item.get("content") or "").strip()
    user = f"اشرح إرشاد {role} في سياق إدارة الملفات والأمان."
    return {
        "id": f"kb_{idx}",
        "domain": "security_kb",
        "locale": "ar",
        "source": "merged_security_kb",
        "messages": [
            {"role": "user", "content": user},
            {"role": "assistant", "content": content},
        ],
        "instruction": user,
        "output": content,
    }


def _iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def merge_to_jsonl(
    policy_dir: Path,
    out_path: Path,
    synthetic_paths: list[Path] | None = None,
) -> tuple[int, int]:
    """
    يكتب ملف JSONL واحد: مقتطفات مدمجة من السياسة/المستكشف + كل سطور JSONL الإضافية.
    يُرجع (عدد_مقتطفات_المعرفة، عدد_سطور_من_الملفات).
    """
    from hassan12.security_kb import merged_training_snippets

    policy_dir = Path(policy_dir)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    snippets = merged_training_snippets(policy_dir)
    kb_records = [_snippet_to_record(i, s) for i, s in enumerate(snippets)]

    extra = 0
    extra_rows: list[dict[str, Any]] = []
    for p in synthetic_paths or []:
        p = Path(p)
        if not p.is_file():
            continue
        for row in _iter_jsonl(p):
            extra_rows.append(row)
            extra += 1

    n_kb = 0
    with out_path.open("w", encoding="utf-8") as f:
        for rec in kb_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_kb += 1
        for row in extra_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return n_kb, extra
