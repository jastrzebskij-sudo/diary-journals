# STATUS-C (workstream C) - rewritten 2026-11-11 ~12:10 local
STATE: loki-only work paused at SadTalker (two-failure rule); brokkr on hold until Jim says go.
DONE
- Git: baseline + snapshots, local only. Assets\Diary toolchain: Python 3.11, ffmpeg, venv\face (torch cu128, numpy 1.26.4).
- Placeholder PL narration (Edge-TTS, 24.8 s) and tools\c_assemble.py; test mp4 built from a still portrait:
  Assets\Diary\video\test_ep01_p1_stillface.mp4 (sepia, grain, flicker, moving division, title crossfade).
- SadTalker installed; runs reach 3DMM extraction, then fail in third-party face3d\util\preprocess.py:101
  (np.array of unequal t[0],t[1] shapes). Proposed fix: float(t[0]), float(t[1]) in that file.
IN PROGRESS: nothing running.
NEXT
1. If Jim OKs: patch that line (third-party, in Assets), rerun SadTalker on WA0003 and WA0005; else pick another model.
2. Add --jx offset to c_assemble.py so the face does not cover the handwriting; rerun with real face video.
3. Candidates 2-3 for the bake-off (MuseTalk / Hallo2 / Sonic: need model downloads, several GB each).
4. After Jim's go: brokkr discovery, XTTS-v2 candidate voices, HTML listening sheet (his choice of narrator).
NEEDS JIM
- OK to edit the one line in SadTalker's third-party source (under Assets) or to switch model.
- Say go for brokkr when the agent is fixed. Docker use on brokkr still unconfirmed.
- FYI tools\ now has a_*.py files from another workstream; tools\snapshot commits them too.
SPEND: ~60 tool calls, ~65 min, moderate tokens.
