#!/usr/bin/env python3
"""PyQt — يتطلب: pip install PyQt5"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
except ImportError:
    print("ثبّت PyQt5: pip install PyQt5")
    sys.exit(1)


def main():
    app = QApplication(sys.argv)
    QMessageBox.information(
        None,
        "AliJaddi Account",
        "واجهة سطح المكتب الكاملة: انسخ مجلد alijaddi_platform من مشروعك السابق\n"
        "أو استخدم: streamlit run run.py",
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
