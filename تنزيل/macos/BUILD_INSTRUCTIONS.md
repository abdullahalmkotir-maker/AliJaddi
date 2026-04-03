# AliJaddi Beta 0.2 — بناء macOS (PySide6)

## المتطلبات
- macOS 11 (Big Sur) أو أحدث
- Python 3.10+
- pip

## خطوات البناء

```bash
# 1. انتقل إلى مجلد المشروع
cd AliJaddi

# 2. ثبّت المتطلبات (Qt for Python)
pip3 install PySide6-Essentials python-dotenv httpx requests pyinstaller

# 3. شغّل سكريبت البناء
chmod +x build_macos.sh
./build_macos.sh

# 4. الناتج في dist/AliJaddi/
open dist/AliJaddi/AliJaddi
```

- لا يُدمج ملف `.env` في الحزمة؛ انسخ `.env.example` إلى `.env` بجانب التطبيق عند التوزيع.
- سيتم إنشاء حزمة التطبيق في مجلد `dist/`.
