# STATUS-B (workstream B: archival images, clips, audio) - rewritten at every stop
Stopped 2026-11-12 ~19:10 local. Fetcher and queue are ready; Jim runs the fetch (nothing downloaded yet).

## State
- tools\b_fetch.py + tools\b_fetch.config.json (contact set by Jim). Stdlib only. Offline-tested; dry-run on the real queue OK (18 rows). Not yet run against Wikimedia. Destinations are relative to the project root.
- Queue: Archival-Images\fetch-queue.csv, 18 files (about 15-25 min, one day's cap is 40): Ep2 pending L7 x2, L9 x3, L10 x1 + L5 x2 (modern Ventoux photos, context only); Ep1 E1-L2 x2 (Bundesarchiv Stukas), E1-L4 x2; Ep3 E3-L2 x2; Ep4 E4-L1 x2, E4-L3 x2. Built by tools\b_build_queue.py from hand-picked titles; search results in Archival-Images\queue-search-results.json and queue-cats-results1/2.json (titles only, no image viewed).
- Still NO candidate: Ep2 L4, L6, L8 (Commons text/category search found nothing relevant); Ep1 E1-L3, E1-L5, E1-L6, E1-L7; Ep4 E4-L4 (only Saliers Roma camp, copyrighted). Ep4 E4-L2 is "covered" only by an occupation photo (assumption).
- Landmark lists: Archival-Images\ep01, ep02, ep03, ep04 \landmarks.md (Ep1/3/4 from the storyboards' notable-pages tables). Coverage unchanged: Ep1 3/9, Ep2 3/10, Ep3 1/2, Ep4 1/4 (queue adds candidates for 1+1+1+2 landmarks, none reviewed).
- Tracker flags untouched. DISAGREEMENT: archival_images_sourced = TRUE for Ep1, Ep3, Ep4 vs archival_coverage 3/9, 1/2, 1/4 (Ep2 FALSE, consistent with 3/10).
- Licenses: Bundesarchiv items are CC BY-SA 3.0 de (credit "Bundesarchiv, Bild ..."; share-alike matters if the video is ever monetized); several PD claims are from uploaders only; fetch-results.csv will record API license, artist and credit per file. Avoided Commons copies of IWM "HU" images (no IWM downloads until Jim approves).
- IWM: Non-Commercial Licence (CC BY-NC equivalent), free standard-res; not used. NAC: nac.gov.pl says online copies are free unless noted; reuse terms vary by fonds (list: NAC_SPIS_ZESPOLOW_2024.pdf; contact czytelnia@nac.gov.pl). Read in the built-in browser, one page only, nothing saved.

## Run (from D:\Claude\Projects\Diary)
- PowerShell: D:\Claude\Assets\Diary\venv\face\Scripts\python.exe tools\b_fetch.py --queue Archival-Images\fetch-queue.csv
- Preview: add --dry-run. Stop cleanly: create STOP.txt in the project root (delete before next run). Resume is automatic (tools\b_fetch_state.json); if a lock is stale delete tools\b_fetch.lock.
- Task Scheduler: Action = the python.exe above; Arguments = tools\b_fetch.py --queue Archival-Images\fetch-queue.csv; Start in = D:\Claude\Projects\Diary; daily trigger; "Do not start a new instance".
- Output: images in Archival-Images\epNN\thumbs\; log lines in RUNLOG-B.md; per-file license/credit in Archival-Images\fetch-results.csv.

## Next action
After the run: a later session reviews all new thumbnails on one contact sheet, updates manifests and archival_coverage; then second-round searches for the no-candidate landmarks (try Commons subcategories e.g. "Winter at Mont Ventoux", Polish/French archives).

## Blockers
- Sandbox proxy blocks commons.wikimedia.org (403); searches were run on Jim's machine via PowerShell instead. No Wikimedia 429 this session.

## Needs Jim
- Run the fetch (commands above).
- Decide whether modern Ventoux photos (L5) and the Bundesarchiv German-propaganda images are acceptable as context imagery.

## Notebook 2 manifest
Not ready (unchanged).
