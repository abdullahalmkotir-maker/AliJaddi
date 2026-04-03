<#
.SYNOPSIS
    AliJaddi — سكربت بناء موحّد (Windows / Android / iOS)
.DESCRIPTION
    يثبّت Flutter SDK تلقائياً إذا لم يكن موجوداً، ثم يبني التطبيق للمنصة المطلوبة.
.PARAMETER Platform
    windows | android | ios | all
.EXAMPLE
    .\AliJaddi_Build.ps1 -Platform windows
    .\AliJaddi_Build.ps1 -Platform android
    .\AliJaddi_Build.ps1 -Platform all
#>
param(
    [ValidateSet("windows","android","ios","all")]
    [string]$Platform = "windows"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  AliJaddi — Build System v0.2.0-beta" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# ─── 1. Check Python ───
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
$pyVer = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Python not found. Install Python 3.10+." -ForegroundColor Red
    exit 1
}
Write-Host "  OK: $pyVer" -ForegroundColor Green

# ─── 2. Install Flet ───
Write-Host "[2/6] Checking Flet..." -ForegroundColor Yellow
$fletVer = pip show flet 2>&1 | Select-String "Version"
if (-not $fletVer) {
    Write-Host "  Installing flet..." -ForegroundColor Yellow
    pip install flet --quiet
}
Write-Host "  OK: flet $($fletVer -replace 'Version: ','')" -ForegroundColor Green

# ─── 3. Check / Install Flutter ───
Write-Host "[3/6] Checking Flutter SDK..." -ForegroundColor Yellow
$flutterPath = $null

# Check if flutter is in PATH
try {
    $flutterCheck = flutter --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $flutterPath = (Get-Command flutter).Source
        Write-Host "  OK: Flutter found at $flutterPath" -ForegroundColor Green
    }
} catch {}

if (-not $flutterPath) {
    # Check common install locations
    $commonPaths = @(
        "$env:LOCALAPPDATA\flutter\bin\flutter.exe",
        "$env:USERPROFILE\flutter\bin\flutter.exe",
        "C:\flutter\bin\flutter.exe",
        "$env:ProgramFiles\flutter\bin\flutter.exe"
    )
    foreach ($p in $commonPaths) {
        if (Test-Path $p) {
            $flutterPath = $p
            $flutterDir = Split-Path -Parent (Split-Path -Parent $p)
            $env:PATH = "$flutterDir\bin;$env:PATH"
            Write-Host "  Found Flutter at: $flutterDir" -ForegroundColor Green
            break
        }
    }
}

if (-not $flutterPath) {
    Write-Host "  Flutter not found. Installing..." -ForegroundColor Yellow
    $flutterDir = "$env:LOCALAPPDATA\flutter"

    if (-not (Test-Path $flutterDir)) {
        Write-Host "  Downloading Flutter SDK (this may take 5-10 minutes)..." -ForegroundColor Yellow
        $zipUrl = "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.32.0-stable.zip"
        $zipPath = "$env:TEMP\flutter_sdk.zip"

        try {
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
            $wc = New-Object System.Net.WebClient
            $wc.DownloadFile($zipUrl, $zipPath)
            Write-Host "  Download complete. Extracting..." -ForegroundColor Yellow
            Expand-Archive -Path $zipPath -DestinationPath $env:LOCALAPPDATA -Force
            Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Host "  ERROR: Could not download Flutter." -ForegroundColor Red
            Write-Host "  Please install Flutter manually from: https://flutter.dev/docs/get-started/install" -ForegroundColor Yellow
            Write-Host "  Then re-run this script." -ForegroundColor Yellow
            exit 1
        }
    }

    $env:PATH = "$flutterDir\bin;$env:PATH"
    Write-Host "  Flutter installed at: $flutterDir" -ForegroundColor Green

    # Add to user PATH permanently
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($userPath -notlike "*flutter\bin*") {
        [Environment]::SetEnvironmentVariable("PATH", "$flutterDir\bin;$userPath", "User")
        Write-Host "  Added Flutter to user PATH" -ForegroundColor Green
    }
}

# ─── 4. Flutter doctor (quick) ───
Write-Host "[4/6] Running Flutter doctor..." -ForegroundColor Yellow
flutter doctor --verbose 2>&1 | Select-String "Flutter|Android|Windows|Xcode" | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

# ─── 5. Create Windows icon if missing ───
Write-Host "[5/6] Preparing Windows icon..." -ForegroundColor Yellow
$iconIco = Join-Path $ProjectRoot "assets\icon.ico"
$iconPng = Join-Path $ProjectRoot "assets\icon.png"
if (-not (Test-Path $iconIco) -and (Test-Path $iconPng)) {
    python -c "from PIL import Image; img=Image.open(r'$iconPng'); img.save(r'$iconIco', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"
    Write-Host "  Created icon.ico from icon.png" -ForegroundColor Green
}

# ─── 6. Build ───
Write-Host "[6/6] Building AliJaddi..." -ForegroundColor Yellow
Write-Host ""

Set-Location $ProjectRoot

function Build-Platform($plat) {
    $cmd = switch ($plat) {
        "windows" { "flet pack `"main.py`" -n `"AliJaddi`" -i `"assets/icon.ico`" --distpath `"dist`" --add-data `"assets:assets`" --product-name `"AliJaddi`" --file-description `"AliJaddi Desktop App`" --product-version `"0.2.0`" --file-version `"0.2.0.0`" --company-name `"AliJaddi`" -y" }
        "android" { "flet build apk --product AliJaddi --org com.alijaddi --project AliJaddi --description `"منصة نماذج الذكاء الاصطناعي`"" }
        "ios"     { "flet build ipa --product AliJaddi --org com.alijaddi --project AliJaddi --description `"منصة نماذج الذكاء الاصطناعي`"" }
    }

    Write-Host "  Building for $plat..." -ForegroundColor Cyan
    Write-Host "  > $cmd" -ForegroundColor Gray
    Invoke-Expression $cmd

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  SUCCESS: $plat build complete!" -ForegroundColor Green
    } else {
        Write-Host "  FAILED: $plat build failed." -ForegroundColor Red
    }
    Write-Host ""
}

if ($Platform -eq "all") {
    Build-Platform "windows"
    Build-Platform "android"
    Write-Host "  NOTE: iOS builds require macOS + Xcode." -ForegroundColor Yellow
} else {
    Build-Platform $Platform
}

# ─── Output ───
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Build output:" -ForegroundColor Cyan
if (Test-Path "$ProjectRoot\dist\AliJaddi.exe") {
    Write-Host "    Windows: $ProjectRoot\dist\AliJaddi.exe" -ForegroundColor Green
}
if (Test-Path "$ProjectRoot\build\apk") {
    Write-Host "    Android: $ProjectRoot\build\apk\" -ForegroundColor Green
}
if (Test-Path "$ProjectRoot\build\ipa") {
    Write-Host "    iOS:     $ProjectRoot\build\ipa\" -ForegroundColor Green
}
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
