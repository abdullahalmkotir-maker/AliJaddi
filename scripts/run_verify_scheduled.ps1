# تشغيل verify_ecosystem --quick بدون نافذة (مناسب لجدولة المهام)
# السجل: %USERPROFILE%\AliJaddi_verify.log
$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$log = Join-Path $env:USERPROFILE "AliJaddi_verify.log"
$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $log -Encoding utf8 -Value ""
Add-Content -Path $log -Encoding utf8 -Value "===== $stamp verify_ecosystem --quick (ps1) ====="

function Invoke-PythonVerify([string] $fileName, [string] $arguments) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $fileName
    $psi.Arguments = $arguments
    $psi.WorkingDirectory = $root
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    [void]$p.Start()
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    if ($stdout) { Add-Content -Path $log -Value $stdout.TrimEnd() -Encoding utf8 }
    if ($stderr) { Add-Content -Path $log -Value $stderr.TrimEnd() -Encoding utf8 }
    return $p.ExitCode
}

$candidates = @(
    "$env:LocalAppData\Programs\Python\Python311\python.exe",
    "$env:LocalAppData\Programs\Python\Python312\python.exe",
    "$env:LocalAppData\Programs\Python\Python310\python.exe"
)
$py = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

$ec = 1
if ($py) {
    $ec = Invoke-PythonVerify $py "scripts\verify_ecosystem.py --quick"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pyLauncher = (Get-Command py).Source
    $ec = Invoke-PythonVerify $pyLauncher "-3 scripts\verify_ecosystem.py --quick"
} else {
    Add-Content -Path $log -Encoding utf8 -Value "ERROR: Python not found. Install Python or edit scripts\run_verify_scheduled.ps1"
}

Add-Content -Path $log -Encoding utf8 -Value "exit_code=$ec"
exit $ec
