# STATUS-B (workstream B: archival images, clips, audio) - rewritten at every stop
Stopped 2026-11-11 ~12:50 local. Cause: two-failures rule (Wikimedia downloads), see Blockers.

## State
- Ep2 first: landmark list done (12 landmarks, Archival-Images\ep02\landmarks.md; the storyboard's "none" was wrong).
- Ep2 candidates: 12 external listed in ep02\manifest.csv, only 1 on disk (L3 infantry drill). 4 in-notebook items listed.
- In-notebook (Notebook 1, Eps 1-4): found by contact sheets. Ep1: title page (pos 1), 2 photos (13). Ep2: photos at 15, 16, 18 (nativity-play star carollers), clipping at 33 (camp newsletter, Raczkiewicz visit; sits in May 1940 scan order). Ep3: none seen. Ep4: none besides pos 33. File: Archival-Images\notebook1-glued-items.csv.
- Gap check done from storyboards: Ep1 3 of 9 landmarks covered, Ep3 1 of 2, Ep4 about 1 of 4. Tracker TRUE for 1/3/4 looks overstated; not changed.
- Not started: Ep1/3/4 sourcing, Eps 5, 6, 16, music/audio, Ep2 images for L2, L4-L6, L8.

## Next action (when unblocked)
Ep2 downloads from other hosts (NAC szukajwarchiwach.gov.pl, LoC, NARA, Europeana) or Wikimedia after the throttle clears; contact sheet of Ep2 candidates; then Ep1/3/4 gaps.

## Blockers
- upload.wikimedia.org answers HTTP 429 to loki (3 attempts incl. polite Retry-After retry); commons API also 429 under load. Listed, not worked around. Possibly loki's IP is throttled; may clear on its own.
- Searching free text on Commons is noisy; category listings worked better.

## Needs Jim
- Decide: OK to try other hosts for the same images (NAC original site) for downloads?
- Confirm scan 33 (nativity-play clipping) placement: glued in May 1940 or out of order?
- Tracker flags for Eps 1/3/4: want them reset to FALSE? (I was told to touch only fully covered episodes.)

## Notebook 2 manifest
Notebook2\manifest.csv exists but type/date columns are empty: NOT ready for use.

## Spend (rough)
~150k tokens, ~45 min. Images viewed: 8 contact sheets. Files written: tools\b_*.py (4 scripts), ep02 CSVs, RUNLOG-B, STATUS-B.
