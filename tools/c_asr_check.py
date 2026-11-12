"""c_asr_check.py - transcribe narration audio back to text (Whisper) to expose TTS artifacts. Workstream C, 2026-11-12.
Usage (Assets venv python):  python c_asr_check.py WAV [WAV ...] [--model openai/whisper-medium] [--lang pl] [--csv out.csv]
For each file prints the transcript and per-word timestamps (start-end, s). Extra words, odd spellings or long words
around a TTS artifact show up here. ASR is itself imperfect: treat it as a hint, the ear decides. Model weights come from
Hugging Face on first use (cached under <assets>\\models\\hf). Originals only read."""
import argparse, csv, os, sys
a = argparse.ArgumentParser(); a.add_argument("wavs", nargs="+"); a.add_argument("--model", default="openai/whisper-medium")
a.add_argument("--lang", default="pl"); a.add_argument("--csv"); a.add_argument("--assets", default=r"D:\Claude\Assets\Diary")
o = a.parse_args()
os.environ.setdefault("HF_HOME", os.path.join(o.assets, "models", "hf"))
import torch, soundfile as sf, numpy as np
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", model=o.model, torch_dtype=torch.float16, device=0)
rows = []
for f in o.wavs:
    y, sr = sf.read(f, dtype="float32")
    if y.ndim > 1: y = y.mean(axis=1)
    if sr != 16000:
        import torchaudio.functional as AF
        y = AF.resample(torch.from_numpy(y), sr, 16000).numpy()
    r = asr({"raw": y, "sampling_rate": 16000}, return_timestamps="word", generate_kwargs={"language": o.lang, "task": "transcribe", "temperature": 0.0})
    print("==", os.path.basename(f)); print(r["text"].strip())
    print(" ".join(f"{c['text'].strip()}[{c['timestamp'][0]:.2f}-{(c['timestamp'][1] or 0):.2f}]" for c in r["chunks"]))
    rows += [(os.path.basename(f), c["text"].strip(), c["timestamp"][0], c["timestamp"][1]) for c in r["chunks"]]
if o.csv:
    with open(o.csv, "w", newline="", encoding="utf-8") as fh: w = csv.writer(fh); w.writerow(["file", "word", "start", "end"]); w.writerows(rows)
