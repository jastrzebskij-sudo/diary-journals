#!/bin/bash
cd ~/c-workstream
w=$(ls /srv/tts-out/render/c-ep01p1takes1/take_s05_t0.wav 2>/dev/null || find /srv/tts-out -name 'take_s0*_t0.wav' | head -1)
echo "$w"
time venv-asr/bin/python c_brokkr_asr.py "$w" --out ~/c-workstream/asr-test
cat ~/c-workstream/asr-test/*.json | head -20
