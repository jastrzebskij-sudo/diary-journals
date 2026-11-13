"""c_prep_ep_pages.py - build per-page narration texts for one episode (PL or EN). Workstream C, 2026-11-12.
Usage:  python c_prep_ep_pages.py --lang pl|en --pages 1-2 ... 2-5 --out DIR [--approved-pl-page1 FILE]
Reads Text\\<LANG>\\<page>.txt for the listed pages, joins them (a page that ends without terminal punctuation continues into the next page),
spells out numbers/dates/times/abbreviations (PL: rules below; EN: tools\\c_tts_prep_en.py, run on the joined text), adds conservative pacing commas (PL only),
splits into sentences (same regex as the XTTS tool), and assigns every sentence to the page on which it STARTS. Writes DIR\\p<page>.txt (paragraphs of
that page's sentences), DIR\\pages.txt (page order), DIR\\prep-report.txt (every changed sentence with its source) and DIR\\names.txt (EN, Spoken=Written).
Anything with a digit left is an error (exit 2) listing the context - add a rule, never guess. Originals are only read. Rules are assumptions where flagged FLAG."""
import argparse, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent   # Diary\ (works from Windows and from the Linux mount)
SENT_END = re.compile(r"(?<=[.!?…])[\"”»)]*\s+(?=[\"„«(]*[A-ZĄĆĘŁŃÓŚŹŻ])")
TERMINAL = tuple('.!?…"»:;)')
ap = argparse.ArgumentParser(); ap.add_argument("--lang", required=True, choices=["pl", "en"]); ap.add_argument("--pages", nargs="+", required=True)
ap.add_argument("--out", required=True); ap.add_argument("--approved-pl-page1"); ap.add_argument("--skip-heading", nargs="*", default=[]); a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
raw_pages = {p: (ROOT / "Text" / a.lang.upper() / f"{p}.txt").read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip() for p in a.pages}
for _p in a.pages:                                   # drop a listed heading line at the start of a page; a very short page gets a closing period
    t = raw_pages[_p]
    for h in a.skip_heading:
        if t.startswith(h): t = t[len(h):].lstrip()
    if len(t) < 120 and t and not t.endswith(TERMINAL): t += "."
    raw_pages[_p] = t
TAG = {p: chr(0xE000 + i) for i, p in enumerate(a.pages)}            # private-use marker char per page, no digits/letters
joined = ""
for p in a.pages:
    t = raw_pages[p]
    if joined:
        prev_tail = joined.rstrip()
        joined += (" " if not prev_tail.endswith(TERMINAL) else "\n\n")
    joined += TAG[p] + t
# ---------------------------------------------------------------- Polish rules
ORD_UNITS = "zero pierwszego drugiego trzeciego czwartego piątego szóstego siódmego ósmego dziewiątego".split()
ORD_TEENS = "dziesiątego jedenastego dwunastego trzynastego czternastego piętnastego szesnastego siedemnastego osiemnastego dziewiętnastego".split()
def ord_gen(n):                                    # 1-39 genitive masculine ("szóstego")
    if n < 10: return ORD_UNITS[n]
    if n < 20: return ORD_TEENS[n - 10]
    tens = {2: "dwudziestego", 3: "trzydziestego"}[n // 10]
    return tens + (" " + ORD_UNITS[n % 10] if n % 10 else "")
fem = lambda w: re.sub(r"ego\b", "ej", w)           # genitive/locative feminine ("szóstej") for hours
MONTHS = {"I": "stycznia", "II": "lutego", "III": "marca", "IV": "kwietnia", "V": "maja", "VI": "czerwca", "VII": "lipca", "VIII": "sierpnia",
          "IX": "września", "X": "października", "XI": "listopada", "XII": "grudnia"}
RM = "|".join(sorted(MONTHS, key=len, reverse=True))
YEAR39 = "tysiąc dziewięćset trzydziestego dziewiątego roku"
CARD = [(r"\b5 minut\b", "pięć minut"), (r"\b2 dni i 2 noce\b", "dwa dni i dwie noce"), (r"\b25 kgr\. Winogron\b", "dwadzieścia pięć kilogramów winogron"),
        (r"\b13\.000\b", "trzynaście tysięcy"), (r"\b2\.000 lei\b", "dwa tysiące lei"), (r"\b2 tysiące\b", "dwa tysiące"), (r"\b5 tysięcy\b", "pięć tysięcy"),
        (r"\b15 letniego\b", "piętnastoletniego"), (r"\b1000 franków\b", "tysiąc franków"), (r"\b200 zł\b", "dwieście złotych"),
        (r"\b100 franków i 100 złotych\b", "sto franków i sto złotych"), (r"około 2 po południu", "około drugiej po południu"),
        (r"godziny 8 rano", "godziny ósmej rano"), (r"\bB 15\b", "B piętnaście"), (r"numer 1262\b", "numer tysiąc dwieście sześćdziesiąt dwa"),
        (r"\bC 1\b", "C jeden"), (r"około 3 tygodnie\b", "około trzech tygodni"), (r"Około 3 tygodnie\b", "Około trzech tygodni"),
        (r"\bdo 4 p\.p\.", "do czwartego pułku piechoty"), (r"\bw 7 komp\. podchorążych", "w siódmej kompanii podchorążych"),
        (r"\ba 11 kompania\b", "a jedenasta kompania"), (r"\btransport 500 ludzi\b", "transport pięciuset ludzi"),
        (r"\(około 150 ludzi\)", "(około stu pięćdziesięciu ludzi)"), (r"około 1000 ludzi\b", "około tysiąca ludzi"), (r"\b50 franków\b", "pięćdziesiąt franków"),
        (r"\b3 baraki\b", "trzy baraki"), (r"\bH\.81,(\s*[\uE000-\uE0FF]?)\s*79, 77\.", r"H osiemdziesiąt jeden,\1 H siedemdziesiąt dziewięć, H siedemdziesiąt siedem.")]
# abbreviations: nominative / genitive / instrumental ; case chosen from the previous word (default nominative)
AB = {"ppor": ("podporucznik", "podporucznika"), "por": ("porucznik", "porucznika"), "kpt": ("kapitan", "kapitana"), "mjr": ("major", "majora"),
      "ppłk": ("podpułkownik", "podpułkownika"), "płk": ("pułkownik", "pułkownika"), "gen": ("generał", "generała"), "sierż": ("sierżant", "sierżanta"),
      "kpr": ("kapral", "kaprala"), "plut": ("plutonowy", "plutonowego"), "chor": ("chorąży", "chorążego"), "inż": ("inżynier", "inżyniera"),
      "p": ("pan", "pana"), "strz": ("strzelec", "strzelca"), "wach": ("wachmistrz", "wachmistrza"), "prezyd": ("prezydent", "prezydenta"),
      "st": ("starszy", "starszego")}
GEN_PREV = {"do", "od", "z", "ze", "bez", "u", "dla", "około", "rozkaz", "wstawiennictwem", "dowództwem", "powrót", "jednego", "generała", "pana", "przez",
            "dow.", "o", "na"}
def abbr_sub(t):
    def rep(m):
        key = m.group(2).lower().rstrip("."); cap = m.group(2)[0].isupper(); pre = m.group(1).split()[-1].lower().strip(".,;:()") if m.group(1).strip() else ""
        nxt = m.group(3)
        gen = pre in GEN_PREV or nxt.lower().endswith(("ego", "iego")) and key not in ("st",)
        w = AB[key][1 if gen else 0]
        if key == "st" and re.match(r"(sierż|wach|strz|sier)", nxt, re.I): w = "starszy"
        return m.group(1) + (w.capitalize() if cap else w) + " " + m.group(3)
    return re.sub(r"((?:\S+\s+)?)\b(ppor|por|kpt|mjr|ppłk|płk|gen|sierż|kpr|plut|chor|inż|prezyd|strz|wach|st|p)\.\s+(\S+)", rep, t, flags=re.I)
def prep_pl(t):
    t = t.replace("sp[osób", "sposób").replace("/podpis/", "").replace("(zdjęcie)", "").replace("„ „", "nic ważnego")
    t = re.sub(r"\b(\d{1,2})³⁰", lambda m: ord_gen(int(m.group(1))).replace("ego", "ej") + " trzydzieści", t)
    t = re.sub(r"\b(\d{1,2}) (%s) 1939(?: r\b\.?)?" % RM, lambda m: ord_gen(int(m.group(1))) + " " + MONTHS[m.group(2)] + " " + YEAR39 + ("." if m.group(3) else ""), t)
    t = re.sub(r"\bdnia (\d{1,2}) (%s)\b" % RM, lambda m: "dnia " + ord_gen(int(m.group(1))) + " " + MONTHS[m.group(2)], t)
    t = re.sub(r"\b(\d{1,2})/(%s)/1939\.?" % RM, lambda m: ord_gen(int(m.group(1))) + " " + MONTHS[m.group(2)] + " " + YEAR39 + ".", t)
    t = re.sub(r"\b(\d{1,2})\.(%s)\.(?!\d)" % RM, lambda m: ord_gen(int(m.group(1))) + " " + MONTHS[m.group(2)] + ".", t)
    t = re.sub(r"\b20, 21, 22 (%s)\b" % RM, lambda m: "dwudziestego, dwudziestego pierwszego, dwudziestego drugiego " + MONTHS[m.group(1)], t)
    t = re.sub(r"\b(\d{1,2}) (%s)\b" % RM, lambda m: ord_gen(int(m.group(1))) + " " + MONTHS[m.group(2)], t)
    t = re.sub(r"\b[Oo] godz\. (\d{1,2})\b", lambda m: m.group(0)[0] + " godzinie " + fem(ord_gen(int(m.group(1)))), t)
    t = re.sub(r"\bgodz\. (\d{1,2})\b", lambda m: "godziny " + fem(ord_gen(int(m.group(1)))), t)
    t = re.sub(r"\bgodziny (\d{1,2})\b", lambda m: "godziny " + fem(ord_gen(int(m.group(1)))), t)
    t = re.sub(r"\bo (\d{1,2})\.", lambda m: "o " + fem(ord_gen(int(m.group(1)))) + ".", t)
    for p, r in CARD: t = re.sub(p, r, t)
    t = re.sub(r"\b(III|II)\b(?= Baonu)", lambda m: {"III": "Trzeciego", "II": "Drugiego"}[m.group(1)], t)
    t = (t.replace("Komp. Gospodarczej", "Kompanii Gospodarczej").replace("Baonu Panc.", "Batalionu Pancernego").replace("Baonem Panc.", "Batalionem Pancernym")
         .replace("Baonu", "Batalionu").replace("dow. Kolumny", "dowódca Kolumny").replace("pod dow.", "pod dowództwem").replace("komp. Zamk.", "kompanii zamkowej")
         .replace("Komp. Adm.", "Kompanii Administracyjnej").replace("dr lasów", "dyrekcja lasów").replace("Marji", "Marji"))
    t = abbr_sub(t)
    t = re.sub(r"\bkpr\.(?=\s*$)", "kapral", t)
    return t
COMMA_BEFORE = r"(że|lecz|ale|aby|żeby|gdy|gdzie|ponieważ|który|która|które|którego|której|którym|którą|którzy|którym)"
def commas_pl(t):                                   # FLAG conservative standard-Polish clause commas; skips if a comma/sentence start precedes
    return re.sub(r"(?<=[\wąćęłńóśźż])\s+(?=%s\b)" % COMMA_BEFORE, lambda m: ", ", t)
# ---------------------------------------------------------------- EN rules (delegated)
if a.lang == "en":
    tmp = out / "_joined_en.txt"; tmp.write_text(joined, encoding="utf-8")
    prepped_path = out / "_prepped_en.txt"
    r = subprocess.run([sys.executable, str(Path(__file__).with_name("c_tts_prep_en.py")), str(tmp), str(prepped_path), "--names", str(Path(__file__).with_name("c_tts_names_en.txt")), "--auto-names"], capture_output=True, text=True)
    print(r.stdout.strip()); 
    if r.returncode: print(r.stderr[-1500:]); sys.exit(r.returncode)
    prepped = prepped_path.read_text(encoding="utf-8")
    if (out / "_prepped_en.txt.names.txt").exists(): (out / "names.txt").write_text((out / "_prepped_en.txt.names.txt").read_text(encoding="utf-8"), encoding="utf-8")
else:
    paras = [prep_pl(" ".join(p.split())) for p in re.split(r"\n\s*\n", joined) if p.strip()]
    prepped = "\n\n".join(commas_pl(p) for p in paras)
# ---------------------------------------------------------------- sentences -> pages
paras = [p for p in re.split(r"\n\s*\n", prepped) if p.strip()]
sents = []                                           # (paragraph id, page, sentence)
cur_page = a.pages[0]; rev = {v: k for k, v in TAG.items()}
for pi, p in enumerate(paras):
    p = " ".join(p.split()); pos = 0
    pieces = SENT_END.split(p) if True else [p]
    # recompute start offsets in p for the page lookup
    offs = []; i = 0
    for s in pieces:
        j = p.index(s, i); offs.append(j); i = j + len(s)
    for s, j in zip(pieces, offs):
        # page = last page tag at or before the sentence start (tags may sit anywhere in p)
        pg = cur_page
        for k in range(0, j + 1):
            if p[k] in rev: pg = rev[p[k]]
        sents.append((pi, pg, s))
    for ch in p:
        if ch in rev: cur_page = rev[ch]
clean = lambda s: " ".join(re.sub("[\uE000-\uE0FF]", "", s).split())
left = []
for pi, pg, s in sents:
    for m in re.finditer(r"\S*\d\S*", clean(s)): left.append((pg, clean(s)[max(0, m.start() - 40):m.end() + 30]))
if left:
    print("DIGITS LEFT:"); [print("  ", p, repr(c)) for p, c in left]; sys.exit(2)
if a.lang == "pl" and a.approved_pl_page1:         # Jim-approved commas for the first 10 sentences of the first page: same words, his punctuation
    ap_text = Path(a.approved_pl_page1).read_text(encoding="utf-8-sig"); ap_s = [x for x in SENT_END.split(" ".join(ap_text.split())) if x]
    strip = lambda x: re.sub(r"[,\s]+", " ", x).strip().lower()
    first = [i for i, (pi, pg, s) in enumerate(sents) if pg == a.pages[0]][:len(ap_s)]
    ok = all(strip(clean(sents[i][2])) == strip(ap_s[k]) for k, i in enumerate(first))
    print("approved page-1 commas applied:", ok, "(sentences compared: %d)" % len(first))
    if ok:
        for k, i in enumerate(first): sents[i] = (sents[i][0], sents[i][1], ap_s[k])
pages_out = []
for pg in a.pages:
    mine = [(pi, clean(s)) for pi, g, s in sents if g == pg]
    if not mine: continue
    blocks = []; last = None
    for pi, s in mine:
        if pi == last: blocks[-1] += " " + s
        else: blocks.append(s)
        last = pi
    (out / f"p{pg}.txt").write_text("\n\n".join(blocks) + "\n", encoding="utf-8", newline="\n"); pages_out.append(pg)
(out / "pages.txt").write_text("\n".join(pages_out) + "\n", encoding="utf-8", newline="\n")
rep = [f"{pg}\t{clean(s)}" for pi, pg, s in sents]
(out / "prep-report.txt").write_text("\n".join(rep) + "\n", encoding="utf-8", newline="\n")
print("pages:", pages_out, "sentences:", len(sents), "chars:", sum(len(clean(s)) for _, _, s in sents))
