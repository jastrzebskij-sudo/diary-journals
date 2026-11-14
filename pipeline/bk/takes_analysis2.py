import json, glob, statistics as st
R = []
for lang in ("pl", "en"):
    for f in sorted(glob.glob(f"/srv/tts-out/render/ep01_{lang}/*/picked.json")):
        for c in json.load(open(f, encoding="utf-8"))["chunks"]:
            R.append([(t["word_errors"], t["extra_words"], t["pick_score"]) for t in c["takes"]])
def sim(minmatch, k0, kmax=8):
    used, loss, big = [], [], 0
    for ts in R:
        n = k0
        while True:
            seen = ts[:n]; fl = min(e for e, x, s in seen); hit = sum(1 for e, x, s in seen if e == fl and x == 0)
            if hit >= minmatch or n >= kmax: break
            n += 1
        used.append(n); d = min(s for e, x, s in ts[:n]) - min(s for e, x, s in ts); loss.append(d); big += d > 1.0
    return st.mean(used), st.mean(loss), big
print("rule: after k0 takes, stop when >=m takes sit at the observed error floor with no extra words; else add takes up to 8")
for m, k0 in ((1, 2), (2, 3), (2, 4), (3, 4)):
    u, l, b = sim(m, k0); print(f"m={m} k0={k0}: mean takes {u:.2f} (vs 8) -> compute saved {100*(1-u/8):.0f}%; mean score excess vs best-of-8 {l:.2f}; chunks >1.0 worse: {b}/{len(R)}")
print("distribution of chunk error floors (min word_errors over 8):", {k: sum(1 for ts in R if min(e for e,x,s in ts) == k) for k in range(0, 6)})
