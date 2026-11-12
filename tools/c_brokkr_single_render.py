#!/usr/bin/env python
# c_brokkr_single_render.py - EXPERIMENT: render text with NO sentence chunking, to compare against the
# sentence-by-sentence pipeline (c_brokkr_page_takes.py). Bypasses the 250-char limit check on purpose.
# Usage (on brokkr, from ~/work/tts):  python c_brokkr_single_render.py LATENT TEXT.txt OUT_DIR [--seed 5000]
# Writes OUT_DIR/single_para_P.wav (each paragraph as ONE chunk), OUT_DIR/single_page.wav (whole page as ONE chunk)
# and OUT_DIR/manifest.json (model, latent, seed, char counts, durations, any error per job).
import argparse, datetime, json, sys
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, "scripts")
import common

ap = argparse.ArgumentParser(); ap.add_argument("latent"); ap.add_argument("text"); ap.add_argument("out")
ap.add_argument("--seed", type=int, default=5000)
a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
raw = Path(a.text).read_text(encoding="utf-8").replace("\r\n", "\n")
common.require_no_digits(raw, "pl")
paras = [" ".join(p.split()) for p in raw.split("\n\n") if p.strip()]
jobs = [(f"single_para_{i}", p) for i, p in enumerate(paras, 1)] + [("single_page", " ".join(paras))]
model = common.load_model(); cond, emb = common.load_voice(model, a.latent)
lim = common.model_char_limit(model, "pl"); rec = []
for name, text in jobs:
    r = dict(name=name, chars=len(text), char_limit=lim)
    try:
        torch.manual_seed(a.seed); torch.cuda.manual_seed_all(a.seed)
        w, dt = common.synth(model, text, "pl", cond, emb)
        w = common.trim_silence(np.asarray(w, dtype="float32"), -38.0, 0.08, 0.03)
        common.save_wav(out / f"{name}.wav", w); r.update(dur_s=round(len(w) / common.SAMPLE_RATE, 2), gen_s=round(dt, 1))
    except Exception as e:
        r.update(error=repr(e)[:300])
    print(r, flush=True); rec.append(r)
json.dump(dict(model="XTTS-v2 fp32 GPU1", latent=a.latent, text=a.text, seed=a.seed, no_chunking=True,
               date=datetime.datetime.now().isoformat(timespec="seconds"), jobs=rec),
          open(out / "manifest.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)