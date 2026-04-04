# AliJaddi scheduled verify task helper (fixes cmd window popping every few minutes)
# status:  powershell -ExecutionPolicy Bypass -File scripts\manage_verify_task.ps1
# remove:  ... -Action remove
# install: ... -Action install-daily   (once per day at 12:30, hidden)
param(
    [ValidateSet("status", "remove", "install-daily")]
    [string] $Action = "status"
)

$taskNames = @(
    "AliJaddi_VerifyEcosystem",
    "AliJaddiVerifyEcosystem",
    "AliJaddiVerify",
    "AliJaddi Verify"
)
$scriptPath = Join-Path (Split-Path -Parent $PSScriptRoot) "scripts\run_verify_scheduled.ps1"
$scriptPath = (Resolve-Path $scriptPath).Path

function Find-AliJaddiTasks {
    Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object {
        if ($_.TaskName -match "AliJaddi|alijaddi") {
            $true
        } else {
            $hit = $false
            foreach ($a in $_.Actions) {
                $blob = "$($a.Execute) $($a.Arguments)"
                if ($blob -match "run_verify_scheduled|verify_ecosystem") {
                    $hit = $true
                    break
                }
            }
            $hit
        }
    }
}

if ($Action -eq "status") {
    Write-Host "=== Scheduled tasks that may be AliJaddi / verify ===" -ForegroundColor Cyan
    $found = @(Find-AliJaddiTasks)
    if ($found.Count -eq 0) {
        Write-Host "No obvious tasks. Open taskschd.msc and search for run_verify_scheduled or verify." -ForegroundColor Yellow
    } else {
        $found | ForEach-Object {
            Write-Host ("- {0} | State={1}" -f $_.TaskName, $_.State)
            $_.Actions | ForEach-Object { Write-Host ("    Execute: {0} {1}" -f $_.Execute, $_.Arguments) }
        }
    }
    Write-Host ""
    Write-Host "If cmd flashes every ~10 min, a task likely runs run_verify_scheduled.bat. Run:" -ForegroundColor Gray
    Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\manage_verify_task.ps1 -Action remove" -ForegroundColor Gray
    exit 0
}

if ($Action -eq "remove") {
    $removed = 0
    foreach ($n in $taskNames) {
        Unregister-ScheduledTask -TaskName $n -Confirm:$false -ErrorAction SilentlyContinue
        if ($?) { $removed++; Write-Host "Removed: $n" -ForegroundColor Green }
    }
    foreach ($t in Find-AliJaddiTasks) {
        try {
            Unregister-ScheduledTask -TaskName $t.TaskName -Confirm:$false -ErrorAction Stop
            Write-Host "Removed: $($t.TaskName)" -ForegroundColor Green
            $removed++
        } catch { }
    }
    if ($removed -eq 0) {
        Write-Host "No task removed automatically. Delete manually in taskschd.msc any task running run_verify_scheduled.bat" -ForegroundColor Yellow
    }
    exit 0
}

if ($Action -eq "install-daily") {
    $taskName = "AliJaddi_VerifyEcosystem"
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    $arg = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`""
    $taskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg
    $trigger = New-ScheduledTaskTrigger -Daily -At "12:30pm"
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $desc = 'AliJaddi verify_ecosystem quick; silent; log AliJaddi_verify.log in user profile'
    Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $trigger -Settings $settings -Description $desc | Out-Null
    Write-Host "Registered daily task $taskName at 12:30 with hidden window." -ForegroundColor Green
    exit 0
}
