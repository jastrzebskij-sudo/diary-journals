import json, glob, statistics as st
rows = []
for lang in ("pl", "en"):
    for f in sorted(glob.glob(f"/srv/tts-out/render/ep01_{lang}/*/picked.json")):
        pj = json.load(open(f, encoding="utf-8"))
        for c in pj["chunks"]:
            ts = c["takes"]; sc = [t["pick_score"] for t in ts]; clean = [t["word_errors"] == 0 and t["extra_words"] == 0 for t in ts]
            rows.append((lang, f.split("/")[-2], c["index"], len(c["text"]), clean, sc, sum(t["synth_s"] for t in ts), sum(t.get("asr_s", 0) for t in ts)))
print("chunks", len(rows), "by lang", {l: sum(1 for r in rows if r[0] == l) for l in ("pl", "en")})
K = 8
print("clean takes per chunk (of 8): mean %.2f; chunks with 0 clean: %d; with >=1: %d" % (st.mean(sum(r[4]) for r in rows), sum(1 for r in rows if not any(r[4])), sum(1 for r in rows if any(r[4]))))
for k in (2, 3, 4):
    gotclean = sum(1 for r in rows if any(r[4][:k])); 
    # quality loss: best pick_score among first k vs among all 8
    loss = [min(r[5][:k]) - min(r[5]) for r in rows]
    worse = sum(1 for d in loss if d > 0.01); big = sum(1 for d in loss if d > 1.0)
    print(f"first {k} takes: chunk has a clean take {gotclean}/{len(rows)} ({100*gotclean/len(rows):.0f}%); best-of-{k} score worse than best-of-8 in {worse} chunks, by >1.0 in {big}; mean excess {st.mean(loss):.2f}")
# sequential stopping: stop at first clean take with score <= median pace penalty? use: stop at first clean take; else continue to 8
exp_takes = []; unresolved = 0
for r in rows:
    idx = next((i for i, c in enumerate(r[4]) if c), None)
    if idx is None: exp_takes.append(8); unresolved += 1
    else: exp_takes.append(idx + 1)
print("stop at first clean take: mean takes %.2f vs 8; unresolved (no clean in 8): %d" % (st.mean(exp_takes), unresolved))
tot_s = sum(r[6] for r in rows); tot_a = sum(r[7] for r in rows)
saved_s = sum(r[6] * (1 - e / 8) for r, e in zip(rows, exp_takes)); saved_a = sum(r[7] * (1 - e / 8) for r, e in zip(rows, exp_takes))
print("Ep1 compute: synth %.0f s + asr %.0f s = %.1f h at 8 takes; sequential stop saves ~%.0f%% (%.1f h)" % (tot_s, tot_a, (tot_s + tot_a) / 3600, 100 * (saved_s + saved_a) / (tot_s + tot_a), (saved_s + saved_a) / 3600))
long = [r for r in rows if r[3] > 150]; print("long chunks (>150 chars):", len(long), "mean clean takes %.2f" % st.mean(sum(r[4]) for r in long), "| short:", "mean clean takes %.2f" % st.mean(sum(r[4]) for r in rows if r[3] <= 150))
