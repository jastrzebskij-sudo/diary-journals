---
title: Sub-agent prompts
status: convention v1
created: 2026-11-13
tags: [diary, prompts, convention]
---
# Sub-agent prompts (Diary)

Convention (Jim, 2026-11-13). Related: [[Diary/PIPELINE-SPEC]] · [[Hub/diary-tasks]]

- **One prompt = one todo.** Each `<name>.md` here is one item in `Hub\diary-tasks.md` (section "Sub-agent prompts").
- **Sub-tasks** live in `<name>-tasks.md` beside the prompt. The parent session maintains it after checking the outputs; agents never edit it (no write races between parallel runs).
- **Minimal model and minimal context:** run with the cheapest model that can do the job, give it only this prompt file and the files the prompt lists. Nothing else.
- **Every prompt states:** goal, model, inputs (exact paths), outputs (exact paths), allowed writes, forbidden actions, done criteria, report format.
- **Run log:** each run is appended to `<name>-tasks.md` under "Runs" (date, model, what ran, result, tokens if known). Purpose: reconstruction if something breaks, retrospective analysis, and the "making of" episode.
- **Results are drafts.** Jim decides.
- **Launch line:** "Read `D:\Claude\Projects\Diary\prompts\<name>.md` and follow it exactly. Arguments: ..."
