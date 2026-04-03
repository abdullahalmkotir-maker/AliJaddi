#!/usr/bin/env python3
"""
AliJaddi — المُشغِّل الموحّد
بدون وسيطة: يفتح تطبيق سطح المكتب (AliJaddiAccount)
مع وسيطة model_id: يشغّل النموذج المطلوب
مع --status: يعرض حالة جميع النماذج
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PLATFORM_ROOT = Path(__file__).resolve().parent


def _resolve_account_root() -> Path:
    import os
    raw = os.getenv("ALIJADDI_ACCOUNT_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return PLATFORM_ROOT.parent / "AliJaddiAccount"


def launch_desktop() -> None:
    account = _resolve_account_root()
    launcher = account / "alijaddi_platform" / "desktop" / "launcher.py"
    if not launcher.is_file():
        print(f"[!] launcher.py not found at {launcher}")
        sys.exit(1)
    print("=" * 60)
    print("  AliJaddi Platform — Starting Desktop App ...")
    print("=" * 60)
    try:
        subprocess.run([sys.executable, str(launcher)], cwd=str(account), check=True)
    except KeyboardInterrupt:
        print("\n[*] Application closed")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error: {e}")
        sys.exit(1)


def launch_model(model_id: str) -> None:
    from alijaddi.launcher import launch_model as _launch, discover_models
    models = discover_models()
    if model_id not in models:
        print(f"[!] Model '{model_id}' not found. Available:")
        for mid, (info, _, _) in models.items():
            print(f"    {mid} — {info['name']}")
        sys.exit(1)
    info, path, _ = models[model_id]
    print(f"[*] Launching {info['icon']} {info['name']} ({model_id}) ...")
    print(f"    {path}")
    proc = _launch(model_id)
    if proc:
        proc.wait()


def show_status() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    from alijaddi.launcher import status_report
    from alijaddi.workspace import workspace_report
    print(workspace_report())
    print(status_report())


def main() -> None:
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--status":
            show_status()
        else:
            launch_model(arg)
    else:
        launch_desktop()


if __name__ == "__main__":
    main()
