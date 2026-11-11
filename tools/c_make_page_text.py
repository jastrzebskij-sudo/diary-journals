"""c_make_page_text.py - cut a TTS-prepared episode text to about N characters at a sentence boundary (workstream C).
Usage: python c_make_page_text.py SRC.txt OUT.txt [--max-chars 1100]
Keeps paragraph breaks (blank lines), never cuts mid-sentence, takes whole sentences while the running total stays
<= max-chars. At ~12.5 characters per second of Polish narration, 1100 characters is roughly 88 s.
Writes OUT.txt and OUT.txt.manifest.txt (source, characters kept, sentences kept, date). Originals are only read."""
import argparse, datetime, re
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("--max-chars", type=int, default=1100)
a = ap.parse_args()
paras = [p.strip() for p in Path(a.src).read_text(encoding="utf-8-sig").split("\n\n") if p.strip()]
out, total, n = [], 0, 0
for p in paras:
    keep = []
    for s in re.split(r"(?<=[.!?])\s+", p):
        if total + len(s) + (1 if total else 0) > a.max_chars:
            break
        keep.append(s); total += len(s) + 1; n += 1
    if keep: out.append(" ".join(keep))
    if len(keep) < len(re.split(r"(?<=[.!?])\s+", p)): break
Path(a.out).write_text("\n\n".join(out) + "\n", encoding="utf-8", newline="\n")
Path(a.out + ".manifest.txt").write_text(f"c_make_page_text.py {datetime.datetime.now().isoformat(timespec='seconds')} src={a.src} max_chars={a.max_chars} kept_chars={total} sentences={n} paragraphs={len(out)}\n")
print(f"kept {total} chars, {n} sentences, {len(out)} paragraphs -> {a.out}")
