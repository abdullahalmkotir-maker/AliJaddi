-- واجهة PostgREST عبر المخطط public (معرّض افتراضياً) دون الحاجة لـ «Exposed schemas → core».
-- الجداول الحقيقية تبقى في core و qanun؛ RLS يُطبَّق عبر (security_invoker = true).

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
