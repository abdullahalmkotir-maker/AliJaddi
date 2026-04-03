-- مدير التواصل (Mudir) — ملخص جدولة المنشورات للمزامنة مع علي جدي سحابة / AliJaddiAccount
-- بيانات وصفية فقط (لا رموز منصات ولا مسارات ملفات)

CREATE TABLE IF NOT EXISTS core.social_post_queue (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES core.users(id) ON DELETE CASCADE,
  client_local_id BIGINT NOT NULL,
  status TEXT NOT NULL DEFAULT 'scheduled',
  caption_excerpt TEXT DEFAULT '',
  scheduled_at TIMESTAMPTZ,
  platforms TEXT DEFAULT '',
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (user_id, client_local_id)
);

CREATE INDEX IF NOT EXISTS idx_social_post_queue_user ON core.social_post_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_social_post_queue_scheduled ON core.social_post_queue(scheduled_at);

ALTER TABLE core.social_post_queue ENABLE ROW LEVEL SECURITY;

CREATE POLICY social_post_queue_select_self ON core.social_post_queue
  FOR SELECT TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY social_post_queue_insert_self ON core.social_post_queue
  FOR INSERT TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY social_post_queue_update_self ON core.social_post_queue
  FOR UPDATE TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY social_post_queue_delete_self ON core.social_post_queue
  FOR DELETE TO authenticated
  USING (auth.uid() = user_id);

INSERT INTO core.model_catalog (model_id, display_name_ar, description) VALUES
  ('mudir', 'مدير التواصل', 'جدولة ونشر محتوى على فيسبوك وإنستغرام وتيك توك وX — مزامنة ملخص مع السحابة')
ON CONFLICT (model_id) DO UPDATE SET
  display_name_ar = EXCLUDED.display_name_ar,
  description = EXCLUDED.description,
  updated_at = now();

GRANT ALL ON TABLE core.social_post_queue TO postgres, anon, authenticated, service_role;
GRANT USAGE, SELECT ON SEQUENCE core.social_post_queue_id_seq TO postgres, anon, authenticated, service_role;
