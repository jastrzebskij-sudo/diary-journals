#!/usr/bin/env python3
"""b_queue_cats.py - job-file driven Commons category lookups (metadata only; shares b_fetch pacing/state).
Usage: python tools\\b_queue_cats.py JOBS.json OUT.json
JOBS = [{"key": "...", "kind": "catsearch"|"members", "arg": "text or Category:Name"}]
catsearch -> category titles with file/subcat counts; members -> files in a category (+ license/size/date)."""
import json, os, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b_fetch as bf
bf.MAX_PAUSES_PER_RUN = 1
FILTER = "LicenseShortName|Artist|DateTimeOriginal|ImageDescription"


def api(ctx, p):
    p.update(action="query", format="json", formatversion="2", maxlag="5")
    _, body = bf.http_get(ctx, "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p))
    d = json.loads(body.decode("utf-8"))
    if "error" in d:
        raise bf.Transient("API error %s" % d["error"].get("code"))
    return d


def main():
    jobs = json.load(open(sys.argv[1], encoding="utf-8"))
    out_path = sys.argv[2]
    cfg = {"contact": "", "assets_root": r"D:\\Claude\\Assets\\Diary", "allowed_hosts": bf.DEFAULT_HOSTS}
    cfg.update(json.load(open(bf.CONFIG, encoding="utf-8")))
    ctx = bf.Ctx(cfg)
    res = json.load(open(out_path, encoding="utf-8")) if os.path.exists(out_path) else {"_done": []}
    try:
        for j in jobs:
            tag = j["kind"] + "|" + j["arg"]
            if tag in res["_done"]:
                continue
            if j["kind"] == "catsearch":
                d = api(ctx, dict(generator="search", gsrsearch=j["arg"], gsrnamespace="14", gsrlimit="8", prop="categoryinfo"))
                items = [{"title": p["title"], "files": (p.get("categoryinfo") or {}).get("files"),
                          "subcats": (p.get("categoryinfo") or {}).get("subcats")}
                         for p in sorted(d.get("query", {}).get("pages", []), key=lambda x: x.get("index", 0))]
            else:
                d = api(ctx, dict(generator="categorymembers", gcmtitle=j["arg"], gcmtype="file|subcat", gcmlimit="40",
                                  prop="imageinfo", iiprop="size|mime|extmetadata", iiextmetadatafilter=FILTER))
                items = []
                for p in d.get("query", {}).get("pages", []):
                    ii = (p.get("imageinfo") or [{}])[0]
                    em = ii.get("extmetadata", {}) or {}
                    g = lambda k: bf.clean((em.get(k) or {}).get("value", ""))
                    items.append({"title": p["title"], "w": ii.get("width"), "h": ii.get("height"),
                                  "license": g("LicenseShortName"), "date": g("DateTimeOriginal")[:30],
                                  "desc": g("ImageDescription")[:120]})
            res.setdefault(j["key"], []).append({"kind": j["kind"], "arg": j["arg"], "items": items})
            res["_done"].append(tag)
            json.dump(res, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            bf.log("CATS %s %s -> %d items" % (j["key"], tag, len(items)))
    except bf.Stop:
        bf.log("CATS stopped by STOP.txt")
    except bf.HostBlocked:
        bf.log("CATS host refused (429/503): ended, partial results kept")
    except (bf.Transient, bf.Permanent) as e:
        bf.log("CATS error: %s" % e)
    finally:
        ctx.save()


if __name__ == "__main__":
    main()
