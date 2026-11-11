# STATUS-C (workstream C) - rewritten 2026-11-11 ~11:50 local
STATE: working loki-only; brokkr on hold until Jim says go.
DONE
- Git baseline c315de5 + notes snapshot; tools\snapshot tested. Nothing pushed/deleted.
- Assets\Diary set up: Python 3.11, ffmpeg (libx264, nvenc), venv\face (torch 2.11 cu128, CUDA OK on RTX 4080 SUPER 16 GB).
- SadTalker installed (candidate 1) with checkpoints; setup script tools\c_setup_sadtalker.ps1.
- brokkr ssh: refused 3x; client offered no key (no agent reachable from loki's shell). Server side untested.
- FaceTest\tts = brokkr XTTS-v2 Docker repo @50943d9 (GTX 1080 Ti, GPU idx 1); its docker build log ends FAILED.
IN PROGRESS
- Placeholder PL narration with Edge-TTS (online Microsoft service; placeholder only, not the final voice).
- SadTalker run on WA0003/WA0005 with that audio; then tools\c_assemble.ps1/py (ffmpeg).
NEXT
1. Face bake-off candidates 2-3 (pending SadTalker result); judge sync, likeness, artifacts, speed.
2. Assembly script, page/episode as arguments, sepia/grain/moving division.
3. After Jim's go: brokkr discovery and XTTS-v2 renders (step 3), HTML listening sheet.
BLOCKERS / NEEDS JIM
- brokkr ssh agent for loki's shell (Jim working on it). Docker use on brokkr still unconfirmed.
- Narrator voice choice (step 3) is Jim's.
SPEND: ~40 tool calls, ~35 min, modest tokens.
