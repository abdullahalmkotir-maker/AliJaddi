<#
.SYNOPSIS
    AliJaddi — بناء سطح المكتب (PySide6 + PyInstaller فقط).
.DESCRIPTION
    مسار Flet/Android/iOS أزيل من المستودع؛ استخدم scripts/build_windows_release.ps1 مباشرة إن رغبت.
.PARAMETER Platform
    windows | all — كلاهما يبني نسخة Qt لـ Windows
.EXAMPLE
    .\AliJaddi_Build.ps1 -Platform windows
#>
param(
    [ValidateSet("windows", "all")]
    [string]$Platform = "windows"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  AliJaddi — Windows build (Qt / PyInstaller)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

$script = Join-Path $ProjectRoot "scripts\build_windows_release.ps1"
& powershell -NoProfile -ExecutionPolicy Bypass -File $script
exit $LASTEXITCODE
