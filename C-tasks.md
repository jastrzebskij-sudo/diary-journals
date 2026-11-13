# C-tasks (Workstream C: TTS, face, assembly)

## 2026-11-12 - build the production skeleton (first prompt)
Intent: Whisper ASR on brokkr, one-command PL/EN audio pipeline, EN sample, throughput numbers, batch face render, --jx and Ep1 p1 mp4, README.
- [x] 1. Whisper on brokkr GPU 0 + tools\c_brokkr_asr.py (2026-11-12)
- [x] 2. One-command episode audio pipeline; reproduces v3 picks exactly (2026-11-12)
- [x] 2b. Finals and manifests pulled to Assets\Diary\tts (2026-11-12)
- [x] 3. EN text prep + 67 s EN page-1 sample sent (2026-11-12)
- [ ] BLOCKED: Jim's listen-check of EN v1 and PL v3 before any further EN render
- [x] 4. Throughput report (PL ~10.2 s, EN ~9.5 s compute per audio second; Ep1-4 projection in README)
- [x] 5. tools\c_render_faces.ps1 tested on v3: 2.4 s per audio second (2026-11-12)
- [ ] BLOCKED: Jim runs c_render_faces.ps1 overnight himself
- [x] 6. c_assemble.py --jx, ep01_p1_PL_v2.mp4, README-C-pipeline.md (2026-11-12)
- [x] STATUS-C.md, NOTES [C] lines, snapshot (2026-11-12)

## 2026-11-12 (later) - English voice sounds synthetic; longer sentence gaps
Intent: find a comparable English-tuned voice for the narrator; lengthen pauses between sentences.
- [x] Voice-search scope and gap values chosen by Jim (2026-11-12)
- [ ] Voice candidates rendered for EN page 1 and ASR-checked
- [ ] Gap change applied to pipeline (EN, optionally PL) and sample re-rendered
- [x] Jim chose: gaps 0.5 s / 1.0 s EN only; voice search = XTTS English built-ins (2026-11-12)
- [x] Pipeline: --gap-sent/--gap-para (env GAP_S/GAP_P), built-in speaker names, DEEPEN_ST=0 skips deepen (2026-11-12)
- [ ] (running, ETA ~20:10; first two sent) Round 1 EN voices rendering on brokkr: current (control), current without deepen, Damien Black, Dionisio Schuyler, Damjan Chapman, Abrahan Mack, Royston Min, Kumar Dahl (paragraph 1, 4 takes)
- [ ] Round 2 (Jim's tinny-archival idea): higher-pitch built-ins Luis Moray, Ludvig Milivoj, Marcos Rudaski, Viktor Menelaos
- [ ] Archival band-limit demo on the best candidate (tinny via filter, not pitch)
- [ ] BLOCKED: Jim's listen-check of the candidate mp3s
- [x] Jim: keeps the higher-toned EN (cur_nodeep: no deepen) (2026-11-12)
- [x] Sent PL page 1 both ways for comparison: v3 deepened and undeepened, same takes (2026-11-12)
- [ ] BLOCKED: Jim to say whether PL also drops the deepen (match EN) or stays deepened
- [x] Jim: PL stays deepened (2026-11-12)
- [x] PL 5% faster clip (tempo 1.05, pitch kept) sent; pipeline got TEMPO env (2026-11-12)
- [x] Jim approved the 5% faster PL clip as is (gaps stay 0.3/0.7 s before the stretch) (2026-11-12)
- [ ] Next on Jim's go: render full Ep1 in PL (deepen -1.0, TEMPO 1.05, gaps 0.3/0.7) and EN (no deepen, gaps 0.5/1.0)

## 2026-11-12 (night) - full Ep1 overnight run, PL then EN, two portraits, 8 takes (Jim: "go")
Intent: build retry/independent brokkr job + loki pull/face/assemble loop, prep Ep1 PL and EN text per page, launch; hands-off overnight.
- [ ] Ep1 page list = Text\PL 1-2..1-12 and 2-1..2-5 (1-1 title page not narrated); sentences assigned to the page where they start
- [ ] PL Ep1 text prep: numbers/dates/times/abbreviations in correct case, bracket/ditto fixes, conservative commas; page 1-2 keeps Jim-approved commas
- [ ] EN Ep1 text prep per page (names respelled, first guesses)
- [ ] Brokkr job: pages one by one, 3 retries, PL and EN independent, STOP file, flags list
- [ ] Loki loop: pull finished pages, faces (WA0003 + WA0005), assemble both variants, resumable
- [ ] Launch and verify first page end to end
- [ ] BLOCKED (morning): Jim's listen-check; flagged sentences list
