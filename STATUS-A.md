# STATUS-A (workstream A) - rewritten 2026-11-11 ~12:45 local
STATE: pilot 1 of 3 model passes done (Fable, 6 pages at 1200 px). Waiting for Jim to switch model.
DONE
- Steps 1-2: tools\a_*.py, image copies (1568/1200/900 px, plain + contrast), glossary (91 entries), manifest, viewer.
- Fable pass: Notebook2\pilot\fable-e1200\ pages 01, 17, 33, 40 (clipping), 55, 75. Each page viewed once.
  Self-marked uncertain words: 1.5% on the five undamaged pages (18 of 1190); 12.4% on p.33, which is torn.
  Stop rule (15% on typical pages) is not triggered. These are the model's own doubts, not measured errors.
- Viewer tested in a headless browser: scan beside text, highlights, edit mode, paging all work.
NOT DONE
- Opus pass and Sonnet 5.5 pass on the same six pages (same 1200 px copies).
- Resolution test (900 px, contrast copies). Survey of page types. Order of 40_, "_ 2z 84", "_ 2z 84a".
- No measured accuracy yet: that needs Jim's proofreading of 3 pages.
NEEDS JIM
1. Switch this chat to Opus and say "go"; after that pass, switch to Sonnet 5.5 and say "go".
2. After the three passes: proofread 3 pages in Notebook2\viewer.html (suggest 01, 55, 75).
3. Before bulk: sign in to Claude Code on loki again so subagents work.
NEXT ACTION
- On "go" under Opus: read the same six staged pages once each -> pilot\opus-e1200\. Same under Sonnet.
- Then a_compare.py across the three sets, resolution test on 2 pages with the cheapest plausible model,
  report differences per page and relative cost, stop for proofreading.
SPEND: ~1 h 10 min total. Tokens (estimate, no meter): ~300k so far, ~50k of it wasted earlier.
  Fable pass itself: about 6 images + 6 transcripts, small next to the conversation's running context.
