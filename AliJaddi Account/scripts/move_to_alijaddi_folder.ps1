# نقل مشروع AliJaddiAccount إلى مجلد هذا المشروع: ...\AliJaddi\AliJaddi Account
# المسارات تُشتق من موقع السكربت (لا تعتمد على اسم مستخدم ثابت).
# شغّل PowerShell كمسؤول إن لزم. أغلق Cursor/VS Code من المجلد القديم قبل التشغيل.

$ErrorActionPreference = "Stop"

function Get-DesktopPath {
    $one = Join-Path $env:USERPROFILE "OneDrive\Desktop"
    if (Test-Path -LiteralPath $one) { return $one }
    return Join-Path $env:USERPROFILE "Desktop"
}

$desktop = Get-DesktopPath
$accountRoot = Split-Path $PSScriptRoot -Parent
$alijaddiRoot = Split-Path $accountRoot -Parent
$src = Join-Path $desktop "AliJaddiAccount"
$dest = Join-Path $alijaddiRoot "AliJaddi Account"

if (-not (Test-Path -LiteralPath $src)) {
    Write-Error "المصدر غير موجود: $src`nعدّل `$src في السكربت إن كان المجلد باسم آخر على سطح المكتب."
    exit 1
}

if (-not (Test-Path -LiteralPath $alijaddiRoot)) {
    New-Item -ItemType Directory -Path $alijaddiRoot -Force | Out-Null
}

if (Test-Path -LiteralPath $dest) {
    $n = @(Get-ChildItem -LiteralPath $dest -Force -ErrorAction SilentlyContinue).Count
    if ($n -eq 0) {
        Remove-Item -LiteralPath $dest -Force
    } else {
        Write-Error @"
الوجهة غير فارغة: $dest
انقل المحتويات يدوياً أو استخدم مجلداً فارغاً، أو شغّل نسخ الدمج أدناه بعد النسخ الاحتياطي.
"@
        exit 1
    }
}

Write-Host "محاولة نقل المجلد بالكامل (Move-Item)..."
try {
    Move-Item -LiteralPath $src -Destination $dest
    Write-Host "تم النقل بنجاح إلى:`n  $dest"
    Write-Host "افتح المشروع في Cursor من المسار الجديد."
    exit 0
} catch {
    Write-Warning "Move-Item فشل (غالباً المجلد مفتوح في محرر): $($_.Exception.Message)"
}

Write-Host "نسخ كامل بـ robocopy ثم احذف المصدر يدوياً بعد إغلاق المحرر..."
New-Item -ItemType Directory -Path $dest -Force | Out-Null
$null = & robocopy.exe $src $dest /E /COPY:DAT /R:2 /W:2
if ($LASTEXITCODE -ge 8) {
    Write-Error "فشل robocopy (رمز $LASTEXITCODE)"
    exit $LASTEXITCODE
}

Write-Host @"

تم النسخ إلى:
  $dest

الخطوات التالية:
  1) أغلق Cursor/Terminal من المجلد القديم.
  2) احذف المجلد القديم يدوياً إن رغبت: $src
  3) افتح المشروع من: $dest
"@
