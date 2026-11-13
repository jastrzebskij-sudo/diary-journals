#!/usr/bin/env python3
"""b_build_queue3.py - APPENDS round-3 hand-picked Commons titles (gap fill + context) to Archival-Images\\fetch-queue.csv.
Safe to rerun: skips titles already in the queue. Titles come from queue-cats-results1-3.json."""
import csv, glob, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE); AI = os.path.join(P, "Archival-Images")
seen = {}
for f in glob.glob(os.path.join(AI, "queue-search-results.json")) + glob.glob(os.path.join(AI, "queue-cats-results*.json")):
    d = json.load(open(f, encoding="utf-8"))
    for k, v in d.items():
        if k == "_done": continue
        for q in v:
            for h in q.get("hits", q.get("items", [])):
                if h["title"].startswith("File:"): seen[h["title"]] = h
def find(prefix):
    m = [t for t in seen if t.startswith("File:" + prefix) and "(crop" not in t]
    return m[0] if m else None
def safe(t):
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", t[5:]).strip("-")
    return s[:90] if len(s) <= 90 else s[:86] + os.path.splitext(s)[1]
qf = os.path.join(AI, "fetch-queue.csv")
have = {r["url_or_title"] for r in csv.DictReader(open(qf, encoding="utf-8-sig"))}
rows, missing = [], []
def add(prefix, ep, lm, lic, credit, title=None):
    t = title or find(prefix)
    if not t: missing.append(prefix); return
    if t in have: return
    have.add(t)
    rows.append({"url_or_title": t, "destination": "Archival-Images\\ep%s\\thumbs\\%s__%s" % (ep, lm, safe(t)), "source": "Wikimedia Commons",
                 "license": lic, "credit": credit, "episode": ep, "landmark": lm})
PD = "Public domain (per Commons; verify)"; V = "per Commons page (verify provenance)"; BA = "Bundesarchiv, CC BY-SA 3.0 de"
IWM = "IWM (Imperial War Museums), per Commons page (verify attribution)"
# gap fills, priority order
add("", "01", "E1-L5", PD, IWM, title="File:The Nazi-soviet Invasion of Poland, 1939 HU106377.jpg")   # Polish troops crossing into Romania (IWM HU 106377)
add('"A testimony of senseless Polish destruction', "01", "E1-L3", PD, V)
add("Bundesarchiv Bild 101I-012-0016-20", "01", "E1-L3", "CC BY-SA 3.0 de", BA)
add("Bundesarchiv Bild 101I-012-0018-06A", "01", "E1-L3", "CC BY-SA 3.0 de", BA)
add("Lviv. September 1939", "01", "E1-L4", PD, V)
add("Brest, 22 september 1939", "01", "E1-L4", PD, V)
add("Jeńcy1", "01", "E1-L4", PD, V)
add("Serignan du Comtat 1 by JM Rosier", "02", "L4", "CC BY-SA 3.0", "JM Rosier (modern photo, 2007; context only)")
add("Sérignan - Remparts", "02", "L4", "CC BY-SA 3.0", "Commons contributor (modern photo, 2013; context only)")
add("Sérignan - Campanile", "02", "L4", PD, "Commons contributor (modern photo, 2009; context only)")
add("Sainte Cécile les vignes 2 by JM Rosier", "02", "L4", "CC BY-SA 3.0", "JM Rosier (modern photo, 2007; context only)")
add("British troops and Belgian refugees on the Brussels-Louvain road", "04", "E4-L1", PD, IWM)
add("Belgian refugees during the Battle of Belgium", "04", "E4-L1", PD, V)
add("Bundesarchiv Bild 121-0400", "04", "E4-L3", "CC BY-SA 3.0 de", BA)
add("6th Panzer Div 1940 HU111379", "04", "E4-L3", PD, IWM)
add("BramRetirada2", "04", "E4-L4", "CC BY-SA 3.0", "Commons contributor (Bram camp 1939, Spanish refugees; context only, not Polish internees)")
add("22NUM1PH2-24", "04", "E4-L4", "CC BY-SA 4.0", "Archives departementales (Barcares camp 1939, Spanish refugees; context only)")
# French army early 1940 context for Ep2 (train journey/camp life), landmark CTX
for p in ("25mm antitank gun in French service, January 1940", "French D2 tank, January 1940 01", "Anti-aircraft St Etienne Mle 1907",
          "Deux prisonniers allemands emmenés"):
    add(p, "02", "CTX", PD, V)
with open(qf, "a", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, ["url_or_title", "destination", "source", "license", "credit", "episode", "landmark"]); w.writerows(rows)
print(len(rows), "rows appended; missing prefixes:", missing)
