@echo off
title AliJaddi Installer
cd /d "%~dp0"

where ISCC >nul 2>nul
if errorlevel 1 (
  echo Inno Setup Compiler ^(ISCC^) is not installed.
  echo Install Inno Setup, then run this file again to build AliJaddi_Setup.exe
  pause
  exit /b 1
)

ISCC "AliJaddi_Setup.iss"
if errorlevel 1 (
  echo Installer build failed.
) else (
  echo Installer built successfully in installer\
)
pause
