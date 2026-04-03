@echo off
chcp 65001 >nul 2>&1
echo ═══════════════════════════════════════════
echo   AliJaddi — Windows Build (Beta 0.1)
echo ═══════════════════════════════════════════
echo.

pip install pyinstaller PySide6-Essentials python-dotenv httpx requests --quiet

echo [1/3] Cleaning previous build...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo [2/3] Building executable with PyInstaller...
pyinstaller ^
    --name "AliJaddi" ^
    --windowed ^
    --onedir ^
    --icon "icon.png" ^
    --add-data "icon.png;." ^
    --add-data ".env;." ^
    --add-data "addons;addons" ^
    --add-data "services;services" ^
    --add-data "ui;ui" ^
    --hidden-import "PySide6.QtWidgets" ^
    --hidden-import "PySide6.QtCore" ^
    --hidden-import "PySide6.QtGui" ^
    --hidden-import "services.auth_service" ^
    --hidden-import "services.addon_manager" ^
    --hidden-import "services.local_store" ^
    --hidden-import "ui.theme_qt" ^
    --hidden-import "ui.main_window" ^
    --hidden-import "ui.login_dialog" ^
    --noconfirm ^
    main_qt.py

echo [3/3] Copying assets...
if exist "dist\AliJaddi" (
    copy /Y icon.png "dist\AliJaddi\" >nul 2>&1
    xcopy /E /I /Y addons "dist\AliJaddi\addons" >nul 2>&1
    echo.
    echo ═══════════════════════════════════════════
    echo   BUILD COMPLETE!
    echo   Output: dist\AliJaddi\AliJaddi.exe
    echo ═══════════════════════════════════════════
) else (
    echo BUILD FAILED — check errors above.
)
pause
