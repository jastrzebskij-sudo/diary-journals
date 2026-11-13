#!/usr/bin/env python3
"""b_credits.py - merges every manifest/queue/result into Archival-Images\\credits.csv and Credits.md
(credit line, license, source URL per image; description block for the finished video)."""
import csv, glob, os, re, collections
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE); AI = os.path.join(P, "Archival-Images")
rd = lambda f: list(csv.DictReader(open(f, newline="", encoding="utf-8-sig"))) if os.path.exists(f) else []

def credit_for(name, src, lic):
    m = re.search(r"Bundesarchiv Bild ([\w-]+)", name)
    if m: return "Bundesarchiv, Bild %s, CC BY-SA 3.0 de" % m.group(1), "yes"
    m = re.search(r"NAC (\d+-\d+(?:-\d+)?)", name) or re.search(r"NAC[-_ ](\d+-\d+(?:-\d+)?)", name)
    if m or "Narodowe Archiwum Cyfrowe" in src: return "Narodowe Archiwum Cyfrowe (NAC)%s" % (", sygn. " + m.group(1) if m else ""), "yes (credit the archive)"
    if "NARA" in src: return "National Archives and Records Administration (NARA)", "yes (credit as source)"
    if "Bundesarchiv" in src: return src, "yes"
    if "CC BY" in lic: return (src or "Wikimedia Commons") + " - " + lic, "yes"
    return (src or "Wikimedia Commons") + " (credit to verify on the Commons page)", "unknown - verify"

rows = {}
for r in rd(os.path.join(AI, "manifest.csv")):
    for ep in [re.match(r"\d+", e).group(0) if re.match(r"\d+", e) else e for e in re.split(r";\s*", r["episode"])]:
        c, att = credit_for(r["filename"], r["source_archive"], r["license"])
        rows[(r["filename"], ep)] = dict(file=r["filename"], episode=ep, landmark="", status="on disk", source=r["source_archive"],
            source_url=r["source_url"], license=r["license"], credit_line=c, attribution_required=att, notes=r["notes"][:200])
for r in rd(os.path.join(AI, "ep02", "manifest.csv")):
    if r["kind"] != "external (Wikimedia Commons)":
        rows[(r["file_or_scan"], "02")] = dict(file=r["file_or_scan"], episode="02", landmark=r["landmark"], status="family notebook", source="family notebook 1",
            source_url="", license="family-owned", credit_line="Family archive (notebook of Stefan)", attribution_required="n/a", notes=r["rationale"][:200]); continue
    c, att = credit_for(r["file_or_scan"], "Wikimedia Commons", r["license"])
    st = "on disk" if r["status"].startswith(("thumbnail reviewed", "downloaded")) else "queued"
    rows[(r["file_or_scan"], "02")] = dict(file=r["file_or_scan"], episode="02", landmark=r["landmark"], status=st, source="Wikimedia Commons",
        source_url=r["source_url"], license=r["license"], credit_line=c, attribution_required=att, notes=r["verify_before_monetized_use"][:200])
for r in rd(os.path.join(AI, "fetch-queue.csv")):
    t = r["url_or_title"]; ep = r["episode"]; key = (t[5:] if t.startswith("File:") else t, ep)
    if key in rows: continue
    c, att = credit_for(t, r["source"], r["license"])
    rows[key] = dict(file=key[0], episode=ep, landmark=r["landmark"], status="queued", source=r["source"], source_url="",
        license=r["license"], credit_line=c, attribution_required=att, notes=r["credit"])
import urllib.parse
norm = lambda t: re.sub(r"\W+", "", re.sub(r"^file:", "", urllib.parse.unquote(t).replace("_", " ").lower()))
done = []
for r in rd(os.path.join(AI, "fetch-results.csv")):
    if r["status"] == "OK" and r["commons_url"]: done.append((norm(r["commons_url"].split("/wiki/")[-1].replace("File:", "")), r))
for k, v in rows.items():           # upgrade with API facts once fetched
    for n, r in done:
        if norm(v["file"]) == n and v["episode"].lstrip("0") == r["episode"].lstrip("0"):
            v["status"] = "on disk (fetched)"; v["license"] = r["license_api"] or v["license"]
            art = re.sub(r"(.+?)\1$", r"\1", r["artist_api"]).strip()   # API text can be doubled
            base = v["credit_line"].split(" (credit")[0]
            if r["license_api"] and art and not art.lower().startswith("unknown") and "Bundesarchiv" not in base:
                v["credit_line"] = "%s / %s, %s" % (v["source"] or "Wikimedia Commons", art, r["license_api"])
            elif r["license_api"] and "verify" in v["attribution_required"]:
                v["credit_line"] = "%s, %s (author unknown per Commons)" % (v["source"] or "Wikimedia Commons", r["license_api"])
            if "verify" in v["attribution_required"] and r["license_api"]: v["attribution_required"] = "yes (per Commons licence)" if "CC" in r["license_api"] else "none required (public domain per Commons); credit source anyway"
            v["source_url"] = r["commons_url"]
cols = ["file", "episode", "landmark", "status", "source", "source_url", "license", "credit_line", "attribution_required", "notes"]
with open(os.path.join(AI, "credits.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, cols); w.writeheader(); [w.writerow(v) for v in sorted(rows.values(), key=lambda x: (x["episode"], x["file"]))]

by = collections.defaultdict(list)
for v in rows.values(): by[v["episode"]].append(v)
out = ["# Credits and attribution", "",
 "This project is a personal, educational, non-commercial family archive. Every archival image below is credited to its source; "
 "the credit lines and licenses must go into the finished video and its description. Items marked *verify* still need the exact credit confirmed on the source page.", ""]
for ep in sorted(by):
    out.append("## Episode %s" % ep)
    for v in sorted(by[ep], key=lambda x: x["file"]):
        flag = " *(verify)*" if "verify" in v["attribution_required"] or "verify" in v["credit_line"] else ""
        out.append("- %s - %s%s [%s]" % (v["file"][:90], v["credit_line"], flag, v["status"]))
    out.append("")
srcs = collections.Counter(v["credit_line"].split(",")[0].split(" / ")[0] for v in rows.values() if v["status"] != "family notebook")
out += ["## Description block (copy into the video description)", "",
 "Archival images courtesy of: " + "; ".join(sorted(srcs)) + ". Images from Bundesarchiv are licensed CC BY-SA 3.0 de. "
 "Family photographs and notebook pages: family archive. This video is a non-commercial, educational family project."]
open(os.path.join(P, "Credits.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print(len(rows), "images credited;", sum(1 for v in rows.values() if "verify" in v["attribution_required"] or "verify" in v["credit_line"]), "need verification")
