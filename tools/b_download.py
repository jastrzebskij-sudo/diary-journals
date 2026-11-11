r"""b_download.py - download selected Commons candidates (workstream B). Run on loki with the face venv python.

Usage:
  python -I b_download.py --selection tools\b_select_ep02.json --catalogs <csv> [<csv> ...]
                          --dest Archival-Images\ep02 --big D:\Claude\Assets\Diary\B\big\ep02 --log Archival-Images\ep02\downloads.csv

selection: JSON list of {"landmark": "L1-camp-winter", "prefix": "Camp de Coetquidan - napis"}; the first catalog row
(from b_commons_search.py output) whose file title starts with the prefix is used. Only candidates, no finals.
Files over --maxmb go to --big instead of --dest. Paced; on HTTP 429/403 the item is logged as REFUSED and skipped
(no workaround). Written by workstream B, 2026-11-11.
"""
import argparse, csv, hashlib, json, re, sys, time, unicodedata
from pathlib import Path
import requests
from PIL import Image

UA = {"User-Agent": "DiaryArchivalSourcing/1.0 (family history project; contact via project owner)"}

def norm(s):
    s = s.replace("ł", "l").replace("Ł", "L")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()

def slug(title):
    t = title[5:] if title.startswith("File:") else title
    stem, _, ext = t.rpartition(".")
    stem = re.sub(r"[^A-Za-z0-9]+", "-", unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode()).strip("-")
    return stem[:80], ext.lower()

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", required=True)
    ap.add_argument("--catalogs", nargs="+", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--big", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--maxmb", type=float, default=8.0)
    ap.add_argument("--pause", type=float, default=4.0)
    a = ap.parse_args()

    cat = []
    for c in a.catalogs:
        cat += list(csv.DictReader(open(c, encoding="utf-8")))
    dest, big = Path(a.dest), Path(a.big)
    dest.mkdir(parents=True, exist_ok=True); big.mkdir(parents=True, exist_ok=True)
    log_rows, seen, refused_hosts = [], set(), set()
    for item in json.load(open(a.selection, encoding="utf-8")):
        p = norm(item["prefix"])
        row = next((r for r in cat if norm(r["title"][5:]).startswith(p)), None)
        if not row:
            print("NOT IN CATALOG:", item["prefix"]); continue
        if row["title"] in seen:
            continue
        seen.add(row["title"])
        s, ext = slug(row["title"])
        name = f'{item["landmark"].split("-")[0]}__{s}.{ext}'
        status, size, w, h, sha, where = "ok", 0, "", "", "", dest
        if (dest / name).exists() or (big / name).exists():
            print("already have:", name[:70]); continue
        if refused_hosts:
            print("SKIPPED (host refused earlier):", name[:70]); continue
        try:
            r = requests.get(row["file_url"], headers=UA, timeout=90)
            if r.status_code == 429:   # one polite retry after Retry-After, then give up on the host
                time.sleep(min(int(r.headers.get("Retry-After", "60") or 60), 120))
                r = requests.get(row["file_url"], headers=UA, timeout=90)
            if r.status_code in (429, 403):
                refused_hosts.add(row["file_url"].split("/")[2])
                status = f"REFUSED http {r.status_code}"
            else:
                r.raise_for_status()
                size = len(r.content)
                where = big if size > a.maxmb * 1e6 else dest
                (where / name).write_bytes(r.content)
                sha = hashlib.sha256(r.content).hexdigest()[:16]
                try:
                    with Image.open(where / name) as im:
                        w, h = im.size
                except Exception:
                    pass
        except Exception as e:
            status = f"ERROR {type(e).__name__}"
        print(f'{status:>14} | {item["landmark"][:14]:14} | {name[:70]} | {size/1e6:.2f} MB | {w}x{h}')
        log_rows.append({"landmark": item["landmark"], "filename": name, "folder": str(where), "title": row["title"],
                         "page_url": row["page_url"], "file_url": row["file_url"], "license": row["license"],
                         "date": row["date"], "catalog_size": f'{row["width"]}x{row["height"]}',
                         "actual_size": f"{w}x{h}", "bytes": size, "sha256_16": sha, "status": status,
                         "retrieved": time.strftime("%Y-%m-%d"), "credit": row.get("credit", ""),
                         "desc": row.get("desc", "")})
        time.sleep(a.pause)
    cols = list(log_rows[0].keys()) if log_rows else []
    new = not Path(a.log).exists()
    with open(a.log, "a", newline="", encoding="utf-8") as f:   # append: earlier runs stay in the log
        wr = csv.DictWriter(f, fieldnames=cols)
        if new:
            wr.writeheader()
        wr.writerows(log_rows)
    if refused_hosts:
        print("HOST REFUSED (429/403 after one polite retry):", ", ".join(sorted(refused_hosts)))
    print("logged", len(log_rows), "->", a.log)

if __name__ == "__main__":
    sys.exit(main())
