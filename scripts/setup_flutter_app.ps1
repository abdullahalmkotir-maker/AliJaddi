# يولّد مجلدات android / ios / web لمشروع Flutter الموجود تحت flutter_alijaddi
# يتطلب Flutter SDK: https://docs.flutter.dev/get-started/install/windows
$ErrorActionPreference = "Stop"
$flutterDir = Join-Path (Split-Path -Parent $PSScriptRoot) "flutter_alijaddi"
if (-not (Test-Path (Join-Path $flutterDir "pubspec.yaml"))) {
    Write-Error "Missing flutter_alijaddi/pubspec.yaml"
}
$fc = Get-Command flutter -ErrorAction SilentlyContinue
if (-not $fc) {
    Write-Host "Flutter غير موجود في PATH. ثبّت Flutter ثم أعد التشغيل."
    exit 1
}
Set-Location $flutterDir
flutter create . --project-name alijaddi_flutter --org app.alijaddi --platforms=android,ios,web
flutter pub get
Write-Host "OK: يمكنك التشغيل من flutter_alijaddi: flutter run"
