#!/bin/bash
# EN voice candidates: paragraph 1 of EN page 1 (4 sentences) x 4 takes each, gaps 0.5/1.0, Whisper-picked. Sequential, STOP file honoured.
# Tags: current = control (the v1 narrator, deepened -1.0), cur_nodeep = same blend without deepen, others = XTTS built-in speakers (no deepen).
W=~/c-workstream; R=/srv/tts-out/render/c-en-voice; mkdir -p $R/finals
python3 - <<'PY'
t = open("/srv/tts-out/c-input/ep01-en-page1.txt", encoding="utf-8").read().split("\n\n")[0].strip() + "\n"
open("/srv/tts-out/c-input/ep01-en-p1a.txt", "w", encoding="utf-8").write(t); print(len(t), "chars")
PY
run() { tag=$1; lat=$2; shift 2
  env GAP_S=0.5 GAP_P=1.0 "$@" bash $W/c_brokkr_episode.sh en /srv/tts-out/c-input/ep01-en-p1a.txt $R/$tag en_$tag "$lat" --takes 4 --seed 5000 --names /srv/tts-out/c-input/ep01-en-page1.names.txt
  rc=$?; cp $R/$tag/final/en_$tag.mp3 $R/finals/ 2>/dev/null; return $rc; }
run current c_Kumar65_Ilkin35_80_Damien20.pth || exit $?
run cur_nodeep c_Kumar65_Ilkin35_80_Damien20.pth DEEPEN_ST=0 DEEPEN_BASS=0 || exit $?
run Damien_Black "Damien Black" DEEPEN_ST=0 DEEPEN_BASS=0 || exit $?
run Dionisio_Schuyler "Dionisio Schuyler" DEEPEN_ST=0 DEEPEN_BASS=0 || exit $?
run Damjan_Chapman "Damjan Chapman" DEEPEN_ST=0 DEEPEN_BASS=0 || exit $?
run Abrahan_Mack "Abrahan Mack" DEEPEN_ST=0 DEEPEN_BASS=0 || exit $?
run Royston_Min "Royston Min" DEEPEN_ST=0 DEEPEN_BASS=0 || exit $?
run Kumar_Dahl "Kumar Dahl" DEEPEN_ST=0 DEEPEN_BASS=0 || exit $?
echo ALL-VOICES-DONE
