r"""a_paths.py - shared paths for workstream A (notebook 2 transcription).
Works on Windows (loki) and inside the Cowork Linux VM. Originals under Images\ are never written.
"""
from pathlib import Path
import os, re

ROOT = Path(__file__).resolve().parent.parent            # ...\Projects\Diary
SRC = ROOT / "Images" / "Notebooks" / "2"                 # READ-ONLY originals
OUT = ROOT / "Notebook2"                                  # text outputs (in git)
TRANSCRIPTS = OUT / "transcripts"
PILOT = OUT / "pilot"

def assets_dir() -> Path:
    """Large files: D:\\Claude\\Assets\\Diary\\Notebook2 (override with DIARY_ASSETS)."""
    env = os.environ.get("DIARY_ASSETS")
    if env:
        return Path(env) / "Notebook2"
    win = ROOT.parent.parent / "Assets" / "Diary"         # D:\Claude\Assets\Diary
    if win.exists():
        return win / "Notebook2"
    vm = ROOT.parent / "Assets--Diary"                    # Cowork VM mount name
    if vm.exists():
        return vm / "Notebook2"
    return win / "Notebook2"

ASSETS = assets_dir()
PREP = ASSETS / "prep"

# Order decision for the extra files (logged in NOTES.md). Key = original stem, value = (sort key, page id).
EXTRA = {
    "40_": (40.5, "40a"),
    "_ 2z 84": (84.3, "84a"),
    "_ 2z 84a": (84.6, "84b"),
}

def page_id(stem: str):
    """Return (sort_key, page_id) for an original file stem."""
    if stem in EXTRA:
        return EXTRA[stem]
    if re.fullmatch(r"\d+", stem):
        return (float(int(stem)), f"{int(stem):02d}")
    raise ValueError(f"unexpected file name: {stem!r}")

def pages():
    """Ordered list of (page_id, original Path)."""
    items = []
    for p in SRC.iterdir():
        if p.suffix.lower() in (".jpg", ".jpeg", ".png"):
            k, pid = page_id(p.stem)
            items.append((k, pid, p))
    items.sort()
    return [(pid, p) for _, pid, p in items]

# ---- transcript helpers (shared by a_manifest, a_stamp, a_compare, a_viewer) ----
MARKUP_LINE = re.compile(r"^\s*\[(/?wycinek|zdjęcie:[^\]]*)\]\s*$")
UNCERTAIN = re.compile(r"\[\?\]|\[\.{3,}\]|\[[^\]\s|]+\|[^\]]*\?\]")

def tokens(text: str):
    """Whitespace tokens of transcribed text, without pure markup lines and the [margines] tag."""
    out = []
    for line in text.splitlines():
        if MARKUP_LINE.match(line):
            continue
        line = line.replace("[margines]", " ")
        out.extend(line.split())
    return out

def count(text: str):
    """(words, uncertain_words)"""
    t = tokens(text)
    return len(t), sum(1 for w in t if UNCERTAIN.search(w))
