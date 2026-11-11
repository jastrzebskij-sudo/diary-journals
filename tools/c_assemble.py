"""c_assemble.py - assemble one episode page into an mp4 per Vision.md (workstream C, 2026-11-11).

Usage (run with the Assets venv python):
  python c_assemble.py --episode 1 --page 1 --audio narration.wav --face face.mp4|portrait.jpg \
        --journal <scan.jpg> [--title <title-page.jpg>] [--out out.mp4] [--lang PL]
        [--look sepia|grey] [--grain 12] [--no-period-audio] [--assets D:\\Claude\\Assets\\Diary]

Layout (1280x720): journal panel (720 px wide, zoomed, panning top to bottom over the audio length) on the
left; face panel (720x720) overlaid from the right with a MOVING DIVISION that drifts slowly (+-40 px).
Journal fades in from black (optionally title page first, crossfade at 3 s); face fades in 1.5 s later.
Look: greyscale -> sepia, film grain, light flicker and vignette, 1 s fade in/out. Voice gets a period-style
band-limit unless --no-period-audio. ffmpeg comes from <assets>\\bin. Writes OUT and OUT.manifest.json
(settings, model inputs, ffmpeg version, date). Episode/page are labels for the output name and manifest.
Originals are only read."""
import argparse, datetime, json, subprocess, sys
from pathlib import Path

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--episode", required=True); ap.add_argument("--page", required=True)
ap.add_argument("--audio", required=True); ap.add_argument("--face", required=True)
ap.add_argument("--journal", required=True); ap.add_argument("--title")
ap.add_argument("--out"); ap.add_argument("--lang", default="PL")
ap.add_argument("--look", choices=["sepia", "grey"], default="sepia")
ap.add_argument("--grain", type=int, default=12); ap.add_argument("--zoom", type=float, default=1.6)
ap.add_argument("--no-period-audio", action="store_true")
ap.add_argument("--assets", default=r"D:\Claude\Assets\Diary")
a = ap.parse_args()
ff = str(Path(a.assets) / "bin" / "ffmpeg.exe"); fp = str(Path(a.assets) / "bin" / "ffprobe.exe")
out = a.out or str(Path(a.assets) / "video" / f"ep{int(a.episode):02d}_p{a.page}_{a.lang}.mp4")
Path(out).parent.mkdir(parents=True, exist_ok=True)

T = float(subprocess.check_output([fp, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.audio]).decode())
T += 1.0  # one second of tail for the fade-out
W, H, PW, FPS = 1280, 720, 720, 25
face_is_img = Path(a.face).suffix.lower() in (".jpg", ".jpeg", ".png")
inputs = []
def add(path, loop):
    inputs.extend((["-loop", "1", "-framerate", str(FPS)] if loop else []) + ["-t", f"{T:.2f}", "-i", path])
    return sum(1 for x in inputs if x == "-i") - 1
j = add(a.journal, True)
t_i = add(a.title, True) if a.title else None
f = add(a.face, face_is_img)
inputs.extend(["-i", a.audio]); au = sum(1 for x in inputs if x == "-i") - 1
Z = int(H * a.zoom)
fc = []
fc.append(f"[{j}:v]scale=-2:{Z},crop={PW}:{H}:'(iw-{PW})/2':'(ih-{H})*t/{T:.2f}',setsar=1,fps={FPS}[jp]")
jl = "jp"
if t_i is not None:
    fc.append(f"[{t_i}:v]scale=-2:{Z},crop={PW}:{H}:'(iw-{PW})/2':'(ih-{H})/2',setsar=1,fps={FPS}[tp]")
    fc.append(f"[tp][jp]xfade=transition=fade:duration=1:offset=3[jx]"); jl = "jx"
fc.append(f"[{jl}]fade=t=in:st=0:d=1.2[jf]")
fc.append(f"[{f}:v]scale={PW}:{H}:force_original_aspect_ratio=increase,crop={PW}:{H},setsar=1,fps={FPS},"
          f"format=yuva420p,fade=t=in:st=1.5:d=1.2:alpha=1[fp]")
fc.append(f"color=c=black:s={W}x{H}:r={FPS}:d={T:.2f}[bg]")
fc.append(f"[bg][jf]overlay=0:0[b1]")
fc.append(f"[b1][fp]overlay=x='560+40*sin(2*PI*t/45)':y=0:shortest=1[b2]")
look = "format=gray,format=rgb24,colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131" if a.look == "sepia" else "format=gray,format=rgb24"
fc.append(f"[b2]{look},eq=brightness='0.012*sin(2*PI*7.3*t)+0.008*sin(2*PI*2.1*t)':eval=frame,"
          f"noise=alls={a.grain}:allf=t+u,vignette=PI/5,fade=t=in:st=0:d=1:color=black,fade=t=out:st={T-1:.2f}:d=1,format=yuv420p[v]")
af = ("highpass=f=140,lowpass=f=5800,acompressor=threshold=-18dB:ratio=3," if not a.no_period_audio else "") + \
     f"afade=t=in:d=0.5,afade=t=out:st={T-1:.2f}:d=1,apad"
fc.append(f"[{au}:a]{af}[a]")
cmd = [ff, "-hide_banner", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
       "-t", f"{T:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
       "-movflags", "+faststart", out]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode:
    print(r.stderr[-3000:], file=sys.stderr); sys.exit(r.returncode)
ver = subprocess.run([ff, "-version"], capture_output=True, text=True).stdout.splitlines()[0]
Path(out + ".manifest.json").write_text(json.dumps({
    "script": "c_assemble.py", "date": datetime.datetime.now().isoformat(timespec="seconds"), "episode": a.episode,
    "page": a.page, "lang": a.lang, "duration_s": round(T, 2), "ffmpeg": ver, "inputs": {
        "audio": a.audio, "face": a.face, "journal": a.journal, "title": a.title},
    "settings": {"look": a.look, "grain": a.grain, "zoom": a.zoom, "period_audio": not a.no_period_audio,
                 "frame": f"{W}x{H}@{FPS}", "division": "560+40*sin(2*pi*t/45)"}}, indent=1), encoding="utf-8")
print("wrote", out, f"{T:.1f}s")
