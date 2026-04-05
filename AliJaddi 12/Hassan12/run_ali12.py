# -*- coding: utf-8 -*-
"""Ali12 — سطر أوامر التثبيت والتصدير."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ali12 import BRAND, DESCRIPTION_AR
from ali12.export_ops import write_policy_bundle_zip, write_training_json
from ali12.install_ops import install
from hassan12.synthetic_training import SyntheticGenerator


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="run_ali12.py",
        description=f"{BRAND}: {DESCRIPTION_AR}",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_inst = sub.add_parser("install", help="تثبيت التطبيق واختصار سطح المكتب (ويندوز)")
    p_inst.add_argument("--source", type=Path, default=None)
    p_inst.add_argument("--target", type=Path, default=None)

    p_tr = sub.add_parser("export-training", help="تصدير JSON للتدريب")
    p_tr.add_argument("--out", type=Path, required=True)
    p_tr.add_argument(
        "--policy-dir",
        type=Path,
        default=Path.home() / ".hassan12_policy",
    )

    p_b = sub.add_parser("export-bundle", help="تصدير ZIP (سجلات + تدريب مدمج)")
    p_b.add_argument("--out", type=Path, required=True)
    p_b.add_argument(
        "--policy-dir",
        type=Path,
        default=Path.home() / ".hassan12_policy",
    )

    p_syn = sub.add_parser("generate-synthetic", help="توليد عينات JSONL للتدريب")
    p_syn.add_argument("--out", type=Path, required=True)
    p_syn.add_argument("--count", type=int, default=10_000)
    p_syn.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    if args.command == "install":
        root = install(source_root=args.source, install_root=args.target)
        print(f"[{BRAND}] install OK: {root}")
        if sys.platform == "win32":
            print(f"[{BRAND}] shortcut: Desktop\\مدير الملفات Hassan12.lnk")
    elif args.command == "export-training":
        write_training_json(args.policy_dir, args.out)
        print(f"[{BRAND}] training JSON: {args.out.resolve()}")
    elif args.command == "export-bundle":
        write_policy_bundle_zip(args.policy_dir, args.out)
        print(f"[{BRAND}] bundle: {args.out.resolve()}")
    elif args.command == "generate-synthetic":
        n = SyntheticGenerator(seed=args.seed).write_jsonl(args.out, args.count)
        print(f"[{BRAND}] Hassan12 synthetic: {n} samples -> {args.out.resolve()}")


if __name__ == "__main__":
    main()
