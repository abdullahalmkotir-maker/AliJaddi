# -*- coding: utf-8 -*-
"""تصدير: JSON للتدريب وحزم أرشيف للسياسات والسجلات."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path


def write_training_json(policy_dir: Path, dest_file: Path) -> None:
    """مقتطفات التدريب (الافتراضية + المستكشف) إلى ملف JSON."""
    from hassan12.security_kb import merged_training_snippets

    dest_file.parent.mkdir(parents=True, exist_ok=True)
    data = merged_training_snippets(Path(policy_dir))
    dest_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_policy_bundle_zip(policy_dir: Path, dest_zip: Path) -> None:
    """أرشيف يضم السجل والموافقات والتعلم (إن وُجد) + نسخة training مدمجة."""
    from hassan12.security_kb import merged_training_snippets

    policy_dir = Path(policy_dir).resolve()
    dest_zip = Path(dest_zip).resolve()
    dest_zip.parent.mkdir(parents=True, exist_ok=True)

    training_bytes = json.dumps(
        merged_training_snippets(policy_dir),
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")

    names = (
        "pending_approvals.json",
        "audit_log.jsonl",
        "learned_from_explorer.json",
    )
    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("training_merged.json", training_bytes)
        for name in names:
            p = policy_dir / name
            if p.is_file():
                zf.write(p, arcname=name)
