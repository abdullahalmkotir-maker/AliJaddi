#!/usr/bin/env python3
"""تشغيل واجهة سطح المكتب (PyQt) إن وُجدت."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
LAUNCHER = os.path.join(ROOT, "alijaddi_platform", "desktop", "launcher.py")


def main():
    if not os.path.isfile(LAUNCHER):
        print("[!] launcher.py غير موجود")
        sys.exit(1)
    subprocess.run([sys.executable, LAUNCHER], check=True)


if __name__ == "__main__":
    main()
