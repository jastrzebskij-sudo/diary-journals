# fetch_jobs.ps1 PREFIX  - copy finished, trimmed job data from brokkr into Assets\Diary\review\jobs-cache (e.g. PREFIX = ep03-en-)
param([string]$Prefix)
$base = 'D:\Claude\Assets\Diary\review\jobs-cache'
$list = ssh brokkr-agent "cd /srv/tts-out/pipe/jobs; for d in ${Prefix}*; do [ -e `$d/DONE ] && [ -e `$d/trim_report.json ] && echo `$d; done"
foreach ($j in $list) {
  if (-not $j) { continue }
  New-Item -ItemType Directory -Force "$base\$j\final_trim" | Out-Null
  scp "brokkr-agent:/srv/tts-out/pipe/jobs/$j/picked.json" "$base\$j\"
  scp "brokkr-agent:/srv/tts-out/pipe/jobs/$j/trim_report.json" "$base\$j\"
  scp "brokkr-agent:/srv/tts-out/pipe/jobs/$j/final_trim/narration_trim.wav" "$base\$j\final_trim\"
  Write-Host "fetched $j"
}
