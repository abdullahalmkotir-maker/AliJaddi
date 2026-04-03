#!/bin/bash
# AliJaddi — macOS Build (Beta 0.2, PySide6)
set -e
echo "═══════════════════════════════════════════"
echo "  AliJaddi — macOS Build (Beta 0.2, PySide6)"
echo "═══════════════════════════════════════════"

pip3 install pyinstaller PySide6-Essentials python-dotenv httpx requests --quiet

echo "[1/3] Cleaning previous build..."
rm -rf build dist

echo "[2/3] Building .app bundle..."
pyinstaller \
    --name "AliJaddi" \
    --windowed \
    --onedir \
    --icon "icon.png" \
    --add-data "icon.png:." \
    --add-data "addons:addons" \
    --add-data "services:services" \
    --add-data "ui:ui" \
    --add-data "alijaddi:alijaddi" \
    --hidden-import "PySide6.QtWidgets" \
    --hidden-import "PySide6.QtCore" \
    --hidden-import "PySide6.QtGui" \
    --hidden-import "services.auth_service" \
    --hidden-import "services.addon_manager" \
    --hidden-import "services.local_store" \
    --hidden-import "ui.theme_qt" \
    --hidden-import "ui.main_window" \
    --hidden-import "ui.login_dialog" \
    --hidden-import "ui.i18n" \
    --hidden-import "ui.toast" \
    --hidden-import "ui.download_dialog" \
    --hidden-import "alijaddi" \
    --noconfirm \
    main_qt.py

echo "[3/3] Copying assets..."
cp -f icon.png dist/AliJaddi/ 2>/dev/null || true
cp -f .env.example dist/AliJaddi/ 2>/dev/null || true
cp -r addons dist/AliJaddi/ 2>/dev/null || true

echo ""
echo "═══════════════════════════════════════════"
echo "  BUILD COMPLETE!"
echo "  Output: dist/AliJaddi/AliJaddi"
echo "═══════════════════════════════════════════"
