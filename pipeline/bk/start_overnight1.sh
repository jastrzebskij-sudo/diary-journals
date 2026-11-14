set -e
mkdir -p ~/diary-pipeline/jobs; cp /tmp/ov1/*.txt /tmp/ov1/overnight1.json ~/diary-pipeline/jobs/
cd ~/diary-pipeline; python3 orch.py add jobs/overnight1.json
setsid nohup python3 orch.py run > /srv/tts-out/pipe/orch_run1.out 2>&1 < /dev/null &
sleep 4; python3 orch.py status | sed -n 4,12p
