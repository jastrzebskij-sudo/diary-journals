#!/bin/bash
cd ~/work/tts
CUDA_VISIBLE_DEVICES=1 COQUI_TOS_AGREED=1 .venv/bin/python - <<'PY' 2>&1 | tail -3
import sys; sys.path.insert(0, "scripts"); import common
m = common.load_model(); print("EN", common.model_char_limit(m, "en"), "PL", common.model_char_limit(m, "pl"))
PY
ls /srv/tts-out/c-input
which python3 ffprobe ffmpeg
