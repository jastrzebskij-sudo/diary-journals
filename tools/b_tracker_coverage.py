r"""b_tracker_coverage.py - add/update an archival_coverage column in Production-Tracker.csv (workstream B). No other column is changed.
Usage: python -I b_tracker_coverage.py --tracker Production-Tracker.csv --set 1=3/9 2=3/10 3=1/2 4=1/4
Definition (also in NOTES.md): covered/total landmarks with >=1 candidate image reviewed or in-notebook; not final picks. Idempotent.
"""
import argparse, csv, sys

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tracker", required=True); ap.add_argument("--set", nargs="+", required=True)
    a = ap.parse_args()
    vals = dict(s.split("=", 1) for s in a.set)
    raw = open(a.tracker, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    nl = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8-sig")
    rows = list(csv.reader(text.splitlines()))
    hdr = rows[0]
    if "archival_coverage" not in hdr:
        hdr.append("archival_coverage")
        for r in rows[1:]: r.append("")
    ci, ei = hdr.index("archival_coverage"), hdr.index("episode")
    for r in rows[1:]:
        if r[ei] in vals: r[ci] = vals[r[ei]]
    with open(a.tracker, "w", newline="", encoding="utf-8-sig" if bom else "utf-8") as f:
        csv.writer(f, lineterminator=nl).writerows(rows)
    print("ok; flags untouched; coverage set for episodes", ",".join(vals))

if __name__ == "__main__":
    sys.exit(main())
