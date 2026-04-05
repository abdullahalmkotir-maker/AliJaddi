# متجر علي جدّي — تثبيت بيتا (نمط Ali12 / Store12)
# التشغيل بعد فك الضغط: powershell -ExecutionPolicy Bypass -File Install-StoreAliJaddi.ps1

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Windows.Forms

$msg = @"
متجر علي جدّي (بيتا 0.1) سيُثبَّت في:
  $env:LOCALAPPDATA\AliJaddiStore

سيتم نسخ الملفات، إنشاء بيئة Python، تثبيت المتطلبات، واختصار على سطح المكتب.

هل توافق على المتابعة？
"@

$r = [System.Windows.Forms.MessageBox]::Show(
    $msg,
    "متجر علي جدّي — التثبيت",
    [System.Windows.Forms.MessageBoxButtons]::YesNo,
    [System.Windows.Forms.MessageBoxIcon]::Question
)
if ($r -ne [System.Windows.Forms.DialogResult]::Yes) { exit 0 }

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    [System.Windows.Forms.MessageBox]::Show("لم يُعثر على Python في PATH.", "متجر علي جدّي", "OK", "Error")
    exit 1
}

& $py.Source "$here\run_store12.py" install --source $here
if ($LASTEXITCODE -ne 0) {
    [System.Windows.Forms.MessageBox]::Show("فشل التثبيت. راجع مخرجات الطرفية.", "متجر علي جدّي", "OK", "Error")
    exit 1
}

[System.Windows.Forms.MessageBox]::Show(
    "اكتمل التثبيت. شغّل «متجر علي جدّي — بيتا» من سطح المكتب.",
    "متجر علي جدّي",
    "OK",
    "Information"
)
