# Ali12 — تثبيت أدوات التدريب والتصدير بعد الموافقة
# التشغيل: powershell -ExecutionPolicy Bypass -File Install-Ali12.ps1

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Windows.Forms

$msg = @"
Ali12 سيثبّت الحزمة في:
  $env:LOCALAPPDATA\Ali12

سيتم نسخ الملفات، إنشاء بيئة Python، تثبيت المتطلبات، واختصار على سطح المكتب.

هل توافق على المتابعة؟
"@

$r = [System.Windows.Forms.MessageBox]::Show(
    $msg,
    "Ali12 — التثبيت",
    [System.Windows.Forms.MessageBoxButtons]::YesNo,
    [System.Windows.Forms.MessageBoxIcon]::Question
)
if ($r -ne [System.Windows.Forms.DialogResult]::Yes) { exit 0 }

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    [System.Windows.Forms.MessageBox]::Show("لم يُعثر على Python في PATH.", "Ali12", "OK", "Error")
    exit 1
}

& $py.Source "$here\run_ali12.py" install
if ($LASTEXITCODE -ne 0) {
    [System.Windows.Forms.MessageBox]::Show("فشل التثبيت. راجع مخرجات الطرفية.", "Ali12", "OK", "Error")
    exit 1
}

[System.Windows.Forms.MessageBox]::Show(
    "اكتمل التثبيت. يمكنك تشغيل «Ali12 — أدوات التدريب» من اختصار سطح المكتب.",
    "Ali12",
    "OK",
    "Information"
)
