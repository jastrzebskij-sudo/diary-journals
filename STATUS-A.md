# STATUS-A (workstream A) - rewritten 2026-11-11 ~17:40 local
STATE: pilot 2 of 3 model passes done (Fable, Opus; 6 pages at 1200 px). Waiting for Jim to switch to Sonnet 5.5.
DONE
- Steps 1-2: tools\a_*.py, image copies (1568/1200/900 px, plain + contrast), glossary (91 entries), manifest, viewer.
- Fable pass: Notebook2\pilot\fable-e1200\ pages 01, 17, 33 (torn), 40 (clipping), 55, 75.
- Opus pass: Notebook2\pilot\opus-e1200\ same pages, same 1200 px copies, each page viewed once,
  transcript written straight after. Fable files were not opened until all six Opus files were written.
  Self-marked uncertain: five undamaged pages 20 of 1193 (1.7%); p.33 30 of 188 (16.0%, torn - holes as [...]).
- a_compare.py Fable (ref) vs Opus: Notebook2\pilot\compare_fable_vs_opus_e1200.csv
  Raw diff_rate: 01 5.8%, 17 7.4%, 33 11.3%, 40 10.5%, 55 6.5%, 75 3.7%; all 7.3% (101 of 1376 words).
  Readings only (punctuation, line-break hyphens, margin-note position removed): 01 5.0%, 17 6.0%,
  33 8.2%, 55 3.3%, 75 2.7%; p.40 ~2 real word differences (rest is layout/markup convention).
  Only 17 of 73 reading differences fall on words either model flagged [?] -> self-marked doubt
  under-reports real uncertainty by roughly 4x. Neither pass is a reference; no accuracy is measured yet.
- Notable disagreements (proofreader to settle): p.55 "7 tuneli" (F) vs "4 tunele" (O); p.01 "sierż." vs
  "siła" before Nowicki; p.17 "wyspali" vs "wypości"; p.75 "szkociąt"/"szkocistów", "czerstwe"/"chrześcijańskie";
  p.40 margin "dezbarkowaniu" vs "desantowaniu"; p.01 case endings "dzisiejszą zbiórkę zwołano" vs
  "dzisiejsza zbiórka zwołana"; p.17 diplomatic spellings "obejżeć"/"złe" (F) vs "obejrzeć"/"źle" (O).
  On first sight several Fable readings look more plausible in context (sierż., wyspali, czerstwe, szkociąt).
- Convention gaps seen between passes: where margin notes go (before/after a clipping); whether a map gets a
  [zdjęcie: ...] line; crossed-out words marked (O) or skipped (F). Fix in prompt v2 before bulk.
NOT DONE
- Sonnet 5.5 pass on the same six pages (same 1200 px copies).
- Resolution test (900 px, contrast copies). Survey of page types. Order of 40_, "_ 2z 84", "_ 2z 84a".
- Viewer not rebuilt with the Opus set.
- No measured accuracy yet: that needs Jim's proofreading of 3 pages.
NEEDS JIM
1. Switch this chat to Sonnet 5.5 and say "go".
2. After the three passes: proofread 3 pages in Notebook2\viewer.html (suggest 01, 17, 55: most disagreement among
   the undamaged pages).
3. Before bulk: sign in to Claude Code on loki again so subagents work.
4. snapshot.ps1 hard-codes a "Claude Sonnet 5.5" co-author trailer; commits made under other models carry the
   wrong attribution (workstream C's script, not changed by A).
NEXT ACTION
- On "go" under Sonnet 5.5: stage the six e1200 pages, read each once -> pilot\sonnet-e1200\ (don't open the
  other sets first). Then a_compare.py with both earlier sets, resolution test on 2 pages with the cheapest
  plausible model, report per page and relative cost, stop for proofreading.
SPEND: ~1 h 25 min total. Tokens (estimate, no meter): ~360k so far. Opus pass: 6 images + 6 transcripts + compare.
