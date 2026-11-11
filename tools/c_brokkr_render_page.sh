#!/usr/bin/env bash
# c_brokkr_render_page.sh - render the first N paragraphs of a TTS-prepared text with XTTS-v2 in several saved voices.
# Runs ON brokkr as claude-agent (GPU index 1, fp32, venv ~/work/tts/.venv, weights cached; no Docker, no sudo).
# Usage: c_brokkr_render_page.sh SRC_TEXT N_PARAGRAPHS LANG TAG VOICE [VOICE ...]
#   VOICE = a saved latent name (latents/<VOICE>.pth) or, if none exists, a built-in speaker with _ for spaces (Baldur_Sanjin).
#   e.g. c_brokkr_render_page.sh /srv/tts-out/c-input/trial-PL-tts.txt 2 pl ep01p1 Kumar65_Ilkin35 Kumar35_Ilkin65
# Output: /srv/tts-out/render/c-<TAG>-<LATENT>/ (NNN.wav, *_all.wav, manifest.txt with model, settings, date, seconds).
# Digit guard of render.py applies (Polish input with digits is refused). Workstream C, 2026-11-11.
set -euo pipefail
src=$1; n=$2; lang=$3; tag=$4; shift 4
cd ~/work/tts
mkdir -p /srv/tts-out/c-input
txt=/srv/tts-out/c-input/${tag}.txt
awk -v n="$n" 'BEGIN{RS="";ORS="\n\n"} NR<=n' "$src" > "$txt"
export COQUI_TOS_AGREED=1 CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1
for lat in "$@"; do
  job=c-$tag-$lat; t0=$(date +%s)
  if [ -f "latents/$lat.pth" ]; then voice="latents/$lat.pth"; else voice="${lat//_/ }"; fi
  .venv/bin/python scripts/render.py "$txt" --lang "$lang" --voice "$voice" --job "$job"
  { echo "model=XTTS-v2 (coqui-tts $(.venv/bin/python -c 'import TTS;print(TTS.__version__)')) fp32 GPU1 GTX 1080 Ti"
    echo "voice=$voice lang=$lang gap=0.3 para_gap=0.7 (render.py defaults) repo=$(git rev-parse --short HEAD)"
    echo "text=$txt ($(wc -c < "$txt") bytes, $n paragraphs) date=$(date -Is) seconds=$(( $(date +%s) - t0 ))"; } > "/srv/tts-out/render/$job/manifest.txt"
done
echo RENDER-DONE
