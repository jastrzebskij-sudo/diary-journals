r"""b_thumbs.py - fetch review thumbnails (default 1400 px wide) of selected Commons candidates via the Commons API.
Wikimedia-friendly: descriptive User-Agent, one API call for all titles, then ONE thumb at a time with a pause.
On HTTP 429/403: wait Retry-After once; if refused again, STOP on Wikimedia (no workaround) and list what is left.
Usage: python -I b_thumbs.py --selection tools\b_select_ep02.json --catalogs <csv>... --dest Archival-Images\ep02\thumbs --log Archival-Images\ep02\thumbs.csv
Originals are NOT fetched here (finals only, later). Written by workstream B, 2026-11-11.
"""
import argparse, csv, hashlib, json, re, sys, time, unicodedata
from pathlib import Path
import requests
from PIL import Image

UA = {"User-Agent": "DiaryResearch/1.0 (family-history project, non-commercial)"}
API = "https://commons.wikimedia.org/w/api.php"

def norm(s):
    s = s.replace("ł", "l").replace("Ł", "L")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()

def slug(title):
    t = title[5:] if title.startswith("File:") else title
    stem = t.rpartition(".")[0]
    return re.sub(r"[^A-Za-z0-9]+", "-", unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode()).strip("-")[:80]

def polite_get(url, **kw):
    r = requests.get(url, headers=UA, timeout=60, **kw)
    if r.status_code == 429:
        time.sleep(min(int(r.headers.get("Retry-After", "60") or 60), 120))
        r = requests.get(url, headers=UA, timeout=60, **kw)
    return r

def main():
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", required=True); ap.add_argument("--catalogs", nargs="+", required=True)
    ap.add_argument("--dest", required=True); ap.add_argument("--log", required=True)
    ap.add_argument("--width", type=int, default=1400); ap.add_argument("--pause", type=float, default=6.0)
    a = ap.parse_args()
    cat = []
    for c in a.catalogs: cat += list(csv.DictReader(open(c, encoding="utf-8")))
    dest = Path(a.dest); dest.mkdir(parents=True, exist_ok=True)
    items, seen = [], set()
    for it in json.load(open(a.selection, encoding="utf-8")):
        row = next((r for r in cat if norm(r["title"][5:]).startswith(norm(it["prefix"]))), None)
        if row and row["title"] not in seen:
            seen.add(row["title"]); items.append((it, row))
    # one API call for all thumb URLs
    thumbs = {}
    r = polite_get(API, params={"action": "query", "format": "json", "prop": "imageinfo", "iiprop": "url|size",
                                "iiurlwidth": a.width, "titles": "|".join(r["title"] for _, r in items)})
    print("API status", r.status_code)
    if r.status_code != 200:
        print("API REFUSED; stopping on Wikimedia."); return 1
    for p in r.json()["query"]["pages"].values():
        ii = (p.get("imageinfo") or [{}])[0]
        thumbs[p["title"]] = ii
    # normalised titles may differ; map by norm()
    tmap = {norm(k): v for k, v in thumbs.items()}
    log, refused = [], False
    for it, row in items:
        name = f'{it["landmark"].split("-")[0]}__{slug(row["title"])}.jpg'
        if (dest / name).exists():
            print("already have", name[:60]); continue
        if refused:
            log.append({"landmark": it["landmark"], "filename": name, "status": "NOT FETCHED (host refused)", "title": row["title"]}); continue
        ii = tmap.get(norm(row["title"]), {})
        url = ii.get("thumburl") or ii.get("url")
        if not url:
            print("no thumb url:", row["title"][:60]); continue
        rr = polite_get(url)
        if rr.status_code in (429, 403):
            refused = True; status = f"REFUSED http {rr.status_code}"; w = h = ""; sha = ""
        else:
            rr.raise_for_status()
            (dest / name).write_bytes(rr.content)
            sha = hashlib.sha256(rr.content).hexdigest()[:16]
            with Image.open(dest / name) as im: w, h = im.size
            status = "ok"
        print(f"{status:>14} | {name[:70]} | {w}x{h}")
        log.append({"landmark": it["landmark"], "filename": name, "status": status, "title": row["title"],
                    "thumb_size": f"{w}x{h}", "orig_size": f'{ii.get("width","")}x{ii.get("height","")}',
                    "page_url": row["page_url"], "license": row["license"], "sha256_16": sha, "retrieved": time.strftime("%Y-%m-%d")})
        time.sleep(a.pause)
    cols = ["landmark", "filename", "status", "title", "thumb_size", "orig_size", "page_url", "license", "sha256_16", "retrieved"]
    new = not Path(a.log).exists()
    with open(a.log, "a", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        if new: wr.writeheader()
        wr.writerows(log)
    if refused: print("HOST REFUSED after one polite retry: stop on Wikimedia; left over listed in log.")
    print("done", len(log))

if __name__ == "__main__":
    sys.exit(main())
