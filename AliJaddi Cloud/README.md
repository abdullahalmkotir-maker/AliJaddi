# AliJaddi Cloud — مسؤولية السحابة فقط

هذا المجلد **للمخطط السحابي على Supabase فقط**: تعريف الجداول، سياسات RLS، وبذور الكتالوج.  
**ليس** مكان تخزين بيانات المستخدمين محلياً ولا ملفات تشغيل التطبيقات.

| يُخزَّن هنا | لا يُخزَّن هنا |
|-------------|----------------|
| `migrations/*.sql` — نُفَّذ على Supabase | قواعد SQLite أو `users.db` |
| وثائق تطبيق الهجرات | ملفات JWT أو كلمات مرور |
| مراجع رسمية للمشروع السحابي | بيانات عيادة، عقد، أو AliJaddi 12 |

## أين تذهب بيانات المستخدم؟

- **AliJaddi Account** و **Store AliJaddi:** الحساب والربط المحلي في `data/users.db`؛ المزامنة **ترفع/تقرأ** من Supabase عبر API فقط.
- **Applications AliJaddi:** بيانات كل تطبيق في مجلده (مثل SQLite للعيادة).
- **AliJaddi 12:** بيانات أدوات التطوير في `AliJaddi 12/data/` — لا علاقة لها بمجلد `AliJaddi Cloud`.

## روابط

- **مشروع Supabase:** [nzevwjghbvrrmmshnvem.supabase.co](https://nzevwjghbvrrmmshnvem.supabase.co)
- **المستودع:** [alijadditechnology/AliJaddi](https://github.com/alijadditechnology/AliJaddi)

## الهجرات

نفّذ بالترتيب من **SQL Editor** في لوحة Supabase:

1. `migrations/001_core_tables.sql`
2. `migrations/002_seed_model_catalog.sql`

التفاصيل: `migrations/README.md`.

**لا ترفع** مفاتيح `service_role` أو **anon** إلى Git — ضع `SUPABASE_ANON_KEY` في `.env` داخل **Account** أو **Store** فقط.
