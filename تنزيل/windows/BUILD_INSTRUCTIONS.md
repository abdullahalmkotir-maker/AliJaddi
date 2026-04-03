# AliJaddi Beta 0.2 — بناء Windows (Qt for Python / PySide6)

## ما تبنيه

تطبيق سطح مكتب **AliJaddi** باستخدام **PySide6** (Qt for Python)، مع تجميع **PyInstaller** (‎`--onedir`‎) لتوزيع مجلد يحتوي ‎`AliJaddi.exe`‎ وجميع المكتبات.

---

## المتطلبات

- Windows 10/11 (64-bit)
- Python 3.10 أو أحدث
- اتصال إنترنت لتثبيت الحزم (مرة واحدة)

---

## البناء السريع

من **جذر المشروع** ‎`AliJaddi`‎:

```cmd
build_windows.bat
```

السكربت يقوم بـ:

1. تثبيت ‎`pyinstaller`‎، ‎`PySide6-Essentials`‎، ‎`python-dotenv`‎، ‎`httpx`‎، ‎`requests`‎  
2. مسح ‎`build`‎ و‎`dist`‎ السابقة  
3. تشغيل PyInstaller على ‎`main_qt.py`‎ مع أيقونة ‎`.ico`‎ إن وُجدت (‎`assets\icon.ico`‎) وإلا ‎`icon.png`‎  
4. نسخ ‎`addons`‎ إلى مجلد الإخراج عند الحاجة  
5. إنشاء أرشيف التوزيع:  
   **`تنزيل\windows\AliJaddi-Beta-0.2-Windows.zip`**

**الناتج المباشر للتنفيذ:** ‎`dist\AliJaddi\AliJaddi.exe`‎

---

## ملف البيئة ‎`.env`‎

- **لا يُضمَّن** ‎`.env`‎ داخل الحزمة (مفاتيح وخصوصية).
- بعد التثبيت، انسخ ‎`.env.example`‎ إلى ‎`.env`‎ **في نفس مجلد** ‎`AliJaddi.exe`‎ (أو اضبط المتغيرات يدوياً).

---

## استكشاف الأخطاء

| المشكلة | اقتراح |
|--------|--------|
| نافذة لا تفتح / خطأ Qt | جرّب إعادة البناء بعد ‎`pip install --upgrade PySide6-Essentials pyinstaller`‎ |
| فشل PyInstaller | تأكد أنك من جذر المشروع وأن ‎`main_qt.py`‎ و‎`ui\`‎ و‎`services\`‎ موجودة |
| الأرشيف لم يُنشأ | تأكد أن مجلد ‎`dist\AliJaddi`‎ وُجد بعد البناء؛ أنشئ يدوياً ‎`تنزيل\windows`‎ إن لزم |

---

## التوافق مع بيتا 0.2

- رقم الإصدار في التطبيق يطابق ‎`alijaddi.__version__`‎ و‎`pyproject.toml`‎ (‎`0.2.0-beta`‎).
- سجل الإضافات: ‎`addons/registry.json`‎ (حقل ‎`platform`‎ / ‎`min_platform`‎).

---

© 2026 AliJaddi
