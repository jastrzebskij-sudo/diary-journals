#!/usr/bin/env python3
"""orch.py - Diary pipeline orchestrator v0 (PIPELINE-SPEC sections 4, 6, 7). Runs ON brokkr. stdlib only. No AI tokens.
Wraps the proven audio path (ep_audio.sh = render takes -> Whisper pick -> deepen) in: a queue, content-keyed output dirs, an append-only ledger,
a single-writer lock with heartbeat, STOP file, retry, and an atomically written status (status.json + STATUS-PIPELINE.md).
  orch.py add JOBS.json      append jobs (a JSON list; each: id, kind=audio, lang, text, name, takes, seed, names?, extra?[list])
  orch.py run                process the queue (exit 0 all done/failed-marked, 3 STOP, 4 another orchestrator holds the lock)
  orch.py status             print STATUS-PIPELINE.md
Output dir of a job = ROOT/jobs/<id>-<key> where key = hash(text bytes + names bytes + recipe + takes + seed + extra): edit the text and the job
gets a NEW dir (old one is kept); unchanged jobs are skipped because their dir has DONE. A killed run resumes (ep_audio.sh is resumable per take/step).
Stop cleanly: touch ROOT/STOP. Recipes are frozen in recipes.json (PL/EN); a job cannot override them."""
import fcntl, hashlib, json, os, subprocess, sys, threading, time
from pathlib import Path
ROOT = Path(os.environ.get("PIPE_ROOT", "/srv/tts-out/pipe")); CODE = Path(__file__).resolve().parent
QUEUE, LEDGER, LOCK, HB, STOP = ROOT/"queue.jsonl", ROOT/"ledger.jsonl", ROOT/"orch.lock", ROOT/"heartbeat", ROOT/"STOP"
RECIPES = json.loads((CODE/"recipes.json").read_text(encoding="utf-8"))
AUDIO = os.environ.get("PIPE_AUDIO_SH", str(Path.home()/"diary-pipeline"/"ep_audio.sh"))
now = lambda: time.strftime("%Y-%m-%dT%H:%M:%S")
def atomic(path, text):
    tmp = Path(str(path) + ".tmp"); tmp.write_text(text, encoding="utf-8"); os.replace(tmp, path)
def ledger(ev, **kw):
    with open(LEDGER, "a", encoding="utf-8") as f: f.write(json.dumps(dict(ts=now(), ev=ev, **kw), ensure_ascii=False) + "\n"); f.flush(); os.fsync(f.fileno())
def jobs():
    out = {}
    if QUEUE.exists():
        for ln in QUEUE.read_text(encoding="utf-8").splitlines():
            if ln.strip(): j = json.loads(ln); out[j["id"]] = j       # a later line with the same id replaces the earlier one
    return list(out.values())
def key(j):
    h = hashlib.sha256()
    for p in (j["text"], j.get("names")):
        if p: h.update(Path(p).read_bytes())
    h.update(json.dumps([RECIPES[j["lang"]], j.get("takes", 8), j.get("seed", 5000), j.get("extra", [])], sort_keys=True).encode())
    return h.hexdigest()[:10]
def outdir(j): return ROOT/"jobs"/f"{j['id']}-{key(j)}"
def state(j):
    o = outdir(j)
    if (o/"DONE").exists(): return "done"
    if (o/"FAILED").exists(): return "failed"
    return "todo"
def flags(j):
    m = list((outdir(j)/"final").glob("*.manifest.json")); n = []
    if m:
        for c in json.loads(m[0].read_text(encoding="utf-8")).get("chunks", []):
            if (c.get("word_errors") or 0) >= 2 or c.get("clean_takes", 1) == 0: n.append(f"s{c['index']} errs={c.get('word_errors')} {c['text'][:70]}")
    return n
def write_status(cur=None):
    rows, js = [], jobs()
    for j in js:
        s = "running" if cur == j["id"] else state(j); fl = flags(j) if s == "done" else []
        rows.append(dict(id=j["id"], lang=j["lang"], state=s, key=key(j), flags=len(fl)))
    st = dict(updated=now(), host=os.uname().nodename, current=cur, counts={k: sum(1 for r in rows if r["state"] == k) for k in ("todo", "running", "done", "failed")}, jobs=rows)
    atomic(ROOT/"status.json", json.dumps(st, indent=1))
    L = ["---\ntitle: Pipeline status\n---", f"# Pipeline status (orchestrator v0, {st['host']})", f"Updated {st['updated']} | {st['counts']} | current: {cur}", "",
         "| job | lang | state | key | flagged chunks |", "|---|---|---|---|---|"] + [f"| {r['id']} | {r['lang']} | {r['state']} | {r['key']} | {r['flags']} |" for r in rows]
    for j in js:
        if state(j) == "done" and flags(j): L += ["", f"### Flags: {j['id']}"] + [f"- {x}" for x in flags(j)]
    tail = LEDGER.read_text(encoding="utf-8").splitlines()[-12:] if LEDGER.exists() else []
    L += ["", "### Recent ledger"] + [f"- `{x}`" for x in tail]
    atomic(ROOT/"STATUS-PIPELINE.md", "\n".join(L) + "\n")
def run_job(j):
    o = outdir(j); o.mkdir(parents=True, exist_ok=True); r = RECIPES[j["lang"]]
    env = dict(os.environ, DEEPEN_ST=str(r["deepen_st"]), DEEPEN_BASS=str(r["bass"]), GAP_S=str(r["gap_s"]), GAP_P=str(r["gap_p"]))
    extra = ["--takes", str(j.get("takes", 8)), "--seed", str(j.get("seed", 5000))] + ([ "--names", j["names"]] if j.get("names") else []) + j.get("extra", [])
    cmd = ["bash", AUDIO, j["lang"], j["text"], str(o), j["name"], r["latent"]] + extra
    for attempt in (1, 2, 3):
        if STOP.exists(): return "stop"
        ledger("start", job=j["id"], key=key(j), attempt=attempt); write_status(j["id"]); t0 = time.time()
        with open(o/"job.log", "ab") as lf: rc = subprocess.run(cmd, env=env, stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL).returncode
        ledger("end", job=j["id"], key=key(j), attempt=attempt, rc=rc, wall_s=round(time.time() - t0, 1)); write_status(j["id"])
        if rc == 3: return "stop"
        if rc == 0 and list((o/"final").glob("*.wav")): (o/"DONE").write_text(key(j)); return "done"
        time.sleep(15)
    (o/"FAILED").write_text(key(j)); return "failed"
def cmd_run():
    ROOT.mkdir(parents=True, exist_ok=True); (ROOT/"jobs").mkdir(exist_ok=True)
    lk = open(LOCK, "w")
    try: fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError: print("another orchestrator holds the lock; exiting", file=sys.stderr); return 4
    lk.write(f"{os.getpid()} {now()}\n"); lk.flush(); alive = True
    def beat():
        while alive: atomic(HB, f"{now()} pid {os.getpid()}\n"); time.sleep(30)
    threading.Thread(target=beat, daemon=True).start(); ledger("orch_start", pid=os.getpid()); write_status(); rc = 0
    for j in jobs():
        if STOP.exists(): rc = 3; break
        if state(j) != "todo": ledger("skip", job=j["id"], why=state(j)); continue
        res = run_job(j); write_status()
        if res == "stop": rc = 3; break
    ledger("orch_stop", rc=rc); write_status(); alive = False; return rc
if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "add":
        ROOT.mkdir(parents=True, exist_ok=True)
        with open(QUEUE, "a", encoding="utf-8") as f:
            for j in json.load(open(sys.argv[2], encoding="utf-8")):
                assert j["lang"] in RECIPES and Path(j["text"]).exists(), j; f.write(json.dumps(j, ensure_ascii=False) + "\n"); ledger("queued", job=j["id"])
        write_status()
    elif c == "run": sys.exit(cmd_run())
    elif c == "status": write_status(); print((ROOT/"STATUS-PIPELINE.md").read_text(encoding="utf-8"))
    else: print(__doc__); sys.exit(2)
