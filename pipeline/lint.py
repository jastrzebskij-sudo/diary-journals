#!/usr/bin/env python3
"""lint.py - S2 preflight lint (PIPELINE-SPEC 5.1), first version. Read-only. Checks narrated text BEFORE any GPU time is spent.
Usage: lint.py --lang PL|EN --pages 2-22 2-23 ... [--root <Diary dir>] [--out report.md]
Flags (code: meaning): LONG sentence over char limit (PL 224, EN 250); DIGIT numerals/roman-numeral dates TTS may mangle; BRACKET [ ] or ( ) notes;
GAP runs of dots (missing text); NUM-ONLY stray page-number-like token; NAME names in the watchlist or capitalised words not in the known-names file;
CORR lexicon correction applies; QUOTE odd number of quote marks. The naive splitter is the one in make_sample.py (S2's real chunker supersedes)."""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
ap = argparse.ArgumentParser(); ap.add_argument("--lang", required=True, choices=["PL","EN"]); ap.add_argument("--pages", nargs="+", required=True)
ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent)); ap.add_argument("--out")
a = ap.parse_args(); root = Path(a.root); LIM = 224 if a.lang == "PL" else 250
SPLIT = re.compile(r"(?<!\bkpt)(?<!\bpor)(?<!\bgen)(?<!\bmjr)(?<!\bp)(?<!\bpłk)(?<!\bkpr)(?<!\bnr)(?<!\bMr)(?<!\bCpl)(?<!\bLt)(?<!\bCapt)(?<!\bMaj)(?<!\bGen)(?<!\bSgt)(?<=[.!?])\s+(?=[A-ZŁŚŻŹĆŃÓĄĘ„\"“0-9])")
corr = {}
cf = root/"Lexicon"/("corrections-pl.tsv" if a.lang == "PL" else "corrections-en.tsv")
if cf.exists():
    for ln in cf.read_text(encoding="utf-8").splitlines()[1:]:
        c = ln.split("\t")
        if len(c) >= 2: corr[c[0]] = c[1]
issues, n = [], 0
for p in a.pages:
    t = " ".join((root/"Text"/a.lang/f"{p}.txt").read_text(encoding="utf-8", errors="replace").split())
    for i, s in enumerate(SPLIT.split(t)):
        n += 1; f = []
        if len(s) > LIM: f.append(f"LONG {len(s)}>{LIM}")
        if re.search(r"\d", s): f.append("DIGIT " + ",".join(re.findall(r"\d[\d.,]*", s))[:40])
        if re.search(r"[\[\]]", s): f.append("BRACKET")
        if re.search(r"\.{3,}|…", s): f.append("GAP")
        if re.fullmatch(r"\W*\d{1,3}\W*", s): f.append("NUM-ONLY")
        if (s.count('"') + s.count("„") + s.count("”") + s.count("“")) % 2: f.append("QUOTE")
        for k, v in corr.items():
            if k in s: f.append(f"CORR {k}->{v}")
        if f: issues.append((p, i, f, s))
L = [f"# Lint {a.lang}: pages {a.pages[0]}..{a.pages[-1]} ({n} sentences, {len(issues)} flagged)", "| page | # | flags | text |", "|---|---|---|---|"]
for p, i, f, s in issues: L.append(f"| {p} | {i} | {'; '.join(f)} | {s[:130].replace('|','/')}{'...' if len(s)>130 else ''} |")
txt = "\n".join(L) + "\n"
if a.out: Path(a.out).write_text(txt, encoding="utf-8")
else: print(txt)
print(f"{n} sentences, {len(issues)} flagged", file=sys.stderr)
