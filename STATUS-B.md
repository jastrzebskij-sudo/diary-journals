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

- Image count 2026-11-12: 27 unique external images on disk (Ep1 4, Ep2 6, Ep3 1, Ep4 1, Ep7 1, Ep8 1, Ep9 1, Ep10 2, Ep11 1, Ep12 2, Ep13 1, Ep14 1, Ep15 1, General 4; Ep5, Ep6, Ep16 none) + 7 glued-in notebook items; fetch not yet run, 18 queued.
- Source map for more images: Archival-Images\sources-directory.md (tiers: free/open, museums needing permission, restricted/commercial).

## Run (from D:\Claude\Projects\Diary)
- PowerShell: D:\Claude\Assets\Diary\venv\face\Scripts\python.exe tools\b_fetch.py --queue Archival-Images\fetch-queue.csv
- Preview: add --dry-run. Stop cleanly: create STOP.txt in the project root (delete before next run). Resume is automatic (tools\b_fetch_state.json); if a lock is stale delete tools\b_fetch.lock.
- Task Scheduler: Action = the python.exe above; Arguments = tools\b_fetch.py --queue Archival-Images\fetch-queue.csv; Start in = D:\Claude\Projects\Diary; daily trigger; "Do not start a new instance".
- Output: images in Archival-Images\epNN\thumbs\; log lines in RUNLOG-B.md; per-file license/credit in Archival-Images\fetch-results.csv.

## Next action
Second-round search using the sources directory; contact museums only on Jim's go. After the run: a later session reviews all new thumbnails on one contact sheet, updates manifests and archival_coverage; then second-round searches for the no-candidate landmarks (try Commons subcategories e.g. "Winter at Mont Ventoux", Polish/French archives).

## Blockers
- Sandbox proxy blocks commons.wikimedia.org (403); searches were run on Jim's machine via PowerShell instead. No Wikimedia 429 this session.

## Needs Jim
- Run the fetch (commands above).
- Pick which restricted/permission sources to approach (IWM, Sikorski Museum, Pilsudski Institute, ECPAD, KARTA).
- Decide whether modern Ventoux photos (L5) and the Bundesarchiv German-propaganda images are acceptable as context imagery.

## Notebook 2 manifest
Not ready (unchanged).

## Credits and use (2026-11-12)
- Project use: personal, educational, non-commercial only. Credit every source; credits go into the videos and descriptions.
- Credits: `Credits.md` (per episode + description block) and `Archival-Images\credits.csv`. 50 images listed, 17 still marked *verify* until the fetch runs and the Commons API fills artist/licence. Rerun `python tools\b_credits.py` after the fetch.
- Next: IWM feasibility check (robots.txt/terms) before any IWM download; museum outreach needs Jim's explicit go.

## Fetch run 1 (2026-11-12 19:03-19:15)
- 12 of 18 downloaded OK, 6 failed ("unexpected file host"): files wider than 1920 px are served from thumb.wikimedia.org, which was not allowlisted. Fixed (same rate bucket). Failed: NAC 18-264-6 tanks (Ep2 L7), Aulnois choir and 5e génie flag (Ep2 L9), BA-10 Lublin (Ep1 L4), Bundesarchiv Stukas 183-1987-1210-502 (Ep1 L2), Leopold III poster (Ep4 L1).
- Jim: rerun with `--retry-failed` (same command as above plus that flag) to pick up the 6.
- Credits regenerated from API data; `_to_delete\_dbg_hosts.py` is a throwaway debug script (safe to delete).

## IWM (2026-11-12)
- Feasible but manual: collections search is robots-disallowed, item pages are fine. Free low-res images under the Non-Commercial Licence with a mandatory per-item attribution statement. Keep videos non-monetized. Details in sources-directory.md.

## Fetch run 2 (retry, 19:19-19:24)
- All 6 retried files downloaded OK; 18 of 18 queued files are on disk. The "failed_total=6" in the run log was a stale counter (failures were not cleared on success); fixed in b_fetch.py and state cleaned.

## Round 3 (2026-11-12, evening)
- Jim authorized me to run fetches. Fetch run 3: 20 more files OK (38/38 queued on disk, 0 failed). Total external images on disk: ~65 incl. earlier (credits.csv lists 70 rows incl. 4 notebook items).
- New coverage: E1-L3, E1-L5 now have images; E1-L4, E2-L4, E4-L1, E4-L3, E4-L4 extended (E4-L4 context-only). Review in Archival-Images\review-notes.md.
- Still no candidates: E1-L6, E1-L7, E2-L6, E2-L8, E4-L2, Italian air attack (E4-L3).
- IWM leads to confirm by hand (share-and-reuse + attribution): HU 30523, HU 109706, HU 128179, 205039122 (Polish troops marching), Pawlik albums 205313939 (rights not shown), negative album 10 (205409289). Details in B-tasks.md.
- 9 older manifest items still marked *verify* in Credits.md (pre-existing, not from this fetch).
