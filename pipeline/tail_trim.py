#!/usr/bin/env python3
"""tail_trim.py - remove XTTS trailing garbage (the extra mumbled word after a sentence's last real word) from the PICKED takes of a job.
Usage (on brokkr): CUDA_VISIBLE_DEVICES=0 ~/c-workstream/venv-asr/bin/python tail_trim.py JOBDIR --lang pl|en [--semi -1.0 --bass 2] [--pad 0.02]
For each chunk: Whisper word timestamps on the picked take -> end of the last word that matches the expected last word -> cut at the quietest 10 ms frame
in [word_end-0.04, word_end+0.35] s (a pause, not mid-phoneme), 30 ms fade-out. Rebuilds picked_all_trim.wav with the job's gaps (and, if --semi/--bass given,
the deepen as stage 3 of ep_audio.sh) -> final_trim/. Writes trim_report.json (per chunk: cut seconds, anchor, 'no-anchor' where the last word was not found).
Originals are never modified. Added 2026-11-14 (Jim heard garbage after 'wina' in ep01 PL tail; all 8 takes of that sentence had it)."""
import argparse, difflib, json, os, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.expanduser("~/c-workstream"))
from c_brokkr_asr import load_asr, transcribe
ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--lang", required=True); ap.add_argument("--semi", type=float, default=0.0)
ap.add_argument("--bass", type=float, default=0.0); a = ap.parse_args()
D = Path(a.dir); P = json.loads((D / "picked.json").read_text(encoding="utf-8")); SR = 24000
norm = lambda s: [w for w in re.findall(r"[\wąćęłńóśźż']+", s.lower()) if not w.isdigit()]
sim = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()
asr = load_asr(); parts = []; prev = 0; rep = []
for c in P["chunks"]:
    i, k = c["index"], c["picked"]; w, _ = sf.read(D / f"take_s{i:02d}_t{k}.wav", dtype="float32"); dur = len(w) / SR
    et = c["text"]
    for sp, wr in P.get("names", []): et = et.replace(sp, wr)
    exp = norm(et); info = dict(index=i, text=c["text"][:60], dur=round(dur, 2), cut_to=round(dur, 2), status="kept")
    if exp:
        res = transcribe(asr, D / f"take_s{i:02d}_t{k}.wav", a.lang); words = res["words"]
        hits = [j for j, wd in enumerate(words) if (norm(wd["w"]) and sim(exp[-1], norm(wd["w"])[0]) >= 0.8)]
        if hits:
            j = hits[-1]; wend = words[j]["end"]
            if wend < dur - 0.25:                      # something follows the last expected word
                lo, hi = max(0, wend - 0.04), min(dur, wend + 0.35); fr = int(0.01 * SR)
                rms = [(float(np.sqrt(np.mean(w[s:s + fr] ** 2))), s) for s in range(int(lo * SR), int(hi * SR) - fr, fr)]
                cut = min(rms)[1] if rms else int(wend * SR)
                w = w[:cut].copy(); f = int(0.03 * SR); w[-f:] *= np.linspace(1, 0, f)
                info.update(cut_to=round(len(w) / SR, 2), status="trimmed", removed=round(dur - len(w) / SR, 2), anchor=words[j]["w"], after=" ".join(x["w"] for x in words[j + 1:]))
        else: info.update(status="no-anchor", asr=res["text"])
    rep.append(info)
    if i: parts.append(np.zeros(int(SR * (P["gap_paragraph_s"] if c["paragraph"] != prev else P["gap_sentence_s"])), dtype="float32"))
    parts.append(w); prev = c["paragraph"]
allw = np.concatenate(parts); sf.write(D / "picked_all_trim.wav", allw, SR, subtype="PCM_16")
(D / "trim_report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
out = D / "final_trim"; out.mkdir(exist_ok=True); name = D.name.split("-")[0] if False else "trim"
if a.semi or a.bass:
    ratio = 2 ** (a.semi / 12); af = f"rubberband=pitch={ratio}:formant=shifted:pitchq=quality,bass=g={a.bass}:f=160:w=0.7"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(D / "picked_all_trim.wav"), "-af", af, "-ar", "24000", str(out / "narration_trim.wav")], check=True)
else: subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(D / "picked_all_trim.wav"), "-ar", "24000", str(out / "narration_trim.wav")], check=True)
for r in rep: print(r["index"], r["status"], r["dur"], "->", r["cut_to"], r.get("anchor", ""), "| after:", r.get("after", ""), "|", r["text"][:40])
