<#!
  يبني dental_assistant.zip لرفعه على GitHub Releases (نفس tag مثل euqid: models-v1.0).
  المطوّر المعروض في المتجر: أحمد الياسري. الجذر داخل الأرشيف يبقى AhmadFalahDentalAssistant كما في manifest (توافق الرابط الثابت).

  مثال:
    powershell -ExecutionPolicy Bypass -File scripts\pack_dental_assistant.ps1 `
      -SourcePath "C:\path\to\Ahmed Al-Yassiri's Smart Assistant" `
      -OutDir "C:\temp"
#>
param(
    [Parameter(Mandatory = $false)]
    [string] $SourcePath = "",
    [Parameter(Mandatory = $false)]
    [string] $OutDir = ""
)

$ErrorActionPreference = "Stop"
$rootName = "AhmadFalahDentalAssistant"
$zipName = "dental_assistant.zip"

if (-not $SourcePath) {
    $SourcePath = Join-Path $env:USERPROFILE "OneDrive\Desktop\تطبيقات علي جدي\Ahmed Al-Yassiri's Smart Assistant"
}
if (-not $OutDir) {
    $OutDir = Join-Path $env:TEMP "alijaddi_model_packs"
}

if (-not (Test-Path -LiteralPath $SourcePath)) {
    Write-Error "SourcePath not found: $SourcePath"
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$staging = Join-Path $OutDir $rootName
if (Test-Path -LiteralPath $staging) {
    Remove-Item -LiteralPath $staging -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $staging | Out-Null

Get-ChildItem -LiteralPath $SourcePath -Force | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $staging $_.Name) -Recurse -Force
}

$zipPath = Join-Path $OutDir $zipName
if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
Compress-Archive -Path $staging -DestinationPath $zipPath -CompressionLevel Optimal
Write-Host "OK: $zipPath (top folder: $rootName)"
