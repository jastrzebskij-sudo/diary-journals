# RUNLOG-A (workstream A: notebook 2 transcription) - append-only

## 2026-11-11 (Wed), session 1, ~11:35-12:15 local
- Access granted by Jim: Projects\Diary, Assets\Diary; staging image copies into the session; subagents with chosen models; PowerShell for tools\snapshot.cmd only. Added rule from Jim: in bulk, stop after the first 20 pages and report cost.
- Read Vision.md, NOTES.md, STATUS-C.md, head/tail of Diary-PL.txt. Inventory: 87 scans in Images\Notebooks\2 (1..84, 40_, "_ 2z 84", "_ 2z 84a"), ~1400x1780 px JPEG, 49 MB.
- Wrote tools: a_paths.py, a_prep_images.py, a_glossary_seed.py, a_stamp.py, a_manifest.py, a_compare.py, a_viewer.py, a_transcribe_prompt.md (v1).
- Ran a_prep_images.py: 87 pages x (e1568, e1200, e900) x (plain, contrast "c") + 8 contact sheets -> Assets\Diary\Notebook2\prep (~230 MB).
- Ran a_glossary_seed.py: 325 candidates -> Notebook2\glossary_candidates.csv. Hand-curated Notebook2\glossary.csv (78 entries, weighted to Dec 1941-Jan 1942 names/places).
- Ran a_manifest.py: Notebook2\manifest.csv, 87 rows, type/date columns still empty (no page has been read yet).
- Ran a_viewer.py: Notebook2\viewer.html builds; JS syntax-checked with node; NOT yet opened in a browser, no transcripts in it yet.
- Self-test of a_compare.py / a_stamp.py on synthetic text: OK.
- FAILED (mistake, mine): read 2 contact sheets with the loki Read tool; in this session it returns the image as base64 text, not as a picture. Nothing learned from them, roughly 50k tokens wasted. Do not read images that way again.
- FAILED x2: subagent on loki (survey of page types; then a one-line check): "OAuth session expired and could not be refreshed". Stopped per the two-failures rule.
- Not available in this session: the file-staging tool that would bring image copies into the session. It is only offered behind the "enable computer use" switch, which is outside the approved list, so not called.
- Result: no page has been read by any model. Pilot (step 3) not started. Extra-file order is provisional only.
- tools\snapshot.cmd run via PowerShell on loki: commit e480033 (local only). STATUS-A.md written. Stopped to wait for Jim.

## 2026-11-11 (Wed), session 1 continued, ~12:10-12:45 local
- Jim approved: device tools switch on, file staging only, no computer_* tools; pilot in the chat, one model at a time (Fable, then Opus, then Sonnet); read each page once; 1200 px copies; keep verbatim spelling. Bulk later through subagents once Jim fixes the Claude Code sign-in.
- Staged prep\e1200\{01,17,33,40,55,75}.jpg into the session. Pilot pages chosen by spread, without a survey.
- Fable pass (configured id claude-fable-5-2): each page viewed once, transcript written straight after -> Notebook2\pilot\fable-e1200\<id>.txt/.json. a_stamp.py recounted and stamped.
- Counts (words / marked uncertain): 01 329/6 (1.8%); 17 244/3 (1.2%); 33 186/23 (12.4%, torn page); 40 209/2 (1.0%, French clipping); 55 217/4 (1.8%); 75 191/3 (1.6%). All six 1376/41 (3.0%); the five undamaged pages 1190/18 (1.5%). These are self-marked doubts, not measured errors.
- Content found: p.01 opens 1 II 1942 (camp at km 98); p.33 = 29 VI-4 VII 1942; p.40 = Echo d'Oran clipping, dateline 19 Aug 1942, Polish note along its left edge; p.55 = 10-12 X 1942, train to Casablanca; p.75 = 8-9 XII 1942, Scotland.
- Glossary: +13 entries from the pilot pages (Nowicki, Aïn Sefra, siroko, Berguent, Oujda, Taza, Fez, Casablanca, D.I.M., trawajerzy, Auchtertool, Baczyński, Echo d'Oran).
- a_viewer.py rebuilt. Viewer tested in a headless browser in the session (copy of viewer.html + staged images): loads, image shows, 23 highlights on p.33, edit mode and paging work, no script errors. That test screenshot showed p.33 on screen again; the transcript was not changed afterwards.
- Not done: Opus and Sonnet passes (need Jim to switch model); resolution test (900 px / contrast); survey of page types; order of the three extra files.

## 2026-11-11 (Wed), session 2, ~17:27-17:40 local (Opus 5.5, configured id claude-opus-5-5)
- Fresh conversation. Read STATUS-A, RUNLOG-A, NOTES, tools\a_transcribe_prompt.md only.
- Access granted by Jim: Projects\Diary and Assets\Diary\Notebook2, file staging only. The staging tools were not
  offered at first; Jim approved turning on the device switch for file staging only. No computer_* tools used.
- Staged glossary, a_compare/a_stamp/a_paths, prep\e1200\{01,17,33,40,55,75}.jpg.
- Opus pass: each page viewed once, transcript + json written straight after -> Notebook2\pilot\opus-e1200\.
  A few readings were revised from the same single view while writing (p.17, p.55 "tra-/cimy", p.75 "rumiane");
  no page was viewed twice. a_stamp.py recounted and stamped.
- Counts (words / marked uncertain): 01 328/5; 17 244/5; 33 188/30 (torn); 40 209/3; 55 220/4; 75 192/3.
- Fable transcripts staged only after all six Opus files were written. a_compare.py fable-e1200 (ref) vs opus-e1200:
  all pages 101 of 1376 words differ (7.3%); readings-only 5.5%; worst undamaged pages 17 and 01; see STATUS-A.
- Wrote pilot\compare_fable_vs_opus_e1200.csv. STATUS-A rewritten. Snapshot via tools\snapshot.cmd (local only, no push).

## 2026-11-11 (Wed), session 2 continued, ~17:38-17:55 local (Sonnet 5.5, configured id claude-sonnet-5-5)
- Jim switched the model to Sonnet 5.5 and said "go". Same conversation, so earlier Opus work was in context.
- Sonnet pass: six staged prep\e1200 pages, each viewed once, transcript + json written straight after -> Notebook2\pilot\sonnet-e1200\.
  a_stamp.py recounted and stamped. Counts (words / marked uncertain): 01 328/4; 17 246/4; 33 188/27 (torn); 40 209/2; 55 220/3; 75 191/3.
- CAVEAT (my mistake in process): before this pass the Opus transcripts and a printed list of Fable-vs-Opus word differences were
  already in this conversation. I did not open any transcript files during the pass, but I could not unsee them. Several Sonnet
  readings coincide with Fable's (sierż., szkociąt, czerstwe, wyspali). The set is not independent.
- a_compare.py: Fable ref vs Opus + Sonnet; Opus ref vs Sonnet; readings-only pairwise table. Results in STATUS-A.
- Wrote compare_fable_ref_e1200.csv and compare_opus_ref_sonnet_e1200.csv. STATUS-A rewritten. Snapshot via tools\snapshot.cmd (local only, no push).
- Not done: resolution test (not requested in this message; waits for Jim), viewer rebuild.

## 2026-11-11 (Wed), session 2 continued, ~18:00-18:15 local (Sonnet 5.5)
- Jim: no more passes; (1) write rules v2, (2) rebuild the viewer with all three sets, highlighting disagreements, script only, no scans viewed; (3) snapshot, stop.
- tools\a_transcribe_prompt.md rewritten as v2 (conventions in STATUS-A). Reading of "(clippings first)": clipping/photo/map blocks come first, then the handwritten main text, then [margines: ...] notes last. Words written in a margin that belong to a line stay in place.
- tools\a_paths.py: MARKUP_LINE also skips [mapa: ...]; tokens() reads v2 [margines: text] (words of the note count). Regression: counts of fable/opus/sonnet sets unchanged (1376/41, 1381/50, 1382/43).
- tools\a_viewer.py: disagreement marking (blue), rejoins line-end hyphens, ignores crossed-out words, gaps and margin position in the comparison, per-page disagreement count in the page list, toggle button. Built in the session from a scratch copy of the tree (empty placeholder files named like the originals, so a_paths.pages() works; no scan content touched); viewer references images, none embedded. Output Notebook2\viewer.html, 3 sets, 87 pages, image base e1568 unchanged. Checked with a headless browser on the text only: no script errors, marks and tooltips present, toggle and paging work.
- Disagreement counts per page (words in the busiest set that another set reads differently): 01 16, 17 14, 33 12, 40 2, 55 5, 75 5. (Opus-vs-Fable p.55 count was 7 before allowing [?] after a hyphen.)
- NOTES.md: two [A] lines appended. Snapshot via tools\snapshot.cmd (local only, no push).

## 2026-11-12T04:01:07 calib-fable (blind cost calibration, prompt v2 + override rules)
- model: claude-fable-5-2; images: e1200; .txt only (no .json, no stamp)
- timestamps (VM clock, UTC): start 2026-11-12T03:57:55; pause 1 2026-11-12T03:59:06; end 2026-11-12T04:01:07
- pages done: 01, 17, 28, 29, 30 -> Notebook2/calib-fable/
- counts: 01: 323 words, 4 uncertain; 17: 237 words, 3 uncertain; 28: 216 words, 9 uncertain; 29: 211 words, 7 uncertain; 30: 238 words, 3 uncertain
- tool calls: 20 (incl. 2 folder-access requests, 1 call that did not run)

## 2026-11-12T04:10:11 calib-fable batch 2 (blind cost calibration, prompt v2 + override rules)
- model: claude-fable-5-2; images: e1200; .txt only (no .json, no stamp)
- timestamps (VM clock, UTC): start 2026-11-12T04:05:57; end 2026-11-12T04:10:11
- pages done: 31-40 (none missing; 40a not included) -> Notebook2/calib-fable/
- counts (words/uncertain): 31: 261/4; 32: 222/6; 33: 185/25; 34: 260/2; 35: 252/4; 36: 248/3; 37: 238/5; 38: 221/3; 39: 249/6; 40: 205/3; total 2341/61
- tool calls: 22

## 2026-11-12T04:41:49 calib-fable batch 3 (blind cost calibration, prompt v2 + override rules)
- model: claude-fable-5-2; images: e1200; .txt only (no .json, no stamp)
- timestamps (VM clock, UTC): start 2026-11-12T04:26:56; end 2026-11-12T04:41:49
- pages done: 02-16, 18-27, 40a, 41-49 (35 pages, manifest order; no errors or limit messages) -> Notebook2/calib-fable/
- counts (words/uncertain): 35 pages; 02: 326/9; 03: 238/3; 04: 347/5; 05: 268/6; 06: 317/1; 07: 240/4; 08: 264/4; 09: 251/2; 10: 234/2; 11: 280/4; 12: 235/2; 13: 260/1; 14: 259/4; 15: 240/2; 16: 282/7; 18: 292/8; 19: 256/5; 20: 265/5; 21: 241/2; 22: 247/3; 23: 244/2; 24: 206/4; 25: 216/2; 26: 255/1; 27: 242/3; 40a: 221/4; 41: 190/3; 42: 191/4; 43: 214/4; 44: 206/6; 45: 248/3; 46: 214/3; 47: 184/1; 48: 179/1; 49: 233/5; total 8585/125
- tool calls: 72

## 2026-11-12T17:11:35+00:00  Workstream A - calib-fable, pages 50-84b
- model: claude-fable-5-2 (configured id; serving model may differ); images: e1200; prompt: a_transcribe_prompt.md v2 + session rules
- start: 2026-11-12T16:53:06+00:00  end: 2026-11-12T17:11:35+00:00
- pages=37 words=6181 uncertain=113 total_txt=87
- output: .txt only (no .json, not stamped); one view per page, no proofreading
- tool calls: about 90 (37 image views, 37 transcript writes, 2 staging, 2 access requests, rest setup/count)

## 2026-11-12 read2-fable (blind second read, Notebook 2)
- model: claude-fable-5-2 (configured id; serving model may differ)
- start 2026-11-12T17:35:15Z, end 2026-11-12T17:49:06Z (the two date calls)
- pages done: 40 (01-39, 40), images prep/e1200, prompt v2 + run rules; output Notebook2/read2-fable/<page>.txt (txt only, no json)
- words: 10069; uncertain tokens ([?], [...], [.....], [a|b?]): 114 (shell count per v2 counting rule, not a_paths.py)
- tool calls: 90 (44 shell, 40 image views, 2 staging, 3 tool lookups, 1 access request)
- no errors or limit messages; each page viewed once, no proofreading
