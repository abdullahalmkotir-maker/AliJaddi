# Removes previous Beta output folders/zips under تنزيل\windows and old installer exes.
# Run from repo root: powershell -ExecutionPolicy Bypass -File scripts\clean_old_releases.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$tanzeel = "$([char]0x062A)$([char]0x0646)$([char]0x0632)$([char]0x064A)$([char]0x0644)"
$win = Join-Path (Join-Path $root $tanzeel) "windows"
$inst = Join-Path $root "installer"

if (Test-Path $win) {
    Get-ChildItem -LiteralPath $win -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.Name -match '^AliJaddi-Beta-0\.3\.(0|1)') {
            Remove-Item -LiteralPath $_.FullName -Recurse -Force
            Write-Host "Removed: $($_.FullName)"
        }
    }
}
if (Test-Path $inst) {
    Get-ChildItem -LiteralPath $inst -Filter "*.exe" -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.Name -match '0\.3\.(0|1)') {
            Remove-Item -LiteralPath $_.FullName -Force
            Write-Host "Removed: $($_.FullName)"
        }
    }
}
Write-Host "Done."
