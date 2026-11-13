# Workstream C pipeline (TTS, face, assembly) - README

Last updated 2026-11-12. Everything is scripts; no AI tokens are used while a job runs. Nothing is uploaded or pushed.

## Machines
- **brokkr** (`ssh brokkr-agent`, user claude-agent, no sudo/Docker): 2x GTX 1080 Ti. XTTS-v2 renders on GPU 1 (`~/work/tts/.venv`), Whisper-medium ASR on GPU 0 (`~/c-workstream/venv-asr`). Static ffmpeg 7.0.2 (with rubberband) in `~/.local/bin`. Scripts live in `~/c-workstream`, renders in `/srv/tts-out/render/<run>`.
- **loki** (RTX 4080 SUPER): face render (patched SadTalker) and assembly. Toolchain under `D:\Claude\Assets\Diary` (python\, bin\ffmpeg.exe, venv\face). Final audio is pulled to `Assets\Diary\tts\`.

Tip: over ssh from PowerShell never pass quoted multi-part commands; `scp` a script file and run `ssh brokkr-agent bash c-workstream/<script>`.

## 1. Text preparation (before the pipeline; the pipeline takes prepared text)
- **PL**: `tts_prep_pl.py` (numbers/abbreviations spelled out, digit-free; the TTS guard refuses digits) then, for narration pacing, hand-written comma insertions (`c_tts_commas_ep01.py`, narration copy only).
- **EN**: `python tools\c_tts_prep_en.py SRC.txt OUT.txt [--from "first words"] [--to "last words."]` - joins wrapped lines, abbreviations, dates/years/times/ordinals/numbers to words, dashes, and Polish names respelled from `tools\c_tts_names_en.txt` (Written=Spoken; the first guesses are Claude's assumption, Jim's ear decides). Unknown digits are an error. Also writes `OUT.txt.names.txt` (Spoken=Written) so the ASR pick compares against the spelling Whisper writes.
- Chunking is one chunk per sentence; XTTS char limit: **pl 224, en 250**; a longer sentence is an error (split it in the text). Unchunked paragraphs were tested and rejected (truncation, rate/pitch drift).

## 2. Episode audio, one command (brokkr)
```
scp tools\c_brokkr_episode*.{sh,py} brokkr-agent:c-workstream/
ssh brokkr-agent 'nohup bash ~/c-workstream/c_brokkr_episode.sh LANG TEXT.txt OUTDIR NAME LATENT.pth [--takes 8] [--seed 5000] [--merge N ...] [--names FILE] [--respell OLD=NEW ...] > ~/c-workstream/NAME.out 2>&1 < /dev/null &'
```
`LANG` pl|en; `LATENT` = file in `~/work/tts/latents` (episode narrator: `c_Kumar65_Ilkin35_80_Damien20.pth`); `--merge N` renders 0-based sentence N together with the next (use when a rare name ends a chunk, e.g. Otwock; XTTS appends a junk word after a chunk-final rare name).
Steps and outputs in `OUTDIR`: (1) `c_brokkr_episode_render.py` N takes per chunk, seed = seed + 100*chunk + take, `take_sNN_tK.wav/.json`; (2) `c_brokkr_episode_pick.py` Whisper transcribes every take, score = word errors + 2 x extra trailing words + 5 x |pace/median - 1|, best take per chunk, joined with 0.3 s (sentence) / 0.7 s (paragraph) gaps -> `picked_all.wav`, `picked.json`; (3) deepen -1.0 semitone + bass +2 dB (`DEEPEN_ST`, `DEEPEN_BASS` env override), `final/NAME.wav` (24 kHz), `NAME_16k.wav`, `NAME.mp3` (192 kb/s), `NAME.manifest.json` (text, latent, seeds, picks, ASR text per chunk, compute seconds).
- **Resumable**: re-run the same command; finished takes/ASR/steps are skipped (`OUTDIR/state/*.done`).
- **STOP**: `touch OUTDIR/STOP` (or `~/c-workstream/STOP`); the current take/ASR item finishes, exit code 3. Remove the file to resume.
- **Log**: `OUTDIR/run.log`. Pull only finals: `scp brokkr-agent:OUTDIR/final/* Assets\Diary\tts\<ep>\`.
- `c_brokkr_asr.py` alone: wav -> JSON with word timestamps (`ASR` check of any file; GPU 0).
- **Validated**: Ep1 p1 PL reproduces loki's v3 picks [0,6,1,3,5,2,2,5,3] and the picked audio is byte-identical (MD5) to loki's `takes3\picked_all.wav`.
- Known limits: Whisper writes digits, so number words are ignored in scoring; chunk-final names that Whisper spells differently need a names file; ASR is a hint, the ear decides.

## 3. Face render (loki, run by Jim)
`tools\c_render_faces.ps1 -AudioDir <folder of narration wavs> -Image <portrait.jpg>[,<portrait2.jpg>] -OutDir <dir> [-Size 256] [-Preprocess full]`
Picks the GPU with most free memory (needs 6000 MB free), converts audio to 16 kHz, one SadTalker job per page x portrait, `OutDir\<page>\<portrait>\DONE` = checkpoint (re-run skips done jobs, redoes a half-finished one), `results.csv` (seconds per audio second), `run.log`, STOP file `OutDir\STOP` or `Assets\Diary\face\STOP`. Exit 0 done, 3 stopped, 4 no free GPU, 1 a job failed.

## 4. Assembly (loki)
`python tools\c_assemble.py --episode 1 --page 1 --audio narration.wav --face face.mp4 --journal scan.jpg [--title title.jpg] [--jx PX] [--lang PL]` (run with `Assets\Diary\venv\face\Scripts\python.exe`). `--jx` shifts the journal crop horizontally from centre (clamped); for the Ep1 p1 spread use `--jx 400` (clamps to the right-hand page with the handwriting). Face division drifts 600 +- 40 px.

## 5. Throughput (measured)
Measured on Ep1 page 1 (10 sentences -> 9 chunks, 8 takes each = 72 takes, same latent, brokkr GTX 1080 Ti):

| run | audio | XTTS compute | Whisper compute | wall (sequential) |
|---|---|---|---|---|
| PL (val1) | 85.2 s | 158 s = 1.86 s/audio s | 712 s = 8.35 s/audio s | 886 s = 10.4 x |
| EN (v1) | 67.3 s | 124 s = 1.85 s/audio s | 512 s = 7.60 s/audio s | 651 s = 9.7 x |

Speech pace: PL 12.45 chars/s, EN 15.68 chars/s (final page incl. gaps). So an EN page is ~20% shorter than the same PL passage.
Whisper picking, not XTTS, is 80-85% of the compute (plain decode is CPU-bound, ~9 s/take on this host; word-timestamp mode is faster but changes the text slightly and was not adopted; fp32 is not faster).

Projection Ep1-4 (ASSUMPTION: audio = raw script characters / measured pace; text prep changes length by a few %): PL ~92 min audio, EN ~84 min audio (about 21-23 min per episode).
- Current pipeline, 8 takes, sequential: PL ~15.6 h, EN ~13.2 h (10.2 / 9.5 s per audio second).
- ASR overlapped with rendering on the other GPU (not built yet): PL ~12.8 h, EN ~10.6 h.
- ASR also split over both GPUs (not built yet, ideal): ~5 s per audio second, PL ~7.8 h, EN ~7.1 h.
- 4 takes instead of 8 halves each figure; the PL page had chunks with 0 clean takes of 8 (names), so fewer takes raises the chance of keeping an artifact.
Face render (loki, 256 px, one portrait): 2.4 s per audio second -> Ep1-4 PL ~3.7 h per portrait, EN ~3.3 h.
