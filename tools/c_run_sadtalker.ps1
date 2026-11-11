<#
 c_run_sadtalker.ps1 - animate one portrait with one audio file using SadTalker (candidate 1).
 Usage: tools\c_run_sadtalker.ps1 -Image <jpg> -Audio <wav> -OutDir <dir> [-Size 256|512] [-Preprocess full|crop] [-Assets ...]
 Writes <OutDir>\*.mp4 and <OutDir>\manifest.txt (model, settings, date, seconds taken). Originals are only read.
 Workstream C, 2026-11-11.
#>
param([Parameter(Mandatory)][string]$Image, [Parameter(Mandatory)][string]$Audio, [Parameter(Mandatory)][string]$OutDir,
      [int]$Size = 256, [string]$Preprocess = "full", [string]$Assets = "D:\Claude\Assets\Diary")
$ErrorActionPreference = "Stop"
$env:PATH = "$Assets\bin;$env:PATH"
$py = "$Assets\venv\face\Scripts\python.exe"; $st = "$Assets\face\SadTalker"
New-Item -ItemType Directory -Force $OutDir | Out-Null
$t0 = Get-Date
Push-Location $st
& $py "$PSScriptRoot\c_sadtalker_shim.py" $st --driven_audio $Audio --source_image $Image --result_dir $OutDir --size $Size --preprocess $Preprocess --still --enhancer none
$code = $LASTEXITCODE; Pop-Location
$secs = [int]((Get-Date) - $t0).TotalSeconds
@("model=SadTalker commit $(git -C $st rev-parse --short HEAD)", "size=$Size preprocess=$Preprocess still enhancer=none", "image=$Image", "audio=$Audio",
  "date=$(Get-Date -Format s) seconds=$secs exit=$code") | Out-File "$OutDir\manifest.txt"
exit $code
