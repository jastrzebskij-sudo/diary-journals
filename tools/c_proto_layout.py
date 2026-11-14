#!/usr/bin/env python3
"""c_proto_layout.py - PROTOTYPE layouts for smooth journal scroll + stationary corner face (2026-11-13, Jim's request).
Fixes the choppy pan of c_assemble.py: the journal is supersampled 4x, cropped at integer positions of the 4x image, then scaled
down, so the scroll moves in 1/4-pixel steps (c_assemble crops at 1 px steps = ~5 jumps/s at this scroll speed). No moving division.
Layouts: full = journal fills the frame, face in a corner (feathered oval); side = journal in a centred-left panel on a dark backdrop, face in the right column.
Usage: c_proto_layout.py --audio A.wav --face F.mp4 --journal J.jpg --out O.mp4 [--layout full|side] [--seconds 45] [--ffmpeg ffmpeg]"""
import argparse, subprocess, sys
ap = argparse.ArgumentParser()
ap.add_argument("--audio", required=True); ap.add_argument("--face", required=True); ap.add_argument("--journal", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--layout", default="full", choices=["full", "side"]); ap.add_argument("--seconds", type=float, default=0)
ap.add_argument("--ffmpeg", default="ffmpeg"); ap.add_argument("--ffprobe", default="ffprobe")
ap.add_argument("--face-crop", default="400:400:37:8", help="w:h:x:y crop of the face video (head and shoulders)")
ap.add_argument("--face-size", type=int, default=340); ap.add_argument("--grain", type=int, default=12)
a = ap.parse_args()
Tfull = float(subprocess.check_output([a.ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.audio]).decode()) + 1.0
T = min(Tfull, a.seconds) if a.seconds else Tfull
W, H, FPS, S = 1280, 720, 25, 4
SCROLL_T = Tfull  # scroll speed is set by the full duration, so a shortened preview scrolls at the real speed
if a.layout == "full":
    jw, jx, jy = W, 0, 0           # page scaled to frame width; viewport = whole frame
    vw, vh = W, H
else:
    jw = 860; vw, vh = jw, H; jx, jy = 50, 0
jf = (f"[0:v]scale={jw*S}:-2:flags=lanczos,pad=iw:max(ih\,{vh*S}):0:0:color=0x1a1612,crop={vw*S}:{vh*S}:0:'min(ih-{vh*S},(ih-{vh*S})*t/{SCROLL_T:.2f})',scale={vw}:{vh}:flags=lanczos,setsar=1,fps={FPS}[jp]")
fs = a.face_size
if a.layout == "full":
    fx, fy = f"W-{fs}-30", f"H-{fs}-30"
else:
    fx, fy = f"W-{fs}-60", f"(H-{fs})/2"
fc = [jf,
      f"color=c=0x1a1612:s={W}x{H}:r={FPS}:d={T:.2f}[bg]",
      f"[bg][jp]overlay={jx}:{jy}[b1]",
      f"[1:v]crop={a.face_crop},scale={fs}:{fs},fps={FPS},format=yuva420p,"
      f"geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':a='255*clip((1-hypot((X-W/2)/(W/2),(Y-H/2)/(H/2)))*5,0,1)',"
      f"fade=t=in:st=1.5:d=1.2:alpha=1[fp]",
      f"[b1][fp]overlay=x='{fx}':y='{fy}':shortest=1[b2]",
      "[b2]format=gray,format=rgb24,colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,"
      "eq=brightness='0.012*sin(2*PI*7.3*t)+0.008*sin(2*PI*2.1*t)':eval=frame,"
      f"noise=alls={a.grain}:allf=t+u,vignette=PI/5,fade=t=in:st=0:d=1:color=black,fade=t=out:st={T-1:.2f}:d=1,format=yuv420p[v]",
      f"[2:a]highpass=f=140,lowpass=f=5800,acompressor=threshold=-18dB:ratio=3,afade=t=in:d=0.5,afade=t=out:st={T-1:.2f}:d=1,apad[a]"]
cmd = [a.ffmpeg, "-hide_banner", "-y", "-loop", "1", "-framerate", str(FPS), "-t", f"{T:.2f}", "-i", a.journal,
       "-t", f"{T:.2f}", "-i", a.face, "-t", f"{T:.2f}", "-i", a.audio,
       "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", f"{T:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
       "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", a.out]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode: print(r.stderr[-2500:], file=sys.stderr); sys.exit(r.returncode)
print("ok", a.out, f"{T:.1f}s")
