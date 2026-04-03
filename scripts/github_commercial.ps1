<#
.SYNOPSIS
  إعداد GitHub للاستخدام التجاري — بعد المصادقة فقط.

.DESCRIPTION
  1) ثبّتنا لك GitHub CLI (winget). يجب مرة واحدة:
       & "$env:ProgramFiles\GitHub CLI\gh.exe" auth login
     أو ضع رمزاً Classic PAT مع صلاحيات repo في المتغير:
       $env:GH_TOKEN = "ghp_...."

  2) شغّل هذا السكربت بمعاملات:
       .\scripts\github_commercial.ps1 -Action list
       .\scripts\github_commercial.ps1 -Action create-cloud -OrgOrUser YOUR_USER
       .\scripts\github_commercial.ps1 -Action archive -Repo OWNER/old-repo-name

  حذف المستودع نهائياً من الويب: Settings → Danger zone → Delete (لا يُنصح بالأتمتة بدون قائمة واضحة).

.NOTES
  بيتا 0.2 — AliJaddi
#>
param(
    [ValidateSet("list", "whoami", "create-cloud", "create-account", "archive", "help")]
    [string]$Action = "help",
    [string]$OrgOrUser = "",
    [string]$Repo = ""
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($Action)) { $Action = "help" }
$gh = Join-Path ${env:ProgramFiles} "GitHub CLI\gh.exe"
if (-not (Test-Path $gh)) {
    Write-Host "gh not found at $gh - install: winget install GitHub.cli"
    exit 1
}

function Invoke-Gh { param([string[]]$Args)
    & $gh @Args
    if ($LASTEXITCODE -ne 0) { throw "gh failed: $($Args -join ' ')" }
}

if ($Action -eq "help") {
    Write-Host ""
    Write-Host "github_commercial.ps1 (AliJaddi Beta 0.2)"
    Write-Host "  -Action whoami | list | create-cloud | create-account | archive"
    Write-Host "  Example: .\scripts\github_commercial.ps1 -Action create-cloud -OrgOrUser YOUR_USER"
    Write-Host "  First login:  $gh auth login"
    Write-Host ""
    exit 0
}

# Auth check (gh writes to stderr when not logged in)
$prevEap = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$null = & $gh auth status 2>&1
$authOk = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = $prevEap
if (-not $authOk) {
    Write-Host "Not logged in to GitHub."
    Write-Host "Run:  $gh auth login"
    Write-Host "Or set env:  `$env:GH_TOKEN = '<PAT with repo scope>'"
    exit 2
}

switch ($Action) {
    "whoami" {
        $login = & $gh api user --jq .login
        Write-Host "Logged in as: $login"
    }
    "list" { Invoke-Gh @("repo", "list", "--limit", "100") }
    "create-cloud" {
        if (-not $OrgOrUser) { throw "Use -OrgOrUser your-github-username-or-org" }
        $name = "AliJaddi-Cloud"
        Invoke-Gh @("repo", "create", "$OrgOrUser/$name", "--private", "--description", "AliJaddi Cloud backend helpers (commercial)", "--clone=false")
        Write-Host "Created: https://github.com/$OrgOrUser/$name"
        Write-Host "Next: cd to AliJaddi Cloud folder, then:"
        Write-Host "  git remote add origin https://github.com/$OrgOrUser/$name.git"
        Write-Host "  git branch -M main"
        Write-Host "  git push -u origin main"
    }
    "create-account" {
        if (-not $OrgOrUser) { throw "Use -OrgOrUser your-github-username-or-org" }
        $name = "AliJaddiAccount"
        Invoke-Gh @("repo", "create", "$OrgOrUser/$name", "--private", "--description", "AliJaddi Account (commercial)", "--clone=false")
        Write-Host "Created: https://github.com/$OrgOrUser/$name"
    }
    "archive" {
        if (-not $Repo) { throw "Use -Repo OWNER/name" }
        $ok = Read-Host "Archive $Repo on GitHub? Type YES"
        if ($ok -ne "YES") { Write-Host "Cancelled."; exit 0 }
        Invoke-Gh @("repo", "archive", $Repo, "--yes")
        Write-Host "Archived: $Repo"
    }
}
