# المعيار الرسمي لتوزيع منصّة علي جدّي على Windows: مثبّت Inno (مثل Blender)
# — Program Files، قائمة ابدأ، إزالة من «التطبيقات»/«البرامج والميزات».
# يبني ‎AliJaddi-Beta-…-Setup.exe‎ من ‎dist\AliJaddi‎ وينسخه إلى ‎تنزيل\windows‎.
# تجاوز البناء بدون مثبّت (مطوّرون فقط): ‎$env:ALIJADDI_SKIP_INNO = "1"
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $root "dist\AliJaddi"
$iss = Join-Path $root "AliJaddi_Setup.iss"
$setupName = "AliJaddi-Beta-0.5.1-Setup.exe"
$built = Join-Path $root "installer\$setupName"

if (-not (Test-Path $dist)) {
    Write-Host "build_inno_installer: dist\AliJaddi not found."
    exit 1
}
if (-not (Test-Path $iss)) {
    Write-Host "build_inno_installer: AliJaddi_Setup.iss not found."
    exit 1
}

$candidates = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "${env:LOCALAPPDATA}\Programs\Inno Setup 6\ISCC.exe",
    "${env:LocalAppData}\Programs\Inno Setup 6\ISCC.exe"
)
$iscc = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $iscc) {
    if ($env:ALIJADDI_SKIP_INNO -eq "1") {
        Write-Host "[warn] ALIJADDI_SKIP_INNO=1 - skipping official installer (ZIP-only; not the primary distribution channel)."
        exit 0
    }
    Write-Host ""
    Write-Host "FAILED: Inno Setup 6 is required for the official Windows installer (Blender-style)."
    Write-Host "  Install: https://jrsoftware.org/isdl.php"
    Write-Host "  Or: winget install JRSoftware.InnoSetup"
    Write-Host "  Developers may set: `$env:ALIJADDI_SKIP_INNO='1'  (zip-only build)"
    Write-Host ""
    exit 1
}

New-Item -ItemType Directory -Force -Path (Join-Path $root "installer") | Out-Null
if (Test-Path $built) { Remove-Item -LiteralPath $built -Force }

Write-Host "[Inno] $iscc $iss"
& $iscc $iss
if ($LASTEXITCODE -ne 0) { throw "ISCC failed with exit $LASTEXITCODE" }
if (-not (Test-Path $built)) { throw "Expected installer not found: $built" }

$tanzeel = "$([char]0x062A)$([char]0x0646)$([char]0x0632)$([char]0x064A)$([char]0x0644)"
$outDir = Join-Path (Join-Path $root $tanzeel) "windows"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$dest = Join-Path $outDir $setupName
Copy-Item -Force $built $dest
Write-Host "Installer: $dest"
