---
prompt: event-openings
todo: Hub\diary-tasks.md > Sub-agent prompts > event-openings
model: haiku
arguments: none
created: 2026-11-13
---
# event-openings: which episodes open with a major world event

## Goal
Jim is making a video series from his grandfather Stefan's WWII diary (16 episodes). Standard episode opening: the grandfather's face, then the journal page, with a title overlay. **Exception:** if an episode opens with or focuses on a major world event, an image tied to that event is shown first with the title information, then the usual pattern resumes. Decide, from the actual text, which of the 16 episodes warrant the event opening. This is a recommendation for Jim.

## Read only these files
1. `D:\Claude\Projects\Diary\Storyboards\00-Series-Overview.md`
2. For each episode NN = 01..16: `D:\Claude\Projects\Diary\Storyboards\Episode-NN-storyboard.md` (title, page table, notable pages), plus the English text of the **first two pages** of the episode: `D:\Claude\Projects\Diary\Text\EN\<page>.txt` (first pages are in the storyboard's page table).
3. `D:\Claude\Projects\Diary\Archival-Images\ep01\landmarks.md` ... `ep04\landmarks.md` where they exist (for known imagery), nothing else from that folder.
Do not view image files. Do not read other pages.

## Criteria
"Major world event" = a widely known historical event that an archival photo or clip would instantly convey (for example the invasion of Poland, the fall of France, the German attack on the USSR). Routine camp or garrison life is not. An episode qualifies if the event is in its first two pages or is the clear subject of the episode (title, notable pages).

## Output (create one new file)
`D:\Claude\Projects\Diary\Storyboards\enriched\event-openings.md`: a table with columns `ep`, `title`, `recommend` (event_first / standard), `event`, `evidence` (page and a short paraphrase, no long quotes), `known imagery` (from landmarks.md, or "none known"), `confidence` (high/medium/low). Then a 3-line note on anything ambiguous. Mark guesses "(assumption)".

## Rules
Do not edit, move or delete any existing file. No network. No git. Do not edit any tasks file.

## Done when
All 16 episodes have a row.

## Report back (under 80 words)
Output path, the list of event_first episodes, and any low-confidence rows.
