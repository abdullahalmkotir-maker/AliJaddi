# متجر علي جدّي (`Store AliJaddi`)

جزء من مستودع الجذر [AliJaddi](../README.md). **بيانات المستخدم محلية** في `data/users.db`. المزامنة مع **Supabase** عبر API فقط. مجلد **`AliJaddi Cloud`** في المستودع = **هجرات SQL** للمخطط السحابي فقط، وليس مجلد تخزين للمستخدمين. الواجهة بمنطق **المتجر**.

- **المستودع:** [github.com/alijadditechnology/AliJaddi](https://github.com/alijadditechnology/AliJaddi)
- **Supabase:** `https://nzevwjghbvrrmmshnvem.supabase.co` — المفتاح السري في `.env` فقط.

## التشغيل السريع

```bash
cd "Store AliJaddi"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run run.py
```

## بيتا 0.1 — تثبيت سطح المكتب (معايير Ali12 / Store12)

- **الإصدار:** `VERSION.txt` (`0.1.0-beta`).
- **من المستودع:** شغّل `python run_store12.py export-zip` — يُنشئ `AliJaddiStore-0.1.0-beta.zip` في **مجلد التنزيلات** ونسخة في `releases/` للرفع.
- **للمستخدم:** فك الضغط → `Install-StoreAliJaddi.ps1` (أو من الطرفية: `python run_store12.py install --source .`).
- **بعد التثبيت:** اختصار **«متجر علي جدّي — بيتا»** على سطح المكتب؛ التطبيق في `%LOCALAPPDATA%\AliJaddiStore\app` مع `venv` منفصل.

- سطح المكتب (PyQt اختصاري): `pip install PyQt5` ثم `python run_desktop.py`
- API: يُستورد عند الحاجة من `auth_model.api`

## الهيكل

- `run.py` — تشغيل Streamlit، ثيم المتجر، التوجيه بعد الدخول
- `store/` — واجهة المتجر:
  - `theme.py` — ثيم RTL وألوان المتجر
  - `shell.py` — الشريط الجانبي والتنقّل
  - `home.py` — الصفحة الرئيسية وملخص الحساب
  - `catalog.py` — كتالوج التطبيقات (إضافة / إلغاء ربط)
- `platform_linking/` — يعيد تصدير `show_linking_ui` من `store.catalog` (توافق خلفي)
- `auth_model/` — مصادقة، مركز الحساب، عميل السحابة، API
- `alijaddi_platform/` — سطح المكتب (PyQt) الاختياري
- `config.py` — `AVAILABLE_MODELS` متوافق مع `model_catalog` في السحابة (بعد هجرات `AliJaddi Cloud`)

## السحابة

انسخ `.env.example` إلى `.env` وضع `SUPABASE_ANON_KEY`. **تعريف السحابة:** طبّق `AliJaddi Cloud/migrations/` على Supabase؛ لا تضع قاعدة المستخدمين داخل مجلد `AliJaddi Cloud`.

## الترخيص

استخدام حر ضمن المشروع.
