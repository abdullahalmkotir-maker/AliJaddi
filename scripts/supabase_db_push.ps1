#Requires -Version 5.1
<#
.SYNOPSIS
  يطبّق هجرات Supabase على المشروع المرتبط (db push)، أو يوجّهك لملف SQL اليدوي.

.DESCRIPTION
  يبحث عن supabase في PATH ثم في مسارات شائعة. إن وُجد: ينفّذ من جذر المستودع (مجلد يحوي supabase/).
  إن لم يُوجد: يعرض مسار remote_apply_radt_removal_and_grants.sql للصقه في SQL Editor.
#>
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Find-SupabaseExe {
    $cmd = Get-Command supabase -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $candidates = @(
        "$env:USERPROFILE\scoop\shims\supabase.exe",
        "$env:LOCALAPPDATA\supabase-cli\supabase.exe",
        "$env:ProgramFiles\Supabase\supabase.exe"
    )
    foreach ($p in $candidates) {
        if (Test-Path -LiteralPath $p) { return $p }
    }
    return $null
}

$exe = Find-SupabaseExe
if ($exe) {
    Write-Host "Using: $exe"
    & $exe db push @args
    exit $LASTEXITCODE
}

Write-Host "Supabase CLI not in PATH (install from https://supabase.com/docs/guides/cli )" -ForegroundColor Yellow
$sql = Join-Path $repoRoot "supabase\remote_apply_radt_removal_and_grants.sql"
Write-Host "Paste this file in Supabase Dashboard > SQL Editor:" -ForegroundColor Cyan
Write-Host $sql
if (Test-Path -LiteralPath $sql) {
    Get-Content -LiteralPath $sql -Raw | Set-Clipboard
    Write-Host "Copied SQL to clipboard." -ForegroundColor Green
}
exit 1
