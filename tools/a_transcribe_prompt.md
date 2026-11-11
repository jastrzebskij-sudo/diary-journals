# Transcription instructions (workstream A, notebook 2) - version 2, 2026-11-11
Supersedes v1 (kept in git history). Changes in v2: margin notes go after the main text as [margines: ...];
photos and maps always get a description line; crossed-out words are marked, never skipped; numbers and
suffixes are copied as written; line-end hyphens are rejoined. Everything else is as in v1.

You are transcribing scanned pages of a handwritten Polish war diary (Stefan Pisulewski, notebook 2,
starting 1 Feb 1942, a forced-labour camp for interned Polish soldiers on the Bou Arfa - Colomb-Béchar
railway in the Sahara). Neat blue cursive on grid paper. The output is a first draft for a human proofreader.

## What to produce, per page
Two files in the output folder you are given, named by page id (e.g. 07):
1. `<id>.txt`  - the transcript only, UTF-8, no commentary.
2. `<id>.json` - {"page":"07","type":"handwriting|clipping|photo|mixed|blank|cover",
   "language":"pl|fr|pl+fr|none","dates":["1942-02-01", ...],"words":123,"uncertain":7,
   "margin_notes":"short description or empty","notes":"anything the proofreader should know"}
   (a_stamp.py recounts words and uncertain and adds model, image set, prompt version and date.)

## Order of material in the .txt
1. Glued-in clippings, photos and maps first, in the order they appear on the page (top to bottom).
2. Then the handwritten main text, in reading order.
3. Then margin notes, last, one per line, each as  [margines: text]  (see below).
A page with only handwriting has just 2 and 3. A page that is only a clipping has just 1 and 3.

## Rules for the transcript
- Diplomatic transcription: copy what is written. KEEP the writer's spelling, even when it is non-standard
  (he writes e.g. "bendąc", "zawrucić", "przypendził", "sprzęd", "Marsylji", "obejżeć"). Do NOT modernise or correct.
  Keep his punctuation, capitalisation and abbreviations (d-ca, fr., godz., por., kpt.).
- Numbers and suffixes exactly as written: "12tu" if written joined, "12 tu" if written apart; "18tą"; "3½";
  Roman-numeral dates as written ("27 I 1942 Wtorek"). Do not normalise spacing, case or digits.
- Line breaks: one written line = one line of text, with one exception. A word split across two lines with a
  line-end hyphen is REJOINED: write the whole word, without the hyphen, at the end of the line where it
  starts; the next line then begins with the word after it. (Written "przy-" / "jedzie" -> "przyjedzie" ending
  the first line.) A hyphen that is part of the word (Bou-Arfa, d-ca) stays. A standalone dash stays.
  Blank line between entries/paragraphs.
- Entry headers look like "27 I 1942 Wtorek" (day, month in Roman numerals, year, weekday). Copy as written.
- Uncertain word: write your best reading followed immediately by [?]  e.g.  Kenadsa[?]
  Two candidate readings: write  [jedna|jedno?]
  Illegible word: [...]   Illegible stretch of several words: [.....]
  Be honest: mark a word [?] whenever you are guessing from context rather than reading the letters.
  Do not mark words you can read clearly. Names of people and places deserve extra care; mark them [?]
  unless the letters are clear or the name is in the glossary.
- Crossed-out text: ALWAYS mark it, never skip it:  <skreślone: tekst>  ; if it cannot be read:  <skreślone: [...]>
  Same rules for [?] inside. Text inserted above the line or squeezed between lines: put it in place, no markup.
  Words overwritten by the writer himself: write the final reading, and say so in notes.
- Margin notes: anything written in a margin or around a clipping or photo that is NOT part of a line of
  the main text goes at the end of the page, one note per line:  [margines: text of the note]
  Use [?] inside as usual:  [margines: Echo d'Oran[?]]  A word that is written in the margin but belongs
  to a line of the main text (an added word with an insertion mark) goes in its place in the text instead.
  Page numbers or counters in the margin are margin notes.
- Glued-in printed clipping: start with a line  [wycinek]  then transcribe the printed text in ITS language
  (French stays French, with accents), then a line  [/wycinek]. Hyphen rejoining applies to printed text too.
  Handwriting on the same page follows the normal rules and comes after the clipping(s).
- Photo: one line  [zdjęcie: short neutral description in Polish]  plus any caption as written on the next line.
  Map: one line  [mapa: short neutral description in Polish]  (what area it shows); printed place labels on a map
  are not transcribed, but a printed caption or credit line under it is. Every photo and every map on the page
  gets its line, also when it is part of a clipping (then the line is inside [wycinek] ... [/wycinek], at the
  position where the picture appears).
- Never invent text to fill a gap. Never translate. Never summarise.

## Counting
"words" = whitespace-separated tokens of transcribed text, including the words inside [margines: ...] and
inside <skreślone: ...>, but not the lines [wycinek], [/wycinek], [zdjęcie: ...], [mapa: ...] and not the
opening tag "[margines:". "uncertain" = number of tokens containing [?], [...], [.....], or [a|b?].

## Use the glossary
Read Notebook2/glossary.csv first: names and places known from notebook 1, with spelling variants the
writer uses. Prefer a glossary spelling only when the letters on the page agree with it.

## Example of the expected output (made up, to show the markup only)
Source: a clipping whose text breaks "co-" / "lonne suivante." and a handwritten line that breaks "wag-" /
"onach kamień." with one crossed-out word and a page counter in the margin. Expected .txt:

    [wycinek]
    [mapa: mapa północnej Afryki z linią kolejową]
    TITRE EN FRANÇAIS
    Le texte continue ici dans la colonne
    suivante.
    [/wycinek]
    12 X 1942 Poniedziałek
    Dziś <skreślone: poszliśmy> pracowaliśmy 12tu godzin przy wagonach
    kamień.
    [margines: 32=[?]]

The rejoined word ("colonne", "wagonach") ends the line where it starts; the next line carries on with the
word after it.
