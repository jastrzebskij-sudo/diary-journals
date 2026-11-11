r"""a_prep_images.py - make working copies of the notebook 2 scans (originals untouched).
Usage:  python tools/a_prep_images.py [--edges 1568 1200 900] [--force]
Writes  <Assets>\Notebook2\prep\e<edge>\<page_id>.jpg       plain downscale (long edge = edge, never upscaled)
        <Assets>\Notebook2\prep\e<edge>c\<page_id>.jpg      same + mild contrast (autocontrast 1% cutoff, unsharp)
        <Assets>\Notebook2\prep\contact\sheet_NN.jpg        contact sheets, 12 pages each, for a quick overview
Requires Pillow only.
"""
import argparse, sys
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parent))
from a_paths import PREP, pages

def fit(im, edge):
    w, h = im.size
    s = edge / max(w, h)
    if s >= 1:
        return im.copy()
    return im.resize((round(w * s), round(h * s)), Image.LANCZOS)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edges", type=int, nargs="+", default=[1568, 1200, 900])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    pp = pages()
    n = 0
    for pid, src in pp:
        im = None
        for e in a.edges:
            for suffix in ("", "c"):
                d = PREP / f"e{e}{suffix}"
                d.mkdir(parents=True, exist_ok=True)
                dst = d / f"{pid}.jpg"
                if dst.exists() and not a.force:
                    continue
                if im is None:
                    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
                out = fit(im, e)
                if suffix == "c":
                    out = ImageOps.autocontrast(out, cutoff=1)
                    out = out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
                out.save(dst, "JPEG", quality=88)
                n += 1
    # contact sheets
    cd = PREP / "contact"; cd.mkdir(parents=True, exist_ok=True)
    tw, th, cols, rows = 300, 390, 6, 2
    for i in range(0, len(pp), cols * rows):
        dst = cd / f"sheet_{i // (cols * rows) + 1:02d}.jpg"
        if dst.exists() and not a.force:
            continue
        sheet = Image.new("RGB", (cols * tw, rows * th), "white")
        dr = ImageDraw.Draw(sheet)
        for j, (pid, src) in enumerate(pp[i:i + cols * rows]):
            t = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            t.thumbnail((tw - 6, th - 22))
            x, y = (j % cols) * tw, (j // cols) * th
            sheet.paste(t, (x + 3, y + 20))
            dr.text((x + 5, y + 4), pid, fill="red")
        sheet.save(dst, "JPEG", quality=85); n += 1
    print(f"pages={len(pp)} files_written={n} prep={PREP}")

if __name__ == "__main__":
    main()
