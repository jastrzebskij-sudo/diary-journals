export PIPE_ROOT=/srv/tts-out/pipe-test; cd ~/diary-pipeline
python3 - <<'PY'
import importlib.util,sys,os
sp=importlib.util.spec_from_file_location("orch","/home/claude-agent/diary-pipeline/orch.py"); o=importlib.util.module_from_spec(sp); sp.loader.exec_module(o)
j=[x for x in o.jobs() if x["id"]=="test-pl-b"][0]; k1=o.key(j)
open("/tmp/t_pl2.txt","a").write("\nDodane zdanie.\n"); k2=o.key(j)
open("/tmp/t_pl2.txt","w").write(open("/tmp/t_pl2.txt").read().replace("\nDodane zdanie.\n","")); k3=o.key(j)
print("key before",k1,"after edit",k2,"after revert",k3, "-> edit changes key:",k1!=k2, "revert restores:",k1==k3)
PY
touch $PIPE_ROOT/STOP; python3 orch.py run; echo "run with STOP rc=$? (3 expected)"; rm $PIPE_ROOT/STOP
