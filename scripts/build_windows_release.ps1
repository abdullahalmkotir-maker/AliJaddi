# AliJaddi Beta 0.2 - Windows release build (PyInstaller + PySide6) + zip
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "=========================================="
Write-Host " AliJaddi - Windows Build (Beta 0.2, PySide6)"
Write-Host "=========================================="

python -m pip install pyinstaller PySide6-Essentials python-dotenv httpx requests --quiet

Write-Host "[1/4] Cleaning..."
Remove-Item -Path (Join-Path $root "build") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $root "dist") -Recurse -Force -ErrorAction SilentlyContinue

$icon = Join-Path $root "icon.png"
if (Test-Path (Join-Path $root "assets\icon.ico")) {
    $icon = Join-Path $root "assets\icon.ico"
}

Write-Host "[2/4] PyInstaller..."
$pyi = @(
    "--name", "AliJaddi",
    "--windowed",
    "--onedir",
    "--icon", $icon,
    "--add-data", "icon.png;.",
    "--add-data", "addons;addons",
    "--add-data", "services;services",
    "--add-data", "ui;ui",
    "--add-data", "alijaddi;alijaddi",
    "--hidden-import", "alijaddi",
    "--hidden-import", "PySide6.QtWidgets",
    "--hidden-import", "PySide6.QtCore",
    "--hidden-import", "PySide6.QtGui",
    "--hidden-import", "services.auth_service",
    "--hidden-import", "services.addon_manager",
    "--hidden-import", "services.local_store",
    "--hidden-import", "ui.theme_qt",
    "--hidden-import", "ui.main_window",
    "--hidden-import", "ui.login_dialog",
    "--hidden-import", "ui.i18n",
    "--hidden-import", "ui.toast",
    "--hidden-import", "ui.download_dialog",
    "--noconfirm",
    (Join-Path $root "main_qt.py")
)
& pyinstaller @pyi
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit $LASTEXITCODE" }

$out = Join-Path $root "dist\AliJaddi"
if (-not (Test-Path $out)) { throw "dist\AliJaddi not found" }

Write-Host "[3/4] Copy assets..."
Copy-Item -Force (Join-Path $root "icon.png") $out
if (Test-Path (Join-Path $root "assets\icon.ico")) {
    Copy-Item -Force (Join-Path $root "assets\icon.ico") $out
}
Copy-Item -Force (Join-Path $root ".env.example") $out
Copy-Item -Recurse -Force (Join-Path $root "addons") (Join-Path $out "addons")

Write-Host "[4/4] Creating zip (pack_windows_zip.ps1)..."
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "pack_windows_zip.ps1")
if ($LASTEXITCODE -ne 0) { throw "pack_windows_zip.ps1 failed" }

Write-Host ""
Write-Host "=========================================="
Write-Host " BUILD COMPLETE"
Write-Host " Run: dist\AliJaddi\AliJaddi.exe"
Write-Host " Zip: AliJaddi-Beta-0.2-Windows.zip"
Write-Host "=========================================="
