r"""
tts_prep_pl.py - prepare Polish diary scripts for XTTS-v2 narration.

NEVER modifies the originals. Writes NEW files beside them:
  Episodes\<ep>\script-PL-tts-reflowed.txt   (stage 1: reflow only, digits still present)
  Episodes\01-Invasion-and-Flight\trial-PL-tts.txt   (stage 2 sample: numbers/abbreviations
                                                       spelled out, digit-free)
  TTS-Prep-Report.md                          (what is left to convert, per episode)

Stage 1 rules (from HomeLab postcard 2026-10-27):
  * one paragraph per line, no hard line breaks mid-paragraph
  * a page-break gap (blank line) in the middle of a sentence is joined, not kept as a paragraph break
Stage 2 (numbers in words, correct Polish case) is NOT automated: each replacement below is
hand-written so the grammatical case is right, and the script asserts that every replacement
matched exactly once and that no digit survives (same idea as the planned render.py guard).
"""
import re
from pathlib import Path

ROOT = Path(r"D:\Claude\Projects\Diary")
EPISODES = ROOT / "Episodes"
TERMINAL = tuple('.!?…"»:;)')

ABBREVIATIONS = ["godz", "ppor", "por", "kpt", "mjr", "ppłk", "płk", "gen", "sierż", "kpr", "st",
                 "strz", "kgr", "km", "ul", "dow", "komp", "baon", "panc", "p", "r", "tzw", "ks",
                 "dr", "inż", "mgr", "tel", "np", "itd", "itp", "pp", "kol", "szt"]
ABBR_RE = re.compile(r"\b(" + "|".join(ABBREVIATIONS) + r")\.", re.IGNORECASE)


def reflow(text):
    """Return (paragraphs, joins). Blocks are blank-line separated; single newlines inside a block
    are wrapped lines. A block is a continuation of the previous one (page break mid-sentence) if it
    starts lowercase, or the previous block is long and has no terminal punctuation."""
    text = text.replace("\r\n", "\n").lstrip("\ufeff")
    blocks = re.split(r"\n[ \t]*\n", text)
    paras, joins, last_len = [], 0, 0
    for block in blocks:
        line = " ".join(p.strip() for p in block.split("\n") if p.strip())
        if not line:
            continue
        # last_len is the length of the previous *block* (not the merged paragraph), so short
        # title lines without a full stop are never mistaken for a sentence cut by a page break.
        if paras and (line[0].islower() or
                      (last_len > 150 and not paras[-1].endswith(TERMINAL))):
            paras[-1] += " " + line
            joins += 1
        else:
            paras.append(line)
        last_len = len(line)
    return paras, joins


def stage1():
    rows = []
    for ep in sorted(p for p in EPISODES.iterdir() if p.is_dir()):
        src = ep / "script-PL.txt"
        if not src.exists():
            continue
        raw = src.read_text(encoding="utf-8-sig")
        paras, joins = reflow(raw)
        out = ep / "script-PL-tts-reflowed.txt"
        out.write_text("\n\n".join(paras) + "\n", encoding="utf-8", newline="\n")
        body = "\n".join(paras)
        rows.append((ep.name, len(re.split(r"\n[ \t]*\n", raw.strip())), len(paras), joins,
                     len(re.findall(r"\S*\d\S*", body)), len(ABBR_RE.findall(body)),
                     body.count("[")))
    return rows


# ---- stage 2: hand-written replacements for the trial excerpt (Episode 1) -------------------
TRIAL_PARAGRAPHS = [
    # (paragraph starts with, [(old, new), ...])
    ("Pamiętnik zaczynam", [
        ("1 IX 1939 r.", "pierwszego września tysiąc dziewięćset trzydziestego dziewiątego roku."),
        ("około godz. 15", "około godziny piętnastej"),
    ]),
    ("Dnia 6 IX", [
        ("Dnia 6 IX", "Dnia szóstego września"),
        ("Komp. Gospodarczej III Baonu Panc.", "Kompanii Gospodarczej Trzeciego Batalionu Pancernego."),
        ("Około godz. 11 ", "Około godziny jedenastej "),
        ("sierż. Wrona", "sierżant Wrona"),
        ("Około godz. 13 ", "Około godziny trzynastej "),
        ("w koszarach Baonu Panc.", "w koszarach Batalionu Pancernego."),
    ]),
]
# Sentences pulled from later in the episode to exercise number inflection.
TRIAL_SENTENCES = [
    (r"Co tylko dojeżdżamy do niej.*?nasza kolumna\.", [("5 minut", "pięć minut")]),
    (r"Cyfra na liczniku mego samochodu stanęła na 13\.000\.",
     [("na 13.000.", "na trzynastu tysiącach.")]),
    (r"Rano już pobliscy mieszkańcy.*?Winogron\.",
     [("25 kgr. Winogron.", "dwadzieścia pięć kilogramów winogron.")]),
]


def apply(text, repls):
    for old, new in repls:
        assert text.count(old) == 1, f"replacement must match exactly once: {old!r} ({text.count(old)})"
        text = text.replace(old, new)
    return text


def stage2_trial():
    ep = EPISODES / "01-Invasion-and-Flight"
    paras, _ = reflow((ep / "script-PL.txt").read_text(encoding="utf-8-sig"))
    out = []
    for start, repls in TRIAL_PARAGRAPHS:
        match = [p for p in paras if p.startswith(start)]
        assert len(match) == 1, f"paragraph not found: {start}"
        out.append(apply(match[0], repls))
    body = " ".join(paras)
    for pattern, repls in TRIAL_SENTENCES:
        m = re.search(pattern, body)
        assert m, f"sentence not found: {pattern}"
        out.append(apply(m.group(0), repls))
    for line in out:
        assert not re.search(r"\d", line), f"digit survived: {line[:60]}"
        left = re.findall(r"\b(?:Baon\w*|Panc\.|godz\.|sierż\.|Komp\.|ppor\.|kpt\.|mjr\.|kgr\.)", line,
                          re.IGNORECASE)
        assert not left, f"abbreviation survived {left}: {line[:60]}"
    (ep / "trial-PL-tts.txt").write_text("\n\n".join(out) + "\n", encoding="utf-8", newline="\n")
    return out


def main():
    rows = stage1()
    trial = stage2_trial()
    lines = ["# TTS prep report (Polish)", "",
             "Generated by `tts_prep_pl.py`. Originals untouched; new files are "
             "`Episodes\\<ep>\\script-PL-tts-reflowed.txt` (reflow only) and "
             "`Episodes\\01-Invasion-and-Flight\\trial-PL-tts.txt` (numbers/abbreviations spelled out).", "",
             "| Episode | blocks in original | paragraphs after reflow | page-break joins | tokens with digits left | abbreviations left | `[` marks |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append("| " + " | ".join(str(x) for x in r) + " |")
    tot = [sum(r[i] for r in rows) for i in range(1, 7)]
    lines.append("| **Total** | " + " | ".join(f"**{x}**" for x in tot) + " |")
    lines += ["", f"Trial file: {len(trial)} lines, {sum(len(t) for t in trial)} characters, no digits.", ""]
    (ROOT / "TTS-Prep-Report.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
