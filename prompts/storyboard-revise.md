---
prompt: storyboard-revise
todo: Hub\diary-tasks.md > Sub-agent prompts > storyboard-revise
model: sonnet
arguments: none (one run covers Episodes 1-4)
created: 2026-11-13
---
# storyboard-revise: apply Jim's decisions to the Ep1-4 scene plans + find an Ep1 newsreel

## Goal
Revise the four draft scene plans in one pass (one context, to save tokens) after Jim's review, and research candidate newsreel clips for the Episode 1 opening. Drafts stay drafts; Jim decides.

## Read only these files (nothing else; do not search the tree)
1. `D:\Claude\Projects\Diary\Storyboards\enriched\Episode-01-enriched.md` .. `Episode-04-enriched.md` (the drafts to revise)
2. `D:\Claude\Projects\Diary\Text\EN\2-5.txt` and `2-6.txt` (boundary edit only)
3. `D:\Claude\Projects\Diary\Archival-Images\ep01\landmarks.md`, `ep03\landmarks.md`, `ep04\landmarks.md`, and directory listings (ls) of `ep03\thumbs` and `ep04\thumbs` (to settle which landmark images really exist)
4. `D:\Claude\Projects\Diary\PIPELINE-SPEC.md` section 5.6 only
Do NOT view image files. Do not re-read the other page texts; the drafts already summarise them.

## Decisions by Jim (final; do not reopen)
- **Ep1 opening = event_first:** a newsreel clip of the invasion of Poland (1 Sept 1939) comes first, then a fade into the standard opening (face half-frame fades in, the journal page follows, he begins speaking, overlay shows title, topic, date range, page range). Add this as a new first scene e01-s00 (newsreel) with a fade transition into the face opening. The scene list still covers the narrated text exactly once; s00 carries no narration, only archival audio or music.
- **Ep1/Ep2 boundary moves:** Ep1 ends after the sentence "We go to sleep at 9:30." (the first three sentences of page 2-6, which complete the sentence cut at the end of 2-5). Extend Ep1's outro scene to include them; Ep1 page range becomes 1-2 .. 2-6 (2-6 partial). Ep2 begins at "January 1, 1940 - NEW YEAR" (page 2-6, partial); redo Ep2's first scene start, page range 2-6 (partial) .. 2-21, and recheck its date range.
- **Keep as written, no questions about these:** the taxi-driver/brothel anecdote (p.1-9, e01-s10); the "December 23, 1939 - Christmas Eve" heading (p.2-4); the Sudanese-soldiers passage (pp.2-49/2-50, e04-s18; keep original Polish and the English translation verbatim); all surname/place spelling variants in source text.
- **Captions use corrected spellings** (orthography only; source text is never edited): Gigondes and Gigadas -> **Gigondas**; Harbowski -> **Habowski**; Sodecki -> **Sadecki**. Put these in the pronunciation watchlist as `source -> caption/spoken form` pairs.

## Tasks
1. Write revised plans as NEW files `Episode-01-enriched-v2.md` .. `Episode-04-enriched-v2.md` in `D:\Claude\Projects\Diary\Storyboards\enriched\` (same sections as the drafts; keep the originals untouched). Ep3 and Ep4 change only where the decisions above or the checks in task 2 require; say "unchanged" rather than rewriting. Remove the questions Jim has answered; keep the rest, max 5 per episode.
2. Landmark check: for Ep3 and Ep4, state for each landmark whether its candidate file is actually present in `thumbs` (drafts say Ep3 E3-L1 Pilsudski portrait and Ep4 L2 Paris file are missing; Ep4 landmarks.md marks L1/L3/L4 as gaps though thumbs may exist). Report facts only; do not edit landmarks.md. Keep Ep4's proposed armistice landmark (L5) as a proposal.
3. Newsreel research (WebSearch/WebFetch; do not download): find 3-6 candidate public or archival newsreel/film clips of the German invasion of Poland, 1 Sept 1939 (bombing of Polish cities, Wehrmacht crossing the border, Wielun/Warsaw), prioritising sources that state their rights clearly (National Archives NARA, Wikimedia Commons, Internet Archive, Imperial War Museum, US Holocaust Memorial Museum, Polish Filmoteka / NAC). Write `D:\Claude\Projects\Diary\Storyboards\enriched\ep01-newsreel-candidates.md`: a table with title, URL, holder, stated rights/licence (quote the site's wording briefly or say "unclear"), approx. duration, audio (narration language / silent), and why it fits; note which would work with the project's non-commercial status and what credit line each needs. Do not claim a licence you did not see on the page.

## Allowed writes
Only the five new files named above. Edit nothing else. You have device_bash for the PC files (ToolSearch "select:mcp__remote-devices__device_bash"; `D:\Claude\...` is `$HOME/mnt/Claude/...`; calls are 120 s, batch commands).

## Report (to the parent, under 25 lines)
Files written; per episode: scene count and page range; any coverage doubt; landmark check results; newsreel candidates ranked with the best one and its rights status; anything you could not do.
