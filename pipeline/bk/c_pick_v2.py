"""c_pick_v2.py (copy of c_brokkr_episode_pick.py with the empty-expectation guard) - step 2: Whisper-verified take pick + merge. Runs ON brokkr with ~/c-workstream/venv-asr, GPU 0.
  python c_brokkr_episode_pick.py DIR --lang pl|en
Reads DIR/chunks.json + take_*.wav/json from the render step. Transcribes every take (cached in the take JSON, so resumable),
score = word errors + 2 x extra words after the last expected word + 5 x |pace/median pace - 1| (same rule as loki's c_pick_takes.py,
which this reproduces). Best take per chunk, joined with --gap-sent (default 0.3 s) / --gap-para (default 0.7 s) gaps -> DIR/picked_all.wav (24 kHz) and
DIR/picked.json. STOP file honoured between takes (exit 3). Numbers: Whisper writes digits, so digit tokens are ignored in the hypothesis
and number words listed in NUMW (pl) are ignored in the expectation. Workstream C, 2026-11-12."""
import argparse, difflib, json, os, re, sys, time
from pathlib import Path
import numpy as np, soundfile as sf
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, os.path.expanduser('~/c-workstream'))
from c_brokkr_asr import load_asr, read16k
ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--lang", required=True, choices=["pl", "en"]); ap.add_argument("--gap-sent", type=float, default=0.3); ap.add_argument("--gap-para", type=float, default=0.7); a = ap.parse_args()
D = Path(a.dir); SR = 24000
stop = lambda: (D / "STOP").exists() or (Path.home() / "c-workstream" / "STOP").exists()
log = lambda *x: print(time.strftime("%H:%M:%S"), *x, flush=True)
NUMW = {"pierwszego", "tysiąc", "dziewięćset", "trzydziestego", "dziewiątego", "piętnastej", "jedenastej", "trzeciego", "iii"} if a.lang == "pl" else set("first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth fourteenth fifteenth one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand oh o'clock".split())
norm = lambda s: [w for w in re.findall(r"[\wąćęłńóśźż']+", s.lower()) if not w.isdigit() and w not in NUMW]
sim = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()
def score(exp, hyp):
    n, k = len(exp), len(hyp); INF = 1e9
    if n == 0: return float(k), 0   # v2: expected text normalises to nothing (all number words); the v1 code crashed here (IndexError on exp[-1])
    d = np.full((n + 1, k + 1), INF); d[0, 0] = 0
    for i in range(n + 1):
        for j in range(k + 1):
            if i < n and j < k: d[i + 1, j + 1] = min(d[i + 1, j + 1], d[i, j] + (0 if sim(exp[i], hyp[j]) >= 0.8 else 1))
            if i < n: d[i + 1, j] = min(d[i + 1, j], d[i, j] + 1)
            if j < k: d[i, j + 1] = min(d[i, j + 1], d[i, j] + 1)
    errs = d[n, k]; last = 0
    for j in range(k):
        if sim(exp[-1], hyp[j]) >= 0.8: last = j + 1
    return float(errs), (max(0, k - last) if last else 0)
cj = json.loads((D / "chunks.json").read_text(encoding="utf-8")); chunks = cj["chunks"]; K = cj["takes"]
asr = load_asr(); asr_s = 0.0
for c in chunks:
    et = c["text"]
    for sp, wr in cj.get("names", []): et = et.replace(sp, wr)   # spoken respelling -> the spelling Whisper writes
    exp = norm(et); c["takes"] = []
    for k in range(K):
        jp = D / f"take_s{c['index']:02d}_t{k}.json"; t = json.loads(jp.read_text(encoding="utf-8"))
        if "asr" not in t:
            if stop(): log("STOP file found, exiting cleanly"); sys.exit(3)
            t0 = time.time(); y = read16k(D / f"take_s{c['index']:02d}_t{k}.wav")
            t["asr"] = asr({"raw": y, "sampling_rate": 16000}, generate_kwargs={"language": a.lang, "task": "transcribe", "temperature": 0.0})["text"].strip()
            t["asr_s"] = round(time.time() - t0, 2); jp.write_text(json.dumps(t, ensure_ascii=False), encoding="utf-8")
        asr_s += t.get("asr_s", 0); c["takes"].append(t)
med = float(np.median([t["chars_per_s"] for c in chunks for t in c["takes"] if t["chars_per_s"]]))
for c in chunks:
    et = c["text"]
    for sp, wr in cj.get("names", []): et = et.replace(sp, wr)
    exp = norm(et)
    for t in c["takes"]:
        e, x = score(exp, norm(t["asr"])); t.update(word_errors=e, extra_words=x, pick_score=round(e + 2 * x + 5 * abs(t["chars_per_s"] / med - 1), 2))
    c["picked"] = min(c["takes"], key=lambda t: t["pick_score"])["take"]; p = c["takes"][c["picked"]]
    log(c["index"], "pick", c["picked"], "errs", p["word_errors"], "extra", p["extra_words"], "| clean", sum(1 for t in c["takes"] if t["word_errors"] == 0 and t["extra_words"] == 0), "/", K, "|", c["text"][:36])
parts = []; prev = 0
for c in chunks:
    w, _ = sf.read(D / f"take_s{c['index']:02d}_t{c['picked']}.wav", dtype="float32")
    if c["index"]: parts.append(np.zeros(int(SR * (a.gap_para if c["paragraph"] != prev else a.gap_sent)), dtype="float32"))
    parts.append(w); prev = c["paragraph"]
sf.write(D / "picked_all.wav", np.concatenate(parts), SR, subtype="PCM_16")
cj.update(gap_sentence_s=a.gap_sent, gap_paragraph_s=a.gap_para, chunks=chunks, median_chars_per_s=round(med, 2), asr_seconds=round(asr_s, 1)); (D / "picked.json").write_text(json.dumps(cj, indent=1, ensure_ascii=False), encoding="utf-8")
log("picks", [c["picked"] for c in chunks]); log("wrote", D / "picked_all.wav")
