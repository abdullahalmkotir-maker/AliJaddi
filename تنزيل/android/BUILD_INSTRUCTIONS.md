# AliJaddi — بناء Android

## المتطلبات
- Python 3.10+
- Android SDK (API 26+)
- Android NDK
- PySide6 (النسخة الكاملة، ليست Essentials)

## الإعداد

```bash
# 1. ثبّت Android SDK/NDK عبر Android Studio
# 2. اضبط المتغيرات:
export ANDROID_SDK_ROOT=/path/to/android-sdk
export ANDROID_NDK_ROOT=/path/to/android-ndk

# 3. ثبّت PySide6 كاملاً
pip install PySide6

# 4. شغّل البناء
chmod +x build_android.sh
./build_android.sh
```

## ملاحظات
- دعم Android في PySide6 تجريبي (Qt 6.6+)
- يتطلب إعداد Android SDK/NDK مسبقاً
- APK الناتج في مجلد `android-build/`
