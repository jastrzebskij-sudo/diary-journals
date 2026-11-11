"""Shared helpers for the XTTS-v2 scripts (fp32, GPU index 1, model cache under ./models)."""
import os
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Must be set before torch initialises CUDA.
os.environ.setdefault("CUDA_DEVICE_ORDER", "PCI_BUS_ID")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "1")
os.environ.setdefault("TTS_HOME", str(ROOT / "models"))
os.environ.setdefault("HF_HOME", str(ROOT / "models" / "hf"))

import torch  # noqa: E402
import soundfile as sf  # noqa: E402

MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
SAMPLE_RATE = 24000
OUT_ROOT = Path(os.environ.get("TTS_OUT", "/srv/tts-out"))


def require_tos():
    if os.environ.get("COQUI_TOS_AGREED") != "1":
        raise SystemExit("Set COQUI_TOS_AGREED=1 (Coqui Public Model License) to download/use XTTS-v2.")


def load_model():
    """Return the raw Xtts model on cuda, fp32."""
    require_tos()
    from TTS.api import TTS

    tts = TTS()
    tts.load_tts_model_by_name(MODEL_NAME, gpu=True)
    import TTS.tts.models.xtts as xtts_mod

    xtts_mod.load_audio = _load_audio_sf
    model = tts.synthesizer.tts_model
    model.float()
    model.eval()  # Xtts.eval() returns None, so don't chain
    return model


def _load_audio_sf(audiopath, sampling_rate):
    """soundfile-based replacement for TTS's torchaudio loader (torchaudio 2.11 needs torchcodec + system ffmpeg)."""
    import torchaudio.functional as AF

    data, sr = sf.read(str(audiopath), dtype="float32", always_2d=True)
    audio = torch.from_numpy(data.mean(axis=1)).unsqueeze(0)
    if sr != sampling_rate:
        audio = AF.resample(audio, sr, sampling_rate)
    return audio.clip_(-1, 1)


def builtin_speakers(model):
    return sorted(model.speaker_manager.speakers.keys())


def vram_mb():
    return torch.cuda.max_memory_allocated() / 2**20


SENTENCE_GAP_S = 0.3
PARAGRAPH_GAP_S = 0.7
SENTENCE_END = re.compile(r"(?<=[.!?…])[\"”»)]*\s+(?=[\"„«(]*[A-ZĄĆĘŁŃÓŚŹŻ])")


def model_char_limit(model, lang):
    return model.tokenizer.char_limits.get(lang, 250)


def split_sentences(text, lang, max_chars, split=True):
    """One chunk per sentence. Never splits inside a sentence: a sentence longer than the
    model's character limit is an error (edit the text, e.g. make it two sentences).
    split=False keeps the whole text as a single chunk (same limit check)."""
    sentences = [s for s in SENTENCE_END.split(text.strip()) if s] if split else [text.strip()]
    for s in sentences:
        if len(s) > max_chars:
            raise SystemExit(
                f"Sentence is {len(s)} chars, over the {max_chars}-char limit for {lang!r}; "
                f"split it into sentences in the source text:\n  {s}")
    return sentences


def trim_silence(wav, thresh_db=-45.0, pad_s=0.02, fade_s=0.005):
    """Cut leading/trailing samples below thresh_db (10 ms RMS frames), keep pad_s, fade the edges."""
    import numpy as np

    frame = SAMPLE_RATE // 100
    n = len(wav) // frame
    if n == 0:
        return wav
    rms = np.sqrt((wav[: n * frame].reshape(n, frame) ** 2).mean(axis=1))
    loud = np.flatnonzero(rms > 10 ** (thresh_db / 20))
    if loud.size == 0:
        return wav
    pad = int(pad_s * SAMPLE_RATE)
    start = max(0, loud[0] * frame - pad)
    end = min(len(wav), (loud[-1] + 1) * frame + pad)
    out = wav[start:end].copy()
    k = min(int(fade_s * SAMPLE_RATE), len(out) // 2)
    if k:
        ramp = np.linspace(0, 1, k, dtype="float32")
        out[:k] *= ramp
        out[-k:] *= ramp[::-1]
    return out


def find_digits(text):
    """[(line, col, token)] for every whitespace-delimited token containing a digit (1-based)."""
    hits = []
    for ln, line in enumerate(text.split("\n"), 1):
        for m in re.finditer(r"\S+", line):
            if any(ch.isnumeric() for ch in m.group()):
                hits.append((ln, m.start() + 1, m.group()))
    return hits


def require_no_digits(text, lang, source="<text>"):
    """Polish only: XTTS reads digits unreliably and without grammatical case, so refuse them."""
    if lang.split("-")[0] != "pl":
        return
    hits = find_digits(text)
    if hits:
        where = "\n".join(f"  {source}:{ln}:{col}: {tok!r}" for ln, col, tok in hits)
        raise SystemExit(
            f"Polish text contains digits; spell every number out in words, in the correct case:\n{where}")


def read_paragraphs(path, lang=None, lines_as_paragraphs=False):
    """Paragraphs from a UTF-8 file: blank-line separated blocks, lines within a block joined with spaces.

    lines_as_paragraphs=True makes every line its own paragraph instead.
    If lang is given and is Polish, digits in the file are refused (see require_no_digits).
    """
    raw = Path(path).read_text(encoding="utf-8").replace("\r\n", "\n")
    if lang:
        require_no_digits(raw, lang, str(path))
    if lines_as_paragraphs:
        paras = [" ".join(l.split()) for l in raw.split("\n")]
    else:
        paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", raw)]
    return [p for p in paras if p]


def synth(model, text, lang, cond, emb, **kw):
    """Synthesize text (already <= max chars); returns (float32 numpy wav, seconds elapsed)."""
    torch.cuda.synchronize()
    t = time.perf_counter()
    out = model.inference(text, lang, cond, emb, **kw)
    torch.cuda.synchronize()
    wav = out["wav"]
    wav = wav.squeeze().cpu().numpy() if hasattr(wav, "cpu") else wav
    return wav, time.perf_counter() - t


def silence(seconds):
    import numpy as np

    return np.zeros(int(SAMPLE_RATE * seconds), dtype="float32")


def synth_long(model, text, lang, cond, emb, gap_s=SENTENCE_GAP_S, split=True, **kw):
    """One paragraph: synthesize sentence by sentence, trim each, join with gap_s of silence.
    Returns (wav, seconds spent generating)."""
    import numpy as np

    require_no_digits(text, lang)
    parts, elapsed = [], 0.0
    for sentence in split_sentences(text, lang, model_char_limit(model, lang), split):
        wav, dt = synth(model, sentence, lang, cond, emb, **kw)
        parts += [trim_silence(wav), silence(gap_s)]
        elapsed += dt
    return np.concatenate(parts[:-1]), elapsed


def synth_paragraphs(model, paras, lang, cond, emb, gap_s=SENTENCE_GAP_S, para_gap_s=PARAGRAPH_GAP_S, log=None, split=True, **kw):
    """Synthesize paragraphs. Returns ([per-paragraph wavs], joined wav with para_gap_s between, seconds generating)."""
    import numpy as np

    wavs, elapsed = [], 0.0
    for i, para in enumerate(paras, 1):
        wav, dt = synth_long(model, para, lang, cond, emb, gap_s=gap_s, split=split, **kw)
        wavs.append(wav)
        elapsed += dt
        if log:
            log(i, len(paras), wav, dt)
    joined = np.concatenate([x for w in wavs for x in (w, silence(para_gap_s))][:-1])
    return wavs, joined, elapsed


def save_wav(path, wav):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), wav, SAMPLE_RATE, subtype="PCM_16")


def load_voice(model, spec, device="cuda"):
    """spec: saved latent .pth path, built-in speaker name, or reference WAV. -> (cond, emb)"""
    p = Path(spec)
    if p.suffix == ".pth":
        d = torch.load(p, map_location=device)
        return d["gpt_cond_latent"].to(device), d["speaker_embedding"].to(device)
    if spec in model.speaker_manager.speakers:
        d = model.speaker_manager.speakers[spec]
        return d["gpt_cond_latent"].to(device), d["speaker_embedding"].to(device)
    if p.suffix.lower() in (".wav", ".flac", ".mp3") and p.exists():
        cond, emb = model.get_conditioning_latents(audio_path=[str(p)])
        return cond, emb
    raise SystemExit(f"Unknown voice {spec!r}: not a .pth latent, built-in speaker, or existing audio file.")
