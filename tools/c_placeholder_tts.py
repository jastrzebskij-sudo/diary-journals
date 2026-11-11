"""c_placeholder_tts.py - PLACEHOLDER narration via Edge-TTS (Microsoft online service, NOT the final XTTS voice).
Usage: python c_placeholder_tts.py TEXTFILE OUT.mp3 [--paragraphs N] [--voice pl-PL-MarekNeural]
Sends the chosen paragraphs of TEXTFILE to Microsoft's TTS endpoint; writes OUT.mp3 and OUT.manifest.json
(tool, voice, date, source file, characters). Used only to exercise the face-animation pipeline.
Workstream C, 2026-11-11."""
import argparse, asyncio, datetime, json
from pathlib import Path
import edge_tts

ap = argparse.ArgumentParser()
ap.add_argument("textfile"); ap.add_argument("out")
ap.add_argument("--paragraphs", type=int, default=1)
ap.add_argument("--voice", default="pl-PL-MarekNeural")
a = ap.parse_args()
paras = [p.strip() for p in Path(a.textfile).read_text(encoding="utf-8-sig").split("\n\n") if p.strip()]
text = " ".join(paras[:a.paragraphs])
asyncio.run(edge_tts.Communicate(text, a.voice).save(a.out))
Path(a.out).with_suffix(".manifest.json").write_text(json.dumps({
    "tool": "edge-tts " + getattr(edge_tts, "__version__", "?"), "voice": a.voice, "placeholder": True,
    "date": datetime.date.today().isoformat(), "source": a.textfile, "paragraphs": a.paragraphs,
    "characters": len(text)}, indent=1), encoding="utf-8")
print(len(text), "chars ->", a.out)
