#!/usr/bin/env python3
"""period_fx.py - 'historical recording' treatment for narration: band-limit, light compression, wow/flutter, hiss, crackle, optional soft clip.
Usage: period_fx.py IN.wav OUT.wav --preset L|M|H [--seed N]
L = tape-lite, M = wire/film, H = radio/newsreel. Masks short clicks/ticks and rough edges; it does NOT restore dropped words (re-render those).
Deterministic (seeded). Needs ffmpeg + numpy. Added 2026-11-14 (Jim: add 'historical' noise to disguise TTS glitches)."""
import sys, argparse, subprocess, wave, numpy as np, tempfile, os
P = {"L": dict(hp=90,  lp=7000, comp=False, wow=(0.5, 0.002), flut=None,       hiss=-44, crk=0.0, crk_db=-34, clip=False),
     "M": dict(hp=200, lp=5000, comp=True,  wow=(0.6, 0.004), flut=(6.0, 0.001), hiss=-38, crk=0.6, crk_db=-30, clip=False),
     "H": dict(hp=300, lp=3800, comp=True,  wow=(0.7, 0.006), flut=(5.0, 0.002), hiss=-33, crk=2.0, crk_db=-24, clip=True)}
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--preset", default="M", choices=list(P)); ap.add_argument("--seed", type=int, default=11)
a = ap.parse_args(); p = P[a.preset]
af = [f"highpass=f={p['hp']}", f"lowpass=f={p['lp']}"]
if p["comp"]: af.append("acompressor=threshold=-24dB:ratio=3:attack=15:release=250:makeup=3")
af.append(f"vibrato=f={p['wow'][0]}:d={p['wow'][1]}")
if p["flut"]: af.append(f"vibrato=f={p['flut'][0]}:d={p['flut'][1]}")
if p["clip"]: af.append("asoftclip=type=tanh:threshold=0.6")
tmp = tempfile.mktemp(suffix=".wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.inp, "-af", ",".join(af), "-ac", "1", "-ar", "24000", "-c:a", "pcm_s16le", tmp], check=True)
w = wave.open(tmp); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; w.close(); os.remove(tmp)
rng = np.random.RandomState(a.seed); n = len(x)
rms0 = np.sqrt(np.mean(x ** 2)) + 1e-9
hiss = rng.randn(n).astype(np.float32); k = np.ones(5, np.float32) / 5; hiss = np.convolve(hiss, k, "same")        # mild lowpass hiss
x = x + hiss * 10 ** (p["hiss"] / 20) * 3.0
if p["crk"] > 0:
    nclk = int(p["crk"] * n / sr)
    for pos in rng.randint(0, n - 40, nclk):
        amp = 10 ** (p["crk_db"] / 20) * rng.uniform(0.4, 1.0) * rng.choice([-1, 1]); ln = rng.randint(3, 18)
        x[pos:pos + ln] += amp * np.exp(-np.arange(ln) / (ln / 3)) * rng.choice([-1, 1], ln)
x *= rms0 / (np.sqrt(np.mean(x ** 2)) + 1e-9)               # keep overall level
pk = np.max(np.abs(x)); x = x * (0.97 / pk) if pk > 0.97 else x
w = wave.open(a.out, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close(); print(a.out, a.preset)
