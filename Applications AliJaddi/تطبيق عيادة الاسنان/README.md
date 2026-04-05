# تطبيق عيادة الأسنان

جزء من مستودع [alijadditechnology/AliJaddi](https://github.com/alijadditechnology/AliJaddi).

## المتطلبات

- Node.js 18+

## التشغيل

```bash
npm install
npm run dev
```

- الواجهة: Vite (يُفتح بعد جاهزية الخادم).
- الخادم: `http://127.0.0.1:4000` — مسار صحة: `/api/health`.

## البناء

```bash
npm run build
npm start
```

البيانات المحلية: مجلد `server/data` (يُستثنى من Git عبر `.gitignore` عند الحاجة).

## السحابة

مزامنة المنصة العامة عبر مشروع **AliJaddi Account** / **Store AliJaddi** و [Supabase](https://nzevwjghbvrrmmshnvem.supabase.co)؛ هذا التطبيق حالياً مستقل بقاعدة SQLite محلية.
