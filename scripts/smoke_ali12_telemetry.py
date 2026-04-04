"""
تشغيل بلا واجهة: يولّد أحداث تتبع تجريبية (Ali12) للتحقق من المسار المحلي.
لا يرسل للسحابة إلا إن وُجد JWT ومتغيرات Supabase.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from services.install_telemetry import _TELEMETRY_FILE, emit_install_event
from services.local_store import _DIR


def main() -> None:
    emit_install_event(
        "install_fail",
        model_id="smoke-test-model",
        success=False,
        detail={"http_status": 404, "message_snippet": "smoke 404"},
    )
    emit_install_event(
        "launch_fail",
        model_id="smoke-test-model",
        success=False,
        detail={
            "phase": "smoke",
            "launch_command": "python -m streamlit run app.py",
            "title": "Smoke",
        },
    )
    print("Telemetry dir:", _DIR)
    print("JSONL:", _TELEMETRY_FILE)
    print("راجع آخر أسطر ملف JSONL أعلاه بعد تشغيل الواجهة إن لزم.")


if __name__ == "__main__":
    main()
