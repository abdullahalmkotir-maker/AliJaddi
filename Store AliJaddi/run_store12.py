# -*- coding: utf-8 -*-
"""Store12 — تثبيت وتصدير متجر علي جدّي (معايير Ali12)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from store12 import BRAND, DESCRIPTION_AR, VERSION
from store12.export_ops import build_release_zip
from store12.install_ops import default_install_root, install


def _default_downloads_zip() -> Path:
    home = Path.home()
    dl = home / "Downloads"
    if not dl.is_dir():
        dl = home / "تنزيلات"
    if not dl.is_dir():
        dl = home
    return dl / f"AliJaddiStore-{VERSION}.zip"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="run_store12.py",
        description=f"{BRAND}: {DESCRIPTION_AR}",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_inst = sub.add_parser("install", help="تثبيت إلى LOCALAPPDATA واختصار سطح المكتب")
    p_inst.add_argument("--source", type=Path, default=None, help="مجلد Store AliJaddi")
    p_inst.add_argument("--target", type=Path, default=None, help="جذر التثبيت")

    p_zip = sub.add_parser("export-zip", help="بناء أرشيف للتوزيع")
    p_zip.add_argument(
        "--out",
        type=Path,
        default=None,
        help=f"مسار .zip (افتراضي: مجلد التنزيلات / AliJaddiStore-{VERSION}.zip)",
    )
    p_zip.add_argument("--source", type=Path, default=None, help="مجلد Store AliJaddi المصدر")

    args = parser.parse_args()

    if args.command == "install":
        src = args.source or ROOT
        root = install(source_root=src, install_root=args.target)
        print(f"[{BRAND}] اكتمل التثبيت في: {root}")
        if sys.platform == "win32":
            print(f"[{BRAND}] اختصار سطح المكتب: متجر علي جدّي — بيتا.lnk")
    elif args.command == "export-zip":
        src = (args.source or ROOT).resolve()
        out = args.out or _default_downloads_zip()
        rel = Path(__file__).resolve().parent / "releases"
        rel.mkdir(parents=True, exist_ok=True)
        build_release_zip(src, out)
        print(f"[{BRAND}] تصدير: {out.resolve()}")
        mirror = rel / out.name
        build_release_zip(src, mirror)
        print(f"[{BRAND}] نسخة للمستودع: {mirror.resolve()}")


if __name__ == "__main__":
    main()
