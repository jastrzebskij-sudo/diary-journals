r"""b_contact_sheets.py - numbered contact sheets of notebook scans (workstream B). Originals are only read.

Usage (use the face venv python, it has Pillow):
  python b_contact_sheets.py --src <dir> --out <dir> [--start 1] [--end 60] [--cols 6] [--rows 3]
                             [--tw 290] [--th 380] [--index <csv>]
Scans are put in reading order (numeric index in the file name, 'a' variants right after their base,
stray files last). Position numbers are 1-based and are printed on each thumbnail, so a sheet can be
read back to file names through the index CSV.
Written by workstream B, 2026-11-11.
"""
import argparse, csv, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

def order_key(p: Path):
    m = re.search(r"_(\d+)([A-Za-z]?)$", p.stem)
    if p.stem.startswith("1____"):
        return (0, 0, "")
    if m and len(m.group(1)) <= 3:
        return (1, int(m.group(1)), m.group(2).lower())
    return (2, 0, p.name)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=10**6)
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--tw", type=int, default=290)
    ap.add_argument("--th", type=int, default=380)
    ap.add_argument("--index", default="")
    ap.add_argument("--positions", default="", help="comma list of positions to include instead of --start/--end")
    ap.add_argument("--tag", default="", help="prefix for sheet file names")
    a = ap.parse_args()

    src, out = Path(a.src), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    files = sorted([p for p in src.iterdir() if p.suffix.lower() == ".jpg"], key=order_key)

    rows_idx = []
    for pos, p in enumerate(files, 1):
        with Image.open(p) as im:
            rows_idx.append((pos, p.name, im.width, im.height))
    if a.index:
        with open(a.index, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["position", "filename", "width", "height"])
            w.writerows(rows_idx)

    if a.positions:
        want = [int(x) for x in a.positions.split(",") if x.strip()]
        sel = [r for r in rows_idx if r[0] in want]
    else:
        sel = [r for r in rows_idx if a.start <= r[0] <= a.end]
    per = a.cols * a.rows
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    made = []
    for s in range(0, len(sel), per):
        chunk = sel[s:s + per]
        W, H = a.cols * (a.tw + 6) + 6, a.rows * (a.th + 6) + 6
        sheet = Image.new("RGB", (W, H), (40, 40, 40))
        d = ImageDraw.Draw(sheet)
        for i, (pos, name, _, _) in enumerate(chunk):
            x, y = 6 + (i % a.cols) * (a.tw + 6), 6 + (i // a.cols) * (a.th + 6)
            with Image.open(src / name) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((a.tw, a.th))
                sheet.paste(im, (x, y))
            d.rectangle([x, y, x + 52, y + 26], fill=(0, 0, 0))
            d.text((x + 4, y + 1), str(pos), fill=(255, 255, 0), font=font)
        fn = out / f"{a.tag}sheet_{chunk[0][0]:03d}-{chunk[-1][0]:03d}.jpg"
        sheet.save(fn, quality=88)
        made.append(fn.name)
    print("sheets:", ", ".join(made))
    print("scans in order:", len(rows_idx), "| first/last:", rows_idx[0][1], "/", rows_idx[-1][1])

if __name__ == "__main__":
    sys.exit(main())
