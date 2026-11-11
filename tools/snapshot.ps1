<#
 snapshot.ps1 - commit text, scripts and manifests of the Diary project (LOCAL commit only, never pushes).
 Usage:  tools\snapshot [-Message "why"] [-Retries 6] [-DelaySeconds 3]
 What is committed is decided by .gitignore (no images, audio, video, archives, key-like files).
 Retries when .git\index.lock is held. Never deletes a lock: a stale lock is reported for Jim to remove.
 Written by workstream C, 2026-11-11.
#>
param(
  [string]$Message = ("snapshot " + (Get-Date -Format "yyyy-MM-dd HH:mm")),
  [int]$Retries = 6,
  [int]$DelaySeconds = 3
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$lock = Join-Path $root ".git\index.lock"
for ($i = 1; $i -le $Retries; $i++) {
  if (Test-Path $lock) {
    Write-Host "index.lock present, attempt $i/$Retries, waiting $DelaySeconds s"
    Start-Sleep -Seconds $DelaySeconds
    continue
  }
  git add -A 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) { Start-Sleep -Seconds $DelaySeconds; continue }
  git diff --cached --quiet
  if ($LASTEXITCODE -eq 0) { Write-Host "nothing to commit"; exit 0 }
  git commit -q -m $Message -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
  if ($LASTEXITCODE -eq 0) { git log -1 --oneline; exit 0 }
  Start-Sleep -Seconds $DelaySeconds
}
Write-Error "snapshot failed after $Retries attempts (stale .git\index.lock? remove it by hand if no git process is running)"
exit 1
