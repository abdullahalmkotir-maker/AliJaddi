@echo off
cd /d "%~dp0"
chcp 65001 >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build_windows_release.ps1"
if errorlevel 1 exit /b 1
if not "%SKIP_PAUSE%"=="1" pause
