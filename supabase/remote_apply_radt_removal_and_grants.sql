-- =============================================================================
-- تنفيذ لمرة واحدة من لوحة Supabase → SQL Editor (بدون Supabase CLI على الجهاز).
-- يجمع: إزالة radt + توحيد صلاحيات REST. آمن للتكرار.
-- الهجرات المقابلة: 20260417120000_remove_radt_model_data.sql
--                  20260418120000_rest_facade_grants_reconcile.sql
-- =============================================================================

-- (1) إزالة radt
DELETE FROM storage.objects
WHERE bucket_id = 'model-assets'
  AND split_part(name, '/', 2) = 'radt';

DELETE FROM core.platform_install_events WHERE model_id = 'radt';
DELETE FROM core.user_models WHERE model_name = 'radt';
UPDATE core.stars_log SET source_model = NULL WHERE source_model = 'radt';
DELETE FROM core.model_user_data WHERE model_id = 'radt';
DELETE FROM core.model_catalog WHERE model_id = 'radt';

-- (2) صلاحيات PostgREST
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA core TO postgres, anon, authenticated, service_role;
GRANT USAGE ON SCHEMA qanun TO postgres, anon, authenticated, service_role;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA core TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA core TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA qanun TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA qanun TO postgres, anon, authenticated, service_role;

GRANT SELECT ON public.model_catalog TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.model_user_data TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.users TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_models TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.social_post_queue TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.stars_log TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.qanun_documents TO anon, authenticated, service_role;
GRANT SELECT, INSERT ON public.platform_install_events TO authenticated, service_role;
GRANT SELECT, INSERT ON public.user_contribution_events TO authenticated, service_role;
