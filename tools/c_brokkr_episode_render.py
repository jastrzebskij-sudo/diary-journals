"""c_brokkr_episode_render.py - step 1 of the episode audio pipeline: sentence chunks -> N XTTS takes per chunk.
Runs ON brokkr with the XTTS venv (~/work/tts/.venv), GPU 1, cwd ~/work/tts. Workstream C, 2026-11-12. No AI tokens.
  python c_brokkr_episode_render.py --lang pl|en --latent LATENT.pth --text TEXT.txt --out DIR [--takes 8] [--seed 5000] [--merge N ...] [--respell OLD=NEW ...]
Chunking = blank-line paragraphs -> one chunk per sentence (never split inside a sentence; > model char limit is an error).
--names FILE: Spoken=Written pairs for ASR comparison. --merge N (0-based sentence index) renders sentence N together with the next one. Seed per take = seed + 100*chunk + take.
Resumable: a take is skipped when take_sNN_tK.wav and .json exist. STOP file in DIR (or ~/c-workstream/STOP) ends the run cleanly
after the current take (exit 3). Each take JSON holds seed, tail/head/pace metrics and synth seconds (for throughput).
Metrics and final_trim are identical to c_brokkr_page_takes.py, so picks reproduce."""
import argparse, json, sys, time
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, "scripts")
import common
SR = common.SAMPLE_RATE; F = SR // 100

def dbs(w):
    n = len(w) // F
    return 20 * np.log10(np.sqrt((w[: n * F].reshape(n, F) ** 2).mean(axis=1)) + 1e-9)

def metrics(w, chars):
    d = dbs(w); l45 = np.flatnonzero(d > -45); l28 = np.flatnonzero(d > -28)
    if not len(l45) or not len(l28): return dict(tail_ms=9999, head_ms=9999, dur_s=len(w) / SR, chars_per_s=0)
    dur = (l45[-1] - l45[0] + 1) / 100
    return dict(tail_ms=int((l45[-1] - l28[-1]) * 10), head_ms=int((l28[0] - l45[0]) * 10), dur_s=round(dur, 2), chars_per_s=round(chars / dur, 2))

def final_trim(w):
    d = dbs(w); l = np.flatnonzero(d > -45); l38 = np.flatnonzero(d > -38)
    s = max(0, (l[0] - 2) * F); e = min(len(w), (l38[-1] + 1 + 8) * F)
    o = w[s:e].copy(); k = min(int(0.03 * SR), len(o) // 2); o[-k:] *= np.linspace(1, 0, k, dtype="float32"); o[:k // 3] *= np.linspace(0, 1, k // 3, dtype="float32")
    return o

ap = argparse.ArgumentParser(); ap.add_argument("--lang", required=True, choices=["pl", "en"]); ap.add_argument("--latent", required=True)
ap.add_argument("--text", required=True); ap.add_argument("--out", required=True); ap.add_argument("--takes", type=int, default=8)
ap.add_argument("--seed", type=int, default=5000); ap.add_argument("--merge", type=int, nargs="*", default=[]); ap.add_argument("--respell", nargs="*", default=[])
ap.add_argument("--names", help="file of Spoken=Written pairs (from c_tts_prep_en.py OUT.names.txt); stored in chunks.json so the ASR pick compares against the written spelling")
a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
stop = lambda: (out / "STOP").exists() or (Path.home() / "c-workstream" / "STOP").exists()
log = lambda *x: print(time.strftime("%H:%M:%S"), *x, flush=True)
raw = Path(a.text).read_text(encoding="utf-8-sig").replace("\r\n", "\n")
for r in a.respell:
    o, n = r.split("=", 1); assert o in raw, f"respell target not found: {o}"; raw = raw.replace(o, n)
common.require_no_digits(raw, a.lang)
common.require_tos(); model = common.load_model(); lim = common.model_char_limit(model, a.lang)
paras = [" ".join(p.split()) for p in raw.split("\n\n") if p.strip()]; sents = []
for pi, p in enumerate(paras):
    for s in common.split_sentences(p, a.lang, lim): sents.append((pi, s))
for mi in sorted(a.merge, reverse=True):
    assert sents[mi][0] == sents[mi + 1][0], "can only merge within a paragraph"
    sents[mi] = (sents[mi][0], sents[mi][1] + " " + sents[mi + 1][1]); del sents[mi + 1]
    assert len(sents[mi][1]) <= lim, f"merged chunk over char limit {lim}"
chunks = [dict(index=i, paragraph=pi, text=s, chars=len(s)) for i, (pi, s) in enumerate(sents)]
(out / "chunks.json").write_text(json.dumps(dict(lang=a.lang, char_limit=lim, latent=a.latent, text=a.text, takes=a.takes, seed=a.seed, merge=a.merge, respell=a.respell, names=[l.split("=", 1) for l in Path(a.names).read_text(encoding="utf-8").splitlines() if "=" in l] if a.names else [], chunks=chunks), indent=1, ensure_ascii=False), encoding="utf-8")
log("chunks", len(chunks), "limit", lim, "takes", a.takes)
cond, emb = common.load_voice(model, a.latent)
for c in chunks:
    for k in range(a.takes):
        base = out / f"take_s{c['index']:02d}_t{k}"
        if base.with_suffix(".wav").exists() and base.with_suffix(".json").exists(): continue
        if stop(): log("STOP file found, exiting cleanly"); sys.exit(3)
        seed = a.seed + 100 * c["index"] + k; torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        w, secs = common.synth(model, c["text"], a.lang, cond, emb); w = np.asarray(w, dtype="float32"); m = metrics(w, c["chars"])
        common.save_wav(base.with_suffix(".wav"), final_trim(w))
        base.with_suffix(".json").write_text(json.dumps(dict(take=k, seed=seed, synth_s=round(secs, 2), raw_s=round(len(w) / SR, 2), **m)), encoding="utf-8")
        log(f"s{c['index']:02d} t{k} seed {seed} synth {secs:.1f}s audio {m['dur_s']}s")
log("render complete")
