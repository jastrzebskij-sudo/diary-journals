#!/usr/bin/env python3
"""b_build_queue.py - builds Archival-Images\\fetch-queue.csv from the reviewed search results (hand-picked titles)."""
import csv, glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE); AI = os.path.join(P, "Archival-Images")

# every Commons title seen in the search/category results, with license and date
seen = {}
for f in glob.glob(os.path.join(AI, "queue-search-results.json")) + glob.glob(os.path.join(AI, "queue-cats-results*.json")):
    d = json.load(open(f, encoding="utf-8"))
    for k, v in d.items():
        if k == "_done": continue
        for q in v:
            for h in q.get("hits", q.get("items", [])):
                if h["title"].startswith("File:"): seen[h["title"]] = h

def find(prefix, avoid="(cropped)"):
    m = [t for t in seen if t.startswith("File:" + prefix) and avoid not in t]
    if len(m) < 1: sys.exit("no title for prefix: " + prefix)
    return m[0]

def safe(t):
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", t[5:]).strip("-")
    return s[:90] if len(s) <= 90 else s[:86] + os.path.splitext(s)[1]

rows = []
def add(title, ep, lm, lic, credit, source="Wikimedia Commons"):
    rows.append({"url_or_title": title, "destination": "Archival-Images\\ep%s\\thumbs\\%s__%s" % (ep, lm, safe(title)),
                 "source": source, "license": lic, "credit": credit, "episode": ep, "landmark": lm})

# Ep2 pending (from ep02\thumbs.csv)
for line in csv.DictReader(open(os.path.join(AI, "ep02", "thumbs.csv"), encoding="utf-8")):
    if line["status"].startswith("ok"): continue
    lm = line["landmark"].split("-")[0]
    cred = "Narodowe Archiwum Cyfrowe (NAC)" if "NAC" in line["title"] else "per Commons page (verify provenance)"
    rows.append({"url_or_title": line["title"], "destination": "Archival-Images\\ep02\\thumbs\\" + line["filename"],
                 "source": "Wikimedia Commons", "license": line["license"] or "Public domain (per Commons; verify)",
                 "credit": cred, "episode": "02", "landmark": lm})
BA = "Bundesarchiv, CC BY-SA 3.0 de"
# Ep2 L5 landscape (modern photos, not archival)
add(find("Mont Ventoux par Malauc"), "02", "L5", "CC BY-SA 3.0", "Commons contributor (modern photo, Feb 2008; context only)")
add(find("Mont ventoux par Malaucène - P1000502"), "02", "L5", "CC BY-SA 3.0", "Commons contributor (modern photo, Feb 2008; context only)")
# Ep1
add(find("Bundesarchiv Bild 183-1987-1210-502"), "01", "E1-L2", "CC BY-SA 3.0 de", BA)
add(find("Bundesarchiv Bild 101I-318-0053-35"), "01", "E1-L2", "CC BY-SA 3.0 de", BA)
add(find("BA-10 Lublin 1939"), "01", "E1-L4", "Public domain (per Commons; verify)", "per Commons page")
add(find("Armia Czerwona przekracza"), "01", "E1-L4", "Public domain (per Commons; verify)", "per Commons page")
# Ep3
add(find("Bundesarchiv Bild 146-1972-066-03"), "03", "E3-L2", "CC BY-SA 3.0 de", BA)
add(find("Bundesarchiv Bild 101I-125-0251-08A"), "03", "E3-L2", "CC BY-SA 3.0 de", BA)
# Ep4
add(find("Belgische Propaganda Poster Van Koning Leopold III"), "04", "E4-L1", "Public domain (per Commons; verify)", "per Commons page")
add(find("Bundesarchiv Bild 146-1970-048-11"), "04", "E4-L1", "CC BY-SA 3.0 de", BA)
add(find("Bundesarchiv Bild 121-0398"), "04", "E4-L3", "CC BY-SA 3.0 de", BA)
add(find("Bundesarchiv Bild 121-0411"), "04", "E4-L3", "CC BY-SA 3.0 de", BA)

out = os.path.join(AI, "fetch-queue.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, ["url_or_title", "destination", "source", "license", "credit", "episode", "landmark"])
    w.writeheader(); w.writerows(rows)
print(len(rows), "rows ->", out)
