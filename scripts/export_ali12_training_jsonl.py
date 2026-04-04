# -*- coding: utf-8 -*-
"""
تصدير سجلات التثبيت/التشغيل المحلية إلى JSONL مهيأ لتدريب مساعدي السرب (Ali12 / Hassan12 / Hussein12) — البذور في ``12/seeds/``؛ أضف human_resolution يدوياً أو في خط لاحق.

  python scripts/export_ali12_training_jsonl.py
  python scripts/export_ali12_training_jsonl.py --only-failures path/out.jsonl
  python scripts/export_ali12_training_jsonl.py -o train.jsonl --with-ali12-seed
  python scripts/export_ali12_training_jsonl.py -o train.jsonl --with-all-seeds
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from Ali12 import ALI12_ASSISTANT_ID, recompute_from_telemetry_row, training_payload_stub
from services.install_telemetry import _TELEMETRY_FILE
from services.contribution_stars import record_contribution
from services.squad12_paths import all_seed_jsonl, seeds_dir


def main() -> int:
    p = argparse.ArgumentParser(description="تصدير JSONL لتدريب Ali12")
    p.add_argument("-o", "--output", type=Path, default=Path("ali12_train_export.jsonl"))
    p.add_argument(
        "--only-failures",
        action="store_true",
        help="صفوف نجاح=False أو أحداث فشل فقط",
    )
    p.add_argument(
        "--input",
        type=Path,
        default=_TELEMETRY_FILE,
        help="ملف السجل المحلي NDJSON",
    )
    p.add_argument(
        "--with-ali12-seed",
        action="store_true",
        help="إلحاق 12/seeds/Ali12_seed.jsonl (البذور الموحّدة)",
    )
    p.add_argument(
        "--with-euqid-seed",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    p.add_argument(
        "--with-all-seeds",
        action="store_true",
        help="إلحاق كل ملفات 12/seeds/*_seed.jsonl (Ali12 + Hassan12 + Hussein12 …)",
    )
    args = p.parse_args()

    if not args.input.is_file():
        print(f"لا ملف: {args.input}", file=sys.stderr)
        return 1

    n = 0
    with args.input.open(encoding="utf-8") as fin, args.output.open("w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if args.only_failures:
                if row.get("success") is True:
                    continue
                ek = row.get("event_kind", "")
                if ek in ("install_ok", "uninstall_ok"):
                    continue
            detail = row.get("detail") or {}
            hint = detail.get("ali12_hint", "")
            sigs = detail.get("ali12_signals")
            rid = str(detail.get("ali12_rule_id", "") or "")
            conf = detail.get("ali12_confidence")
            if not hint or not sigs:
                meta = recompute_from_telemetry_row(row)
                hint = hint or meta.get("hint_ar", "")
                sigs = sigs or meta.get("signals")
                rid = rid or str(meta.get("rule_id", ""))
                conf = conf if conf is not None else meta.get("confidence")
            aid = str(row.get("assistant_model") or ALI12_ASSISTANT_ID).strip() or ALI12_ASSISTANT_ID
            payload = training_payload_stub(
                event_kind=str(row.get("event_kind", "")),
                model_id=str(row.get("model_id", "")),
                user_message_snippet=json.dumps(detail, ensure_ascii=False)[:600],
                ali12_hint_ar=str(hint) if hint else "",
                resolution_label=str(detail.get("human_resolution", "")),
                ali12_signals=sigs if isinstance(sigs, dict) else None,
                ali12_rule_id=rid,
                ali12_confidence=conf if isinstance(conf, (int, float)) else None,
                assistant_id=aid,
            )
            fout.write(json.dumps(payload, ensure_ascii=False) + "\n")
            n += 1
    _ALI12_SEED = seeds_dir() / "Ali12_seed.jsonl"
    seed_paths: list[Path] = []
    if args.with_all_seeds:
        seed_paths = all_seed_jsonl()
    elif args.with_ali12_seed or args.with_euqid_seed:
        seed_paths = [_ALI12_SEED]
    for seed in seed_paths:
        if not seed.is_file():
            print(f"تحذير: لا ملف البذرة {seed}", file=sys.stderr)
            continue
        with seed.open(encoding="utf-8") as sf, args.output.open("a", encoding="utf-8") as fout:
            for line in sf:
                line = line.strip()
                if not line:
                    continue
                fout.write(line + "\n")
                n += 1
    print(f"Wrote {n} lines to {args.output.resolve()}")
    if n > 0:
        total = record_contribution(
            "training_export",
            points=None,
            meta={"lines": n, "output": str(args.output.resolve())},
        )
        if total:
            print(f"Contribution recorded — session stars (approx.): {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
