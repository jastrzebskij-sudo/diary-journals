import json, time, sys
sys.path.insert(0, "/home/claude-agent/c-workstream")
from c_brokkr_asr import load_asr, read16k
asr = load_asr(); D = "/srv/tts-out/render/c-pipe-val1/"
names = ["take_s02_t0", "take_s02_t1", "take_s03_t0", "take_s04_t0", "take_s04_t1", "take_s05_t0"]
ref = {n: json.load(open(D + n + ".json", encoding="utf-8"))["asr"] for n in names}
for label, kw in [("temp0.0 (as pick)", dict(generate_kwargs={"language": "pl", "task": "transcribe", "temperature": 0.0})),
                  ("no temperature", dict(generate_kwargs={"language": "pl", "task": "transcribe"}))]:
    t0 = time.time(); same = 0
    for n in names:
        txt = asr({"raw": read16k(D + n + ".wav"), "sampling_rate": 16000}, **kw)["text"].strip(); same += (txt == ref[n])
    print(label, "%.1f s for %d takes" % (time.time() - t0, len(names)), "same-as-pick:", same, "/", len(names), flush=True)
