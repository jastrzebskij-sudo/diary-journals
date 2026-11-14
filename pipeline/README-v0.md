---
title: Pipeline v0 (orchestrator + audio) notes
status: built and tested 2026-11-13; not yet the full pipeline
tags: [diary, pipeline]
---
# Pipeline v0
Spec: [[Diary/PIPELINE-SPEC]]. What exists: `orch.py` + `recipes.json` (runs on brokkr from `~/diary-pipeline/`), wrapping a copy of the proven audio path (`ep_audio.sh` = render takes, Whisper pick, deepen) with the pick-crash fix (`c_pick_v2.py`). Originals in `~/c-workstream` are untouched. Outputs and state: `/srv/tts-out/pipe/` (queue.jsonl, ledger.jsonl, jobs/<id>-<key>/, status.json, STATUS-PIPELINE.md, heartbeat, orch.lock, STOP).

## Use
- Queue jobs: `python3 orch.py add jobs.json` (list of {id, kind:audio, lang, text, name, takes, seed, names?, extra?}); start: `setsid nohup python3 orch.py run > ... &`; stop cleanly: `touch /srv/tts-out/pipe/STOP`; status: `python3 orch.py status` or on loki `pipeline\pull_status.ps1`.
- Recipes are frozen in `recipes.json`; the job key hashes text + names + recipe + takes + seed + extra, so editing a text creates a new output dir, unchanged jobs are skipped.

## Tests run (isolated root /srv/tts-out/pipe-test, 2026-11-13)
| Test | Result |
|---|---|
| 2-sentence job end to end | pass, 54 s |
| second orchestrator while one runs | pass: exits rc 4 on the lock |
| kill -9 the orchestrator and its children mid-job, rerun | pass: lock released, job resumed and finished (41 s), no stray processes, 9 takes total |
| STOP file | pass: rc 3, no job started |
| edit text -> new key | pass (revert check invalid: test script truncated its own file) |
Not yet tested: power loss (all killed + reboot), brokkr unreachable (the queue lives on brokkr, so n/a until the loki worker exists), AWAY switch (loki side), long-run heartbeat staleness alarm.

## Bug found in the old pick script
`c_brokkr_episode_pick.py` crashes (IndexError) when a chunk's expected text normalises to nothing; a lone "." paragraph at the top of PL page 2-2 did exactly that, three times, so PL 2-2 never rendered. v2 guards it; the job text drops the lone "." paragraph.
