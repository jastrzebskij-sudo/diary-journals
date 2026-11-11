<#
 c_setup_sadtalker.ps1 - install SadTalker (face-animation candidate 1) on loki, user-level, under Assets.
 Usage: tools\c_setup_sadtalker.ps1 [-Assets D:\Claude\Assets\Diary] [-Commit <sha>]
 Clones https://github.com/OpenTalker/SadTalker into <Assets>\face\SadTalker, installs deps into
 <Assets>\venv\face (torch already there), downloads checkpoints via the repo's release URLs.
 Logs to <Assets>\tmp\setup_sadtalker.log; writes <Assets>\face\SadTalker\SETUP-MANIFEST.txt (date, commit).
 Workstream C, 2026-11-11. No admin, no Docker, no pushes.
#>
param([string]$Assets = "D:\Claude\Assets\Diary", [string]$Commit = "")
$ErrorActionPreference = "Stop"; $ProgressPreference = "SilentlyContinue"
$py = "$Assets\venv\face\Scripts\python.exe"; $dir = "$Assets\face\SadTalker"
if (-not (Test-Path $dir)) { git clone --depth 1 https://github.com/OpenTalker/SadTalker $dir }
if ($Commit) { git -C $dir fetch --depth 1 origin $Commit; git -C $dir checkout $Commit }
uv pip install --python $py "numpy<2" scipy numba librosa==0.10.2.post1 resampy pydub imageio imageio-ffmpeg scikit-image kornia yacs pyyaml joblib tqdm face_alignment==1.4.1 safetensors av opencv-python-headless facexlib gfpgan basicsr
$ck = "$dir\checkpoints"; New-Item -ItemType Directory -Force $ck | Out-Null
$base = "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc"
foreach ($f in "SadTalker_V0.0.2_256.safetensors","SadTalker_V0.0.2_512.safetensors","mapping_00109-model.pth.tar","mapping_00229-model.pth.tar") {
  if (-not (Test-Path "$ck\$f")) { Invoke-WebRequest "$base/$f" -OutFile "$ck\$f" -UseBasicParsing }
}
"setup $(Get-Date -Format s); commit $(git -C $dir rev-parse HEAD)" | Out-File "$dir\SETUP-MANIFEST.txt"
Write-Host "SadTalker setup done"
