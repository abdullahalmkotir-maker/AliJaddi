# AliJaddi Account — نظام إدارة الحسابات

جزء من مستودع الجذر [AliJaddi](../README.md). **بيانات المستخدم والحساب محلية** في `data/users.db`. المزامنة مع **Supabase** تتم عبر REST/JWT فقط. مجلد **`AliJaddi Cloud`** في المستودع يخص **هجرات SQL** لتعريف السحابة — وليس تخزيناً لبياناتك على القرص.

- **المستودع:** [github.com/alijadditechnology/AliJaddi](https://github.com/alijadditechnology/AliJaddi)
- **Supabase (مشروع المنصة):** `https://nzevwjghbvrrmmshnvem.supabase.co` — انسخ **anon key** من لوحة Supabase إلى `.env` ولا ترفعه إلى Git.

## التشغيل السريع

```bash
cd "AliJaddi Account"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run run.py
```

- سطح المكتب (PyQt): `pip install PyQt5` ثم `python run_desktop.py`
- API: يُشغَّل من التطبيق عند التفعيل أو عبر استيراد `start_api_server` من `auth_model.api`

## الهيكل

- `auth_model/` — مصادقة، واجهة Streamlit، عميل السحابة، API
- `platform_linking/` — واجهة ربط النماذج
- `alijaddi_platform/` — منصة سطح المكتب والحساب المحلي (JSON)
- `config.py` — `AVAILABLE_MODELS` متوافق مع كتالوج النماذج في السحابة (جدول `model_catalog` بعد تطبيق هجرات `AliJaddi Cloud`)

## السحابة

انسخ `.env.example` إلى `.env` وضع `SUPABASE_ANON_KEY` من لوحة Supabase. **هجرات تعريف السحابة** (وليس بيانات المستخدم): مجلد **`AliJaddi Cloud/migrations/`** — تُنفَّذ على الخادم فقط.

## الترخيص

استخدام حر ضمن المشروع.
