#!/bin/bash
# validation run: reproduce v3 take picks for Ep1 page 1 PL
nohup bash ~/c-workstream/c_brokkr_episode.sh pl /srv/tts-out/c-input/ep01-pl-page1-v2.txt /srv/tts-out/render/c-pipe-val1 narration_ep01_p1_PL_val1 c_Kumar65_Ilkin35_80_Damien20.pth --takes 8 --seed 5000 --merge 6 > ~/c-workstream/val1.out 2>&1 < /dev/null &
echo launched
