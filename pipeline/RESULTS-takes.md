---
title: Take-count analysis (Ep1 data, 435 chunks)
created: 2026-11-13
tags: [diary, pipeline, results]
---
# How many takes do we need? (spec 5.2, D8)
Data: Ep1 PL+EN picked.json (218 PL + 217 EN chunks, 8 takes each, Whisper-medium scores). Offline simulation, no GPU. Scores: errors + 2 x extra words + 5 x pace deviation.
- Compute for Ep1 at 8 takes: synth 5060 s + ASR 24186 s = 8.1 h (ASR is 83%).
- 301/435 chunks have an error floor of 0; 95 floor 1; 26 floor 2; 12 floor 3 or more. 134 chunks have no take with zero errors, mostly systematic (digits vs spelled numbers, names), identical across takes, not TTS faults.
- Rule "after k0 takes, stop when m takes sit at the chunk's observed error floor with no extra trailing words, else add takes up to 8":

| m, k0 | mean takes | compute saved | mean score excess vs best-of-8 | chunks >1.0 worse |
|---|---|---|---|---|
| 1, 2 | 2.28 | 72% | 0.32 | 33/435 |
| 2, 3 | 3.66 | 54% | 0.17 | 14/435 |
| 2, 4 | 4.50 | 44% | 0.11 | 8/435 |
| 3, 4 | 4.81 | 40% | 0.10 | 6/435 |
Recommendation (to freeze as acceptance numbers after the sample test): m=2, k0=3, ladder continues to 8 only when no 2 takes agree. Saves about 4.4 of 8.1 h per episode pair. Note: the metric is blind to clicks/noise (the 26 s artifact in p1-10); add a click/noise detector to the score.
Needed build: `--only-chunks`/rounds in the renderer so extra takes are generated only for unsettled chunks.
