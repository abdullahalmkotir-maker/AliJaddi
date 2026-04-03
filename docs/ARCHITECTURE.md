# معمارية منصّة علي جدّي (Beta 0.2)

توثيق يربط **المنصّة الرئيسية**، **السحابة**، **حساب المستخدم**، ومشاريع **النماذج** على سطح المكتب.

## مخطط تدفّق عالٍ

```mermaid
flowchart TB
  subgraph desktop [سطح المكتب]
    AJ[AliJaddi\nPySide6 main_qt.py]
    ACC[AliJaddiAccount\nalijaddi_platform]
    APPS[تطبيقات علي جدي\nZakhrafatan / Euqid / tahlil / ...]
  end

  subgraph cloud [Supabase]
    PG[(PostgreSQL\ncore / qanun / public)]
    ST[Storage\nmodel-assets]
    AUTH[Auth JWT]
  end

  AJ -->|تسجيل / متجر إضافات| PG
  AJ -->|JWT| AUTH
  ACC -->|مزامنة حساب| PG
  APPS -->|alijaddi_cloud_sync.py\nmodel_user_data| PG
  APPS -->|JWT من المنصّة| AUTH
  AJ -.->|launch.py اختياري| ACC
```

## المكوّنات والمسارات

| جزء | المجلد / الملف | الدور |
|-----|-----------------|--------|
| المنصّة | `AliJaddi/` — `main_qt.py`, `ui/`, `services/` | واجهة Qt، متجر النماذج، `addon_manager`، مصادقة |
| السحابة | `AliJaddi Cloud/` — `python/integration/` | أدوات مساعدة، ضغط، REST؛ الهجرات في `AliJaddi/supabase/migrations/` |
| الحساب | `AliJaddiAccount/` — `alijaddi_platform/desktop/launcher.py` | يُستدعى من `AliJaddi/launch.py` عند التشغيل بدون وسيطات |
| نموذج على سطح المكتب | `تطبيقات علي جدي/<Model>/alijaddi_cloud_sync.py` | رفع/جلب `payload` عبر `rest/v1/model_user_data` |

## متغيرات بيئة مشتركة

- `SUPABASE_URL`, `SUPABASE_ANON_KEY` — نفس المشروع لجميع العملاء (انظر `.env.example`).
- JWT المستخدم يُمرَّر أحياناً كـ `ALIJADDI_JWT` من المنصّة عند تشغيل نموذج خارجي.

## بناء التوزيع (Windows)

- `scripts/build_windows_release.ps1` — PyInstaller + PySide6.
- الحزمة: `تنزيل/windows/AliJaddi-Beta-0.2-Windows.zip` (مستثناة من Git).

---

© 2026 AliJaddi — بيتا 0.2
