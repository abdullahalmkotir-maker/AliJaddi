# نسخ مشروع «عقد» (Euqid) إلى هذا المجلد ثم مزامنة مسارات AliJaddi.
# تشغيل: انقر بالزر الأيمن → Run with PowerShell، أو:
#   powershell -ExecutionPolicy Bypass -File "_move_euqid_here.ps1"

$ErrorActionPreference = "Stop"
$Dest = $PSScriptRoot

function Get-DesktopPath {
    $one = Join-Path $env:USERPROFILE "OneDrive\Desktop"
    if (Test-Path -LiteralPath $one) { return $one }
    return Join-Path $env:USERPROFILE "Desktop"
}

$desk = Get-DesktopPath
$candidates = @(
    (Join-Path $desk "تطبيقات علي جدي\Euqid"),
    (Join-Path $desk "Euqid"),
    (Join-Path $env:USERPROFILE "OneDrive\Desktop\تطبيقات علي جدي\Euqid"),
    (Join-Path $env:USERPROFILE "OneDrive\Desktop\Euqid"),
    (Join-Path $env:USERPROFILE "Desktop\Euqid")
)
$Source = $null
foreach ($c in $candidates) {
    if (Test-Path -LiteralPath $c) { $Source = $c; break }
}
if (-not $Source) {
    Write-Host "لم يُعثر على المصدر. عدّل قائمة `$candidates أو `$Source في السكربت."
    exit 1
}

$excludeDirs = @("__pycache__", ".pytest_cache", ".mypy_cache", "dist", "build")
Get-ChildItem -LiteralPath $Source -Force | ForEach-Object {
    $name = $_.Name
    if ($excludeDirs -contains $name) { return }
    if ($name -eq "_move_euqid_here.ps1") { return }
    $target = Join-Path $Dest $name
    if ($_.PSIsContainer) {
        robocopy $_.FullName $target /E /XD __pycache__ .pytest_cache .mypy_cache /XF *.pyc /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
    } else {
        Copy-Item -LiteralPath $_.FullName -Destination $target -Force
    }
}

$alijaddiRoot = Split-Path (Split-Path $Dest -Parent) -Parent
$sync = Join-Path $alijaddiRoot "sync_euqid_folder_path.ps1"
if (Test-Path -LiteralPath $sync) {
    & $sync
}

Write-Host "تم النسخ من: $Source"
Write-Host "إلى: $Dest"
Write-Host "إن أردت حذف المجلد القديم بعد المراجعة، احذفه يدوياً."
