"""c_brokkr_page_takes.py - take-based XTTS-v2 page renderer with measured sentence tails (runs ON brokkr, in ~/work/tts,
.venv python, GPU 1). Workstream C, 2026-11-11. Uses scripts/common.py of the tts repo (model, chunking, digit guard).

  variants: python c_brokkr_page_takes.py variants LATENT VARIANTS.txt OUT_DIR [--takes 2]
            one line per text variant -> OUT_DIR/variant_NN.wav (takes joined by 0.8 s silence) + metrics printed.
  render:   python c_brokkr_page_takes.py render LATENT TEXT.txt OUT_DIR [--takes 4] [--seed 1000] [--respell OLD=NEW ...] [--merge N ...]
            per sentence renders N takes (seed = seed + 100*sentence + take, recorded), measures each take and picks the
            best (lowest tail + pace outlier penalty), joins chosen takes with 0.3 s (sentence) / 0.7 s (paragraph) gaps.
            --merge N renders 0-based sentence N together with the next one as one chunk (so a word that triggers an end-of-chunk artifact is not last).
            Writes take_sNN_tK.wav, chosen_all.wav and manifest.json (text, seeds, metrics, chosen take, model, date).

Metrics per take (10 ms frames): tail_ms = time between the last frame above -28 dB and the last above -45 dB
(low-level trailing junk such as breaths/hum/extra sounds); head_ms likewise; chars_per_s = pace. Final trim keeps speech to the
last frame above -38 dB plus 80 ms and fades 30 ms, so faint end-of-sentence glitches are cut. Originals are only read."""
import argparse, datetime, json, sys
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, "scripts")
import common
SR = common.SAMPLE_RATE; F = SR // 100

def dbs(w):
    n = len(w) // F
    r = np.sqrt((w[: n * F].reshape(n, F) ** 2).mean(axis=1)) + 1e-9
    return 20 * np.log10(r)

def metrics(w, chars):
    d = dbs(w); l45 = np.flatnonzero(d > -45); l28 = np.flatnonzero(d > -28)
    if not len(l45) or not len(l28):
        return dict(tail_ms=9999, head_ms=9999, dur_s=len(w) / SR, chars_per_s=0)
    dur = (l45[-1] - l45[0] + 1) / 100
    return dict(tail_ms=int((l45[-1] - l28[-1]) * 10), head_ms=int((l28[0] - l45[0]) * 10),
                dur_s=round(dur, 2), chars_per_s=round(chars / dur, 2))

def final_trim(w):
    d = dbs(w); l = np.flatnonzero(d > -45); l38 = np.flatnonzero(d > -38)
    s = max(0, (l[0] - 2) * F); e = min(len(w), (l38[-1] + 1 + 8) * F)
    o = w[s:e].copy(); k = min(int(0.03 * SR), len(o) // 2); o[-k:] *= np.linspace(1, 0, k, dtype="float32"); o[:k // 3] *= np.linspace(0, 1, k // 3, dtype="float32")
    return o

def take(model, text, cond, emb, seed):
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    w, _ = common.synth(model, text, "pl", cond, emb)
    return np.asarray(w, dtype="float32")

ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["variants", "render"]); ap.add_argument("latent")
ap.add_argument("text"); ap.add_argument("out"); ap.add_argument("--takes", type=int, default=None)
ap.add_argument("--seed", type=int, default=1000); ap.add_argument("--merge", type=int, nargs="*", default=[]); ap.add_argument("--respell", nargs="*", default=[])
a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
common.require_tos()
model = common.load_model(); cond, emb = common.load_voice(model, a.latent)
if a.mode == "variants":
    K = a.takes or 2
    for i, line in enumerate([l.strip() for l in Path(a.text).read_text(encoding="utf-8").splitlines() if l.strip()], 1):
        common.require_no_digits(line, "pl"); parts = []
        for k in range(K):
            w = take(model, line, cond, emb, a.seed + 10 * i + k); m = metrics(w, len(line)); print(i, k, m, line[-40:], flush=True)
            parts += [final_trim(w), common.silence(0.8)]
        common.save_wav(out / f"variant_{i:02d}.wav", np.concatenate(parts[:-1]))
else:
    K = a.takes or 4
    raw = Path(a.text).read_text(encoding="utf-8-sig")
    for r in a.respell:
        o, n = r.split("=", 1); assert o in raw, f"respell target not found: {o}"; raw = raw.replace(o, n)
    paras = [" ".join(p.split()) for p in raw.split("\n\n") if p.strip()]; common.require_no_digits(raw, "pl")
    lim = common.model_char_limit(model, "pl"); sents = []
    for pi, p in enumerate(paras):
        for s in common.split_sentences(p, "pl", lim): sents.append((pi, s))
    for mi in sorted(a.merge, reverse=True):          # --merge N: render sentence N together with the next one (same paragraph) as one chunk
        assert sents[mi][0] == sents[mi + 1][0], "can only merge within a paragraph"
        sents[mi] = (sents[mi][0], sents[mi][1] + " " + sents[mi + 1][1]); del sents[mi + 1]
        assert len(sents[mi][1]) <= lim, "merged chunk is over the model char limit"
    allm = []; rec = []
    for si, (pi, s) in enumerate(sents):
        tk = []
        for k in range(K):
            seed = a.seed + 100 * si + k; w = take(model, s, cond, emb, seed); m = metrics(w, len(s))
            common.save_wav(out / f"take_s{si:02d}_t{k}.wav", final_trim(w)); tk.append(dict(take=k, seed=seed, **m)); allm.append(m["chars_per_s"])
        rec.append(dict(index=si, paragraph=pi, text=s, takes=tk)); print("sentence", si, "done", flush=True)
    med = float(np.median([x for x in allm if x]))
    for r in rec:
        for t in r["takes"]: t["score"] = round(t["tail_ms"] + 800 * abs(t["chars_per_s"] / med - 1) if t["chars_per_s"] else 99999, 1)
        r["chosen"] = min(r["takes"], key=lambda t: t["score"])["take"]
    parts = []; prev_p = 0
    for r in rec:
        w, _ = __import__("soundfile").read(out / f"take_s{r['index']:02d}_t{r['chosen']}.wav", dtype="float32")
        if r["index"]: parts.append(common.silence(0.7 if r["paragraph"] != prev_p else 0.3))
        parts.append(w); prev_p = r["paragraph"]
    common.save_wav(out / "chosen_all.wav", np.concatenate(parts))
    (out / "manifest.json").write_text(json.dumps(dict(script="c_brokkr_page_takes.py", date=datetime.datetime.now().isoformat(timespec="seconds"),
        model="XTTS-v2 fp32 GPU1", latent=a.latent, text=a.text, respell=a.respell, merge=a.merge, takes=K, median_chars_per_s=round(med, 2),
        sentences=rec), indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", out / "chosen_all.wav", "chosen:", [r["chosen"] for r in rec])
