r"""b_manifest.py - build Archival-Images\epNN\manifest.csv (workstream B).

Usage:
  python -I b_manifest.py --episode 02 --selection tools\b_select_ep02.json --catalogs <csv> ...
                          --downloads Archival-Images\ep02\downloads.csv --notebook Archival-Images\notebook1-glued-items.csv
                          --out Archival-Images\ep02\manifest.csv

One row per candidate (external) plus one per in-notebook item for the episode. 'status' says whether the file is on disk.
No finals are chosen here. Written by workstream B, 2026-11-11.
"""
import argparse, csv, json, re, sys, unicodedata

def norm(s):
    s = s.replace("ł", "l").replace("Ł", "L")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--selection", required=True)
    ap.add_argument("--catalogs", nargs="+", required=True)
    ap.add_argument("--downloads", required=True)
    ap.add_argument("--notebook", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    cat = []
    for c in a.catalogs:
        cat += list(csv.DictReader(open(c, encoding="utf-8")))
    try:
        dl = {r["title"]: r for r in csv.DictReader(open(a.downloads, encoding="utf-8"))}
    except FileNotFoundError:
        dl = {}
    # latest row per title wins, but an 'ok' row is never overwritten by a failure
    best = {}
    for r in csv.DictReader(open(a.downloads, encoding="utf-8")) if dl else []:
        if r["title"] not in best or r["status"] == "ok" or best[r["title"]]["status"] != "ok":
            best[r["title"]] = r

    cols = ["landmark", "kind", "file_or_scan", "status", "source_url", "direct_file_url", "license",
            "resolution", "date_place_accuracy", "rationale", "verify_before_monetized_use", "retrieved"]
    rows = []
    for item in json.load(open(a.selection, encoding="utf-8")):
        p = norm(item["prefix"])
        row = next((r for r in cat if norm(r["title"][5:]).startswith(p)), None)
        if not row:
            continue
        d = best.get(row["title"])
        ok = d and d["status"] == "ok"
        rows.append({"landmark": item["landmark"], "kind": "external (Wikimedia Commons)",
                     "file_or_scan": d["filename"] if ok else row["title"][5:],
                     "status": "downloaded" if ok else "NOT downloaded (upload.wikimedia.org returned HTTP 429)",
                     "source_url": row["page_url"], "direct_file_url": row["file_url"], "license": row["license"],
                     "resolution": (d["actual_size"] if ok else row["width"] + "x" + row["height"] + " (catalogue)"),
                     "date_place_accuracy": item["accuracy"], "rationale": item["why"],
                     "verify_before_monetized_use": "YES - " + item["verify"],
                     "retrieved": row["retrieved"]})
    for r in csv.DictReader(open(a.notebook, encoding="utf-8")):
        if "Ep" + str(int(a.episode)) not in r["episodes"]:
            continue
        rows.append({"landmark": "in-notebook", "kind": "in-notebook",
                     "file_or_scan": "Images\\Notebooks\\1\\" + r["scan_filename"] + f' (position {r["position"]})',
                     "status": "original (read-only)", "source_url": "family notebook 1", "direct_file_url": "",
                     "license": "family-owned original", "resolution": r["resolution"],
                     "date_place_accuracy": r["approx_date"] + " / " + r["confidence"],
                     "rationale": r["description"], "verify_before_monetized_use": "no (family material); check any newspaper clipping's publisher rights",
                     "retrieved": ""})
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print("manifest rows:", len(rows), "->", a.out)

if __name__ == "__main__":
    sys.exit(main())
