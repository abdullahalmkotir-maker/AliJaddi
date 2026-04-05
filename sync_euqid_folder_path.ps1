# يضبط حقل folder في manifest «عقد» ليطابق شجرة المستودع.
# التشغيل من جذر AliJaddi: .\sync_euqid_folder_path.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$manifest = Join-Path $root "addons\manifests\euqid.json"
if (-not (Test-Path -LiteralPath $manifest)) {
    Write-Warning "غير موجود: $manifest"
    exit 0
}

$raw = Get-Content -LiteralPath $manifest -Raw -Encoding UTF8
$replacement = '"folder": "Applications AliJaddi/تطبيق عقد"'
$raw2 = $raw -replace '"folder"\s*:\s*"[^"]*"', $replacement
if ($raw2 -ne $raw) {
    [System.IO.File]::WriteAllText($manifest, $raw2, [System.Text.UTF8Encoding]::new($false))
    Write-Host "تم تحديث folder في euqid.json"
} else {
    Write-Host "euqid.json — folder محدّث مسبقاً."
}
