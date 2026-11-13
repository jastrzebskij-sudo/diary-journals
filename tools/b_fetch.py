#!/usr/bin/env python3
"""b_fetch.py - slow, unattended, resumable fetcher for Workstream B (Wikimedia Commons only).

Stdlib only; any Python 3.8+ works. Zero AI involvement while it runs.

Usage:
  python tools\\b_fetch.py --queue Archival-Images\\fetch-queue.csv [--dry-run] [--max-files N] [--retry-failed]

Queue CSV header: url_or_title,destination,source,license,credit,episode,landmark
  url_or_title : "File:Name.jpg", a commons.wikimedia.org/wiki/File:... URL, or a direct upload.wikimedia.org URL
  destination  : path relative to the project root (e.g. Archival-Images\\ep02\\thumbs\\x.jpg); must stay inside the project or assets_root

Policy (hard-coded, see constants): single-threaded; >=20 s between requests to a host (+0-10 s jitter);
Commons API with maxlag=5 for metadata and standard-size thumbnails; honors Retry-After;
429/503 -> pause that host 30, 60, then 120 min (cap); 3 refusals in one run ends the run;
40 files per host per local day; resume state in JSON; STOP.txt (project root) ends the run cleanly.
commons.wikimedia.org and upload.wikimedia.org share one rate-limit bucket ("wikimedia").
"""
import argparse, csv, datetime, html, json, os, random, re, sys, time
import urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
CONFIG = os.path.join(HERE, "b_fetch.config.json")
STATE = os.path.join(HERE, "b_fetch_state.json")
LOCK = os.path.join(HERE, "b_fetch.lock")
STOPFILE = os.path.join(PROJECT, "STOP.txt")
RUNLOG = os.path.join(PROJECT, "RUNLOG-B.md")
RESULTS = os.path.join(PROJECT, "Archival-Images", "fetch-results.csv")

MIN_GAP, JITTER = 20, 10            # seconds between requests to one host, plus random 0..JITTER
PAUSE_LADDER = [1800, 3600, 7200]   # 30, 60, 120 min (cap)
DAILY_CAP = 40                      # files per host per local day
MAXLAG = 5
THUMB_WIDTH = 1920                  # a standard Wikimedia thumbnail size
MAX_BYTES = 60 * 1024 * 1024
TIMEOUT = 60
MAX_PAUSES_PER_RUN = 3
DEFAULT_HOSTS = ["commons.wikimedia.org", "upload.wikimedia.org", "thumb.wikimedia.org"]
EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp", "image/tiff": ".tif"}
ALT = {"image/jpeg": (".jpg", ".jpeg"), "image/tiff": (".tif", ".tiff")}


class Stop(Exception): pass
class HostBlocked(Exception): pass
class Permanent(Exception): pass
class Transient(Exception): pass


def stamp(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
def today(): return datetime.date.today().isoformat()
def host_key(h): return "wikimedia" if h and h.endswith("wikimedia.org") else h


def log(line):
    with open(RUNLOG, "a", encoding="utf-8") as f:
        f.write("- %s [b_fetch] %s\n" % (stamp(), line))
    print(line, flush=True)


class Ctx:
    def __init__(self, cfg):
        self.cfg = cfg
        self.ua = ("DiaryFamilyArchive/1.0 (private, non-commercial family archive; b_fetch.py; contact: %s)"
                   % cfg["contact"])
        self.pauses = 0
        self.transients = 0
        self.st = {"hosts": {}, "done": {}, "failed": {}}
        if os.path.exists(STATE):
            with open(STATE, encoding="utf-8") as f:
                self.st.update(json.load(f))

    def save(self):
        tmp = STATE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.st, f, indent=1, sort_keys=True)
        os.replace(tmp, STATE)

    def host(self, hk):
        h = self.st["hosts"].setdefault(hk, {"last_request": 0, "pause_until": 0, "level": 0, "day": today(), "files_today": 0})
        if h.get("day") != today():
            h["day"], h["files_today"] = today(), 0
        return h


def wait_until(ts):
    while True:
        if os.path.exists(STOPFILE):
            raise Stop()
        rem = ts - time.time()
        if rem <= 0:
            return
        time.sleep(min(5, rem))


def retry_after(v):
    if not v:
        return 0
    try:
        return max(0, int(v))
    except ValueError:
        try:
            from email.utils import parsedate_to_datetime
            return max(0, int(parsedate_to_datetime(v).timestamp() - time.time()))
        except Exception:
            return 0


def pause_host(ctx, hk, ra, why):
    h = ctx.host(hk)
    secs = max(PAUSE_LADDER[min(h["level"], len(PAUSE_LADDER) - 1)], ra)
    h["level"] += 1
    h["pause_until"] = time.time() + secs
    ctx.pauses += 1
    ctx.save()
    log("PAUSE %s %d min (%s; Retry-After=%ss; refusal %d this run)" % (hk, secs // 60, why, ra, ctx.pauses))
    if ctx.pauses >= MAX_PAUSES_PER_RUN:
        raise HostBlocked()


def http_get(ctx, url):
    hk = host_key(urllib.parse.urlparse(url).hostname)
    while True:
        h = ctx.host(hk)
        wait_until(h["pause_until"])
        wait_until(h["last_request"] + MIN_GAP + random.uniform(0, JITTER))
        h["last_request"] = time.time()
        ctx.save()
        req = urllib.request.Request(url, headers={"User-Agent": ctx.ua, "Accept-Encoding": "identity"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                body = r.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    raise Permanent("larger than 60 MB")
                return r.headers, body
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                pause_host(ctx, hk, retry_after(e.headers.get("Retry-After")), "HTTP %d" % e.code)
                continue
            if e.code in (400, 403, 404, 410):
                raise Permanent("HTTP %d" % e.code)
            raise Transient("HTTP %d" % e.code)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise Transient(str(e))


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def api_info(ctx, title):
    q = dict(action="query", format="json", formatversion="2", maxlag=str(MAXLAG), redirects="1",
             titles=title, prop="imageinfo", iiprop="url|size|mime|extmetadata", iiurlwidth=str(THUMB_WIDTH),
             iiextmetadatafilter="LicenseShortName|UsageTerms|Artist|Credit|Copyrighted")
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(q)
    for _ in range(5):
        hdrs, body = http_get(ctx, url)
        data = json.loads(body.decode("utf-8"))
        if data.get("error", {}).get("code") == "maxlag":
            wait_until(time.time() + max(10, retry_after(hdrs.get("Retry-After"))))
            continue
        if "error" in data:
            raise Permanent("API error: %s" % data["error"].get("code"))
        pages = data.get("query", {}).get("pages", [])
        if not pages or pages[0].get("missing") or not pages[0].get("imageinfo"):
            raise Permanent("file not found on Commons")
        return pages[0]["title"], pages[0]["imageinfo"][0]
    raise Transient("maxlag persisted")


def classify(v):
    v = v.strip()
    if v.lower().startswith("file:"):
        return "title", v
    u = urllib.parse.urlparse(v)
    if u.hostname == "commons.wikimedia.org" and "/wiki/" in u.path:
        return "title", urllib.parse.unquote(u.path.split("/wiki/", 1)[1]).replace("_", " ")
    if u.scheme in ("http", "https"):
        return "direct", v
    return "title", "File:" + v


def resolve_dest(cfg, rel):
    """Relative destinations are under the project root; absolute ones are allowed only inside
    the project root or assets_root. Anything else is refused."""
    roots = [os.path.abspath(PROJECT), os.path.abspath(cfg["assets_root"])]
    p = os.path.abspath(os.path.join(PROJECT, rel))
    for r in roots:
        try:
            if os.path.commonpath([r, p]) == r:
                return p
        except ValueError:
            pass
    raise Permanent("destination outside project and assets_root")


def process(ctx, row):
    cfg = ctx.cfg
    dest = resolve_dest(cfg, row["destination"])
    kind, val = classify(row["url_or_title"])
    meta = {"license_api": "", "artist_api": "", "credit_api": "", "usage_terms": "", "commons_url": "", "note": ""}
    if kind == "direct":
        host = urllib.parse.urlparse(val).hostname
        if host not in cfg["allowed_hosts"]:
            raise Permanent("host not allowed: %s (IWM/NAC need Jim's approval)" % host)
        fetch_url = val
        meta["note"] = "direct upload URL; license not verified by API"
    else:
        title, info = api_info(ctx, val)
        em = info.get("extmetadata", {}) or {}
        g = lambda k: clean((em.get(k) or {}).get("value", ""))
        meta.update(license_api=g("LicenseShortName"), artist_api=g("Artist"), credit_api=g("Credit"),
                    usage_terms=g("UsageTerms"), commons_url="https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_")))
        if not meta["license_api"]:
            meta["note"] = "LICENSE-UNCLEAR in API metadata; review before use"
        fetch_url = info["url"] if info.get("width", 0) <= THUMB_WIDTH else info.get("thumburl") or info["url"]
        if urllib.parse.urlparse(fetch_url).hostname not in cfg["allowed_hosts"]:
            raise Permanent("unexpected file host")
    hdrs, body = http_get(ctx, fetch_url)
    ctype = hdrs.get_content_type()
    if not ctype.startswith("image/") or not body:
        raise Permanent("not an image (%s, %d bytes)" % (ctype, len(body)))
    base, ext = os.path.splitext(dest)
    if ctype in EXT and ext.lower() not in ALT.get(ctype, (EXT[ctype],)):
        dest = base + EXT[ctype]
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    with open(tmp, "wb") as f:
        f.write(body)
    os.replace(tmp, dest)
    return dest, len(body), meta


def write_result(row, status, dest, nbytes, meta, note):
    new = not os.path.exists(RESULTS)
    os.makedirs(os.path.dirname(RESULTS), exist_ok=True)
    with open(RESULTS, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["when", "status", "episode", "landmark", "dest", "bytes", "source", "license_queue",
                        "license_api", "credit_queue", "artist_api", "credit_api", "usage_terms", "commons_url", "note"])
        w.writerow([stamp(), status, row["episode"], row["landmark"], dest, nbytes, row["source"], row["license"],
                    meta.get("license_api", ""), row["credit"], meta.get("artist_api", ""), meta.get("credit_api", ""),
                    meta.get("usage_terms", ""), meta.get("commons_url", ""), note or meta.get("note", "")])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-files", type=int, default=DAILY_CAP)
    ap.add_argument("--retry-failed", action="store_true")
    a = ap.parse_args()

    cfg = {"contact": "", "assets_root": r"D:\Claude\Assets\Diary", "allowed_hosts": DEFAULT_HOSTS}
    with open(CONFIG, encoding="utf-8") as f:
        cfg.update(json.load(f))
    contact = cfg["contact"].strip()
    if not contact or contact.upper().startswith("CHANGE") or "@" not in contact and "://" not in contact:
        sys.exit("Set a real contact (email or URL) in tools\\b_fetch.config.json before running.")
    with open(a.queue, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    need = {"url_or_title", "destination", "source", "license", "credit", "episode", "landmark"}
    if not rows or not need <= set(rows[0].keys()):
        sys.exit("Queue needs columns: " + ",".join(sorted(need)))

    ctx = Ctx(cfg)
    todo = [r for r in rows if r["destination"] not in ctx.st["done"]
            and (a.retry_failed or r["destination"] not in ctx.st["failed"])]
    if a.dry_run:
        n = min(len(todo), a.max_files)
        mins = n * 2 * (MIN_GAP + JITTER / 2) / 60
        print("queue rows: %d | already done: %d | failed: %d | would attempt: %d | est. >= %.0f min (2 requests/file)"
              % (len(rows), len(ctx.st["done"]), len(ctx.st["failed"]), n, mins))
        for r in todo[:n]:
            print("  ep%s %s  %s -> %s" % (r["episode"], r["landmark"], r["url_or_title"], r["destination"]))
        return

    if os.path.exists(STOPFILE):
        log("STOP.txt present, not starting")
        return
    if os.path.exists(LOCK) and time.time() - os.path.getmtime(LOCK) < 86400:
        sys.exit("Lock file present (another run?). Delete tools\\b_fetch.lock if stale.")
    open(LOCK, "w").write(str(os.getpid()))
    attempted = 0
    log("START queue=%s todo=%d" % (os.path.basename(a.queue), len(todo)))
    try:
        for row in todo:
            if os.path.exists(STOPFILE):
                raise Stop()
            hk = "wikimedia"
            if ctx.host(hk)["files_today"] >= DAILY_CAP or attempted >= a.max_files:
                log("CAP reached (%d files today); rerun tomorrow" % ctx.host(hk)["files_today"])
                break
            attempted += 1
            tag = "ep%s %s %s" % (row["episode"], row["landmark"], row["destination"])
            try:
                dest, nbytes, meta = process(ctx, row)
                ctx.transients = 0
                ctx.host(hk)["level"] = 0
                ctx.host(hk)["files_today"] += 1
                ctx.st["done"][row["destination"]] = {"dest": dest, "bytes": nbytes, "at": stamp()}
                ctx.save()
                write_result(row, "OK", dest, nbytes, meta, "")
                log("OK %s %dB lic=%s | queue-lic=%s | credit=%s %s" % (
                    tag, nbytes, meta["license_api"] or "?", row["license"], row["credit"], meta["note"]))
            except Permanent as e:
                ctx.st["failed"][row["destination"]] = {"reason": str(e), "at": stamp()}
                ctx.save()
                write_result(row, "FAIL", "", 0, {}, str(e))
                log("FAIL %s: %s" % (tag, e))
            except Transient as e:
                ctx.transients += 1
                write_result(row, "RETRY-LATER", "", 0, {}, str(e))
                log("RETRY-LATER %s: %s" % (tag, e))
                if ctx.transients >= 3:
                    pause_host(ctx, hk, 0, "3 consecutive transient errors")
                    ctx.transients = 0
    except Stop:
        log("STOP.txt found: ended cleanly (delete STOP.txt before the next run)")
    except HostBlocked:
        log("HOST STILL REFUSING after %d pauses: run ended; state saved" % ctx.pauses)
    finally:
        ctx.save()
        try:
            os.remove(LOCK)
        except OSError:
            pass
        log("END attempted=%d done_total=%d failed_total=%d" % (attempted, len(ctx.st["done"]), len(ctx.st["failed"])))


if __name__ == "__main__":
    main()
