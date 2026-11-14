export PIPE_ROOT=${PIPE_ROOT:-/srv/tts-out/pipe-test}
cd ~/diary-pipeline; python3 orch.py status | sed -n 4,12p; echo; tail -6 $PIPE_ROOT/ledger.jsonl; echo; ls $PIPE_ROOT/jobs/*/ 2>/dev/null | head -20; tail -3 $PIPE_ROOT/jobs/*/run.log 2>/dev/null | cut -c1-160; cat /tmp/orch_t1.out
