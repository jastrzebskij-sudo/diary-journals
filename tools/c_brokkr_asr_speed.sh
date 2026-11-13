#!/bin/bash
cd ~/c-workstream; D=/srv/tts-out/render/c-pipe-val1
for fp in 0 1; do
  echo "FP32=$fp"; ( time C_ASR_FP32=$fp venv-asr/bin/python c_brokkr_asr.py $D/take_s02_t0.wav $D/take_s02_t1.wav $D/take_s03_t0.wav $D/take_s03_t1.wav $D/take_s04_t0.wav $D/take_s04_t1.wav --out /tmp/asrspeed$fp 2>&1 | grep asr.json | cut -c1-110 ) 2>&1 | grep -v "^$" | grep -E "FP32|asr.json|real"
done
