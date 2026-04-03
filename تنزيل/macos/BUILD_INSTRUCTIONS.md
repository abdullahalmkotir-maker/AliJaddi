# AliJaddi — بناء macOS

## المتطلبات
- macOS 11 (Big Sur) أو أحدث
- Python 3.10+
- pip

## خطوات البناء

```bash
# 1. انتقل إلى مجلد المشروع
cd AliJaddi

# 2. ثبّت المتطلبات
pip3 install PySide6-Essentials python-dotenv httpx requests pyinstaller

# 3. شغّل سكريبت البناء
chmod +x build_macos.sh
./build_macos.sh

# 4. الناتج في dist/AliJaddi/
open dist/AliJaddi/AliJaddi
```

سيتم إنشاء ملف `.app` في مجلد `dist/`.
