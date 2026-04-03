-- عمود صريح لمساعد التثبيت (Ali12) لتسهيل الفهرسة والتدريب دون قراءة JSON فقط.

ALTER TABLE core.platform_install_events
  ADD COLUMN IF NOT EXISTS assistant_model TEXT NOT NULL DEFAULT 'Ali12';

CREATE OR REPLACE VIEW public.platform_install_events
  WITH (security_invoker = true) AS
  SELECT * FROM core.platform_install_events;

GRANT SELECT, INSERT ON public.platform_install_events TO authenticated, service_role;
