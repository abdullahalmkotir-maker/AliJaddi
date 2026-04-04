# تشغيل خدمة BentoML لمساعدي السرب (محلي)
# يتطلب: pip install -e ".[bentoml]"
# الاستخدام: powershell -ExecutionPolicy Bypass -File scripts\run_bento_serving.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "bento_serving")
Write-Host "Serving AliJaddiAssistantService — Ctrl+C to stop"
bentoml serve service.py:AliJaddiAssistantService --reload
