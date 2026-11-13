#!/bin/bash
# EN page-1 sample: same latent, same recipe as PL (8 takes, seed 5000, Otwock chunk merged with the next sentence)
cp ~/c-workstream/ep01-en-page1.txt /srv/tts-out/c-input/ep01-en-page1.txt
cp ~/c-workstream/ep01-en-page1.txt.names.txt /srv/tts-out/c-input/ep01-en-page1.names.txt
nohup bash ~/c-workstream/c_brokkr_episode.sh en /srv/tts-out/c-input/ep01-en-page1.txt /srv/tts-out/render/c-ep01p1-EN-1 narration_ep01_p1_EN_v1 c_Kumar65_Ilkin35_80_Damien20.pth --takes 8 --seed 5000 --merge 6 --names /srv/tts-out/c-input/ep01-en-page1.names.txt > ~/c-workstream/en1.out 2>&1 < /dev/null &
echo launched
