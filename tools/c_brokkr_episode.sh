#!/usr/bin/env bash
# c_brokkr_episode.sh - ONE-COMMAND episode/page audio pipeline on brokkr (no AI tokens, resumable, STOP-file aware).
#   bash ~/c-workstream/c_brokkr_episode.sh LANG TEXT.txt OUTDIR NAME LATENT [extra render args: --takes 8 --seed 5000 --merge 6 --respell A=B]
#   LANG = pl|en ; LATENT = file under ~/work/tts/latents (e.g. c_Kumar65_Ilkin35_80_Damien20.pth) ; NAME = output stem (e.g. narration_ep01_p1_PL_v4)
# Steps (state markers in OUTDIR/state): 1 render takes (XTTS, GPU1)  2 ASR pick + merge (Whisper medium, GPU0)  3 deepen -1.0 st / bass +2 dB, wav+16k+mp3, manifest.
# Re-running the same command continues where it stopped. Stop cleanly: touch OUTDIR/STOP (or ~/c-workstream/STOP) - takes in flight finish, exit 3.
# Log: OUTDIR/run.log. Final files: OUTDIR/final/NAME.wav|_16k.wav|.mp3|.manifest.json. Workstream C, 2026-11-12.
set -uo pipefail
export PATH="$HOME/.local/bin:$PATH" COQUI_TOS_AGREED=1 CUDA_DEVICE_ORDER=PCI_BUS_ID
LANGC=$1; TEXT=$2; OUT=$3; NAME=$4; LATENT=$5; shift 5
SEMI=${DEEPEN_ST:--1.0}; BASS=${DEEPEN_BASS:-2}
mkdir -p "$OUT/state" "$OUT/final"; LOG="$OUT/run.log"; W=~/c-workstream
say() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; }
stopped() { [ -e "$OUT/STOP" ] || [ -e "$W/STOP" ]; }
T0=$(date +%s); say "start lang=$LANGC text=$TEXT latent=$LATENT name=$NAME args=$*"
if [ ! -e "$OUT/state/1.done" ]; then
  stopped && { say "STOP present, not starting"; exit 3; }
  ( cd ~/work/tts && CUDA_VISIBLE_DEVICES=1 .venv/bin/python $W/c_brokkr_episode_render.py --lang "$LANGC" --latent "latents/$LATENT" --text "$TEXT" --out "$OUT" "$@" ) >> "$LOG" 2>&1
  rc=$?; [ $rc -eq 0 ] || { say "render step exit $rc"; exit $rc; }; touch "$OUT/state/1.done"
fi
if [ ! -e "$OUT/state/2.done" ]; then
  stopped && { say "STOP present"; exit 3; }
  CUDA_VISIBLE_DEVICES=0 $W/venv-asr/bin/python $W/c_brokkr_episode_pick.py "$OUT" --lang "$LANGC" >> "$LOG" 2>&1
  rc=$?; [ $rc -eq 0 ] || { say "pick step exit $rc"; exit $rc; }; touch "$OUT/state/2.done"
fi
if [ ! -e "$OUT/state/3.done" ]; then
  RATIO=$(python3 -c "print(2**($SEMI/12))")
  AF="rubberband=pitch=$RATIO:formant=shifted:pitchq=quality,bass=g=$BASS:f=160:w=0.7"
  F="$OUT/final/$NAME"
  ffmpeg -hide_banner -loglevel error -y -i "$OUT/picked_all.wav" -af "$AF" -ar 24000 "$F.wav" \
   && ffmpeg -hide_banner -loglevel error -y -i "$F.wav" -ar 16000 -ac 1 "${F}_16k.wav" \
   && ffmpeg -hide_banner -loglevel error -y -i "$F.wav" -codec:a libmp3lame -b:a 192k "$F.mp3" || { say "deepen/encode failed"; exit 4; }
  python3 - "$OUT" "$F" "$AF" "$T0" "$LATENT" "$LANGC" <<'PY'
import json, sys, subprocess, time
out, f, af, t0, latent, lang = sys.argv[1:7]
p = json.load(open(out + "/picked.json", encoding="utf-8"))
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f + ".wav"]))
synth = sum(t["synth_s"] for c in p["chunks"] for t in c["takes"]); asr = p.get("asr_seconds", 0)
m = dict(pipeline="c_brokkr_episode.sh", lang=lang, latent=latent, text=p["text"], deepen=af, takes=p["takes"], seed=p["seed"], merge=p["merge"], respell=p["respell"],
         char_limit=p["char_limit"], audio_s=round(dur, 2), synth_compute_s=round(synth, 1), asr_compute_s=asr, synth_s_per_audio_s=round(synth / dur, 2),
         asr_s_per_audio_s=round(asr / dur, 3), picks=[c["picked"] for c in p["chunks"]],
         chunks=[dict(index=c["index"], paragraph=c["paragraph"], text=c["text"], picked=c["picked"], seed=c["takes"][c["picked"]]["seed"],
                      asr=c["takes"][c["picked"]]["asr"], word_errors=c["takes"][c["picked"]]["word_errors"], extra_words=c["takes"][c["picked"]]["extra_words"],
                      clean_takes=sum(1 for t in c["takes"] if t["word_errors"] == 0 and t["extra_words"] == 0)) for c in p["chunks"]],
         finished=time.strftime("%Y-%m-%dT%H:%M:%S"))
json.dump(m, open(f + ".manifest.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("manifest written; audio %.1f s, synth %.0f s (%.2f x), asr %.0f s" % (dur, synth, synth / dur, asr))
PY
  touch "$OUT/state/3.done"
fi
say "done in $(( $(date +%s) - T0 )) s wall (this invocation)"
