# creates ~/diary-pipeline with PATCHED COPIES of the proven audio scripts (originals in ~/c-workstream untouched)
set -e
mkdir -p ~/diary-pipeline /srv/tts-out/pipe/jobs
cp ~/c-workstream/c_brokkr_episode_pick.py ~/diary-pipeline/c_pick_v2.py
python3 - <<'PY'
import re, os
p = os.path.expanduser("~/diary-pipeline/c_pick_v2.py"); s = open(p, encoding="utf-8").read()
old = "    n, k = len(exp), len(hyp); INF = 1e9\n"
new = "    n, k = len(exp), len(hyp); INF = 1e9\n    if n == 0: return float(k), 0   # v2: expected text normalises to nothing (all number words); the v1 code crashed here (IndexError on exp[-1])\n"
assert s.count(old) == 1; s = s.replace(old, new)
s = s.replace('c_brokkr_episode_pick.py - step 2', 'c_pick_v2.py (copy of c_brokkr_episode_pick.py with the empty-expectation guard) - step 2', 1)
s = s.replace("from c_brokkr_asr import load_asr, read16k", "sys.path.insert(0, os.path.expanduser('~/c-workstream'))\nfrom c_brokkr_asr import load_asr, read16k", 1).replace("import argparse, difflib, json, re, sys, time", "import argparse, difflib, json, os, re, sys, time", 1)
open(p, "w", encoding="utf-8").write(s)
q = os.path.expanduser("~/diary-pipeline/ep_audio.sh"); t = open(os.path.expanduser("~/c-workstream/c_brokkr_episode.sh"), encoding="utf-8").read()
old2 = "$W/venv-asr/bin/python $W/c_brokkr_episode_pick.py"
assert t.count(old2) == 1; t = t.replace(old2, "$W/venv-asr/bin/python ~/diary-pipeline/c_pick_v2.py")
t = t.replace("# c_brokkr_episode.sh - ONE-COMMAND", "# ep_audio.sh (copy of c_brokkr_episode.sh using c_pick_v2.py) - ONE-COMMAND", 1)
open(q, "w", encoding="utf-8").write(t)
PY
chmod +x ~/diary-pipeline/ep_audio.sh
diff <(cat ~/c-workstream/c_brokkr_episode_pick.py) ~/diary-pipeline/c_pick_v2.py || true
diff ~/c-workstream/c_brokkr_episode.sh ~/diary-pipeline/ep_audio.sh || true
bash -n ~/diary-pipeline/ep_audio.sh && python3 -m py_compile ~/diary-pipeline/c_pick_v2.py && echo SYNTAX_OK
