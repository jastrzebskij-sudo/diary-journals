<#
 Milestone backup: commit -> NAS mirror -> brokkr copy -> git push.
 Usage: powershell -File tools\backup.ps1 -Message "milestone: what changed" [-NoPush] [-SkipNas] [-SkipBrokkr] [-Full]
 Write-only copies: nothing is ever deleted on the destinations (no /MIR, no rsync --delete).
 NAS    : X:\Journals-Project\D-Claude  (robocopy /E /XO)
 Brokkr : ~/diary-backup/D-Claude (incremental tar stream over ssh, mtime stamp; -Full ignores stamp)
 Log    : tools\backup.log (git-ignored via *.log)
#>
param([string]$Message = "snapshot", [switch]$NoPush, [switch]$SkipNas, [switch]$SkipBrokkr, [switch]$Full)
$src = "D:\Claude"; $repo = "D:\Claude\Projects\Diary"
$log = Join-Path $repo "tools\backup.log"
$stampFile = "D:\Claude\.backup-brokkr.stamp"
function L($m) { $l = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m; Write-Host $l; Add-Content -Path $log -Value $l }
$start = Get-Date
L "== backup start: $Message"
Set-Location $repo
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
  git commit -q -m "$Message`n`nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`nClaude-Session: https://claude.ai/code/session_01Q1TVEWTB7wSRw1VnyVmJhn"
  L "committed: $(git log --oneline -1)"
} else { L "nothing to commit" }
if (-not $SkipNas) {
  if (Test-Path "X:\Journals-Project") {
    robocopy $src "X:\Journals-Project\D-Claude" /E /XO /MT:8 /R:1 /W:1 /NP /NFL /NDL /NJH /XD "__pycache__" ".venv" "D:\Claude\Assets\Diary\lab\hf" "D:\Claude\Assets\Diary\lab\env-*" "D:\Claude\Assets\Diary\lab\ditto-talkinghead\checkpoints" | Select-Object -Last 8 | ForEach-Object { if ($_.Trim()) { L "nas: $_" } }
    if ($LASTEXITCODE -ge 8) { L "NAS ROBOCOPY ERROR code $LASTEXITCODE" } else { L "nas OK (robocopy code $LASTEXITCODE)" }
  } else { L "NAS NOT REACHABLE (X:\Journals-Project)" }
}
if (-not $SkipBrokkr) {
  $newer = ""
  if ((Test-Path $stampFile) -and -not $Full) { $t = (Get-Content $stampFile -Raw).Trim(); $newer = "--newer-mtime `"$t`"" }
  ssh brokkr-agent "mkdir -p ~/diary-backup/D-Claude"
  $cmd = "tar.exe -C $src $newer --exclude=__pycache__ --exclude=.venv --exclude=*/lab/hf --exclude=*/lab/env-* --exclude=*/lab/ditto-talkinghead/checkpoints --exclude=`"Music Download`" -cf - . | ssh brokkr-agent `"tar -C ~/diary-backup/D-Claude -xf -`""
  cmd /c $cmd
  if ($LASTEXITCODE -eq 0) { $start.AddMinutes(-1).ToString("yyyy-MM-dd HH:mm:ss") | Set-Content $stampFile; L "brokkr OK" } else { L "BROKKR COPY ERROR code $LASTEXITCODE" }
}
if (-not $NoPush) { git push origin main 2>&1 | ForEach-Object { L "git: $_" } }
L "== backup end ($([int]((Get-Date)-$start).TotalSeconds) s)"
