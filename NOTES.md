[C] 2026-11-11 Workstream C runs on loki (RTX 4080 SUPER 16 GB); git for Windows 2.56 is installed, ffmpeg is not on loki's PATH yet.
[C] 2026-11-11 Git repo at Diary\ is local only (remote origin added, no push); .gitignore keeps text, scripts and manifests, excludes media, archives, Images\ and key-like files; core.autocrlf=false so files commit byte-for-byte.
[C] 2026-11-11 Repeatable steps are scripts in Diary\tools\ with prefix c_; tools\snapshot commits locally and retries on index.lock.
[C] 2026-11-11 FaceTest\tts is a Docker (GTX 1080 Ti) build of XTTS-v2 from brokkr commit 50943d9; Docker use needs Jim's OK, so the plan is a user-level venv unless Jim approves Docker.
[C] 2026-11-11 Blocked on brokkr until an ssh key for claude-agent is authorised; TTS and face work on loki wait for D:\Claude\Assets\Diary and a portable ffmpeg.
[C] 2026-11-11 Toolchain lives under D:\Claude\Assets\Diary: python\ (3.11), bin\ffmpeg.exe, venv\face (torch cu128); scripts must call these paths, not system PATH.
[C] 2026-11-11 Jim: brokkr retry only on his word; no ssh key is created by me; loki-only work (Edge-TTS placeholder narration, SadTalker, assembly script) continues meanwhile.
[A] 2026-11-11 Workstream A: scripts are tools\a_*.py (a_paths.py holds all paths and page order); text outputs in Notebook2\, image copies in D:\Claude\Assets\Diary\Notebook2\prep; originals under Images\ are only ever opened for reading.
[A] 2026-11-11 Page ids are zero-padded scan numbers (01..84); transcripts are Notebook2\transcripts\<id>.txt with <id>.json beside them; a_stamp.py recounts words and records model, image set, prompt version and date.
[A] 2026-11-11 Transcription is diplomatic (the writer's spelling is kept, no correction); marks: word[?], [a|b?], [...], [margines], [wycinek]..[/wycinek], [zdjęcie: ...]; rules live in tools\a_transcribe_prompt.md (v1).
[A] 2026-11-11 PROVISIONAL, not confirmed from content: 40_.jpg = 40a (after 40), "_ 2z 84.jpg" = 84a, "_ 2z 84a.jpg" = 84b (after 84); set in a_paths.py EXTRA.
[A] 2026-11-11 In the Cowork chat session the loki Read tool returns images as base64 text, not as pictures: never use it for scans; images must be read by subagents on loki or staged into the session.
[C] 2026-11-11 c_assemble.py is the assembly entry point (args: --episode --page --audio --face --journal [--title]); face may be mp4 or a still; look/grain/zoom are arguments, defaults sepia, grain 12.
[C] 2026-11-11 SadTalker needs a compatibility shim (tools\c_sadtalker_shim.py) and a remaining fix in face3d preprocess.py; no third-party file has been edited yet, awaiting Jim's OK to patch it or to switch candidate.
