r"""a_compare.py - compare transcript sets page by page (no AI).
Usage:  python tools/a_compare.py <reference_folder> <other_folder> [<other_folder> ...] [--csv out.csv]
For each page present in both: words, uncertain words, and word-level differences against the reference
(difflib on tokens with the [?] marks stripped; diff_rate = changed reference words / reference words).
Use it for model-vs-model, resolution-vs-resolution, and draft-vs-proofread (reference = proofread folder,
then diff_rate is the share of words Jim had to correct).
"""
import argparse, csv, difflib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from a_paths import count, tokens

def norm(text):
    return [re.sub(r"\[\?\]", "", w) for w in tokens(text)]

def diff_words(ref, oth):
    sm = difflib.SequenceMatcher(a=ref, b=oth, autojunk=False)
    changed = sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal")
    return changed

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("ref"); ap.add_argument("others", nargs="+"); ap.add_argument("--csv")
    a = ap.parse_args(); ref = Path(a.ref); rows = []
    for o in map(Path, a.others):
        tw = tu = td = trw = 0
        for rp in sorted(ref.glob("*.txt")):
            pid = rp.stem.replace(".corrected", "")
            op = o / f"{pid}.txt"
            if not op.exists():
                continue
            rt, ot = rp.read_text(encoding="utf-8"), op.read_text(encoding="utf-8")
            w, u = count(ot); r = norm(rt); d = diff_words(r, norm(ot))
            rows.append([o.name, pid, w, u, f"{u / max(w, 1):.3f}", d, f"{d / max(len(r), 1):.3f}"])
            tw += w; tu += u; td += d; trw += len(r)
        if tw:
            rows.append([o.name, "ALL", tw, tu, f"{tu / tw:.3f}", td, f"{td / max(trw, 1):.3f}"])
    hdr = ["set", "page", "words", "uncertain", "uncertain_rate", "diff_words_vs_ref", "diff_rate_vs_ref"]
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8-sig") as f:
            wr = csv.writer(f); wr.writerow(hdr); wr.writerows(rows)
    print("\t".join(hdr))
    for r in rows:
        print("\t".join(map(str, r)))

if __name__ == "__main__":
    main()
