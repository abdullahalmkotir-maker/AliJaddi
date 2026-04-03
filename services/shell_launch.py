"""
تجهيز أوامر التشغيل عبر cmd/sh — اختبارات وحدة بدون Qt.
"""
from __future__ import annotations

import os
import shutil


def prepare_shell_command(command: str) -> str:
    """
    - يستبدل بادئة python بمسار مفسر حقيقي (أو py -3 على Windows).
    - يضيف خيارات Streamlit المناسبة للتشغيل من المنصّة (headless + إيقاف telemetry prompt).
    """
    c = (command or "").strip()
    if not c:
        return c

    low = c.lower()
    if low.startswith("python ") or low.startswith("python3 "):
        # "python " = 7 chars; "python3 " = 8 chars
        idx = 8 if low.startswith("python3 ") else 7
        remainder = c[idx:].strip()
        py = shutil.which("python") or shutil.which("python3")
        if py:
            c = f'"{py}" {remainder}'
        elif os.name == "nt":
            py_launcher = shutil.which("py")
            if py_launcher:
                c = f'"{py_launcher}" -3 {remainder}'
        low = c.lower()

    if "streamlit run" in low:
        if "--server.headless" not in low:
            c += " --server.headless true"
        if "--browser.gatherusagestats" not in low:
            c += " --browser.gatherUsageStats false"

    return c
