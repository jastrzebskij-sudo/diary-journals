import sys, glob
sys.path.insert(0, "scripts")
import common
lim = 250; bad = []
for f in sorted(glob.glob("/home/claude-agent/diary-pipeline/jobs/ep0[34]_en/p2-*.txt")):
    raw = open(f, encoding="utf-8-sig").read().replace("\r\n", "\n")
    for p in [" ".join(x.split()) for x in raw.split("\n\n") if x.strip()]:
        try: common.split_sentences(p, "en", lim)
        except BaseException as e: bad.append((f.split("/")[-1], str(e)[:230]))
print("checked; problems:", len(bad))
for b in bad: print(b)
