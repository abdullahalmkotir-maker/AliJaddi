@echo off

title AliJaddi — Build

chcp 65001 >nul 2>&1

echo.

echo ======================================================

echo   AliJaddi — Build (Windows / Qt)

echo ======================================================

echo.

echo   [1] Build for Windows (PyInstaller)

echo   [2] Run the app (development — main_qt.py)

echo.



set /p choice="  Choose [1-2]: "



cd /d "%~dp0"



if "%choice%"=="1" (

    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0AliJaddi_Build.ps1" -Platform windows

) else if "%choice%"=="2" (

    echo   Starting AliJaddi...

    python main_qt.py

) else (

    echo   Invalid choice.

)



pause

