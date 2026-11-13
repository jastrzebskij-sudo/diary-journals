#!/bin/bash
# does --fast reproduce the same picks as the plain pick on the val1 takes?
S=/srv/tts-out/render/c-pipe-val1; D=/srv/tts-out/render/c-pipe-val1fast; rm -rf $D; mkdir -p $D
cp $S/chunks.json $S/take_s*.wav $D/
python3 - <<'PY'
import json, glob, os
for f in glob.glob("/srv/tts-out/render/c-pipe-val1/take_s*.json"):
    t = json.load(open(f, encoding="utf-8")); [t.pop(k, None) for k in ("asr", "asr_s", "word_errors", "extra_words", "pick_score")]
    json.dump(t, open("/srv/tts-out/render/c-pipe-val1fast/" + os.path.basename(f), "w", encoding="utf-8"))
PY
cd ~/c-workstream; time CUDA_VISIBLE_DEVICES=0 venv-asr/bin/python c_brokkr_episode_pick.py $D --lang pl --fast 2>&1 | grep -E "pick|real"
echo FAST-DONE
