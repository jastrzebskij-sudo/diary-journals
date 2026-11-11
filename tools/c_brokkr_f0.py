"""c_brokkr_f0.py - rank rendered voices by median fundamental frequency (F0), lowest first.
Runs on brokkr in ~/work/tts/.venv:  python c_brokkr_f0.py OUT.csv WAV [WAV ...]
Uses librosa.pyin (60-300 Hz) on the first 25 s of each file; reports median F0 in Hz, 10th-90th percentile and voiced %.
Baritone speech is roughly 90-130 Hz, tenor 120-180 Hz. A pitch ranking only; timbre/diction still need ears.
Workstream C, 2026-11-11."""
import csv, sys, numpy as np, librosa
out, files = sys.argv[1], sys.argv[2:]
rows = []
for f in files:
    y, sr = librosa.load(f, sr=16000, duration=25)
    f0, voiced, _ = librosa.pyin(y, fmin=60, fmax=300, sr=sr, frame_length=1024)
    v = f0[~np.isnan(f0)]
    rows.append((f.split("/")[-1], round(float(np.median(v)), 1), round(float(np.percentile(v, 10)), 1),
                 round(float(np.percentile(v, 90)), 1), round(100 * len(v) / len(f0))))
rows.sort(key=lambda r: r[1])
with open(out, "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["file", "median_hz", "p10_hz", "p90_hz", "voiced_pct"]); w.writerows(rows)
for r in rows[:25]: print(*r)
print("... n =", len(rows))
