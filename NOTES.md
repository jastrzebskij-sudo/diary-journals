[C] 2026-11-11 Workstream C runs on loki (RTX 4080 SUPER 16 GB); git for Windows 2.56 is installed, ffmpeg is not on loki's PATH yet.
[C] 2026-11-11 Git repo at Diary\ is local only (remote origin added, no push); .gitignore keeps text, scripts and manifests, excludes media, archives, Images\ and key-like files; core.autocrlf=false so files commit byte-for-byte.
[C] 2026-11-11 Repeatable steps are scripts in Diary\tools\ with prefix c_; tools\snapshot commits locally and retries on index.lock.
[C] 2026-11-11 FaceTest\tts is a Docker (GTX 1080 Ti) build of XTTS-v2 from brokkr commit 50943d9; Docker use needs Jim's OK, so the plan is a user-level venv unless Jim approves Docker.
[C] 2026-11-11 Blocked on brokkr until an ssh key for claude-agent is authorised; TTS and face work on loki wait for D:\Claude\Assets\Diary and a portable ffmpeg.
