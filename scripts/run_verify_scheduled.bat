@echo off
REM تشغيل التحقق بدون إبقاء نافذة cmd ظاهرة (مناسب للجدولة كل X دقائق)
REM للتشغيل التفاعلي مع نافذة: python scripts\verify_ecosystem.py --quick
REM لإزالة مهمة قديمة تفتح cmd كل 10 دقائق: scripts\manage_verify_task.ps1 -Action remove
setlocal
cd /d "%~dp0.."
powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0run_verify_scheduled.ps1"
exit /b %ERRORLEVEL%
