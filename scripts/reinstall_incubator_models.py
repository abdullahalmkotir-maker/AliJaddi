# -*- coding: utf-8 -*-
"""
إعادة تثبيت نماذج المتجر داخل حاضنة «تطبيقات علي جدي» من روابط `addons/manifests/*.json`.

الاستخدام من جذر المستودع:
  python scripts/reinstall_incubator_models.py
  python scripts/reinstall_incubator_models.py --only-missing

يتخطى ``alijaddi_platform`` وأي manifest بلا ``download_url``. يحتاج إنترنت لجلب الـ ZIP من GitHub.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from services.addon_manager import install_model_sync  # noqa: E402
from services.paths import apps_root, bundle_root  # noqa: E402
from services.store_install_standard import STORE_INSTALL_CONTRACT_VERSION  # noqa: E402

_SKIP_IDS = frozenset({"alijaddi_platform"})


def _load_manifests() -> list[dict]:
    d = bundle_root() / "addons" / "manifests"
    out: list[dict] = []
    if not d.is_dir():
        print(f"لا يوجد مجلد manifests: {d}", file=sys.stderr)
        return out
    for f in sorted(d.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            mid = str(data.get("id", f.stem))
            data["id"] = mid
            out.append(data)
        except Exception as e:
            print(f"تجاهل {f.name}: {e}", file=sys.stderr)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--only-missing",
        action="store_true",
        help="تثبيت فقط إن كان مجلد التطبيق غير موجود داخل الحاضنة",
    )
    ns = ap.parse_args()

    root = apps_root().resolve()
    print(f"الحاضنة: {root}\n", flush=True)

    manifests = _load_manifests()
    aparent = root
    ok_n = 0
    fail_n = 0
    skip_n = 0

    for m in manifests:
        mid = str(m.get("id", ""))
        if not mid:
            skip_n += 1
            continue
        if mid in _SKIP_IDS:
            continue
        url = str(m.get("download_url") or "").strip()
        folder = str(m.get("folder") or mid).strip()
        ver = str(m.get("version") or "1.0.0").strip()
        name = str(m.get("name") or mid).strip()
        if not url:
            print(f"⏭  {mid}: لا يوجد download_url في الـ manifest (يتخطى)")
            skip_n += 1
            continue
        target = aparent / folder
        if ns.only_missing and target.is_dir():
            print(f"⏭  {mid}: موجود مسبقاً — {target}")
            skip_n += 1
            continue

        print(f"⬇  {mid} ({name}) …")
        def _log(msg: str) -> None:
            print(f"   {msg}")

        good, msg = install_model_sync(
            mid,
            url,
            folder,
            ver,
            display_name=name,
            apps_parent=aparent,
            install_contract=STORE_INSTALL_CONTRACT_VERSION,
            timeout_sec=1200.0,
            on_progress=_log,
        )
        if good:
            print(f"✓ {mid}: {msg}\n")
            ok_n += 1
        else:
            print(f"✗ {mid}: {msg}\n", file=sys.stderr)
            fail_n += 1

    print(f"انتهى — نجح: {ok_n}  فشل: {fail_n}  تخطٍ: {skip_n}")
    return 0 if fail_n == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
