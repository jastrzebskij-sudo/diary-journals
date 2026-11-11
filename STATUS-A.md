# STATUS-A (workstream A) - rewritten 2026-11-11 ~12:15 local
STATE: steps 1-2 done (scripts, image copies, glossary seed, empty viewer). Step 3 (pilot) BLOCKED: no working way to look at an image.
DONE
- tools\a_*.py (paths, prep_images, glossary_seed, stamp, manifest, compare, viewer) + a_transcribe_prompt.md v1.
- Assets\Diary\Notebook2\prep: 87 pages at long edge 1568/1200/900 px, plain and contrast, + 8 contact sheets.
- Notebook2\glossary.csv (78 curated entries from notebook 1), glossary_candidates.csv (325, raw).
- Notebook2\manifest.csv (87 rows; type/language/date empty until pages are read).
- Notebook2\viewer.html builds and passes a JS syntax check; not yet opened in a browser.
NOT DONE
- No scan has been read by any model. No transcripts, no accuracy or cost numbers.
- Order of 40_, "_ 2z 84", "_ 2z 84a" is provisional (40a after 40; 84a, 84b after 84), not confirmed from content.
BLOCKERS / NEEDS JIM (either one unblocks the pilot)
1. Claude Code on loki: its login has expired ("OAuth session expired and could not be refreshed", twice).
   Sign in again there. Then subagents on loki read the scans locally, with the model chosen per run.
2. OR approve switching on the device tools in this chat (the switch is labelled "computer use"; I would use
   only its file-staging part to bring the downscaled copies into the session, no screen or app control).
NEXT ACTION (once unblocked)
1. Survey: page types, and where the three extra files belong; log the order in NOTES.md.
2. Pilot: 6 pages (incl. clipping p.40) on the strongest model and on Sonnet 5.5 at 1568 px; 2 pages each at
   1200 and 900 px and with contrast copies. a_stamp, a_compare, a_viewer.
3. Stop; ask Jim to proofread 3 pilot pages in the viewer.
SPEND: ~40 min; roughly 200k tokens (my estimate, no meter), of which ~50k wasted on a tool mistake (see RUNLOG-A).
