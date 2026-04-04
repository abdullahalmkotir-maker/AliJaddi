#Requires -Version 5.1
<#
  يطبّق على قاعدة Supabase: إزالة radt + توحيد الصلاحيات (ملف supabase/remote_apply_radt_removal_and_grants.sql).

  الترتيب:
  1) supabase db push — إن وُجد Supabase CLI والمشروع مرتبط (supabase link).
  2) psql + DATABASE_URL — إن وُجد في .env (انسخه من لوحة Supabase: Project Settings → Database → URI).
     يُقبل أيضاً SUPABASE_DB_URL كاسم بديل. يُدعم export وعلامات اقتباس مفردة/مزدوجة.
  3) نسخ SQL إلى الحافظة + طباعة المسار — للصق يدوياً في SQL Editor.

  تشغيل من جذر المستودع:
    powershell -ExecutionPolicy Bypass -File scripts\apply_cloud_migrations.ps1
#>
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$sqlFile = Join-Path $repoRoot "supabase\remote_apply_radt_removal_and_grants.sql"
if (-not (Test-Path -LiteralPath $sqlFile)) {
    Write-Error "Missing file: $sqlFile"
}

$envFile = Join-Path $repoRoot ".env"
if (Test-Path -LiteralPath $envFile) {
    Get-Content $envFile -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) { return }
        $i = $line.IndexOf("=")
        if ($i -lt 1) { return }
        $k = $line.Substring(0, $i).Trim()
        if ($k.StartsWith("export ")) { $k = $k.Substring(7).Trim() }
        $v = $line.Substring($i + 1).Trim()
        if ($v.Length -ge 2 -and $v.StartsWith('"') -and $v.EndsWith('"')) {
            $v = $v.Substring(1, $v.Length - 2)
        }
        if ($v.Length -ge 2 -and $v.StartsWith("'") -and $v.EndsWith("'")) {
            $v = $v.Substring(1, $v.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($k, $v, "Process")
    }
}

if (-not $env:DATABASE_URL -and $env:SUPABASE_DB_URL) {
    [Environment]::SetEnvironmentVariable("DATABASE_URL", $env:SUPABASE_DB_URL, "Process")
}

function Find-SupabaseExe {
    $cmd = Get-Command supabase -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    foreach ($p in @(
            "$env:USERPROFILE\scoop\shims\supabase.exe",
            "$env:LOCALAPPDATA\supabase-cli\supabase.exe"
        )) {
        if (Test-Path -LiteralPath $p) { return $p }
    }
    return $null
}

function Find-PsqlExe {
    $cmd = Get-Command psql -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $pf86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
    $bases = @( (Join-Path $env:ProgramFiles "PostgreSQL") )
    if ($pf86) { $bases += (Join-Path $pf86 "PostgreSQL") }
    foreach ($base in $bases) {
        if (-not (Test-Path -LiteralPath $base)) { continue }
        $candidates = Get-ChildItem -LiteralPath $base -Directory -ErrorAction SilentlyContinue |
            ForEach-Object { Join-Path $_.FullName "bin\psql.exe" } |
            Where-Object { Test-Path -LiteralPath $_ }
        if ($candidates) { return $candidates | Select-Object -First 1 }
    }
    return $null
}

$supabase = Find-SupabaseExe
$psqlPathProbe = Find-PsqlExe

if ($supabase) {
    Write-Host "Running: supabase db push"
    & $supabase db push
    $pushCode = $LASTEXITCODE
    if ($pushCode -eq 0) { exit 0 }
    Write-Host "db push failed (exit $pushCode); trying psql if DATABASE_URL is set..." -ForegroundColor Yellow
}

if ($env:DATABASE_URL) {
    if (-not $psqlPathProbe) {
        Write-Host "DATABASE_URL is set but psql was not found (PATH or Program Files\PostgreSQL\*\bin)." -ForegroundColor Yellow
    }
    else {
        Write-Host "Running psql with remote_apply_radt_removal_and_grants.sql"
        & $psqlPathProbe $env:DATABASE_URL -v ON_ERROR_STOP=1 -f $sqlFile
        exit $LASTEXITCODE
    }
}

Get-Content -LiteralPath $sqlFile -Raw | Set-Clipboard
Write-Host ""
Write-Host "Could not run automatically (need Supabase CLI + link, or DATABASE_URL/SUPABASE_DB_URL + psql)." -ForegroundColor Yellow
Write-Host "SQL copied to clipboard. Open Dashboard > SQL Editor > paste > Run."
Write-Host "File: $sqlFile"
Write-Host "In .env set: DATABASE_URL=... or SUPABASE_DB_URL=... (Supabase Dashboard: Project Settings - Database - URI)"
exit 1
