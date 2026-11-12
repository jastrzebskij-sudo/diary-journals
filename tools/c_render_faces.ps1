<#
 c_render_faces.ps1 - batch face render: every narration wav in a folder x every portrait -> patched SadTalker mp4, with checkpoint/resume.
 Workstream C, 2026-11-12. Runs on loki; no network, no AI tokens. Run it yourself from PowerShell:
   tools\c_render_faces.ps1 -AudioDir D:\Claude\Assets\Diary\tts\ep01_pl\faces_in -Image D:\Claude\Assets\Diary\face\run1\WA0003.jpg,D:\Claude\Assets\Diary\face\run1\WA0005.jpg `
        -OutDir D:\Claude\Assets\Diary\face\ep01
 Options: -Size 256|512 (default 256)  -Preprocess full|crop (default full)  -Assets <dir>  -MinFreeMB 6000 (GPU must have this much free; picks the GPU with most free memory)
 Per job (page wav x portrait) the output is OutDir\<page>\<portrait>\<result>.mp4 plus OutDir\<page>\<portrait>\DONE (checkpoint). Re-running skips jobs with DONE;
 a job killed half-way is redone from scratch. Audio is converted to 16 kHz mono first (OutDir\_audio16k). Results (seconds per audio second) are appended to
 OutDir\results.csv, progress to OutDir\run.log. STOP: create a file named STOP in OutDir (or in <Assets>\face) - the current job finishes, then the script exits.
 Originals are only read. Exit codes: 0 all done, 3 stopped by STOP, 4 no free GPU, 1 a job failed (the script continues with the next job and exits 1 at the end).
#>
param([Parameter(Mandatory)][string]$AudioDir, [Parameter(Mandatory)][string[]]$Image, [Parameter(Mandatory)][string]$OutDir,
      [int]$Size = 256, [string]$Preprocess = "full", [string]$Assets = "D:\Claude\Assets\Diary", [int]$MinFreeMB = 6000)
$ErrorActionPreference = "Stop"
$ff = "$Assets\bin\ffmpeg.exe"; $fp = "$Assets\bin\ffprobe.exe"
$py = "$Assets\venv\face\Scripts\python.exe"; $st = "$Assets\face\SadTalker"; $shim = "$PSScriptRoot\c_sadtalker_shim.py"
New-Item -ItemType Directory -Force $OutDir, "$OutDir\_audio16k" | Out-Null
$log = "$OutDir\run.log"; $csv = "$OutDir\results.csv"
function Say($m) { $l = "$(Get-Date -Format 's') $m"; Write-Host $l; Add-Content -Path $log -Value $l -Encoding UTF8 }
function Stopped { (Test-Path "$OutDir\STOP") -or (Test-Path "$Assets\face\STOP") }
if (-not (Test-Path $csv)) { Add-Content $csv "page,portrait,audio_s,render_s,render_s_per_audio_s,gpu,size,preprocess,finished" -Encoding UTF8 }
# pick the GPU with the most free memory
$gpus = & nvidia-smi --query-gpu=index,memory.total,memory.used --format=csv,noheader,nounits | ForEach-Object { $p = $_ -split ",\s*"; [pscustomobject]@{Index=[int]$p[0]; Free=[int]$p[1]-[int]$p[2]} }
$best = $gpus | Sort-Object Free -Descending | Select-Object -First 1
if ($best.Free -lt $MinFreeMB) { Say "no GPU with $MinFreeMB MB free (best: GPU $($best.Index) $($best.Free) MB). Exiting."; exit 4 }
$env:CUDA_VISIBLE_DEVICES = "$($best.Index)"; $env:PATH = "$Assets\bin;$env:PATH"
$wavs = Get-ChildItem $AudioDir -Filter *.wav | Where-Object { $_.Name -notmatch "_16k" } | Sort-Object Name
Say "start: $($wavs.Count) wavs x $($Image.Count) portraits, GPU $($best.Index) ($($best.Free) MB free), size $Size, preprocess $Preprocess"
$failed = 0
foreach ($w in $wavs) {
  $page = [IO.Path]::GetFileNameWithoutExtension($w.Name); $a16 = "$OutDir\_audio16k\$page.wav"
  if (-not (Test-Path $a16)) { & $ff -hide_banner -loglevel error -y -i $w.FullName -ar 16000 -ac 1 $a16; if ($LASTEXITCODE) { Say "ffmpeg failed for $page"; $failed++; continue } }
  $dur = [double](& $fp -v error -show_entries format=duration -of csv=p=0 $a16)
  foreach ($img in $Image) {
    $pn = [IO.Path]::GetFileNameWithoutExtension($img); $jd = "$OutDir\$page\$pn"
    if (Test-Path "$jd\DONE") { Say "skip $page / $pn (DONE)"; continue }
    if (Stopped) { Say "STOP file found - exiting before $page / $pn"; exit 3 }
    if (Test-Path $jd) { Remove-Item $jd -Recurse -Force }   # half-finished job: redo from scratch
    New-Item -ItemType Directory -Force $jd | Out-Null
    Say "render $page / $pn  (audio $([math]::Round($dur,1)) s)"
    $t0 = Get-Date
    $args2 = @($shim, $st, "--driven_audio", $a16, "--source_image", $img, "--result_dir", $jd, "--size", $Size, "--preprocess", $Preprocess, "--still")
    $proc = Start-Process -FilePath $py -ArgumentList $args2 -WorkingDirectory $st -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$jd\st.out" -RedirectStandardError "$jd\st.err"
    $secs = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
    $mp4 = Get-ChildItem $jd -Filter *.mp4 -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($proc.ExitCode -ne 0 -or -not $mp4) { Say "FAILED $page / $pn exit $($proc.ExitCode), see $jd\st.err"; $failed++; continue }
    $ratio = [math]::Round($secs / $dur, 2)
    Add-Content $csv "$page,$pn,$([math]::Round($dur,1)),$secs,$ratio,$($best.Index),$Size,$Preprocess,$(Get-Date -Format s)" -Encoding UTF8
    Set-Content "$jd\DONE" "$(Get-Date -Format s) $($mp4.Name) render_s=$secs audio_s=$([math]::Round($dur,1))" -Encoding UTF8
    Say "done $page / $pn in $secs s = $ratio s per audio second -> $($mp4.FullName)"
  }
}
if ($failed) { Say "finished with $failed failed job(s)"; exit 1 }
Say "all jobs done"; exit 0
