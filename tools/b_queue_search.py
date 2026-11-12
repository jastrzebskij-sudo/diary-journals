#!/usr/bin/env python3
"""b_queue_search.py - candidate searches on Commons for the fetch queue (metadata only, no downloads).
Shares b_fetch's pacing and state (20-30 s between requests, maxlag=5). The first 429/503 ends the run
and leaves the host paused in tools\\b_fetch_state.json. Output: Archival-Images\\queue-search-results.json"""
import json, os, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b_fetch as bf

bf.MAX_PAUSES_PER_RUN = 1
OUT = os.path.join(bf.PROJECT, "Archival-Images", "queue-search-results.json")
QUERIES = [  # (key, query)
    ("ep02-L4", "Orange Vaucluse 1940 soldats polonais"),
    ("ep02-L4", "Sérignan-du-Comtat 1940"),
    ("ep02-L5", "Mont Ventoux vignes hiver neige"),
    ("ep02-L6", "wagons 40 hommes 8 chevaux 1940 train soldats"),
    ("ep02-L6", "Polish troops train France 1940"),
    ("ep02-L8", "Mechelen incident January 1940"),
    ("ep01-L2", "Stuka Ju 87 Poland September 1939"),
    ("ep01-L3", "Łuck bombed September 1939"),
    ("ep01-L4", "Soviet invasion of Poland 17 September 1939 tanks"),
    ("ep01-L5", "Polish soldiers Romania border September 1939"),
    ("ep01-L6", "Polish refugees Romania Yugoslavia 1939"),
    ("ep01-L7", "Paris 1939 sandbags monuments Invalides"),
    ("ep03-L2", "Luftwaffe bomber shot down France May 1940"),
    ("ep04-L1", "Belgian capitulation May 1940 Leopold III"),
    ("ep04-L1", "Château de Versailles 1940"),
    ("ep04-L3", "French retreat June 1940 Dijon Roanne"),
    ("ep04-L4", "camp d'internement Polonais 1940 France"),
]
FILTER = "LicenseShortName|Artist|Credit|DateTimeOriginal|ImageDescription|Copyrighted"


def main():
    cfg = {"contact": "", "assets_root": r"D:\\Claude\\Assets\\Diary", "allowed_hosts": bf.DEFAULT_HOSTS}
    cfg.update(json.load(open(bf.CONFIG, encoding="utf-8")))
    ctx = bf.Ctx(cfg)
    res = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    done = set(res.get("_done", []))
    res.setdefault("_done", [])
    try:
        for key, q in QUERIES:
            if q in done:
                continue
            p = dict(action="query", format="json", formatversion="2", maxlag="5", generator="search",
                     gsrsearch=q, gsrnamespace="6", gsrlimit="10", prop="imageinfo",
                     iiprop="size|mime|extmetadata", iiextmetadatafilter=FILTER)
            hdrs, body = bf.http_get(ctx, "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p))
            data = json.loads(body.decode("utf-8"))
            if "error" in data:
                bf.log("SEARCH error %s for %r" % (data["error"].get("code"), q))
                continue
            items = []
            for pg in sorted(data.get("query", {}).get("pages", []), key=lambda x: x.get("index", 0)):
                ii = (pg.get("imageinfo") or [{}])[0]
                em = ii.get("extmetadata", {}) or {}
                g = lambda k: bf.clean((em.get(k) or {}).get("value", ""))
                items.append({"title": pg["title"], "w": ii.get("width"), "h": ii.get("height"), "mime": ii.get("mime"),
                              "license": g("LicenseShortName"), "artist": g("Artist")[:80], "credit": g("Credit")[:80],
                              "date": g("DateTimeOriginal")[:40], "desc": g("ImageDescription")[:140]})
            res.setdefault(key, []).append({"query": q, "hits": items})
            res["_done"].append(q)
            json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            bf.log("SEARCH %s %r -> %d hits" % (key, q, len(items)))
    except bf.Stop:
        bf.log("SEARCH stopped by STOP.txt")
    except bf.HostBlocked:
        bf.log("SEARCH host refused (429/503): search ended, partial results kept")
    except bf.Transient as e:
        bf.log("SEARCH transient error: %s" % e)
    except bf.Permanent as e:
        bf.log("SEARCH permanent error: %s" % e)
    finally:
        ctx.save()


if __name__ == "__main__":
    main()
