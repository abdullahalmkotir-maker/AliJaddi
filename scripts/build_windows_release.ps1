# AliJaddi Beta 0.5.2 — Windows release: PyInstaller + ZIP مكمّل + مثبّت Inno (المعيار الرسمي، أسلوب Blender)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "=========================================="
Write-Host " AliJaddi - Windows Build (Beta 0.5.2, PySide6)"
Write-Host "=========================================="

python -m pip install pyinstaller PySide6-Essentials python-dotenv httpx requests --quiet

Write-Host "[1/5] Cleaning..."
Remove-Item -Path (Join-Path $root "build") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path $root "dist") -Recurse -Force -ErrorAction SilentlyContinue

$icon = Join-Path $root "icon.png"
if (Test-Path (Join-Path $root "assets\icon.ico")) {
    $icon = Join-Path $root "assets\icon.ico"
}

Write-Host "[2/5] PyInstaller..."
$pyi = @(
    "--name", "AliJaddi",
    "--windowed",
    "--onedir",
    "--icon", $icon,
    "--add-data", "icon.png;.",
    "--add-data", "assets/branding;assets/branding",
    "--add-data", "addons;addons",
    "--add-data", "services;services",
    "--add-data", "ui;ui",
    "--add-data", "alijaddi;alijaddi",
    "--add-data", "Ali12.py;.",
    "--add-data", "12;12",
    "--add-data", "Hassan12.py;.",
    "--add-data", "Hussein12.py;.",
    "--hidden-import", "alijaddi",
    "--hidden-import", "alijaddi.visual_identity",
    "--hidden-import", "alijaddi.qt_host_bridge",
    "--hidden-import", "PySide6.QtWidgets",
    "--hidden-import", "PySide6.QtCore",
    "--hidden-import", "PySide6.QtGui",
    "--hidden-import", "services.auth_service",
    "--hidden-import", "services.addon_manager",
    "--hidden-import", "services.local_store",
    "--hidden-import", "services.paths",
    "--hidden-import", "services.model_catalog",
    "--hidden-import", "services.platform_data",
    "--hidden-import", "services.platform_update",
    "--hidden-import", "services.shell_launch",
    "--hidden-import", "ui.theme_qt",
    "--hidden-import", "ui.main_window",
    "--hidden-import", "ui.login_dialog",
    "--hidden-import", "ui.i18n",
    "--hidden-import", "ui.toast",
    "--hidden-import", "ui.download_dialog",
    "--hidden-import", "dotenv",
    "--hidden-import", "httpx",
    "--hidden-import", "Ali12",
    "--hidden-import", "Hassan12",
    "--hidden-import", "Hussein12",
    "--hidden-import", "services.assistants_squad",
    "--hidden-import", "services.platform_sync",
    "--hidden-import", "services.squad12_paths",
    "--noconfirm",
    (Join-Path $root "main_qt.py")
)
$envFile = Join-Path $root ".env"
if (Test-Path $envFile) {
    $pyi = $pyi + @("--add-data", ".env;.")
}
& pyinstaller @pyi
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit $LASTEXITCODE" }

$out = Join-Path $root "dist\AliJaddi"
if (-not (Test-Path $out)) { throw "dist\AliJaddi not found" }

Write-Host "[3/5] Copy assets..."
Copy-Item -Force (Join-Path $root "icon.png") $out
if (Test-Path (Join-Path $root "assets\icon.ico")) {
    Copy-Item -Force (Join-Path $root "assets\icon.ico") $out
}
Copy-Item -Force (Join-Path $root ".env.example") $out
Copy-Item -Recurse -Force (Join-Path $root "addons") (Join-Path $out "addons")

Write-Host "[4/5] Creating zip (pack_windows_zip.ps1)..."
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "pack_windows_zip.ps1")
if ($LASTEXITCODE -ne 0) { throw "pack_windows_zip.ps1 failed" }

Write-Host "[5/5] Official Windows installer (Inno Setup - required unless ALIJADDI_SKIP_INNO=1)..."
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "build_inno_installer.ps1")
if ($LASTEXITCODE -ne 0) { throw "build_inno_installer.ps1 failed - install Inno Setup 6 or set ALIJADDI_SKIP_INNO=1 for zip-only" }

Write-Host ""
Write-Host "=========================================="
Write-Host " BUILD COMPLETE"
$tanzeel = "$([char]0x062A)$([char]0x0646)$([char]0x0632)$([char]0x064A)$([char]0x0644)"
Write-Host (" PRIMARY (end users / Blender-style): {0}\windows\AliJaddi-Beta-0.5.2-Setup.exe" -f $tanzeel)
Write-Host (" Supplementary portable: {0}\windows\AliJaddi-Beta-0.5.2-Windows.zip" -f $tanzeel)
Write-Host " Dev run without install: dist\AliJaddi\AliJaddi.exe"
Write-Host "=========================================="
