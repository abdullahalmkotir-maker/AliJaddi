#!/bin/bash
# AliJaddi — Android Build (Beta 0.1)
# Uses pyside6-android-deploy (requires Qt 6.6+ and Android SDK/NDK)
#
# Prerequisites:
#   1. Install Android SDK + NDK (via Android Studio or standalone)
#   2. Set ANDROID_SDK_ROOT and ANDROID_NDK_ROOT environment variables
#   3. pip install PySide6 (full, not Essentials)
#   4. Run this script from the project root
#
# For more info: https://doc.qt.io/qtforpython-6/android.html

set -e
echo "═══════════════════════════════════════════"
echo "  AliJaddi — Android Build (Beta 0.1)"
echo "═══════════════════════════════════════════"

if ! command -v pyside6-android-deploy &>/dev/null; then
    echo "ERROR: pyside6-android-deploy not found."
    echo "Install the full PySide6 package: pip install PySide6"
    echo "And ensure Android SDK/NDK are configured."
    exit 1
fi

echo "[1/2] Generating Android project..."
pyside6-android-deploy \
    --input-file main_qt.py \
    --name "AliJaddi" \
    --wheel-pyside="" \
    --wheel-shiboken="" \
    --extra-modules=QtWidgets,QtCore,QtGui \
    --android-abis arm64-v8a

echo "[2/2] Building APK..."
echo "  The APK will be generated in the android-build/ directory."
echo ""
echo "═══════════════════════════════════════════"
echo "  Android build complete!"
echo "  Check android-build/ for the APK"
echo "═══════════════════════════════════════════"
