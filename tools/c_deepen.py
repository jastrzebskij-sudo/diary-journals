"""c_deepen.py - make a narration WAV deeper/warmer with ffmpeg (rubberband pitch shift + low shelf). Workstream C, 2026-11-11.
Usage (Assets venv python):  python c_deepen.py IN.wav OUT.wav --semitones -2 [--bass-db 2] [--formant shifted|preserved]
  --semitones   pitch shift (negative = lower); with --formant shifted (default) the vocal-tract resonances move down
                too, which reads as a bigger/deeper voice; 'preserved' keeps the original timbre (voice stays 'same person').
  --bass-db     low-shelf boost at 160 Hz (default 2 dB).
Writes OUT.wav and OUT.manifest.txt (tool, settings, date). Keep shifts small (-1 to -3 st): larger values sound artificial."""
import argparse, datetime, subprocess
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--semitones", type=float, default=-2); ap.add_argument("--bass-db", type=float, default=2)
ap.add_argument("--formant", choices=["shifted", "preserved"], default="shifted")
ap.add_argument("--assets", default=r"D:\Claude\Assets\Diary"); a = ap.parse_args()
ff = str(Path(a.assets) / "bin" / "ffmpeg.exe"); ratio = 2 ** (a.semitones / 12)
af = f"rubberband=pitch={ratio:.5f}:formant={a.formant}:pitchq=quality,bass=g={a.bass_db}:f=160:w=0.7"
subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", a.inp, "-af", af, "-ar", "24000", a.out], check=True)
Path(a.out).with_suffix(".manifest.txt").write_text(f"c_deepen.py {datetime.datetime.now().isoformat(timespec='seconds')} in={a.inp} filter={af}\n")
print("wrote", a.out, af)
