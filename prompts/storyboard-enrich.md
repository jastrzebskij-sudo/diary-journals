---
prompt: storyboard-enrich
todo: Hub\diary-tasks.md > Sub-agent prompts > storyboard-enrich
model: sonnet
arguments: EPISODE (1-4)
created: 2026-11-13
---
# storyboard-enrich: turn one episode storyboard into a scene plan

## Goal
Jim is making a bilingual (Polish, English) video series from his grandfather Stefan's WWII diary (Notebook 1, 16 episodes). The production pipeline builds each episode from **scenes**. Draft the scene plan for ONE episode so Jim can approve it and the pipeline can be driven from it. This is a draft for Jim's decision, not a final.

## Read only these files (nothing else; do not search the tree)
Let NN = EPISODE zero-padded (01-04).
1. `D:\Claude\Projects\Diary\Vision.md` (look, structure, landmarks, sparing face use)
2. `D:\Claude\Projects\Diary\Storyboards\Episode-NN-storyboard.md` (page table and notable pages)
3. `D:\Claude\Projects\Diary\Text\EN\<page>.txt` for every page of the episode (page list is in the storyboard; page 1-1 is a title page, not narrated)
4. `D:\Claude\Projects\Diary\Archival-Images\epNN\landmarks.md` (landmark ids and coverage) and, if present, `Archival-Images\epNN\manifest.csv`
5. `D:\Claude\Projects\Diary\PIPELINE-SPEC.md` sections 4.2, 5.4, 5.5, 5.6 only
Do NOT view image files (token cost). Use names, ids and notes in the CSV and md files.

## Decisions already made by Jim (do not reopen)
- Opening (standard): grandfather's face fades in (half frame), the journal page we are on follows quickly, he begins speaking; the overlay shows episode title, short topic, date range and page range. Exception **event_first**: if the episode opens with or focuses on a major world event, an image tied to that event is shown first with the title information, then the usual pattern.
- Faces are used **sparingly**: episode intro and outro, an occasional fade-in mid-episode, key points with no archival imagery. Archival imagery and clips predominate.
- **No hard cuts**: every scene boundary has a transition (default dissolve 1.0 s; fade through black for major events). Major events: both regions fade out and the landmark takes the full frame, with archival audio or music as a break between voice segments.
- Layout is a moving division, not fixed 50/50. Landmark sides used organically, not strictly alternating.
- Scenes must cover the episode text **exactly once, no gaps, no overlap**. Scene boundaries fall between sentences.
- Missing imagery never blocks a scene: give a fallback (journal-only, or face-only).
- Project is personal, educational, non-commercial; every archival image carries its credit.

## Output (create new files only)
Write `D:\Claude\Projects\Diary\Storyboards\enriched\Episode-NN-enriched.md` with these sections:
1. **Summary** (3-4 lines: what happens, date range, mood).
2. **Opening recommendation:** `standard` or `event_first`, with the evidence from the text (page and a short paraphrase) and confidence (high/medium/low).
3. **Scene list**, a table with columns: `scene id` (eNN-s01...), `pages`, `starts at` (first 6-8 English words of the scene's first sentence), `purpose`, `staging` (face on/off with reason; portrait left open), `landmark / assets` (ids from landmarks.md and candidate file names, or "gap"), `fallback`, `transition out`, `audio notes` (music or archival audio idea, flagged as idea).
4. **Pronunciation watchlist:** names, places, dates, numbers and abbreviations likely to trip TTS, with page (feeds the lexicon).
5. **Asset gaps:** landmarks without an image, and what kind of image would fit.
6. **Open questions for Jim** (max 5, each answerable in a line).

## Rules
- Mark every inference or guess with "(assumption)".
- Do not edit, move or delete any existing file. No network. No git. Do not edit `storyboard-enrich-tasks.md`.
- Keep the file under about 250 lines; prefer tables.
- Aim for few, well-chosen scenes (roughly one per natural narrative beat or landmark), not one per paragraph.

## Done when
The output file exists, the scene list covers every narrated page of the episode exactly once, and every landmark in landmarks.md appears in a scene or is listed under asset gaps.

## Report back (under 120 words)
Output path, number of scenes, opening recommendation with confidence, count of asset gaps, and anything you could not do.
