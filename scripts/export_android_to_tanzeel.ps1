# ينسخ APK (أو AAB) إلى تنزيل\android\ ليكون جاهزاً للرفع مع أصول التوزيع.
param(
    [Parameter(Mandatory = $true)]
    [string] $ApkPath,
    [string] $DestName = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$destDir = Join-Path $root "تنزيل\android"
if (-not (Test-Path -LiteralPath $ApkPath)) {
    Write-Error "ApkPath not found: $ApkPath"
}
New-Item -ItemType Directory -Force -Path $destDir | Out-Null
$name = if ($DestName) { $DestName } else { Split-Path -Leaf $ApkPath }
$out = Join-Path $destDir $name
Copy-Item -LiteralPath $ApkPath -Destination $out -Force
Write-Host "Copied to: $out"
