---
prompt: tts-prep-pl
todo: Hub\diary-tasks.md > Sub-agent prompts > tts-prep-pl
model: sonnet
arguments: none (one run covers Episodes 2-4, in order, one context)
created: 2026-11-13
---
# tts-prep-pl: draft the spoken (digit-free) Polish text for Episodes 2-4

## Goal
Narration (XTTS) needs **digit-free Polish with correct grammatical case**, abbreviations expanded, so numerals and abbreviations must be turned into words by hand-checked replacements (the renderer refuses digits). Episode 1 is done and is the style reference. Draft the replacement tables for Episodes 2, 3 and 4 so Jim (Polish speaker) can review them and the pipeline can apply them mechanically. Source text is NEVER edited; this produces `spoken_text` rules only.

## Read only these files (do not search the tree)
1. Style reference (Episode 1 result): `D:\Claude\Projects\Diary\Episodes\01-Invasion-and-Flight\prep-ref-pl\p2-5.txt`, `p1-10.txt`, `p1-9.txt` (prepared, digit-free pages) and the matching originals `D:\Claude\Projects\Diary\Text\PL\2-5.txt`, `1-10.txt`, `1-9.txt`. Learn the conventions from the pair: how dates (e.g. "28 XII"), times, sums, ordinals, abbreviations (kpt., por., mjr., p., gen., Mich.) and roman-numeral months are rendered, and how page-break joins and bracket notes are handled. `prep-ref-pl\prep-report.txt` lists what was converted and any open items.
2. `D:\Claude\Projects\Diary\tts_prep_pl.py` (only the ABBREVIATIONS list and docstring) and `D:\Claude\Projects\Diary\Lexicon\corrections-pl.tsv` (approved spelling corrections; apply them to the spoken form too).
3. The source pages: Episode 2 = `Text\PL\2-6.txt` (start at the line "1 I 1940 NOWY ROK"; the first three sentences of 2-6 now belong to Episode 1) through `2-21.txt`; Episode 3 = `2-22.txt`..`2-36.txt`; Episode 4 = `2-37.txt`..`2-50.txt` (all under `D:\Claude\Projects\Diary\Text\PL\`). Page 2-22 begins mid-sentence (continuation of 2-21).
Do not view images. Do not read other files.

## Rules (Jim, final)
- Source text and original spelling/grammar slips are kept in the source; **the spoken form fixes only orthography/punctuation** (no rewording, no grammar fixes, no cuts). Keep the period vocabulary exactly as written (e.g. "murzynów").
- Every digit and every abbreviation in the narrated text gets a spoken form, inflected correctly for its context (dates in the genitive as in Episode 1: "dwudziestego ósmego grudnia"; years as ordinals; sums and quantities in the case the sentence requires). If the correct case is genuinely ambiguous, choose the most natural reading and flag it.
- Superscript times ("9³⁰") and fractions: spoken naturally (e.g. "wpół do dziesiątej" or "dziewiąta trzydzieści"), flagged for Jim's choice.
- Bracket notes like `[...]`, gaps like `......`, stray page numbers (a lone number on its own, e.g. "12" inside a sentence) are **not narrated text decisions**: list them in the flags section, do not decide.
- Spoken respell of foreign names (French, Arabic, English) only when they are in the pronunciation watchlist of `D:\Claude\Projects\Diary\Storyboards\enriched\Episode-0N-enriched-v2.md` (section "Pronunciation watchlist"; read that section only) and mark each one `proposal`.

## Output (new files only)
For each episode N in 2, 3, 4 write `D:\Claude\Projects\Diary\Episodes\0N-<folder>\prep-PL-replacements.tsv` (folder names: 02-Winter-Quarters, 03-The-Storm-Breaks, 04-The-Fall-of-France). Tab-separated, header `page	find	replace	kind	note`:
- `page`: e.g. 2-7. `find`: an exact substring of the source page text, long enough to be unique on that page (include neighbouring words). `replace`: the spoken-form substring (same context words, digits/abbreviation converted). `kind`: numeral | date | time | abbreviation | name | punctuation | proposal. `note`: the case reasoning in a few words, or "?" if unsure.
- Order by page, then by position. The union of all `find` strings must cover every digit and listed abbreviation on those pages.
Also write `D:\Claude\Projects\Diary\Episodes\prep-PL-flags-ep2-4.md`: per episode, the flagged items (ambiguous case, brackets, gaps, stray numbers, time notation) with page and a 10-word context, each answerable by Jim in a line. Maximum 40 lines.
Self-check before reporting: for every `find`, confirm it occurs exactly once on its page (a short Python script with device_bash is fine) and that applying all replacements leaves no digit in the pages' narrated text (after the Episode 2 start line); fix and recheck. Report any that fail.

## Allowed writes
Only the four new files above. Edit nothing else. Use device_bash for the PC files (ToolSearch "select:mcp__remote-devices__device_bash"; `D:\Claude\...` is `$HOME/mnt/Claude/...`; calls are 120 s, batch commands).

## Report (to the parent, under 20 lines)
Files written; per episode: pages covered, number of replacements by kind, number flagged; the check results; anything you could not do.
