export PIPE_ROOT=/srv/tts-out/pipe-test; cd ~/diary-pipeline
cat > /tmp/t_pl2.txt <<'T'
Tor kolejowy idzie nad morzem na wysokiej skale.

Pierwszy raz widziałem morze i byłem zachwycony jego widokiem.

W południowych godzinach byliśmy w Wenecji.
T
echo '[{"id":"test-pl-b","kind":"audio","lang":"pl","text":"/tmp/t_pl2.txt","name":"test_pl_b","takes":3,"seed":7100}]' > /tmp/t_jobs2.json
python3 orch.py add /tmp/t_jobs2.json
setsid nohup python3 orch.py run > /tmp/orch_t2.out 2>&1 < /dev/null &
sleep 40
PG=$(ps -o pgid= -p $(pgrep -f 'orch.py run' | head -1) | tr -d ' ')
echo "killing process group $PG"; kill -9 -- -$PG; sleep 3
echo "takes after kill: $(ls $PIPE_ROOT/jobs/test-pl-b-*/take_*.wav | wc -l) wavs; state: $(ls $PIPE_ROOT/jobs/test-pl-b-*/ | grep -E 'DONE|FAILED')"
ps aux | grep -E 'episode_render|c_pick_v2|orch.py' | grep -v grep | wc -l
echo "lock after kill (should be free):"; python3 - <<'PY'
import fcntl; f=open('/srv/tts-out/pipe-test/orch.lock','w'); fcntl.flock(f, fcntl.LOCK_EX|fcntl.LOCK_NB); print("lock free")
PY
BEFORE=$(ls $PIPE_ROOT/jobs/test-pl-b-*/take_*.wav | wc -l)
python3 orch.py run; echo "rerun rc=$?"
echo "takes before rerun $BEFORE, after $(ls $PIPE_ROOT/jobs/test-pl-b-*/take_*.wav | wc -l)"
grep -c 'synth' $PIPE_ROOT/jobs/test-pl-b-*/run.log
tail -8 $PIPE_ROOT/ledger.jsonl | cut -c1-150
