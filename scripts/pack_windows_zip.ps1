# ZIP محمول مكمّل — المعيار الرسمي للمستخدمين هو AliJaddi-Beta-…-Setup.exe (Inno، أسلوب Blender).
# Packs dist\AliJaddi → تنزيل\windows\AliJaddi-Beta-0.4.0-Windows.zip + unpacked copy
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $root "main_qt.py"))) {
    Write-Host "pack_windows_zip: main_qt.py not found under $root"
    exit 1
}
$dist = Join-Path (Join-Path $root "dist") "AliJaddi"
# Arabic folder name without non-ASCII in script source (encoding-safe)
$tanzeel = "$([char]0x062A)$([char]0x0646)$([char]0x0632)$([char]0x064A)$([char]0x0644)"
$outDir = Join-Path (Join-Path $root $tanzeel) "windows"
$releaseName = "AliJaddi-Beta-0.4.0-Windows"
$zip = Join-Path $outDir "$releaseName.zip"
$unpackRoot = Join-Path $outDir $releaseName
$unpackApp = Join-Path $unpackRoot "AliJaddi"

if (-not (Test-Path $dist)) {
    Write-Host "pack_windows_zip: dist\AliJaddi not found - run build first."
    exit 1
}
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
if (Test-Path $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -LiteralPath $dist -DestinationPath $zip -CompressionLevel Optimal -Force
Write-Host "Created: $zip"

if (Test-Path $unpackRoot) { Remove-Item -LiteralPath $unpackRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path $unpackRoot | Out-Null
Copy-Item -Recurse -Force $dist $unpackApp
Write-Host "Exported folder: $unpackApp"
