"""c_tts_prep_en.py - prepare English diary text for XTTS-v2 narration (the EN twin of tts_prep_pl.py). Workstream C, 2026-11-12.
Usage:  python c_tts_prep_en.py SRC.txt OUT.txt [--from "I begin this diary"] [--to "none of our officers were among them."] [--names c_tts_names_en.txt]
Never modifies SRC. Steps: (1) optional cut from the paragraph containing --from to the sentence ending with --to; (2) join wrapped lines inside
paragraphs (blank line = paragraph break; the diary's notebook page breaks are mid-paragraph line breaks); (3) abbreviations; (4) dates/years/times/
ordinals/cardinals spelled out in words; (5) Polish names respelled from the names file (spoken form). Anything with a digit left over is listed
and the script exits 2 (like the PL guard). Writes OUT.txt, OUT.txt.manifest.txt and OUT.names.txt (spoken=written, used by the ASR pick to compare
Whisper's real spellings). Rules are hand-written; every unknown digit token is an error, never a guess."""
import argparse, datetime, re, sys
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("--from", dest="frm"); ap.add_argument("--to")
ap.add_argument("--auto-names", action="store_true"); ap.add_argument("--names", default=str(Path(__file__).with_name("c_tts_names_en.txt"))); a = ap.parse_args()
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def card(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")
    if n < 1000: return ONES[n // 100] + " hundred" + (" " + card(n % 100) if n % 100 else "")
    if n < 1000000: return card(n // 1000) + " thousand" + (" " + card(n % 1000) if n % 1000 else "")
    raise ValueError(n)
ORD_IRR = {"one": "first", "two": "second", "three": "third", "five": "fifth", "eight": "eighth", "nine": "ninth", "twelve": "twelfth"}
def ordw(n):
    w = card(n); head, sep, last = re.match(r"(.*?)([- ]?)([a-z]+)$", w).groups()
    if last in ORD_IRR: last = ORD_IRR[last]
    elif last.endswith("y"): last = last[:-1] + "ieth"
    else: last += "th"
    return head + sep + last
def year(n):
    if 2000 <= n <= 2009: return "two thousand" + (" " + card(n - 2000) if n > 2000 else "")
    hi, lo = divmod(n, 100)
    return card(hi) + (" hundred" if lo == 0 else (" oh " + card(lo) if lo < 10 else " " + card(lo)))
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
ABBR = [(r"\bLt\.", "Lieutenant"), (r"\bSgt\.", "Sergeant"), (r"\bCapt\.", "Captain"), (r"\bCol\.", "Colonel"), (r"\bGen\.", "General"),
        (r"\bMaj\.", "Major"), (r"\bCpl\.", "Corporal"), (r"\bSt\.", "Saint"), (r"\bMr\.", "Mister"), (r"\bDr\.", "Doctor"), (r"\bkm\b", "kilometers")]
def pm(m):
    h = int(m.group(1)); ap_ = m.group(2).replace(".", "").lower()
    part = "in the morning" if ap_ == "am" else ("in the afternoon" if h == 12 or h < 6 else "in the evening")
    return f"{card(h)} {part}"
def prep(t):
    t = t.replace("\u2013", "-").replace("\u2014", ", ")  # en dash -> hyphen, em dash -> comma pause
    for p, r in ABBR: t = re.sub(p, r, t)
    t = re.sub(r"\b(\d{1,2}) (a\.m\.|p\.m\.)", pm, t)
    t = re.sub(rf"\b({MONTHS}) (\d{{1,2}})(?:st|nd|rd|th)?, (\d{{4}})\b", lambda m: f"{m.group(1)} {ordw(int(m.group(2)))}, {year(int(m.group(3)))}", t)
    t = re.sub(rf"\b({MONTHS}) (\d{{1,2}})(?:st|nd|rd|th)?\b", lambda m: f"{m.group(1)} {ordw(int(m.group(2)))}", t)
    t = re.sub(r"\b(\d+)(?:st|nd|rd|th)\b", lambda m: ordw(int(m.group(1))), t)
    t = re.sub(r"\b(1[0-9]{3}|20[0-9]{2})\b", lambda m: year(int(m.group(1))), t)
    t = re.sub(r"\b(\d{1,6})\b", lambda m: card(int(m.group(1))), t)
    return t
raw = Path(a.src).read_text(encoding="utf-8-sig").replace("\r\n", "\n")
if a.frm:
    i = raw.index(a.frm); raw = raw[i:]
    if a.to: j = raw.index(a.to); raw = raw[: j + len(a.to)]
paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", raw) if p.strip()]
names = [l.split("=", 1) for l in Path(a.names).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
out_paras, used = [], []
for p in paras:
    p = prep(p)
    for w, s in names:
        if w in p: p = p.replace(w, s); used.append((s, w))
    if a.auto_names:   # unlisted capitalised words with Polish diacritics: plain transliteration as the spoken form (Jim can override in the names file)
        TR = str.maketrans({"ł": "l", "ą": "a", "ę": "e", "ć": "c", "ś": "s", "ź": "z", "ż": "z", "ń": "n", "ó": "o", "Ł": "L", "Ś": "S", "Ż": "Z", "Ź": "Z", "Ć": "C", "Ó": "O"})
        for w in sorted(set(re.findall(r"\b[A-ZŁŚŻŹĆÓ][A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż'-]*[ĄąĆćĘęŁłŃńÓóŚśŹźŻż][A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż'-]*\b", p))):
            sp = w.translate(TR); p = re.sub(r"\b%s\b" % re.escape(w), sp, p); used.append((sp, w))
    out_paras.append(p)
text = "\n\n".join(out_paras) + "\n"; left = re.findall(r"\S*\d\S*", text)
Path(a.out).write_text(text, encoding="utf-8", newline="\n")
Path(a.out + ".names.txt").write_text("\n".join(f"{s}={w}" for s, w in sorted(set(used))) + "\n", encoding="utf-8", newline="\n")
Path(a.out + ".manifest.txt").write_text(f"c_tts_prep_en.py {datetime.datetime.now().isoformat(timespec='seconds')} src={a.src} from={a.frm!r} to={a.to!r} chars={len(text)} paragraphs={len(out_paras)} names={sorted(set(used))} digits_left={left}\n")
print(f"{len(text)} chars, {len(out_paras)} paragraphs, names respelled: {sorted(set(w for _, w in used))}")
if left: print("DIGITS LEFT:", left); sys.exit(2)
