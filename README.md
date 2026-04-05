# AliJaddi

مستودع موحّد لمنصة **علي جدّي**: الحساب، المتجر، التطبيقات، والسحابة.

| المورد | الرابط |
|--------|--------|
| **تنزيل / كود** | [github.com/alijadditechnology/AliJaddi](https://github.com/alijadditechnology/AliJaddi) |
| **السحابة (Supabase)** | [nzevwjghbvrrmmshnvem.supabase.co](https://nzevwjghbvrrmmshnvem.supabase.co) |

## هيكل المشروع

| المجلد | الوصف |
|--------|--------|
| `AliJaddi Account/` | واجهة Streamlit — حساب، نجوم، ربط نماذج، مزامنة JWT |
| `Store AliJaddi/` | المتجر + حزمة **Store12** (بيتا 0.1): `run_store12.py`، `releases/*.zip` |
| `Applications AliJaddi/` | تطبيقات (عقد، عيادة أسنان، …) — `Applications AliJaddi/README.md` |
| `AliJaddi Cloud/` | **السحابة فقط:** هجرات SQL ووثائق مخطط Supabase — **لا** يُخزَّن فيه بيانات المستخدمين محلياً |
| `addons/manifests/` | وصف إضافات المنصة (مثل `euqid.json`) |
| `AliJaddi 12/` | حزم Hassan12 / Ali12 / Hussein12 — `AliJaddi 12/README.md` |

## التشغيل السريع (الحساب أو المتجر)

```bash
cd "AliJaddi Account"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# ضع SUPABASE_ANON_KEY من لوحة Supabase → Settings → API
streamlit run run.py
```

## السحابة (AliJaddi Cloud)

- **مجلد `AliJaddi Cloud/`:** مسؤول عن **تعريف** قاعدة البيانات على Supabase (ملفات SQL). ليس مستودعاً لملفات المستخدمين.
- **بيانات الحساب محلياً:** في `AliJaddi Account/data/` و `Store AliJaddi/data/` (`users.db`).
1. طبّق SQL من `AliJaddi Cloud/migrations/` في [Supabase SQL Editor](https://supabase.com/dashboard).
2. مفاتيح **anon** في `.env` داخل مشروع الحساب أو المتجر فقط — لا ترفعها إلى Git.

## إكمال مشاريع ناقصة

- **عقد (Euqid):** `Applications AliJaddi/تطبيق عقد/` — يوجد `main.py` مؤقت؛ لاستبداله بالمشروع الكامل استخدم `_move_euqid_here.ps1` أو انسخ الملفات يدوياً.
- **مزامنة manifest:** من جذر المستودع: `.\sync_euqid_folder_path.ps1` (إن وُجد).

## Git

```bash
git clone https://github.com/alijadditechnology/AliJaddi.git
cd AliJaddi
```

الرفع يتطلب حساب GitHub مفعّلاً على الجهاز (SSH أو HTTPS + token).
