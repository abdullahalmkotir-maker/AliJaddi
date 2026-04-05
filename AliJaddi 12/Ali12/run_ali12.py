# -*- coding: utf-8 -*-
"""Ali12 — سطر أوامر التثبيت والتصدير ودمج/إعداد التدريب."""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from ali12 import BRAND, DESCRIPTION_AR
from ali12.export_ops import write_policy_bundle_zip, write_training_json
from ali12.install_ops import default_install_root, install
from ali12.merge_training import merge_to_jsonl
from hassan12.synthetic_training import SyntheticGenerator


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="run_ali12.py",
        description=f"{BRAND}: {DESCRIPTION_AR}",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_inst = sub.add_parser("install", help="تثبيت الحزمة واختصار سطح المكتب (ويندوز)")
    p_inst.add_argument(
        "--source",
        type=Path,
        default=None,
        help="مجلد المشروع المصدر (افتراضي: مجلد هذا المستودع)",
    )
    p_inst.add_argument(
        "--target",
        type=Path,
        default=None,
        help="جذر التثبيت (افتراضي: %%LOCALAPPDATA%%\\Ali12)",
    )

    p_tr = sub.add_parser("export-training", help="تصدير JSON للتدريب (مقتطفات مدمجة)")
    p_tr.add_argument(
        "--out",
        type=Path,
        required=True,
        help="مسار ملف JSON الناتج",
    )
    p_tr.add_argument(
        "--policy-dir",
        type=Path,
        default=Path.home() / ".hassan12_policy",
        help="مجلد السياسات والسجلات",
    )

    p_b = sub.add_parser("export-bundle", help="تصدير ZIP (سجلات + تدريب مدمج)")
    p_b.add_argument(
        "--out",
        type=Path,
        required=True,
        help="مسار ملف .zip",
    )
    p_b.add_argument(
        "--policy-dir",
        type=Path,
        default=Path.home() / ".hassan12_policy",
        help="مجلد السياسات والسجلات",
    )

    p_syn = sub.add_parser(
        "generate-synthetic",
        help="توليد بيانات تدريبية اصطناعية (JSONL)",
    )
    p_syn.add_argument(
        "--out",
        type=Path,
        required=True,
        help="ملف JSONL الناتج (سطر = عينة واحدة)",
    )
    p_syn.add_argument(
        "--count",
        type=int,
        default=10_000,
        help="عدد العينات (افتراضي 10000)",
    )
    p_syn.add_argument(
        "--seed",
        type=int,
        default=42,
        help="بذر عشوائية لإعادة إنتاج نفس الدفعة",
    )

    p_merge = sub.add_parser(
        "merge-corpus",
        help="دمج مقتطفات المعرفة + ملفات JSONL في ملف JSONL واحد",
    )
    p_merge.add_argument(
        "--out",
        type=Path,
        required=True,
        help="ملف JSONL المدمج",
    )
    p_merge.add_argument(
        "--policy-dir",
        type=Path,
        default=Path.home() / ".hassan12_policy",
        help="مجلد السياسات (learned_from_explorer.json إن وُجد)",
    )
    p_merge.add_argument(
        "--jsonl",
        type=Path,
        action="append",
        default=[],
        help="ملف JSONL لإضافته (يمكن تكرار الخيار)",
    )

    p_train = sub.add_parser(
        "train-prep",
        help="توليد عينات اصطناعية ثم دمجها مع المقتطفات (إعداد ملف تدريب)",
    )
    p_train.add_argument(
        "--out",
        type=Path,
        required=True,
        help="ملف JSONL النهائي المدمج",
    )
    p_train.add_argument(
        "--policy-dir",
        type=Path,
        default=Path.home() / ".hassan12_policy",
        help="مجلد السياسات",
    )
    p_train.add_argument(
        "--count",
        type=int,
        default=5_000,
        help="عدد العينات الاصطناعية قبل الدمج (افتراضي 5000)",
    )
    p_train.add_argument(
        "--seed",
        type=int,
        default=42,
        help="بذر التوليد الاصطناعي",
    )
    p_train.add_argument(
        "--keep-synthetic",
        type=Path,
        default=None,
        help="إن وُجد: حفظ ملف الاصطناعي المنفصل في هذا المسار بدل حذفه",
    )

    args = parser.parse_args()

    if args.command == "install":
        root = install(source_root=args.source, install_root=args.target)
        print(f"[{BRAND}] اكتمل التثبيت في: {root}")
        if sys.platform == "win32":
            print(f"[{BRAND}] اختصار سطح المكتب: Ali12 — أدوات التدريب.lnk")
    elif args.command == "export-training":
        write_training_json(args.policy_dir, args.out)
        print(f"[{BRAND}] تدريب JSON: {args.out.resolve()}")
    elif args.command == "export-bundle":
        write_policy_bundle_zip(args.policy_dir, args.out)
        print(f"[{BRAND}] الحزمة: {args.out.resolve()}")
    elif args.command == "generate-synthetic":
        n = SyntheticGenerator(seed=args.seed).write_jsonl(args.out, args.count)
        print(f"[{BRAND}] Hassan12 synthetic: {n} samples -> {args.out.resolve()}")
    elif args.command == "merge-corpus":
        extra = list(args.jsonl) if args.jsonl else []
        n_kb, n_extra = merge_to_jsonl(args.policy_dir, args.out, extra)
        print(
            f"[{BRAND}] دمج corpus: {n_kb} مقتطف معرفة + {n_extra} من JSONL -> {args.out.resolve()}"
        )
    elif args.command == "train-prep":
        syn_path = args.keep_synthetic
        cleanup: Path | None = None
        if syn_path is None:
            td = Path(tempfile.mkdtemp(prefix="ali12_syn_"))
            syn_path = td / "synthetic.jsonl"
            cleanup = td
        try:
            n_syn = SyntheticGenerator(seed=args.seed).write_jsonl(syn_path, args.count)
            print(f"[{BRAND}] اصطناعي: {n_syn} -> {syn_path.resolve()}")
            n_kb, n_extra = merge_to_jsonl(
                args.policy_dir,
                args.out,
                [syn_path],
            )
            print(
                f"[{BRAND}] تدريب مدمج: {n_kb} معرفة + {n_extra} اصطناعي = "
                f"{n_kb + n_extra} سطر -> {args.out.resolve()}"
            )
        finally:
            if cleanup is not None and cleanup.is_dir():
                import shutil

                shutil.rmtree(cleanup, ignore_errors=True)


if __name__ == "__main__":
    main()
