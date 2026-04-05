-- AliJaddi Cloud — مخطط Supabase فقط (لا تخزين لمستخدمي التطبيق على القرص هنا).
-- متوافق مع auth_model/cloud_client.py في Account / Store.
-- مشروع: https://nzevwjghbvrrmmshnvem.supabase.co — نفّذ من SQL Editor.

-- ملف تعريف المستخدم + رصيد النجوم (معرّف = auth.users.id)
create table if not exists public.users (
  id uuid primary key references auth.users (id) on delete cascade,
  stars_balance integer not null default 0,
  updated_at timestamptz not null default now()
);

create table if not exists public.model_catalog (
  model_id text primary key,
  display_name_ar text,
  description text
);

create table if not exists public.user_models (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  model_name text not null,
  extra jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (user_id, model_name)
);

create table if not exists public.model_user_data (
  user_id uuid not null references auth.users (id) on delete cascade,
  model_id text not null,
  payload jsonb not null default '{}'::jsonb,
  schema_version integer not null default 1,
  client_updated_at timestamptz,
  primary key (user_id, model_id)
);

-- RLS
alter table public.users enable row level security;
alter table public.model_catalog enable row level security;
alter table public.user_models enable row level security;
alter table public.model_user_data enable row level security;

-- سياسات: المستخدم يصل لبياناته فقط
drop policy if exists "users_select_own" on public.users;
drop policy if exists "users_update_own" on public.users;
create policy "users_select_own" on public.users
  for select using (auth.uid() = id);
create policy "users_update_own" on public.users
  for update using (auth.uid() = id);

drop policy if exists "model_catalog_read_auth" on public.model_catalog;
create policy "model_catalog_read_auth" on public.model_catalog
  for select to authenticated using (true);

drop policy if exists "user_models_own" on public.user_models;
create policy "user_models_own" on public.user_models
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "model_user_data_own" on public.model_user_data;
create policy "model_user_data_own" on public.model_user_data
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- إدراج صف في users عند تسجيل مستخدم (اختياري — يعتمد على إعداداتك)
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.users (id, stars_balance)
  values (new.id, 0)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- بذور أولية (المجموعة الكاملة في 002_seed_model_catalog.sql)
