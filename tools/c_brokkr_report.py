"""c_brokkr_report.py - print timings/picks from a pipeline manifest (runs anywhere). Usage: python3 c_brokkr_report.py MANIFEST.json"""
import json, sys, glob, os
m = json.load(open(sys.argv[1], encoding="utf-8"))
print({k: m[k] for k in ("audio_s", "synth_compute_s", "asr_compute_s", "synth_s_per_audio_s", "asr_s_per_audio_s", "picks")})
d = os.path.dirname(os.path.dirname(sys.argv[1]))
a = [json.load(open(f, encoding="utf-8")).get("asr_s", 0) for f in sorted(glob.glob(d + "/take_s*_t*.json"))]
print("asr_s per take: n=%d min=%.1f median=%.1f max=%.1f" % (len(a), min(a), sorted(a)[len(a) // 2], max(a)))
print("first 12:", a[:12])
