-- تنفيذ يدوي من لوحة Supabase: SQL Editor
-- شرط: وجود الجدول core.model_catalog (يُنشأ بالهجرة الأولى أو db push كامل).
-- استخدم هذا إذا تعذّر supabase db push (مثلاً بدون CLI).
-- الهجرة الإضافية لكتالوج نماذج مساحة العمل:

INSERT INTO core.model_catalog (model_id, display_name_ar, description) VALUES
  ('euqid', 'عقد (Euqid)', 'منصة إدارة وتحليل العقود — دورة حياة العقد والقانون العراقي'),
  ('tahlil', 'تحليل (tahlil)', 'تحليل بيانات وتعلم آلي وتصور — تطبيق Streamlit'),
  ('zakhrafatan', 'زخرفة', 'Zakhrafatan — توليد وتصنيف ومعالجة الزخارف والمكتبة المحلية'),
  ('sniper_perspective', 'منظور القناص', 'SniperPerspective — تتبع YOLO وواجهة استهداف (مشروع سطح المكتب)')
ON CONFLICT (model_id) DO UPDATE SET
  display_name_ar = EXCLUDED.display_name_ar,
  description = EXCLUDED.description,
  updated_at = now();

-- ---------------------------------------------------------------------------
-- واجهة REST عبر public (لا تحتاج Exposed schemas لـ core):
-- نفس محتوى supabase/migrations/20260409120000_public_rest_facade_views.sql

CREATE OR REPLACE VIEW public.model_catalog
  WITH (security_invoker = true) AS
  SELECT * FROM core.model_catalog;

CREATE OR REPLACE VIEW public.model_user_data
  WITH (security_invoker = true) AS
  SELECT * FROM core.model_user_data;

CREATE OR REPLACE VIEW public.users
  WITH (security_invoker = true) AS
  SELECT * FROM core.users;

CREATE OR REPLACE VIEW public.user_models
  WITH (security_invoker = true) AS
  SELECT * FROM core.user_models;

CREATE OR REPLACE VIEW public.social_post_queue
  WITH (security_invoker = true) AS
  SELECT * FROM core.social_post_queue;

CREATE OR REPLACE VIEW public.stars_log
  WITH (security_invoker = true) AS
  SELECT * FROM core.stars_log;

CREATE OR REPLACE VIEW public.qanun_documents
  WITH (security_invoker = true) AS
  SELECT * FROM qanun.documents;

GRANT SELECT ON public.model_catalog TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.model_user_data TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.users TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_models TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.social_post_queue TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.stars_log TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.qanun_documents TO anon, authenticated, service_role;

-- ---------------------------------------------------------------------------
-- صلاحيات core/qanun + أحداث بدون anon (نسخة لوحة SQL — مطابقة لهجرة 20260418120000_rest_facade_grants_reconcile.sql)

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA core TO postgres, anon, authenticated, service_role;
GRANT USAGE ON SCHEMA qanun TO postgres, anon, authenticated, service_role;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA core TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA core TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA qanun TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA qanun TO postgres, anon, authenticated, service_role;

GRANT SELECT, INSERT ON public.platform_install_events TO authenticated, service_role;
GRANT SELECT, INSERT ON public.user_contribution_events TO authenticated, service_role;
