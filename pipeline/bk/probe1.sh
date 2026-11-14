for l in pl en; do B=/srv/tts-out/render/ep01_$l; echo "== $l"; ls $B 2>&1 | head -30; for p in $B/*/; do b=$(basename $p); echo -n "$l $b: "; ls $p | grep -E '^(DONE|FAILED|STOP)$' | tr '\n' ' '; echo; done; tail -2 $B/job.log 2>/dev/null; done
echo ---- render.py; sed -n 1,75p ~/c-workstream/c_brokkr_episode_render.py
