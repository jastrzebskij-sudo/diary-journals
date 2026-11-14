#!/usr/bin/env bash
# post_trim.sh - unattended: as each EN Ep3/Ep4 job finishes, run tail_trim.py on it (writes trim_report.json, picked_all_trim.wav, final_trim/). Exits when queue is empty and all done.
# Originals untouched. Log: /srv/tts-out/pipe/post_trim.log. Started 2026-11-14.
export PATH="$HOME/.local/bin:$PATH" CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0
J=/srv/tts-out/pipe/jobs; LOG=/srv/tts-out/pipe/post_trim.log; echo "$(date) post_trim start" >> $LOG
while true; do
  for d in $J/ep03-en-* $J/ep04-en-*; do
    [ -d "$d" ] && [ -e "$d/DONE" ] && [ ! -e "$d/trim_report.json" ] && [ ! -e "$d/trim_failed" ] || continue
    echo "$(date) trimming $d" >> $LOG
    ~/c-workstream/venv-asr/bin/python ~/diary-pipeline/tail_trim.py "$d" --lang en >> $LOG 2>&1 || { echo "$(date) FAIL $d" >> $LOG; touch "$d/trim_failed"; }
  done
  busy=$(python3 -c "
import json;s=json.load(open('/srv/tts-out/pipe/status.json'));c=s.get('counts',s)
print(int(c.get('todo',0))+int(c.get('running',0)))" 2>/dev/null || echo 1)
  pend=0; for d in $J/ep03-en-* $J/ep04-en-*; do [ -d "$d" ] && [ -e "$d/DONE" ] && [ ! -e "$d/trim_report.json" ] && [ ! -e "$d/trim_failed" ] && pend=1; done
  [ "$busy" = "0" ] && [ "$pend" = "0" ] && break
  sleep 300
done
echo "$(date) post_trim finished" >> $LOG
