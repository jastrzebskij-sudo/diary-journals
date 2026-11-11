#!/usr/bin/env bash
# c_brokkr_deep1_blends.sh - the two 80/20 Damien Black blends for Ep1 page 1 (workstream C, 2026-11-11). Runs on brokkr.
#  A (literal): latent cloned from the deep-1.0 audio (refs/c-Kumar65_Ilkin35_deep1.0.wav) 80% + Damien Black 20%.
#  B (alt):     latent Kumar65_Ilkin35 80% + Damien Black 20%, to be deepened by -1.0 st afterwards (c_deepen.py on loki).
set -euo pipefail
T=/srv/tts-out/c-input/trial-PL-tts.txt
bash ~/c-workstream/c_brokkr_blend.sh c_KID1.0_80_Damien20 $T 2 pl ep01p1 refs/c-Kumar65_Ilkin35_deep1.0.wav:80 Damien_Black:20
bash ~/c-workstream/c_brokkr_blend.sh c_Kumar65_Ilkin35_80_Damien20 $T 2 pl ep01p1 latents/Kumar65_Ilkin35.pth:80 Damien_Black:20
echo ALL-DONE
