r"""b_loc_search.py - metadata-only search of the Library of Congress JSON API (loc.gov/photos/?fo=json), workstream B.
Usage: python -I b_loc_search.py --queries "Polish soldiers France 1940" "French troop train 1940" --out Archival-Images\ep02\loc-results.csv
One request per query, 5 s pause, descriptive UA; stops on HTTP 429/403. Records rights text per item (LoC items often 'no known restrictions' - verify).
"""
import argparse, csv, sys, time
import requests

UA = {"User-Agent": "DiaryResearch/1.0 (family-history project, non-commercial)"}

def main():
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", nargs="+", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=8); ap.add_argument("--pause", type=float, default=5.0)
    a = ap.parse_args()
    rows = []
    for q in a.queries:
        r = requests.get("https://www.loc.gov/photos/", params={"q": q, "fo": "json", "c": a.n, "at": "results"}, headers=UA, timeout=60)
        print(q, "->", r.status_code)
        if r.status_code in (429, 403):
            print("REFUSED; stopping on loc.gov"); break
        if r.status_code != 200: continue
        for it in r.json().get("results", []):
            rows.append({"query": q, "title": it.get("title", ""), "date": it.get("date", ""),
                         "url": it.get("id") or it.get("url", ""), "rights": "; ".join(it.get("rights", [])) if isinstance(it.get("rights"), list) else str(it.get("rights", ""))[:300],
                         "image": (it.get("image_url") or [""])[-1] if isinstance(it.get("image_url"), list) else "",
                         "retrieved": time.strftime("%Y-%m-%d")})
        time.sleep(a.pause)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=["query", "title", "date", "url", "rights", "image", "retrieved"])
        wr.writeheader(); wr.writerows(rows)
    for r in rows: print(f'{r["date"][:10]:10} | {r["title"][:80]} | {r["url"]}')

if __name__ == "__main__":
    sys.exit(main())
