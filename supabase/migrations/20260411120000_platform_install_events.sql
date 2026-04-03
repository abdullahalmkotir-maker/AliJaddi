-- أحداث تثبيت/إزالة التطبيقات الفرعية — لتصحيح الأعطال ولاحقاً تدريب نماذج مساعدة (بدون PII في detail).
-- الإدراج عبر PostgREST + JWT؛ user_id يُستنتج من auth.uid().

CREATE TABLE IF NOT EXISTS core.platform_install_events (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL DEFAULT auth.uid() REFERENCES core.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  event_kind TEXT NOT NULL,
  model_id TEXT,
  platform_app_version TEXT,
  client_os TEXT,
  success BOOLEAN,
  detail JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_platform_install_events_user
  ON core.platform_install_events(user_id, created_at DESC);

ALTER TABLE core.platform_install_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY platform_install_events_insert_self
  ON core.platform_install_events
  FOR INSERT TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY platform_install_events_select_self
  ON core.platform_install_events
  FOR SELECT TO authenticated
  USING (auth.uid() = user_id);

GRANT ALL ON TABLE core.platform_install_events TO postgres, service_role;
GRANT SELECT, INSERT ON TABLE core.platform_install_events TO authenticated;

GRANT USAGE, SELECT ON SEQUENCE core.platform_install_events_id_seq
  TO postgres, authenticated, service_role;

-- واجهة public لـ PostgREST
CREATE OR REPLACE VIEW public.platform_install_events
  WITH (security_invoker = true) AS
  SELECT * FROM core.platform_install_events;

GRANT SELECT, INSERT ON public.platform_install_events TO authenticated, service_role;
