# STATUS-C (workstream C) - rewritten 2026-11-11 ~12:20 local
STATE: step 3 done; waiting on Jim narrator pick (sheet audio replaced by plain MP3s) and SadTalker decision.
DONE
- Git local baseline + snapshots (nothing pushed). Toolchain on loki (Assets\Diary: py3.11, ffmpeg, venv\face).
- brokkr discovery: no XTTS service; ~/work/tts has venv, weights, latents; run as batch scripts (GPU1). uv added user-level.
- Ep1 page 1 (2 paragraphs) rendered in 3 blend voices, 107-118 s each (target was 60-90 s); listening sheet
  Assets\Diary\tts\ep01p1\narrator-choice-ep01p1-PL.html sent to Jim.
- tools\c_assemble.py tested with a still face + placeholder audio.
BLOCKED
- SadTalker fails at face3d\util\preprocess.py:101 (t[0],t[1] arrays); needs a one-line third-party edit (Jim's OK) or another model.
NEXT
1. On Jim's pick: re-render chosen voice if page 1 is to be shortened to ~90 s (first paragraph + part of 2).
2. Face bake-off (3 models) on identical audio: that audio = chosen voice (or Kumar65_Ilkin35 meanwhile).
3. Add --jx to c_assemble.py; assemble final mp4; README.
NEEDS JIM
- Narrator pick (the sheet) and whether page 1 should be cut to ~90 s.
- OK to patch SadTalker line (Assets copy) or choose different models for the bake-off.
- brokkr notes: ~/CLAUDE.md there asks for agent/<topic> branches pushed to outbox; I pushed nothing and committed nothing on brokkr.
SPEND: ~85 tool calls, ~1h45, moderate tokens.
