# -*- coding: utf-8 -*-
"""
تشغيل اختبارات مجمّعة عبر المشاريع الشقيقة — مناسب لفحص دوري سريع.
الاستخدام من جذر AliJaddi:
  python scripts/verify_ecosystem.py
  python scripts/verify_ecosystem.py --quick   # علامات -q فقط
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _store_download_bases() -> list[Path]:
    """جذر مدير التنزيلات + جذور الحاضنة القديمة (انظر ``services.legacy_data``)."""
    out: list[Path] = []
    try:
        from services.paths import apps_root

        out.append(apps_root().resolve())
    except Exception:
        pass
    try:
        from services.legacy_data import legacy_host_roots

        for p in legacy_host_roots():
            if p not in out:
                out.append(p)
    except Exception:
        pass
    return out


def _pytest(root: Path, extra: list[str]) -> int:
    tests = root / "tests"
    if not tests.is_dir():
        print(f"  [skip] no tests/: {root}")
        return 0
    cmd = [sys.executable, "-m", "pytest", str(tests), *extra]
    print(f"\n>> {' '.join(cmd)}\n  cwd={root}", flush=True)
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("CI", "1")
    kwargs: dict = {"cwd": str(root), "env": env}
    if sys.platform == "win32":
        cno = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        if cno:
            kwargs["creationflags"] = cno
    return subprocess.call(cmd, **kwargs)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="جولة تحقق عبر المنظومة")
    p.add_argument("--quick", action="store_true", help="pytest -q فقط")
    args = p.parse_args(argv)
    px = ["-q"] if args.quick else ["-v", "--tb=short"]

    suites: list[tuple[str, Path]] = []
    seen: set[Path] = set()

    def add_suite(label: str, root: Path) -> None:
        if not root.is_dir():
            return
        try:
            key = root.resolve()
        except OSError:
            key = root
        if key in seen:
            return
        seen.add(key)
        suites.append((label, root))

    here = Path(__file__).resolve().parent.parent
    add_suite("AliJaddi", here)

    for d in _desktop_dirs():
        add_suite("AliJaddiAccount", d / "AliJaddiAccount")
        add_suite("AliJaddi Cloud (python)", d / "AliJaddi Cloud" / "python")

    for base in _store_download_bases():
        for sub, label in (
            ("Zakhrafatan", "Zakhrafatan"),
            ("Euqid", "Euqid"),
        ):
            add_suite(label, base / sub)

    failed: list[str] = []
    for label, root in suites:
        print(f"\n{'='*60}\n{label}\n{'='*60}", flush=True)
        code = _pytest(root, px)
        if code != 0:
            failed.append(label)

    print(f"\n{'='*60}", flush=True)
    if failed:
        print("FAILED:", ", ".join(failed), flush=True)
        return 1
    print("All suites passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
