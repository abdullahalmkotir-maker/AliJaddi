# ═══ AliJaddi — Push to GitHub ═══
# يُشغَّل من PowerShell بعد تثبيت Git
# Usage: .\scripts\push_to_github.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path "$root\.gitignore")) { $root = $PSScriptRoot | Split-Path -Parent }

Set-Location $root
Write-Host "=== AliJaddi — Git Setup ===" -ForegroundColor Cyan

# 1) Init
if (-not (Test-Path ".git")) {
    & git init
    Write-Host "Git initialized." -ForegroundColor Green
}

# 2) Add remote
$remoteUrl = "https://github.com/abdullahalmkotir-maker/AliJaddi.git"
$existing = & git remote -v 2>&1
if ($existing -notmatch "origin") {
    & git remote add origin $remoteUrl
    Write-Host "Remote 'origin' added." -ForegroundColor Green
} else {
    Write-Host "Remote 'origin' already exists." -ForegroundColor Yellow
}

# 3) Add all files
& git add -A
Write-Host "All files staged." -ForegroundColor Green

# 4) Commit
& git commit -m "release: AliJaddi v0.2.0-beta — platform + registry alignment

- Unified version across Qt/Flet, pyproject, and addon min_platform
- Beta 0.2 manifests: Mudir, Sniper Perspective; registry platform field
- Profile/about screens read alijaddi.__version__ (no hardcoded drift)"

Write-Host "Committed." -ForegroundColor Green

# 5) Push
& git branch -M main
& git push -u origin main
Write-Host "=== Pushed to GitHub ===" -ForegroundColor Cyan
