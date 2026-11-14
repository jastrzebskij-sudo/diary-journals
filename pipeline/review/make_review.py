#!/usr/bin/env python3
"""make_review.py - build a one-page listening/review tool from finished job dirs (copied locally).
Usage: make_review.py OUT_DIR TITLE JOBDIR [JOBDIR ...]      (JOBDIR needs picked.json + audio; trim_report.json/final_trim used if present)
Writes OUT_DIR/review.html + audio_N.mp3. Open review.html (double-click). While listening press A / W / P to tag problems at the current moment;
marks autosave to a marks.json you pick once (Chrome/Edge) and to the browser; 'Download' as fallback. Unmarked = fine. Added 2026-11-14."""
import sys, json, subprocess, shutil, re
from pathlib import Path
out = Path(sys.argv[1]); title = sys.argv[2]; jobs = [Path(p) for p in sys.argv[3:]]; out.mkdir(parents=True, exist_ok=True)
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))
segs = []
for n, j in enumerate(jobs):
    P = json.loads((j / "picked.json").read_text(encoding="utf-8"))
    tr = {r["index"]: r for r in json.loads((j / "trim_report.json").read_text(encoding="utf-8"))} if (j / "trim_report.json").exists() else {}
    cand = [j / "final_trim" / "narration_trim.wav"] + sorted((j / "final").glob("*.wav")) + [j / "picked_all.wav"]
    audio = next(p for p in cand if p.exists() and not p.name.endswith("_16k.wav"))
    mp3 = f"audio_{n}.mp3"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(audio), "-codec:a", "libmp3lame", "-b:a", "128k", str(out / mp3)], check=True)
    t = 0.0; chunks = []; prev = 0
    for c in P["chunks"]:
        tk = c["takes"][c["picked"]]; d = tr[c["index"]]["cut_to"] if c["index"] in tr else tk["dur_s"]
        if c["index"]: t += P["gap_paragraph_s"] if c["paragraph"] != prev else P["gap_sentence_s"]
        chunks.append(dict(i=c["index"], take=c["picked"], start=round(t, 3), end=round(t + d, 3), text=c["text"], heard=tk.get("asr", ""), errs=tk.get("word_errors"), extra=tk.get("extra_words")))
        t += d; prev = c["paragraph"]
    segs.append(dict(job=j.name, audio=mp3, dur=round(dur(out / mp3), 2), model_end=round(t, 2), chunks=chunks))
    print(j.name, "audio", segs[-1]["dur"], "s; timeline", round(t, 2), "s")
html = (Path(__file__).parent / "review_template.html").read_text(encoding="utf-8")
data = json.dumps(dict(title=title, segments=segs), ensure_ascii=False).replace("</", "<\\/")
(out / "review.html").write_text(html.replace("/*DATA*/null", data), encoding="utf-8"); print("wrote", out / "review.html")
