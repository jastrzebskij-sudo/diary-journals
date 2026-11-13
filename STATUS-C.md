# STATUS-C (2026-11-12 19:3x)
State: production skeleton complete: ASR + one-command audio pipeline on brokkr (validated), EN text prep + 67 s EN sample sent for Jim's listen-check, batch face render and assembly with --jx on loki.
Done: Whisper on brokkr GPU 0 (venv-asr, static ffmpeg); tools\c_brokkr_episode.sh (render -> Whisper pick -> deepen -> manifest, resumable, STOP file) reproduces v3 picks exactly (byte-identical picked audio); tools\c_tts_prep_en.py; tools\c_render_faces.ps1 tested on v3 (2.4 s per audio s); c_assemble.py --jx; ep01_p1_PL_v2.mp4; README-C-pipeline.md.
Next: Jim listen-checks EN sample (names Otvotsk/Vola/Yaronski/Garvolin are my guesses) and PL v3; then render Ep1 full both languages; Jim runs c_render_faces.ps1 overnight; optional: overlap ASR with render and use both brokkr GPUs for ASR.
Blockers: none.
Needs Jim: listen-check EN v1 (accent, cadence, name respellings) and PL v3 (Otwock, pacing); pick the face portrait/model; go before any full-episode run.
Flags: no push/upload done; Whisper pick is ~80% of compute (8-10 x real time for 8 takes); EN page 1 is 67 s, not 90 s (EN is ~20% faster than PL); could not delete scratch scripts tools\c_brokkr_asr_speed.sh etc. (no delete permission); ASR on loki no longer used.
Spend: this session about 1.2 h wall-clock, moderate token use.

## Update 2026-11-12 19:4x
EN voice search running on brokkr (unattended, STOP file /srv/tts-out/render/c-en-voice/STOP): 12 candidates, paragraph 1, 4 takes, gaps 0.5/1.0 s; round 1 (8) then round 2 (4 higher-pitch). First two (control, no-deepen) sent. ETA all done ~20:10. Finals: brokkr /srv/tts-out/render/c-en-voice/finals. Pipeline now has --gap-sent/--gap-para (env GAP_S/GAP_P), built-in speaker names, DEEPEN_ST=0.
Needs Jim: listen to the candidates; say when to pull and send the rest.

## Update 2026-11-12 21:4x - voice recipes locked by Jim
PL: latent c_Kumar65_Ilkin35_80_Damien20, deepen -1.0 st/bass +2, TEMPO 1.05 (pitch-preserving), gaps 0.3/0.7 s. EN: same latent, NO deepen, gaps 0.5/1.0 s, TEMPO 1.0. Archival tinny feel to be done by band-limit filter in assembly. 10 other EN candidates remain on brokkr (finals dir) unreviewed.
Needs Jim: go for full Ep1 PL+EN renders (about 3.7 h PL / 3 h EN compute at 8 takes).
