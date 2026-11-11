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
