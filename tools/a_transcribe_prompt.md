# Transcription instructions (workstream A, notebook 2) - version 1, 2026-11-11

You are transcribing scanned pages of a handwritten Polish war diary (Stefan Pisulewski, notebook 2,
starting 1 Feb 1942, a forced-labour camp for interned Polish soldiers on the Bou Arfa - Colomb-Béchar
railway in the Sahara). Neat blue cursive on grid paper. The output is a first draft for a human proofreader.

## What to produce, per page
Two files in the output folder you are given, named by page id (e.g. 07):
1. `<id>.txt`  - the transcript only, UTF-8, no commentary.
2. `<id>.json` - {"page":"07","type":"handwriting|clipping|photo|mixed|blank|cover",
   "language":"pl|fr|pl+fr|none","dates":["1942-02-01", ...],"words":123,"uncertain":7,
   "margin_notes":"short description or empty","notes":"anything the proofreader should know"}

## Rules for the transcript
- Diplomatic transcription: copy what is written. KEEP the writer's spelling, even when it is non-standard
  (he writes e.g. "bendąc", "zawrucić", "przypendził", "sprzęd", "Marsylji"). Do NOT modernise or correct.
  Keep his punctuation, capitalisation and abbreviations (d-ca, fr., godz., por., kpt.).
- Keep his line breaks: one written line = one line of text. Blank line between entries/paragraphs.
- Entry headers look like "27 I 1942 Wtorek" (day, month in Roman numerals, year, weekday). Copy as written.
- Uncertain word: write your best reading followed immediately by [?]  e.g.  Kenadsa[?]
  Two candidate readings: write  [jedna|jedno?]
  Illegible word: [...]   Illegible stretch of several words: [.....]
  Be honest: mark a word [?] whenever you are guessing from context rather than reading the letters.
  Do not mark words you can read clearly. Names of people and places deserve extra care; mark them [?]
  unless the letters are clear or the name is in the glossary.
- Crossed-out text: <skreślone: tekst>. Text inserted above the line: put it in place, no markup.
- Margin notes or notes written on/around a clipping or photo: start a new line  [margines] text
- Glued-in printed clipping: start with a line  [wycinek]  then transcribe the printed text in ITS language
  (French stays French, with accents), then a line  [/wycinek]. Handwriting on the same page follows the
  normal rules.
- Photo: one line  [zdjęcie: short neutral description in Polish]  plus any caption as written.
- Never invent text to fill a gap. Never translate. Never summarise.

## Counting
"words" = whitespace-separated tokens of transcribed text (not markup lines). "uncertain" = number of
tokens containing [?], [...], or [a|b?].

## Use the glossary
Read Notebook2/glossary.csv first: names and places known from notebook 1, with spelling variants the
writer uses. Prefer a glossary spelling only when the letters on the page agree with it.
