@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

set "LOG=%USERPROFILE%\AliJaddi_verify.log"
>>"%LOG%" echo(
>>"%LOG%" echo ===== %date% %time% verify_ecosystem --quick =====

set "EXE=%LocalAppData%\Programs\Python\Python311\python.exe"
if not exist "%EXE%" set "EXE=%LocalAppData%\Programs\Python\Python312\python.exe"
if not exist "%EXE%" set "EXE=%LocalAppData%\Programs\Python\Python310\python.exe"

if exist "%EXE%" (
  "%EXE%" scripts\verify_ecosystem.py --quick >>"%LOG%" 2>&1
) else (
  where py >nul 2>&1
  if errorlevel 1 (
    >>"%LOG%" echo ERROR: Python not found. Edit scripts\run_verify_scheduled.bat
    exit /b 1
  )
  py -3 scripts\verify_ecosystem.py --quick >>"%LOG%" 2>&1
)

set "EC=%ERRORLEVEL%"
>>"%LOG%" echo exit_code=%EC%
exit /b %EC%
