import json, glob, os
for f in sorted(glob.glob("/tmp/asrspeed0/*.asr.json")):
    b = os.path.basename(f).replace(".asr.json", "")
    a = json.load(open(f, encoding="utf-8"))["text"]; t = json.load(open(f"/srv/tts-out/render/c-pipe-val1/{b}.json", encoding="utf-8"))["asr"]
    print(b, "SAME" if a == t else "DIFF\n  ts : " + a + "\n  pick: " + t)
