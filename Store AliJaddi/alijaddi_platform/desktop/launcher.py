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
        "متجر علي جدّي",
        "تشغيل المتجر الكامل: streamlit run run.py من مجلد Store AliJaddi.\n"
        "واجهة PyQt الكاملة قيد التوسعة هنا.",
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
