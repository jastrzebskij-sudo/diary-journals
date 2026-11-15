# Lab log: TTS and talking-head candidates (started 2026-11-14)

Goal (Jim, 2026-11-14): more reliable audio without XTTS artifacts; a more fully animated avatar than mouth-only. Not monetized, so research/non-commercial licenses are acceptable.
Where: Loki (RTX 4080 SUPER 16 GB, 64 GB RAM), D:\Claude\Assets\Diary\lab\ (uv env per model: env-<name>; HF cache in lab\hf; outputs in lab\out\<model>\). Brokkr = 2x GTX 1080 Ti 11 GB (Pascal), no uv; used only where a model fits.
Test set: lab\testset\pl.json (11 sentences: known problem lines "Wieczorem składamy się na trzy litry wina", "Idziemy spać o wpół do dziesiątej", 2 very short names, medium, 2 long ~200+ chars) and en.json (9 sentences, from Ep3/4 EN prep texts). Voice reference: 11 s clips of the current XTTS voice (lab\refs\ref_pl.wav, ref_en.wav) so cloning targets the project voice. Fixed seed 1234.
Scoring: lab\score.py (Whisper medium, same as pipeline): per sentence WER vs expected, inserted words (esp. trailing = XTTS gibberish signature), largest inter-word gap, "clean" = zero errors. Whisper cannot hear clicks/pops, so listening notes below are still the real test.

## Language/license screen (from web research, 2026-11-14; unverified until tested)
| Model | Polish? | License | Fit on Loki 16 GB | Note |
|---|---|---|---|---|
| XTTS-v2 (baseline) | yes | Coqui CPML (non-commercial) | yes | known trailing-gibberish on short sentences |
| Chatterbox Multilingual | yes (model card lists Polish) | MIT | yes | claims fewer hallucinations in V3 |
| Fish Audio S2 Pro | yes (80+ languages claimed) | research, non-commercial | bf16 ~24 GB no; FP8 ~12 GB (Ada ok) | install heavier (SGLang / ComfyUI node / s2.cpp GGUF) |
| Voxtral TTS (Mistral) | NO (en fr de es nl pt it hi ar) | non-commercial weights | ~16 GB | EN-only candidate |
| Qwen3-TTS | NO (zh en ja ko de fr ru pt es it) | Apache 2.0 | 1.7B ~6-8 GB | EN-only candidate |
| IndexTTS-2 | not checked | not checked | not checked | duration control |

## Setup friction log
- Chatterbox: `uv pip install chatterbox-tts` pulled CPU-only torch 2.6 on Windows -> "Torch not compiled with CUDA" -> reinstalled torch/torchaudio 2.6.0+cu124. Then Resemble watermarker (perth) was None until `setuptools<81` was added (pkg_resources). Model download via HF (~GBs) fine. Total ~25 min of fiddling.

## Setup friction log (continued)
- VoxCPM2: smooth (`pip install voxcpm` + CUDA torch reinstall); seed kwarg unsupported.
- MOSS-TTS: needs Python 3.12 (uv's managed 3.12 install had a broken minor-version link; `uv venv --python 3.12` still produced a working venv), torch 2.9.1+cu128, transformers 5.0.0 (not pulled by `pip install -e`), `--index-strategy unsafe-best-match`, and `torchaudio.load` needs torchcodec (worked around by patching it with soundfile in my script). Loads remote code from HF (trust_remote_code). ~2 h total fiddling; most fragile install so far.
- Loki: no ffmpeg originally -> installed Gyan.FFmpeg via winget (Jim OK'd adding tools). torchaudio on Windows has no audio backend -> use soundfile.

## Results (fill as runs complete)
Same 11 PL + 9 EN sentences, seed 1234, Whisper-medium scoring. Note: Whisper writes digits ("7", "100 km") where the text says words, so a few EN "errors" are formatting, not speech faults.
| Model | Lang | clean / n | mean WER | trailing inserts | gaps >1 s | speed (GPU) | Jim listening notes |
|---|---|---|---|---|---|---|---|
| xtts_1take (baseline, project latent, 1 take, brokkr 1080 Ti) | pl | 4/11 | 0.151 | 4 | 1 | ~0.25 s per s of audio | |
| xtts_1take | en | 5/9 | 0.032 | 0 | 0 | ~0.25 s per s of audio | |
| chatterbox multilingual (ref = 11 s XTTS clip, Loki 4080S) | pl | 2/11 | 0.491 | 0 | 0 | ~0.5-1.2 s per s of audio | |
| chatterbox | en | 5/9 | 0.045 | 0 | 0 | same | |
| voxcpm2 (OpenBMB, 2B, Apache-2.0, ref = same 11 s clip, controllable cloning, cfg 2.0, 10 steps, no torch.compile, Loki 4080S) | pl | 4/11 | 0.127 | 0 | 0 | ~1.5 s per s of audio (48 kHz out) | |
| voxcpm2 | en | 5/9 | 0.032 | 0 | 0 | same | |
| moss15 (MOSS-TTS-Local-Transformer-v1.5, 4B Qwen3 backbone, Apache-2.0, ref clip, Loki 4080S bf16/SDPA) | pl | 2/11 | 0.180 | 1 | 0 | ~1.3 s per s of audio (48 kHz out) | |
| moss15 | en | 4/9 | 0.036 | 0 | 0 | same | |
| STRESS 60 PL sentences (spoken-form Ep1 text, seed 1234): xtts_1take | pl | 27/60 | 0.112 | 19 | 1 | | |
| STRESS 60 PL: voxcpm2 | pl | 25/60 | 0.101 | 0 | 0 | | |

Findings so far (2026-11-14 18:00):
- Chatterbox Polish is clearly worse than XTTS on Whisper accuracy: it garbles ł/ą/ę words ("składamy" -> "skoadamy siatem", "wpół do dziesiątej" -> "Pie of Patrzezio"). Not a candidate for PL (unless a Polish language-pack finetune exists; to check). Whisper listened to a reference that is itself XTTS Polish, so reference quality may matter; not yet tested with a different reference.
- Chatterbox English is on par with XTTS by Whisper (errors are digit formatting and the names Sadecki/Dzierzyk/Judy). No trailing inserts in either. Listening comparison needed for naturalness and artifacts.
- XTTS single-take baseline already hits trailing-gibberish on 4 of 11 PL sentences, which confirms the problem the tail trimmer works around.
- Jim 2026-11-14: using different models per language is acceptable.

- VoxCPM2 (18:25): best Polish result so far. All its PL "errors" are formatting/normalization ("31 grudnia", "w pół", name Pisulewski heard as "Tastan") with ZERO inserted words and zero trailing gibberish; XTTS single take inserted junk words on 4 of 11 sentences ("pancicimy", "Bunto", ...). English on par with XTTS. Apache-2.0 (commercial OK too), 2B, ~8 GB VRAM, 48 kHz. Setup: `pip install voxcpm` + same CUDA-torch reinstall; `seed=` kwarg is not accepted by generate (seed via torch.manual_seed); first call 40 s warmup. Slower than XTTS (about 6x) but a 13-min episode would be ~20 min.
- Scoring caveat: Whisper cannot hear clicks/pops or odd prosody, so this only proves no extra WORDS; Jim's listening is the arbiter.
- Candidates added from search: MOSS-TTS (lists Polish, zero-shot cloning), Zonos2 (permissive, languages unchecked), OuteTTS 1.0 and VoxPolska-Auralis (Polish-specific, per Awesome-Polish-TTS list). EN-only extras: Qwen3-TTS, Voxtral TTS, IndexTTS-2 (en/zh only).
- Loki tooling added: ffmpeg (winget Gyan.FFmpeg), at Jim's OK.

## Talking-head candidates
Source image: pipeline/face/bust_WA0003.jpg (approved 512 bust crop). Audio: 11 s PL/EN clips (lab\refs). Outputs in lab\out... lab\video\.
| Model | License | Setup effort | Speed (4080S, shared GPU) | Output | Notes |
|---|---|---|---|---|---|
| Ditto (antgroup/ditto-talkinghead, PyTorch backend, v0.4 hubert) | Apache-2.0 | Moderate: uv py3.10 + torch 2.6 cu124 + deps (einops, librosa, onnxruntime-gpu, ...); checkpoints from HF digital-avatar/ditto-talkinghead (ditto_pytorch + ditto_cfg only, no TensorRT); needed a lab-only patch: Cython `core/utils/blend` replaced with numpy alpha-blend (no MSVC on Loki; original saved as __init__.py.orig); ffmpeg must be on PATH for the audio mux | 275 frames (11 s) in ~65 s while sharing GPU | 512x512 25 fps, full frame incl. background (putback) | Keeps Stefan's likeness and photo texture; head tilt/shift, expression, blinks come from the model. Tunables found in code: emo, drive_eye, delta_eye_open_n, smo_k_s, sampling_timesteps, crop_scale. First look: subtle head motion, identity stable. Lip accuracy and "life" need Jim's eyes. |

- STRESS TEST (19:15, 60 Polish sentences, single take each): XTTS inserted extra words in 9/60 sentences (ins>0) and shows trailing junk words on 19/60 by the trailing-insert count (some are number-format differences); VoxCPM2 inserted a word in 1/60, trailing 0. Real VoxCPM2 defects seen: a few unusual names/place names run together or slightly mispronounced (Czortków, Triest), "O świcie" slurred to one word, one stray leading word. "Clean" counts are similar (27 vs 25) only because Whisper writes numbers/abbreviations differently; the artifact metric is the difference. XTTS pipeline currently needs 8 takes + ASR pick + tail trim to hide this; VoxCPM2 may need only 1-3 takes.
- Not yet tested: VoxCPM2 with prompt_text ("ultimate cloning", needs reference transcript), different cfg/steps, torch.compile speedup, longer sentences > 230 chars, retake variance across seeds, Fish S2 (needs ~12 GB FP8 route), Zonos2, OuteTTS.

## 2026-11-14 evening update

Tooling: Visual Studio Build Tools 2022 (C++ workload, MSVC 19.44) installed on Loki; uv 0.13.8 installed on brokkr. Ditto's numpy blend patch is still in place (not yet replaced by the compiled routine).

| Test | Where | Result |
|---|---|---|
| voxcpm2 on brokkr (GTX 1080 Ti 11 GB, Pascal; torch 2.14.1+cu126 works on sm_61, fp32/default dtype) | brokkr GPU0 | PL clean 4/11 meanWER 0.143, tail_ins 0; EN clean 6/9 meanWER 0.030, tail_ins 0; matches Loki scores within noise |
| speed | brokkr vs Loki | brokkr 1.77 s per s of audio (20 items, 202 s for 114 s audio); Loki ~1.5 s per s; so brokkr is a usable TTS lane |
| Ditto + voxcpm2 audio, PL 44.8 s | Loki 4080S | A neutral 94 s (2.1x), B sad 93 s (2.1x), C steps100 126 s (2.8x) |
| Ditto + voxcpm2 audio, EN 56.9 s | Loki 4080S | A 118 s, B 117 s, C 159 s (2.8x) |
| lipanim (current mouth-only) PL 44.8 s | Loki CPU | 66 s for 1120 frames |

Jim (21:28): variant C (sampling_timesteps 100) looks best: no audio artifacts, lip sync with head movement very good.
Long-run test started 21:50: 5.6 min EN narration (ep03 p2-22..25, 54 chunks of <=200 chars, 0.3 s chunk gaps, 0.5 s paragraph gaps), VoxCPM2 on Loki 335 s audio in 480 s incl. load; Ditto C render of it in progress (checks drift, memory, seams).

## 2026-11-14 night: tone consistency and non-speech artifact (ep03 p2-24, VoxCPM2 on Loki)

Problem (Jim, from the 5.6 min long render): vocal tone swings from entry to entry (chipper vs somber, not proportional to text); at 3:35 a non-voice suspense-like tone after a date while the avatar nods silently.
Cause of the artifact: the Mar 11 entry has no text, only a date. The date-only chunk was generated alone and the model kept producing non-speech after the words ended (v0: 3.7 s of audio after the last word; Mar 8 chunk 1.8 s). Fix: fold date-only lines into the next entry; automatic check: flag chunks with >1 s after last whisper word.
Tone test (same seed 1234, ref = same 11 s clip, cfg 2.0, 10 steps):

| Variant | Chunks | f0 sd (Hz) | f0 mean | rate sd (c/s) | tail flags |
|---|---|---|---|---|---|
| v0 original chunks (date lines alone) | 17 | 11.5 | 100.6 | 2.21 | 2 |
| v1 merged date lines | 8 | 12.4 | 96.9 | 1.20 | 0 |
| v2 merged + style "(calm, steady documentary narrator, even pace, understated emotion)" | 8 | 8.8 | 99.3 | 1.09 | 0 |
| v3 merged + ultimate cloning (prompt_text = ref transcript) | 8 | 8.8 | 110.5 | 1.78 | 0 |

Reading: merging removes the artifact; the style instruction gives the lowest pitch and rate variance; ultimate cloning raises mean pitch (~+11 Hz vs v2) and has more rate variation. Whisper heard "Grzesi Skowiak" in v3 (name pronunciation split). Caveats: n=8, median f0 is a crude proxy for tone; Jim's ear decides. Files: lab\tone_out\*.mp3; scripts gen_tone.py / an_tone.py.
Next: per-entry tone tagging mapped to a small style set; generate the whole page with v2 settings and compare with Jim's listening notes.

Correction (Jim, 23:58, by ear): v2 (style instruction) still has audible tonal variance, so the pitch/rate numbers above overstated it; v3 (ultimate cloning: reference clip + its transcript as prompt) is very consistent. Use v3 settings (prompt_wav_path + prompt_text + reference_wav_path, merged date lines) as the English baseline. Metric lesson: pitch sd and rate sd do not capture perceived tone; Jim's ear is the arbiter.
Names: EN pronunciation of Polish surnames sounds like an English reader seeing them written; PL is accurate. "Orange" (French town) is spoken as the colour. Testing three treatments per name (plain / diacritics or "town, France" / phonetic respelling), file set out\names.

Names test result (Jim, 00:07): for Polish surnames sometimes the diacritics form (T1) and sometimes the phonetic respelling (T2) sounds best; for French town names (Orange, Gigondas) T2 respelling is always best. Decision: per-name pronunciation lexicon (name, chosen TTS spelling, context note), built from a review page with both candidates; applies only to TTS input, never to displayed text. Orange needs a context mark (town vs colour).

## 2026-11-15 name review (00:58)
Playback finding: Jim's viewer rejects <audio> elements for data and blob URLs ("Media load rejected by URL safety check", error 4); Web Audio API (decodeAudioData) works. Use Web Audio for all listening pages.
Inventory (names_inventory.json): 388 entries = 258 surnames (incl. spelling variants), 43 given names, 19 Polish towns, 68 foreign places. Found by (a) curated Polish-side scan and (b) scanning the English text for capitalised non-English words (wordfreq), which added ~90 surnames.
Clips: 708 (T1 diacritics + T2 rule-based respelling for Polish-origin names; T2 hand-made respelling for foreign places), v3 voice settings, ~3.6 s per clip. Review pages lab\review\names_review_1..7.html sent; Jim's picks will become the pronunciation lexicon.

## 2026-11-15 overnight results
- EN long v3 (ep03 p2-22..25, date lines merged, ultimate cloning = prompt_wav + prompt_text + reference): 37 chunks, 294.8 s audio generated in 446 s on Loki (1.5x); tail check: 0 flags (all chunks <0.4 s after last word); f0 sd 10.6 Hz, rate sd 3.0 c/s (rate sd inflated by short chunks). Ditto setting C render: 818 s for 295 s audio (2.8x). Files: video\ditto_ep03_long_en_v3_C.mp4, tone_out\ep03_long_en_v3.mp3.
- Whisper heard names mangled even in v3: "Waltzack and Miller" (Walczak, Miler), "Gigand as" (Gigondas/Gigadas), "Stacey Seal" (Ste Cecile), "Grzesi Skowiak", "Kruczynski" ok. Confirms the need for the pronunciation lexicon.
- PL tone test on brokkr (both GPUs in parallel, 13 chunks, 1,456 chars, same March entries; ref_pl transcript from Whisper is imperfect: "31 grudnia ... O!"): plain 199 s, ultimate 216 s (Pascal, one GPU each). Files: tone_out\tone_pl_plain.mp3, tone_pl_ultimate.mp3. Awaiting Jim's ear.
- Pipeline fix notes: merge date-only lines into next entry; tail check per chunk; ultimate cloning = baseline candidate for EN pending PL verdict.
