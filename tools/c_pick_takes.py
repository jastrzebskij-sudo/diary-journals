"""c_pick_takes.py - ASR-verified take selection and assembly for a take-rendered page. Workstream C, 2026-11-12.
Usage (Assets venv python, run on loki):  python c_pick_takes.py TAKES_DIR [--model openai/whisper-medium]
TAKES_DIR holds manifest.json and take_sNN_tK.wav from c_brokkr_page_takes.py (copied from brokkr). Every take is
transcribed with Whisper; its words are aligned to the expected sentence (fuzzy word match so the diary's old spellings
still match). Score = word errors + 2 x extra words after the last expected word (the 'foreign name after the sentence'
artifact) + pace outlier penalty. Best take per sentence is chosen; chosen takes are joined with 0.3 s (sentence) and
0.7 s (paragraph) gaps -> TAKES_DIR\\picked_all.wav. Writes picked.json (per take: transcript, errors, extras, score)."""
import argparse, difflib, json, os, re
from pathlib import Path
import numpy as np, soundfile as sf
a = argparse.ArgumentParser(); a.add_argument("dir"); a.add_argument("--model", default="openai/whisper-medium")
a.add_argument("--assets", default=r"D:\Claude\Assets\Diary"); o = a.parse_args()
os.environ.setdefault("HF_HOME", os.path.join(o.assets, "models", "hf"))
import torch, torchaudio.functional as AF
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", model=o.model, torch_dtype=torch.float16, device=0)
D = Path(o.dir); m = json.loads((D / "manifest.json").read_text(encoding="utf-8")); SR = 24000
NUMW = {"pierwszego", "tysiąc", "dziewięćset", "trzydziestego", "dziewiątego", "piętnastej", "jedenastej", "trzeciego", "iii"}
norm = lambda s: [w for w in re.findall(r"[\wąćęłńóśźż]+", s.lower()) if not w.isdigit() and w not in NUMW]  # Whisper writes numbers as digits/roman, so number words are ignored
sim = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()
def score(exp, hyp):
    n, k = len(exp), len(hyp); INF = 1e9
    d = np.full((n + 1, k + 1), INF); d[0, 0] = 0
    for i in range(n + 1):
        for j in range(k + 1):
            if i < n and j < k: d[i + 1, j + 1] = min(d[i + 1, j + 1], d[i, j] + (0 if sim(exp[i], hyp[j]) >= 0.8 else 1))
            if i < n: d[i + 1, j] = min(d[i + 1, j], d[i, j] + 1)
            if j < k: d[i, j + 1] = min(d[i, j + 1], d[i, j] + 1)
    errs = d[n, k]; last = 0
    for j in range(k):                                   # extra words after the last hypothesis word matching the final expected word
        if sim(exp[-1], hyp[j]) >= 0.8: last = j + 1
    extra = max(0, k - last) if last else 0
    return float(errs), extra
allrate = [t["chars_per_s"] for s in m["sentences"] for t in s["takes"] if t["chars_per_s"]]; med = float(np.median(allrate))
for s in m["sentences"]:
    exp = norm(s["text"])
    for t in s["takes"]:
        y, sr = sf.read(D / f"take_s{s['index']:02d}_t{t['take']}.wav", dtype="float32")
        y = AF.resample(torch.from_numpy(y), sr, 16000).numpy()
        txt = asr({"raw": y, "sampling_rate": 16000}, generate_kwargs={"language": "pl", "task": "transcribe", "temperature": 0.0})["text"].strip()
        e, x = score(exp, norm(txt)); t.update(asr=txt, word_errors=e, extra_words=x,
            pick_score=round(e + 2 * x + 5 * abs(t["chars_per_s"] / med - 1), 2))
    s["picked"] = min(s["takes"], key=lambda t: t["pick_score"])["take"]
    p = s["takes"][s["picked"]]; print(s["index"], "pick", s["picked"], "errs", p["word_errors"], "extra", p["extra_words"],
        "| clean takes:", sum(1 for t in s["takes"] if t["word_errors"] == 0 and t["extra_words"] == 0), "/", len(s["takes"]), "|", s["text"][:36], flush=True)
parts = []; prev = 0
for s in m["sentences"]:
    w, _ = sf.read(D / f"take_s{s['index']:02d}_t{s['picked']}.wav", dtype="float32")
    if s["index"]: parts.append(np.zeros(int(SR * (0.7 if s["paragraph"] != prev else 0.3)), dtype="float32"))
    parts.append(w); prev = s["paragraph"]
sf.write(D / "picked_all.wav", np.concatenate(parts), SR, subtype="PCM_16")
(D / "picked.json").write_text(json.dumps(m, indent=1, ensure_ascii=False), encoding="utf-8"); print("wrote", D / "picked_all.wav")
