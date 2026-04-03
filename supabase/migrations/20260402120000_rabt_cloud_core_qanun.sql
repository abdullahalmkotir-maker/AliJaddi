-- AliJaddi Cloud — هجرة أولية: مخططات core و qanun + RLS + كتالوج النماذج (اسم الملف تاريخي)
-- للربط مع GitHub في لوحة Supabase: supabase/migrations/

-- 1. core schema
CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE IF NOT EXISTS core.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT UNIQUE NOT NULL,
  role TEXT DEFAULT 'user',
  stars_balance INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.user_models (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES core.users(id) ON DELETE CASCADE,
  model_name TEXT NOT NULL,
  is_active BOOLEAN DEFAULT true,
  stars_earned_from_model INTEGER DEFAULT 0,
  last_used TIMESTAMPTZ,
  UNIQUE(user_id, model_name)
);

CREATE TABLE IF NOT EXISTS core.stars_log (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES core.users(id) ON DELETE CASCADE,
  amount_change INTEGER NOT NULL,
  reason TEXT,
  source_model TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.model_catalog (
  model_id TEXT PRIMARY KEY,
  display_name_ar TEXT NOT NULL,
  description TEXT DEFAULT '',
  updated_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO core.model_catalog (model_id, display_name_ar, description) VALUES
  ('legal', 'قانون', 'استعلامات قانونية وربط مع نماذج أخرى'),
  ('maps', 'خرائط', 'خرائط تفاعلية وأحداث مواقع'),
  ('adich', 'أدّيش', 'نموذج أدّيش — محتوى يُخزَّن في السحابة ويُعرض من العميل'),
  ('sniper', 'قناص', 'نموذج تفاعلي / ألعاب'),
  ('qanun_example', 'مثال قانون', 'وثائق مضغوطة تجريبية من الديمو')
ON CONFLICT (model_id) DO UPDATE SET
  display_name_ar = EXCLUDED.display_name_ar,
  description = EXCLUDED.description,
  updated_at = now();

ALTER TABLE core.model_catalog ENABLE ROW LEVEL SECURITY;

CREATE POLICY model_catalog_select_authenticated ON core.model_catalog
  FOR SELECT TO authenticated
  USING (true);

-- 2. qanun schema
CREATE SCHEMA IF NOT EXISTS qanun;

CREATE TABLE IF NOT EXISTS qanun.documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES core.users(id) ON DELETE CASCADE,
  title TEXT,
  content_compressed BYTEA,
  doc_type TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. RLS
ALTER TABLE core.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.user_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.stars_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE qanun.documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_select_self ON core.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY user_update_self ON core.users
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY user_models_select_self ON core.user_models
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY stars_log_select_self ON core.stars_log
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY qanun_documents_select ON qanun.documents
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY qanun_documents_insert_self ON qanun.documents
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS idx_gu_user_models_user_id ON core.user_models(user_id);
CREATE INDEX IF NOT EXISTS idx_gu_stars_log_user_id ON core.stars_log(user_id);
CREATE INDEX IF NOT EXISTS idx_q_documents_user_id ON qanun.documents(user_id);

-- 4. صلاحيات PostgREST للمخططات غير public (محلياً + بعد «Exposed schemas» في لوحة التحكم)
GRANT USAGE ON SCHEMA core TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA core TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA core TO postgres, anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA core GRANT ALL ON TABLES TO postgres, anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA core GRANT ALL ON SEQUENCES TO postgres, anon, authenticated, service_role;

GRANT USAGE ON SCHEMA qanun TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA qanun TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA qanun TO postgres, anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA qanun GRANT ALL ON TABLES TO postgres, anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA qanun GRANT ALL ON SEQUENCES TO postgres, anon, authenticated, service_role;
