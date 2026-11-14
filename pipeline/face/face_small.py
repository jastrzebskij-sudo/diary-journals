#!/usr/bin/env python3
"""face_small.py - narrator oval track: audio -> transparent oval video (acoustic-viseme mouth, slow body fuzz, blinks, gaze drift).
Usage: face_small.py IN_AUDIO OUT.mov [--height 300] [--bust face/bust_WA0003.jpg]
Output: OUT.mp4 (H.264 crf 14, 25 fps, size round(height*0.88) x height, the oval crop WITHOUT alpha) + OUT.mask.png (static feathered oval alpha; the composite applies it, e.g. ffmpeg alphamerge). Audio NOT included.
Settings frozen from tests-2026-11-14-v11 (blink awaiting Jim's final eyes). CPU only, ~1x realtime. Test tool lineage: Assets/Diary/lipsync/tests-*."""
import sys, argparse, subprocess, numpy as np, cv2
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import lipanim as L
ap = argparse.ArgumentParser(); ap.add_argument("audio"); ap.add_argument("out"); ap.add_argument("--height", type=int, default=300)
ap.add_argument("--bust", default=str(Path(__file__).parent / "bust_WA0003.jpg")); a = ap.parse_args()
audio = L.load(a.audio); n = int(len(audio) / L.SR * L.FPS)
assert n < 3000, "blink/gaze curves precomputed for 120 s; extend lipanim._NB/_GX for longer audio or render per page"
src = cv2.imread(a.bust); o, s, t = L.params(audio, n, 2)
c0, al0 = L.oval_crop(src, a.height); h, w = c0.shape[:2]  # mask is static
cv2.imwrite(a.out + '.mask.png', (al0 * 255).astype(np.uint8))
pw = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(L.FPS), "-i", "-",
                       "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
for i in range(n):
    fr = L.frame(src, i, o[i], s[i], t[i], True); c, al = L.oval_crop(fr, a.height)
    pw.stdin.write(np.ascontiguousarray(c).tobytes())
pw.stdin.close(); pw.wait(); print(a.out, n, "frames", w, "x", h)
