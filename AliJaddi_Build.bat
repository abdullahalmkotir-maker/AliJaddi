@echo off
title AliJaddi — Build
echo.
echo ======================================================
echo   AliJaddi — Build System
echo ======================================================
echo.
echo   [1] Build for Windows
echo   [2] Build for Android (APK)
echo   [3] Build for iOS (IPA) - requires macOS
echo   [4] Build ALL
echo   [5] Run the app (development)
echo.

set /p choice="  Choose [1-5]: "

cd /d "%~dp0"

if "%choice%"=="1" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0AliJaddi_Build.ps1" -Platform windows
) else if "%choice%"=="2" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0AliJaddi_Build.ps1" -Platform android
) else if "%choice%"=="3" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0AliJaddi_Build.ps1" -Platform ios
) else if "%choice%"=="4" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0AliJaddi_Build.ps1" -Platform all
) else if "%choice%"=="5" (
    echo   Starting AliJaddi...
    python main.py
) else (
    echo   Invalid choice.
)

pause
