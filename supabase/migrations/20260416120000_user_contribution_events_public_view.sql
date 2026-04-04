-- تعريض جدول المساهمات عبر PostgREST (مثل platform_install_events)
GRANT ALL ON TABLE core.user_contribution_events TO postgres, service_role;
GRANT SELECT, INSERT ON TABLE core.user_contribution_events TO authenticated;

CREATE OR REPLACE VIEW public.user_contribution_events
  WITH (security_invoker = true) AS
  SELECT * FROM core.user_contribution_events;

GRANT SELECT, INSERT ON public.user_contribution_events TO authenticated, service_role;
