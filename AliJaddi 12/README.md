# AliJaddi 12

حزم تطوير ومساعدة مرتبطة بمنصة **علي جدّي** (مستودع الجذر [../README.md](../README.md)).

| المجلد | المحتوى |
|--------|---------|
| `Hassan12/` | تطبيق Hassan12، Ali12، أدوات تثبيت |
| `Ali12/` | نسخة Ali12 مع دمج تدريب |
| `Hussein12/` | مكتبة بايثون (`pyproject.toml`)، CLI، واجهات عربية |

**السحابة (مخطط فقط):** هجرات SQL في `AliJaddi Cloud/migrations/` تُطبَّق على [Supabase](https://nzevwjghbvrrmmshnvem.supabase.co). **AliJaddi 12** لا يخزّن بيانات المنصّة في ذلك المجلد — بيانات الأدوات هنا تحت `AliJaddi 12/data/`.  
**حساب المستخدم:** `AliJaddi Account/` أو `Store AliJaddi/`.

### بيانات محلية (`data/`)

ملف `data/workbench_state.json` يستخدم مسارات **نسبية** (`data/workbench_corpus.jsonl`). عدّل المسارات حسب جهازك.

لا ترفع إلى Git ملفات تحتوي مسارات مستخدمين حقيقية أو محادثات حساسة.
