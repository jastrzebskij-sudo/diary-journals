# STATUS-C (2026-11-12 19:3x)
State: production skeleton complete: ASR + one-command audio pipeline on brokkr (validated), EN text prep + 67 s EN sample sent for Jim's listen-check, batch face render and assembly with --jx on loki.
Done: Whisper on brokkr GPU 0 (venv-asr, static ffmpeg); tools\c_brokkr_episode.sh (render -> Whisper pick -> deepen -> manifest, resumable, STOP file) reproduces v3 picks exactly (byte-identical picked audio); tools\c_tts_prep_en.py; tools\c_render_faces.ps1 tested on v3 (2.4 s per audio s); c_assemble.py --jx; ep01_p1_PL_v2.mp4; README-C-pipeline.md.
Next: Jim listen-checks EN sample (names Otvotsk/Vola/Yaronski/Garvolin are my guesses) and PL v3; then render Ep1 full both languages; Jim runs c_render_faces.ps1 overnight; optional: overlap ASR with render and use both brokkr GPUs for ASR.
Blockers: none.
Needs Jim: listen-check EN v1 (accent, cadence, name respellings) and PL v3 (Otwock, pacing); pick the face portrait/model; go before any full-episode run.
Flags: no push/upload done; Whisper pick is ~80% of compute (8-10 x real time for 8 takes); EN page 1 is 67 s, not 90 s (EN is ~20% faster than PL); could not delete scratch scripts tools\c_brokkr_asr_speed.sh etc. (no delete permission); ASR on loki no longer used.
Spend: this session about 1.2 h wall-clock, moderate token use.
