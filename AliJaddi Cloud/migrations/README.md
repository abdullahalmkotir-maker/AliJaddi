# هجرات Supabase (AliJaddi Cloud)

هذه الملفات **تُطبَّق على خادم Supabase** فقط.  
مجلد `AliJaddi Cloud` لا يحتوي على بيانات مستخدمين — فقط تعريف المخطط.

## الترتيب

1. `001_core_tables.sql` — الجداول وRLS والمحفز
2. `002_seed_model_catalog.sql` — بذور `model_catalog` (متطابقة مع `auth_model/model_ids.py` في الحساب والمتجر)

**لوحة التنفيذ:** [Supabase SQL Editor](https://nzevwjghbvrrmmshnvem.supabase.co) لمشروعك.

العميل في التطبيقات: `auth_model/cloud_client.py` في **AliJaddi Account** و **Store AliJaddi** (طلبات REST إلى نفس المشروع).
