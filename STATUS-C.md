# STATUS-C (workstream C) - rewritten 2026-11-11 ~11:45 local
STATE: STOPPED at step 2 (discovery), blocked. Step 1 done. Nothing pushed, nothing deleted.
DONE
- Git: Diary\ repo on main, baseline c315de5 (484 text files), origin added, tools\snapshot (.ps1/.cmd) tested.
- Notes files created fresh: NOTES.md, RUNLOG-C.md, STATUS-C.md.
- Discovered: loki = RTX 4080 SUPER 16 GB, ~890 GB free on D:, git 2.56, Claude CLI present,
  only Python 3.14 (likely too new for coqui-tts), NO ffmpeg.
- FaceTest (14 files): brokkr TTS repo @50943d9 (Docker, GTX 1080 Ti, GPU index 1, XTTS-v2 fp32),
  2 test wavs (Kumar65_Ilkin35 EN + phonetic PL), docker-build.log ends in a FAILED build.
  audition texts that audition.py needs are not in the copy.
NEXT ACTION (once unblocked)
1. brokkr discovery (service, repo, texts, GPU/VRAM, ffmpeg, Claude CLI) via ssh.
2. Portable Python 3.11 (uv) + venv + portable ffmpeg under Assets\Diary on loki.
3. Step 3 TTS trial (page 1, 2-3 voices) and HTML listening sheet.
BLOCKERS / NEEDS JIM
- ssh claude-agent@brokkr: Permission denied (publickey) twice. loki has no keys in ~\.ssh. Please
  authorise a key for claude-agent (or tell me to run ssh-keygen on loki and give you the .pub; that
  creates a credential file, so I did not do it unasked).
- Create D:\Claude\Assets\Diary and connect it (or let me request D:\Claude\Assets).
- Docker: FaceTest\tts is Docker-based; confirm if I may use it on brokkr, else I build a venv.
- Python: OK to fetch portable uv + Python 3.11 under Assets\Diary (user-level, no admin)?
SPEND: ~20 tool calls, ~25 min, low tokens.
