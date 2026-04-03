-- ═══════════════════════════════════════════════════════
-- AliJaddi — Supabase Schema
-- مشروع: mfhtnfxdfpelrgzonxov
-- يُنفَّذ مرة واحدة من SQL Editor في لوحة Supabase
-- ═══════════════════════════════════════════════════════

-- 1) جدول المستخدمين (رصيد النجوم + بيانات إضافية)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    stars_balance INT DEFAULT 0,
    display_name TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own row"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own row"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own row"
    ON public.users FOR INSERT
    WITH CHECK (auth.uid() = id);


-- 2) سجل الإضافات السحابي (مرآة GitHub)
CREATE TABLE IF NOT EXISTS public.addon_registry (
    id TEXT PRIMARY KEY DEFAULT 'main',
    data JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.addon_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read addon_registry"
    ON public.addon_registry FOR SELECT
    USING (true);


-- 3) إضافات المستخدم المثبتة (للمزامنة بين الأجهزة)
CREATE TABLE IF NOT EXISTS public.user_addons (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    installed JSONB NOT NULL DEFAULT '{}',
    favorites JSONB NOT NULL DEFAULT '[]',
    settings JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.user_addons ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own addons"
    ON public.user_addons FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can upsert own addons"
    ON public.user_addons FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own addons"
    ON public.user_addons FOR UPDATE
    USING (auth.uid() = user_id);


-- 4) كتالوج النماذج (اختياري — لعرض تقييمات/تنزيلات حية)
CREATE TABLE IF NOT EXISTS public.model_catalog (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    version TEXT DEFAULT '1.0.0',
    icon TEXT DEFAULT '',
    color TEXT DEFAULT '#3B82F6',
    category TEXT DEFAULT '',
    download_url TEXT DEFAULT '',
    size_mb INT DEFAULT 0,
    rating NUMERIC(3,2) DEFAULT 0,
    total_downloads INT DEFAULT 0,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.model_catalog ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read model_catalog"
    ON public.model_catalog FOR SELECT
    USING (true);


-- 5) trigger لتحديث updated_at تلقائياً
CREATE OR REPLACE FUNCTION public.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'set_updated_users') THEN
        CREATE TRIGGER set_updated_users BEFORE UPDATE ON public.users
        FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'set_updated_user_addons') THEN
        CREATE TRIGGER set_updated_user_addons BEFORE UPDATE ON public.user_addons
        FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'set_updated_model_catalog') THEN
        CREATE TRIGGER set_updated_model_catalog BEFORE UPDATE ON public.model_catalog
        FOR EACH ROW EXECUTE FUNCTION public.update_timestamp();
    END IF;
END $$;
