-- توحيد صلاحيات PostgREST: مخططات core/qanun + عروض public (تكرار آمن).
-- RLS يبقى مسؤولاً عن تصفية الصفوف؛ المنح هنا تسمح للأدوار باستدعاء الواجهة فقط.

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA core TO postgres, anon, authenticated, service_role;
GRANT USAGE ON SCHEMA qanun TO postgres, anon, authenticated, service_role;

-- كائنات مخطط core و qanun الحالية (يشمل الجداول المضافة بعد الهجرة الأولى)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA core TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA core TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA qanun TO postgres, anon, authenticated, service_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA qanun TO postgres, anon, authenticated, service_role;

-- عروض الواجهة في public
GRANT SELECT ON public.model_catalog TO anon, authenticated, service_role;

GRANT SELECT, INSERT, UPDATE, DELETE ON public.model_user_data TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.users TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_models TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.social_post_queue TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.stars_log TO anon, authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.qanun_documents TO anon, authenticated, service_role;

-- أحداث تتطلب هوية (لا تمنح anon)
GRANT SELECT, INSERT ON public.platform_install_events TO authenticated, service_role;
GRANT SELECT, INSERT ON public.user_contribution_events TO authenticated, service_role;
