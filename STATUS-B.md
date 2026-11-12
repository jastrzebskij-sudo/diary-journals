# STATUS-B (workstream B: archival images, clips, audio) - rewritten at every stop
Stopped 2026-11-12 ~18:30 local. Cause: queue-building needs files outside the five I was told to read (see Needs Jim).

## State
- DONE: tools\b_fetch.py + tools\b_fetch.config.json. Offline-tested against a local mock server (429 pause/resume, Retry-After, path-escape refusal, host allowlist, 404, resume skip). Not yet run against Wikimedia.
- NOT DONE: queue CSV (Ep2 pending L7 x2, L9 x3, L10 x1; L4-L6, L8 candidates; Ep1/3/4 gaps) and per-episode landmark lists for Ep1/3/4. Only ep02\landmarks.md exists. Reason: titles are in ep02\manifest.csv / thumbs.csv and the landmark lists come from the storyboards; none of those were in my read list and an attempt to read them was blocked.
- Ep2 (unchanged from 2026-11-11): archival_coverage 3/10; L7 x2, L9 x3, L10 x1 listed but not fetched; no candidates for L4, L5, L6, L8. L3 images look spring, not Jan-Feb (flag).
- Tracker flags untouched. Disagreement to report: archival_images_sourced = TRUE for Ep1, Ep3, Ep4 but archival_coverage = 3/9, 1/2, 1/4 (Ep2 FALSE, consistent with 3/10). Ep1/3/4 coverage is from the 2026-11-11 gap check, not re-reviewed.
- Terms (read from search snippets of the official pages, not the full pages): IWM Non-Commercial Licence = free download of standard-resolution images for non-commercial use, equivalent to CC BY-NC, "All Rights Reserved" items excluded; high-res needs a licence. Family archive fits, but NO IWM downloads until Jim approves. NAC (Narodowe Archiwum Cyfrowe): rights vary by archival fonds (some "free use", some "contact czytelnia@nac.gov.pl before publication"); the per-fonds list is nac.gov.pl NAC_SPIS_ZESPOLOW_2024.pdf. NAC own terms page NOT yet read.

## Run commands (after Jim fills the contact string and I/he build the queue)
- Edit tools\b_fetch.config.json: set "contact".
- Dry run: D:\Claude\Assets\Diary\venv\face\Scripts\python.exe tools\b_fetch.py --queue Archival-Images\fetch-queue.csv --dry-run
- Real run (PowerShell, from D:\Claude\Projects\Diary): D:\Claude\Assets\Diary\venv\face\Scripts\python.exe tools\b_fetch.py --queue Archival-Images\fetch-queue.csv
- Stop cleanly: create STOP.txt in D:\Claude\Projects\Diary (delete it before the next run). Resume is automatic (tools\b_fetch_state.json).
- Task Scheduler: Action = the python.exe above; Arguments = tools\b_fetch.py --queue Archival-Images\fetch-queue.csv; Start in = D:\Claude\Projects\Diary; daily trigger; "Do not start a new instance". It ends at 40 files/day, so a daily trigger finishes the queue over several days.

## Next action
Jim gives contact string + approves reading the files below; then B builds the queue, Jim starts the fetch, a later session reviews results on one contact sheet.

## Blockers
- None on Wikimedia (not touched this session).

## Needs Jim
- Contact string for the User-Agent (email or URL) - not given yet; fetcher refuses to run until set.
- OK to read: Archival-Images\ep02\manifest.csv and thumbs.csv, Archival-Images\manifest.csv, and the Ep1/3/4 storyboards (for landmark lists)?
- NAC: OK to read the NAC terms page in the built-in browser (one page, read-only)?

## Notebook 2 manifest
Not ready (unchanged).
