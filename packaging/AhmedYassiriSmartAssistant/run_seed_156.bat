@echo off
chcp 65001 >nul
cd /d "%~dp0"
python scripts\seed_156_patients.py %*
pause
