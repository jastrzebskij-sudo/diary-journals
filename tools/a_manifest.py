r"""a_manifest.py - page manifest for notebook 2.
Usage:  python tools/a_manifest.py
Writes  Notebook2\manifest.csv with one row per scan, in reading order:
        page, order, source_file, width, height, sha1, type, language, date, words, uncertain, uncertainty,
        model, images, prompt, transcribed_on, margin_notes, notes
Page order and ids come from a_paths.py (EXTRA holds the decision for the oddly named files).
Type/language/date/counts/model come from Notebook2\transcripts\<page>.json when it exists
(falling back to Notebook2\survey.json for type), so re-running after each batch keeps it current.
"""
import csv, hashlib, json, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
from a_paths import OUT, TRANSCRIPTS, pages

COLS = ["page", "order", "source_file", "width", "height", "sha1", "type", "language", "date", "words",
        "uncertain", "uncertainty", "model", "images", "prompt", "transcribed_on", "margin_notes", "notes"]

def main():
    survey = {}
    sp = OUT / "survey.json"
    if sp.exists():
        survey = json.loads(sp.read_text(encoding="utf-8"))
    rows = []
    for i, (pid, src) in enumerate(pages(), 1):
        with Image.open(src) as im:
            w, h = im.size
        row = dict.fromkeys(COLS, "")
        row.update(page=pid, order=i, source_file=src.name, width=w, height=h,
                   sha1=hashlib.sha1(src.read_bytes()).hexdigest()[:12])
        s = survey.get(pid, {})
        row.update(type=s.get("type", ""), language=s.get("language", ""), notes=s.get("notes", ""))
        jp = TRANSCRIPTS / f"{pid}.json"
        if jp.exists():
            m = json.loads(jp.read_text(encoding="utf-8"))
            for k in ("type", "language", "words", "uncertain", "model", "images", "prompt",
                      "transcribed_on", "margin_notes", "notes"):
                if m.get(k) not in (None, ""):
                    row[k] = m[k]
            row["date"] = "; ".join(m.get("dates", []) or [])
            if m.get("words"):
                row["uncertainty"] = f"{m.get('uncertain', 0) / m['words']:.3f}"
        rows.append(row)
    with open(OUT / "manifest.csv", "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.DictWriter(f, fieldnames=COLS); wr.writeheader(); wr.writerows(rows)
    done = sum(1 for r in rows if r["model"])
    print(f"rows={len(rows)} transcribed={done} -> {OUT / 'manifest.csv'}")

if __name__ == "__main__":
    main()
