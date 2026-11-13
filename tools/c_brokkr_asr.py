"""c_brokkr_asr.py - Whisper ASR with word timestamps (runs ON brokkr, venv ~/c-workstream/venv-asr, GPU 0).
Workstream C, 2026-11-12.  Usage:
  CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 ~/c-workstream/venv-asr/bin/python c_brokkr_asr.py IN.wav [IN2.wav ...] [--lang pl] [--out DIR]
Writes IN.asr.json next to each wav (or into --out): {file, model, lang, duration_s, text, words:[{w,start,end}]}.
Importable: from c_brokkr_asr import load_asr, transcribe.  Same model/runtime as loki's c_asr_check.py (whisper-medium, fp16, temperature 0).
Env C_ASR_FP32=1 selects fp32 (Pascal GPUs have weak fp16). Weights cached in ~/c-workstream/hf (offline after first download). No network service; files stay on brokkr."""
import argparse, json, os, sys
from pathlib import Path
os.environ.setdefault("HF_HOME", str(Path.home() / "c-workstream" / "hf"))
os.environ.setdefault("CUDA_DEVICE_ORDER", "PCI_BUS_ID"); os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
MODEL = "openai/whisper-medium"

def load_asr(model=MODEL):
    import torch
    from transformers import pipeline
    return pipeline("automatic-speech-recognition", model=model, dtype=(torch.float32 if os.environ.get("C_ASR_FP32") == "1" else torch.float16), device=0)

def read16k(path):
    import soundfile as sf
    y, sr = sf.read(str(path), dtype="float32")
    if y.ndim > 1: y = y.mean(axis=1)
    if sr != 16000:
        from scipy.signal import resample_poly
        from math import gcd
        g = gcd(16000, sr); y = resample_poly(y, 16000 // g, sr // g).astype("float32")
    return y

def transcribe(asr, path, lang="pl"):
    y = read16k(path); dur = len(y) / 16000
    kw = dict(return_timestamps="word", generate_kwargs={"language": lang, "task": "transcribe", "temperature": 0.0})
    if dur > 30: kw["chunk_length_s"] = 30
    r = asr({"raw": y, "sampling_rate": 16000}, **kw)
    words = [dict(w=c["text"].strip(), start=round(c["timestamp"][0], 2), end=round(c["timestamp"][1] if c["timestamp"][1] is not None else c["timestamp"][0], 2)) for c in r["chunks"]]
    return dict(file=os.path.basename(str(path)), model=MODEL, lang=lang, duration_s=round(dur, 2), text=r["text"].strip(), words=words)

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("wavs", nargs="+"); a.add_argument("--lang", default="pl"); a.add_argument("--out")
    o = a.parse_args(); asr = load_asr()
    for f in o.wavs:
        res = transcribe(asr, f, o.lang)
        dst = Path(o.out) / (Path(f).stem + ".asr.json") if o.out else Path(f).with_suffix(".asr.json")
        dst.parent.mkdir(parents=True, exist_ok=True); dst.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(dst, "|", res["text"][:80], flush=True)
