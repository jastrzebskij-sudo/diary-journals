# STATUS-A (workstream A) - rewritten 2026-11-11 ~17:55 local
STATE: pilot 3 of 3 model passes written (Fable, Opus, Sonnet 5.5; 6 pages at 1200 px). Waiting for Jim: proofreading and decisions below.
DONE
- Steps 1-2: tools\a_*.py, image copies (1568/1200/900 px, plain + contrast), glossary (91 entries), manifest, viewer.
- Pilot passes in Notebook2\pilot\: fable-e1200\, opus-e1200\, sonnet-e1200\ (pages 01, 17, 33 torn, 40 clipping, 55, 75).
  Each page viewed once per model, transcript written straight after.
- INDEPENDENCE CAVEAT: Opus and Sonnet ran in this same conversation lineage. When Sonnet read the pages, the Opus
  transcripts and the printed Fable-vs-Opus word differences (which show Fable's readings for ~70 words) were already in its
  context. The Opus pass was blind to Fable; the Sonnet pass was NOT blind to either. Treat the Sonnet set as contaminated:
  its agreement with Opus/Fable says little about accuracy.
- Self-marked uncertain words, five undamaged pages: Fable 18/1190 (1.5%), Opus 20/1193 (1.7%), Sonnet 16/1193 (1.3%).
  p.33 (torn): Fable 23/186, Opus 30/188 (16.0%), Sonnet 27/188 (14.4%) - mostly holes. Self-marks, not measured errors.
- a_compare (Fable = reference), raw diff_rate over all six pages: Opus 7.3% (101 of 1376), Sonnet 5.7% (79).
  Opus (reference) vs Sonnet: 2.5% (34 words). Files: Notebook2\pilot\compare_fable_vs_opus_e1200.csv,
  compare_fable_ref_e1200.csv, compare_opus_ref_sonnet_e1200.csv.
- Readings only (punctuation, line-break hyphens, margin-note position removed), word differences:
  page   F-O  F-S  O-S      all: F-O 5.5%, F-S 3.8%, O-S 2.1% of 1328 words
  01     16    9    8
  17     14    5    9
  33     14   13    4
  40     17   17    0   (almost all layout/markup convention, ~2 real word differences)
  55      7    4    4
  75      5    2    3
  Pages that differ most between models: 17 and 01 (undamaged), then 33 (torn). 55 and 75 are steadiest.
- Open readings for the proofreader: p.55 tunnels before Fez "7"(F) / "4"(O) / "[4|7?]"(S) - changes a fact;
  p.01 "sierż." / "siła" / "sierż.[?]"; p.17 "wyspali"(F,S[?]) vs "wypości"(O); p.75 "szkociąt"(F,S[?]) / "szkocistów"(O),
  "czerstwe" (F,S[?]) / "chrześcijańskie"(O); p.40 margin "dezbarkowaniu"(F) / "desantowaniu"(O) / "debarkowaniu"(S).
- Convention gaps seen between passes (fix in prompt v2 before bulk): where margin notes go relative to a clipping;
  whether a map gets a [zdjęcie: ...] line (F yes, O no, S no); crossed-out words (O and S mark, F skips); numbers
  with suffixes ("12tu" / "12 tu"); hyphenation at line end kept or not.
NOT DONE
- Resolution test (900 px, contrast copies). Survey of page types. Order of 40_, "_ 2z 84", "_ 2z 84a".
- Viewer not rebuilt with the Opus and Sonnet sets.
- No measured accuracy yet: that needs Jim's proofreading of 3 pages.
- A clean Sonnet run, if wanted: needs a fresh conversation (or a subagent) that has not seen the other transcripts.
NEEDS JIM
1. Decide: accept the contaminated Sonnet set as indicative only, or have Sonnet redone blind (fresh chat, same six pages)?
2. Proofread 3 pages in Notebook2\viewer.html (suggest 01, 17, 55: most disagreement among undamaged pages) so
   diff_rate vs your corrections gives a real accuracy figure per model.
3. Say whether to run the resolution test (900 px, contrast) next, and with which model.
4. Before bulk: sign in to Claude Code on loki again so subagents work.
5. snapshot.ps1 hard-codes a "Claude Sonnet 5.5" co-author trailer; commits made under other models carry that
   attribution (e.g. cdf1a9a was made under Opus). Workstream C's script; not changed by A.
NEXT ACTION
- On Jim's go: prompt v2 (conventions above), resolution test on 2 pages, rebuild viewer with all sets, then stop for proofreading.
SPEND: ~1 h 40 min total. Tokens (estimate, no meter): ~430k so far. Sonnet pass: 6 images + 6 transcripts + compare.
