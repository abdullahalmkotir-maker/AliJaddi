$tokenData = Get-Content "$env:TEMP\supabase_dashboard_token.json" -Raw | ConvertFrom-Json
$token = $tokenData.access_token
$ref = "mfhtnfxdfpelrgzonxov"
$url = "https://api.supabase.com/v1/projects/$ref/database/query"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
    "User-Agent"    = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    "Origin"        = "https://supabase.com"
    "Referer"       = "https://supabase.com/"
}
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12 -bor [System.Net.SecurityProtocolType]::Tls13

function Run-SQL($sql, $label) {
    $body = @{ query = $sql } | ConvertTo-Json -Compress
    try {
        $r = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -ContentType "application/json" -ErrorAction Stop
        Write-Host "  OK  : $label" -ForegroundColor Green
        return $true
    } catch {
        $sc = $_.Exception.Response.StatusCode.value__
        Write-Host "  FAIL: $label (HTTP $sc)" -ForegroundColor Red
        return $false
    }
}

Write-Host "=== Creating tables ===" -ForegroundColor Cyan

Run-SQL @"
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    stars_balance INT DEFAULT 0,
    display_name TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
)
"@ "users table"

Run-SQL @"
CREATE TABLE IF NOT EXISTS public.addon_registry (
    id TEXT PRIMARY KEY DEFAULT 'main',
    data JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
)
"@ "addon_registry table"

Run-SQL @"
CREATE TABLE IF NOT EXISTS public.user_addons (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    installed JSONB NOT NULL DEFAULT '{}',
    favorites JSONB NOT NULL DEFAULT '[]',
    settings JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
)
"@ "user_addons table"

Run-SQL @"
CREATE TABLE IF NOT EXISTS public.model_catalog (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    version TEXT DEFAULT '1.0.0',
    download_url TEXT DEFAULT '',
    size_mb INT DEFAULT 0,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
)
"@ "model_catalog table"

Write-Host "`n=== Enabling RLS ===" -ForegroundColor Cyan
@("users", "addon_registry", "user_addons", "model_catalog") | ForEach-Object {
    Run-SQL "ALTER TABLE public.$_ ENABLE ROW LEVEL SECURITY" "RLS on $_"
}

Write-Host "`n=== Creating policies ===" -ForegroundColor Cyan
$policies = @(
    @{ name="rls_users_s"; tbl="users"; op="SELECT"; clause="USING (auth.uid() = id)" },
    @{ name="rls_users_u"; tbl="users"; op="UPDATE"; clause="USING (auth.uid() = id)" },
    @{ name="rls_users_i"; tbl="users"; op="INSERT"; clause="WITH CHECK (auth.uid() = id)" },
    @{ name="rls_reg_s"; tbl="addon_registry"; op="SELECT"; clause="USING (true)" },
    @{ name="rls_ua_s"; tbl="user_addons"; op="SELECT"; clause="USING (auth.uid() = user_id)" },
    @{ name="rls_ua_i"; tbl="user_addons"; op="INSERT"; clause="WITH CHECK (auth.uid() = user_id)" },
    @{ name="rls_ua_u"; tbl="user_addons"; op="UPDATE"; clause="USING (auth.uid() = user_id)" },
    @{ name="rls_mc_s"; tbl="model_catalog"; op="SELECT"; clause="USING (true)" }
)

foreach ($p in $policies) {
    $sql = "DO `$`$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = '$($p.name)') THEN CREATE POLICY `"$($p.name)`" ON public.$($p.tbl) FOR $($p.op) $($p.clause); END IF; END `$`$"
    Run-SQL $sql "Policy $($p.name)"
}

Write-Host "`n=== Creating trigger ===" -ForegroundColor Cyan
Run-SQL @"
CREATE OR REPLACE FUNCTION public.update_timestamp()
RETURNS TRIGGER AS `$`$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
`$`$ LANGUAGE plpgsql
"@ "update_timestamp function"

@("users", "addon_registry", "user_addons", "model_catalog") | ForEach-Object {
    $sql = "DO `$`$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_${_}_ts') THEN CREATE TRIGGER trg_${_}_ts BEFORE UPDATE ON public.$_ FOR EACH ROW EXECUTE FUNCTION public.update_timestamp(); END IF; END `$`$"
    Run-SQL $sql "Trigger on $_"
}

Write-Host "`n=== Verifying ===" -ForegroundColor Cyan
$body = @{ query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('users', 'addon_registry', 'user_addons', 'model_catalog') ORDER BY table_name" } | ConvertTo-Json -Compress
try {
    $r = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body -ContentType "application/json" -ErrorAction Stop
    Write-Host "Tables found:" -ForegroundColor Green
    $r | ForEach-Object { Write-Host "  - $($_.table_name)" -ForegroundColor White }
} catch {
    Write-Host "Verification failed" -ForegroundColor Red
}

Write-Host "`nDone!" -ForegroundColor Cyan
