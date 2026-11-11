r"""b_manifest_update.py - fold thumbs.csv status into epNN\manifest.csv and mark scan-33 clipping as an Ep2 candidate (placement uncertain).
Usage: python -I b_manifest_update.py --manifest Archival-Images\ep02\manifest.csv --thumbs Archival-Images\ep02\thumbs.csv
Idempotent. Written by workstream B, 2026-11-11.
"""
import argparse, csv, re, sys, unicodedata

def norm(s):
    s = s.replace("ł", "l").replace("Ł", "L")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--thumbs", required=True)
    a = ap.parse_args()
    th = {}
    for r in csv.DictReader(open(a.thumbs, encoding="utf-8")):
        if r["status"] == "ok" or r["title"] not in th:
            th[r["title"]] = r
    tn = {norm(k[5:] if k.startswith("File:") else k): v for k, v in th.items()}
    rows = list(csv.DictReader(open(a.manifest, encoding="utf-8")))
    cols = list(rows[0].keys())
    for r in rows:
        if r["kind"].startswith("external"):
            t = tn.get(norm(r["file_or_scan"]))
            if not t:
                continue
            if t["status"] == "ok":
                r["status"] = f'thumbnail reviewed on contact sheet ({t["thumb_size"]}, thumbs\\{t["filename"]}); original NOT fetched (finals only)'
            else:
                r["status"] = "NOT fetched: Wikimedia 429 after polite retry (stopped on Wikimedia 2026-11-11); thumbnail pending"
        elif r["kind"].startswith("in-notebook") and "32.jpg" in r["file_or_scan"] and "placement uncertain" not in r["status"]:
            r["status"] = (r["status"] + "; placement uncertain (scan order = May 1940; content = Jan 1940, 12 Jan newsletter entry)").lstrip("; ")
    with open(a.manifest, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=cols); wr.writeheader(); wr.writerows(rows)
    print("updated", len(rows))

if __name__ == "__main__":
    sys.exit(main())
