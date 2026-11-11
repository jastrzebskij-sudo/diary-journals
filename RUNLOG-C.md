2026-11-11 11:2x  start: Diary folder connected (loki); read Vision.md, Production-Tracker.csv, TTS-Prep-Report.md, tts_prep_pl.py; NOTES/RUNLOG-C/STATUS-C did not exist, created fresh
2026-11-11 11:2x  wrote .gitignore and tools\snapshot.ps1/.cmd; git init -b main, remote origin added (no push), 484 text files staged
2026-11-11 11:3x  git baseline committed locally c315de5 (484 files); tools\snapshot tested (nothing to commit)
2026-11-11 11:4x  ssh claude-agent@brokkr: Permission denied (publickey) x2; loki has no default ssh keys, none offered. Stopped per two-failure rule; did not use jimj or create keys
2026-11-11 11:4x  FaceTest read: tts\ = brokkr repo @50943d9, Docker image for GTX 1080 Ti (cu126), GPU index 1, XTTS-v2 fp32; docker-build.log ends in a failed build (userdel/useradd step, exit 6); texts\audition_*.txt referenced by audition.py are absent from the copy
2026-11-11 11:4x  loki: RTX 4080 SUPER 16 GB, D: has ~890 GB free, only Python 3.14 (too new for coqui-tts/torch likely), no ffmpeg, Claude CLI present; D:\Claude\Assets\Diary does not exist
