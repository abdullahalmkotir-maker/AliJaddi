# تطبيقات AliJaddi

مجلد التطبيقات ضمن مستودع [alijadditechnology/AliJaddi](https://github.com/alijadditechnology/AliJaddi).

| المجلد | الوصف | التشغيل |
|--------|--------|---------|
| `تطبيق عقد/` | Euqid — مدخل Streamlit مؤقت | `pip install -r requirements.txt` ثم `streamlit run main.py` |
| `تطبيق عيادة الاسنان/` | واجهة React + خادم Node + SQLite | `npm install` ثم `npm run dev` |

**الربط بالمنصّة:** الحساب والنجوم عبر **AliJaddi Account** أو **Store AliJaddi** (قاعدة محلية + مزامنة اختيارية إلى Supabase). **مجلد `AliJaddi Cloud`** في المستودع = هجرات SQL للسحابة فقط، وليس تخزيناً لبيانات تطبيقاتك هنا.

**Manifest إضافة «عقد»:** `addons/manifests/euqid.json` في جذر المستودع.
