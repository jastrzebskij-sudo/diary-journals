# STATUS-C (workstream C) - rewritten 2026-11-11 ~18:35 local
STATE: narration v2 (commas, take-selected) sent; waiting on Jim: Otwock spelling pick + SadTalker patch OK.
DONE
- Narrator chosen by Jim: Kumar65_Ilkin35 80% + Damien_Black 20% blend, deepened -1.0 st. Recorded in NOTES.md.
- Ep1 page 1 narration: Assets\Diary\tts\ep01_pl\narration_ep01_p1_PL.wav (+ _16k.wav, .mp3), 83.3 s, 93.6 Hz.
- Assembly script tools\c_assemble.py works (tested with still face); loki toolchain and brokkr TTS run via scripts.
- Git local snapshots only (nothing pushed).
BLOCKED
- Face models: SadTalker fails at face3d\util\preprocess.py:101 (t[0],t[1] arrays); fix = float() on those two values
  in the Assets copy. Awaiting Jim's OK; alternative = try other models first (MuseTalk/Hallo2/Sonic: several GB each).
NEXT
1. Face bake-off on narration_ep01_p1_PL_16k.wav with WA0003 (young/low-res) and WA0005 (older/sharp), 3 models,
   judge lip sync, likeness, artifacts, speed; manifest per run.
2. Add --jx to c_assemble.py; assemble final mp4 from the best face video; write README.
NEEDS JIM
- OK to patch the SadTalker line (Assets copy), and which other 2 models, if any, you prefer.
- Confirm the narration audio plays and sounds right (sent as mp3).
SPEND: ~140 tool calls, ~6.5 h wall incl. idle, moderate tokens.
