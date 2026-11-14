set -e
export PIPE_ROOT=/srv/tts-out/pipe-test; rm -rf $PIPE_ROOT; mkdir -p $PIPE_ROOT
cat > /tmp/t_pl.txt <<'T'
Wieczorem byłem w Paryżu.

Metrem jedziemy na drugi dworzec i zostawiamy nasze walizki.
T
cat > /tmp/t_jobs.json <<'J'
[{"id":"test-pl-a","kind":"audio","lang":"pl","text":"/tmp/t_pl.txt","name":"test_pl_a","takes":3,"seed":7000}]
J
cd ~/diary-pipeline; python3 orch.py add /tmp/t_jobs.json
nohup python3 orch.py run > /tmp/orch_t1.out 2>&1 < /dev/null &
sleep 3; echo started; cat /srv/tts-out/pipe-test/heartbeat; python3 orch.py status | head -12
echo "--- second orchestrator must refuse:"; python3 orch.py run; echo "rc=$?"
