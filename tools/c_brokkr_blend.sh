#!/usr/bin/env bash
# c_brokkr_blend.sh - blend voices into a saved XTTS latent and render a text with it (runs ON brokkr as claude-agent, GPU 1).
# Usage: c_brokkr_blend.sh NAME SRC_TEXT N_PARAGRAPHS LANG TAG VOICE:WEIGHT [VOICE:WEIGHT ...]
#   VOICE = saved latent (latents/<x>.pth), built-in speaker (underscores for spaces) or reference WAV under refs/.
#   e.g. c_brokkr_blend.sh c_KID1_80_Damien20 /srv/tts-out/c-input/trial-PL-tts.txt 2 pl ep01p1 refs/c-deep1.0.wav:80 Damien_Black:20
# Saves latents/NAME.pth (voices and weights recorded in it), then renders to /srv/tts-out/render/c-TAG-NAME/ via
# c_brokkr_render_page.sh. Workstream C, 2026-11-11.
set -euo pipefail
name=$1; src=$2; n=$3; lang=$4; tag=$5; shift 5
voices=(); weights=()
for vw in "$@"; do v=${vw%:*}; w=${vw##*:}; [[ $v == *.wav || $v == *.pth || $v == refs/* || $v == latents/* ]] || v=${v//_/ }; voices+=("$v"); weights+=("$w"); done
cd ~/work/tts
export COQUI_TOS_AGREED=1 CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1
.venv/bin/python scripts/blend.py --voices "${voices[@]}" --weights "${weights[@]}" --name "$name"
bash ~/c-workstream/c_brokkr_render_page.sh "$src" "$n" "$lang" "$tag" "$name"
