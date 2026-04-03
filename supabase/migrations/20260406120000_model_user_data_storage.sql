-- بيانات النماذج السحابية: JSON لكل (مستخدم × نموذج) + تخزين ملفات اختياري

-- 1) حالة مزامنة منظّمة (تُرفع من التطبيقات عبر REST ب JWT)
CREATE TABLE IF NOT EXISTS core.model_user_data (
  user_id UUID NOT NULL REFERENCES core.users(id) ON DELETE CASCADE,
  model_id TEXT NOT NULL REFERENCES core.model_catalog(model_id) ON DELETE CASCADE,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  schema_version INTEGER NOT NULL DEFAULT 1,
  client_updated_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, model_id)
);

CREATE INDEX IF NOT EXISTS idx_model_user_data_user_id ON core.model_user_data(user_id);
CREATE INDEX IF NOT EXISTS idx_model_user_data_updated ON core.model_user_data(updated_at DESC);

ALTER TABLE core.model_user_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY model_user_data_select_self ON core.model_user_data
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY model_user_data_insert_self ON core.model_user_data
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY model_user_data_update_self ON core.model_user_data
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY model_user_data_delete_self ON core.model_user_data
  FOR DELETE USING (auth.uid() = user_id);

GRANT ALL ON TABLE core.model_user_data TO postgres, anon, authenticated, service_role;

-- 2) Bucket للملفات الكبيرة: مسار مقترح {user_id}/{model_id}/اسم_الملف
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES ('model-assets', 'model-assets', false, 52428800, NULL)
ON CONFLICT (id) DO UPDATE SET
  file_size_limit = EXCLUDED.file_size_limit;

-- سياسات Storage: كل مستخدم على مجلده فقط (أول جزء من المسار = uuid المستخدم)
DROP POLICY IF EXISTS model_assets_select_own ON storage.objects;
CREATE POLICY model_assets_select_own ON storage.objects
  FOR SELECT TO authenticated
  USING (
    bucket_id = 'model-assets'
    AND split_part(name, '/', 1) = auth.uid()::text
  );

DROP POLICY IF EXISTS model_assets_insert_own ON storage.objects;
CREATE POLICY model_assets_insert_own ON storage.objects
  FOR INSERT TO authenticated
  WITH CHECK (
    bucket_id = 'model-assets'
    AND split_part(name, '/', 1) = auth.uid()::text
  );

DROP POLICY IF EXISTS model_assets_update_own ON storage.objects;
CREATE POLICY model_assets_update_own ON storage.objects
  FOR UPDATE TO authenticated
  USING (
    bucket_id = 'model-assets'
    AND split_part(name, '/', 1) = auth.uid()::text
  )
  WITH CHECK (
    bucket_id = 'model-assets'
    AND split_part(name, '/', 1) = auth.uid()::text
  );

DROP POLICY IF EXISTS model_assets_delete_own ON storage.objects;
CREATE POLICY model_assets_delete_own ON storage.objects
  FOR DELETE TO authenticated
  USING (
    bucket_id = 'model-assets'
    AND split_part(name, '/', 1) = auth.uid()::text
  );
