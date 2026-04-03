# AliJaddi — تنزيل (Beta 0.1)

## علي جدّي — منصة نماذج الذكاء الاصطناعي

**الإصدار:** Beta 0.1  
**الإطار:** Qt for Python (PySide6)  
**التاريخ:** أبريل 2026

---

## المنصات المتاحة

### Windows
- **المجلد:** `windows/`
- **التشغيل:** فك ضغط `AliJaddi-Beta-0.1-Windows.zip` ثم شغّل `AliJaddi.exe`
- **المتطلبات:** Windows 10 أو أحدث (64-bit)

### macOS
- **المجلد:** `macos/`
- **التعليمات:** شغّل `build_macos.sh` من مجلد المشروع على جهاز Mac
- **المتطلبات:** macOS 11+ (Intel أو Apple Silicon)

### Android
- **المجلد:** `android/`
- **التعليمات:** شغّل `build_android.sh` من مجلد المشروع (يتطلب Android SDK/NDK)
- **المتطلبات:** Android 8+ (API 26+)

---

## الميزات

- 6 نماذج ذكاء اصطناعي (زخرفة، عقد، تحليل، مدير التواصل، مساعد طبيب الأسنان، منظور القناص)
- متجر إضافات — تثبيت وتحديث النماذج مباشرة
- نظام مصادقة (اختياري) مع مزامنة سحابية
- وضع مظلم / فاتح
- واجهة عربية RTL كاملة
- يعمل بدون إنترنت

---

## البناء من المصدر

```bash
# تثبيت المتطلبات
pip install PySide6-Essentials python-dotenv httpx requests

# تشغيل مباشر
python main_qt.py

# بناء Windows
build_windows.bat

# بناء macOS
chmod +x build_macos.sh && ./build_macos.sh

# بناء Android
chmod +x build_android.sh && ./build_android.sh
```

---

© 2026 AliJaddi — جميع الحقوق محفوظة
