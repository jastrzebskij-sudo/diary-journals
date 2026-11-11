r"""a_glossary_seed.py - seed a names/places glossary for notebook 2 from the typed notebook-1 text (no AI).
Usage:  python tools/a_glossary_seed.py [--min 2]
Reads   Diary-PL.txt
Writes  Notebook2\glossary_candidates.csv   (term, count, mid_sentence_count, example)
Heuristic: capitalised tokens that appear mid-sentence (not after . ! ? or line start), plus rank/unit abbreviations.
The curated glossary lives in Notebook2\glossary.csv and is edited by hand / by the transcription passes.
"""
import argparse, csv, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from a_paths import ROOT, OUT

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--min", type=int, default=2); a = ap.parse_args()
    text = (ROOT / "Diary-PL.txt").read_text(encoding="utf-8", errors="replace")
    tok = re.compile(r"[A-Za-zÀ-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż][A-Za-zÀ-ÿĄąĆćĘęŁłŃńÓóŚśŹźŻż'\-]+")
    total, mid, ex = Counter(), Counter(), {}
    lower = Counter(w.lower() for w in tok.findall(text))
    for line in text.splitlines():
        for m in tok.finditer(line):
            w = m.group(0)
            if not w[0].isupper():
                continue
            total[w] += 1
            before = line[:m.start()].rstrip()
            if before and before[-1] not in ".!?:\"„”(":
                mid[w] += 1
                ex.setdefault(w, line[max(0, m.start() - 40):m.end() + 40].strip())
    rows = []
    for w, n in mid.items():
        if n < a.min:
            continue
        # drop words that are mostly ordinary lowercase vocabulary
        if lower[w.lower()] - total[w] > total[w]:
            continue
        rows.append((w, total[w], n, ex.get(w, "")))
    rows.sort(key=lambda r: (-r[2], r[0]))
    OUT.mkdir(exist_ok=True)
    with open(OUT / "glossary_candidates.csv", "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.writer(f); wr.writerow(["term", "count", "mid_sentence_count", "example"]); wr.writerows(rows)
    print(f"candidates={len(rows)} -> {OUT / 'glossary_candidates.csv'}")

if __name__ == "__main__":
    main()
