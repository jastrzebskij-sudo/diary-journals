"""Blend 2+ voices (built-in names or reference WAVs) into one saved conditioning latent.

  blend.py --voices "Claribel Dervla" "Damien Black" --weights 0.6 0.4 --name calm_mix
  blend.py --voices refs/me.wav "Damien Black" --name mix --sweep
  blend.py --anchor Kumar_Dahl --partners Marcos_Rudaski Ludvig_Milivoj --anchor-pcts 25 50 75 --pure
    (anchor-vs-partner grid, full audition texts, EN+PL; files like Kumar75_Marcos25_en.wav, anchor weight first)
"""
import argparse
import time
from pathlib import Path

import torch

import common
from common import ROOT, OUT_ROOT


def blend(latents, weights):
    w = torch.tensor(weights, dtype=torch.float32)
    w = w / w.sum()
    cond = sum(wi * c for wi, (c, _) in zip(w, latents))
    emb = sum(wi * e for wi, (_, e) in zip(w, latents))
    return cond, emb


def resolve_voice(model, spec):
    """Allow 'Kumar_Dahl' for the built-in 'Kumar Dahl'."""
    spaced = spec.replace("_", " ")
    if spec not in model.speaker_manager.speakers and spaced in model.speaker_manager.speakers:
        return spaced
    return spec


def short(spec):
    return Path(spec).stem.replace("_", " ").split()[0]


def parse_jobs(args):
    """--texts LANG:SUFFIX:PATH[:lines] -> jobs; default is audition_<lang>.txt for each of --langs.
    ':lines' = each line is one paragraph and one chunk (no sentence splitting)."""
    if not args.texts:
        return [{"lang": l, "suffix": l, "path": ROOT / f"texts/audition_{l}.txt", "lines": False} for l in args.langs]
    jobs = []
    for spec in args.texts:
        lang, suffix, path, *flag = spec.split(":")
        jobs.append({"lang": lang, "suffix": suffix, "path": ROOT / path, "lines": flag == ["lines"]})
    return jobs


def anchor_grid(args, model):
    anchor, partners = args.anchor, args.partners
    lat = {v: common.load_voice(model, resolve_voice(model, v)) for v in [anchor, *partners]}
    jobs = parse_jobs(args)
    paras = {j["suffix"]: common.read_paragraphs(j["path"], j["lang"], j["lines"]) for j in jobs}
    out = Path(args.out)
    clips, gen_total, t0 = 0, 0.0, time.perf_counter()

    def render(label, cond, emb, dest):
        nonlocal clips, gen_total
        for j in jobs:
            _, wav, dt = common.synth_paragraphs(model, paras[j["suffix"]], j["lang"], cond, emb, args.gap,
                                                 args.para_gap, split=not j["lines"])
            path = dest / f"{label}_{j['suffix']}.wav"
            common.save_wav(path, wav)
            clips += 1
            gen_total += dt
            print(f"{path}: {len(wav) / common.SAMPLE_RATE:.1f}s audio, gen {dt:.1f}s", flush=True)

    for p in partners:
        for pct in args.anchor_pcts:
            label = f"{short(anchor)}{pct}_{short(p)}{100 - pct}"
            path = ROOT / "latents" / f"{label}.pth"
            if path.exists():
                print(f"reusing {path}")
                cond, emb = common.load_voice(model, str(path))
            else:
                cond, emb = blend([lat[anchor], lat[p]], [pct, 100 - pct])
                path.parent.mkdir(exist_ok=True)
                torch.save({"gpt_cond_latent": cond.cpu(), "speaker_embedding": emb.cpu(),
                            "voices": [anchor, p], "weights": [pct, 100 - pct]}, path)
            render(label, cond, emb, out)
    if args.pure:
        for v in [anchor, *partners]:
            render(resolve_voice(model, v).replace(" ", "_"), *lat[v], out / args.pure_dir)
    print(f"{clips} clips, generation {gen_total:.0f}s, wall {time.perf_counter() - t0:.0f}s")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--voices", nargs="+", help="built-in speaker names or reference WAV paths")
    ap.add_argument("--weights", nargs="+", type=float, help="one per voice (normalised); default equal")
    ap.add_argument("--name", help="output latents/<name>.pth (with --voices)")
    ap.add_argument("--sweep", action="store_true",
                    help="two voices only: render 0/25/50/75/100%% of the 2nd voice in EN and PL to <out>")
    ap.add_argument("--sweep-text", help="text file for the sweep (default: first paragraph of each audition text)")
    ap.add_argument("--out", default=str(OUT_ROOT / "blend"))
    ap.add_argument("--anchor", help="anchor voice for the anchor/partners grid (names may use underscores)")
    ap.add_argument("--partners", nargs="+", help="voices blended against the anchor")
    ap.add_argument("--anchor-pcts", nargs="+", type=int, default=[25, 50, 75], help="anchor weight in %% (default 25 50 75)")
    ap.add_argument("--langs", nargs="+", default=["en", "pl"])
    ap.add_argument("--texts", nargs="+", metavar="LANG:SUFFIX:PATH[:lines]",
                    help="override texts, e.g. en:en:texts/audition_en.txt pl:phon_pl:texts/phonetics_pl.txt:lines")
    ap.add_argument("--pure-dir", default="pure", help="subdir of --out for pure voices ('.' for --out itself)")
    ap.add_argument("--pure", action="store_true", help="also render the unblended voices to <out>/pure/")
    ap.add_argument("--gap", type=float, default=common.SENTENCE_GAP_S, help="seconds of silence between sentences")
    ap.add_argument("--para-gap", type=float, default=common.PARAGRAPH_GAP_S, help="seconds of silence between paragraphs")
    args = ap.parse_args()

    if args.anchor:
        if not args.partners:
            ap.error("--anchor needs --partners")
        if not all(0 < p < 100 for p in args.anchor_pcts):
            ap.error("--anchor-pcts must be between 1 and 99")
        # validate texts (digit guard, sentence length is checked per clip) before loading the model
        for j in parse_jobs(args):
            common.read_paragraphs(j["path"], j["lang"], j["lines"])
        anchor_grid(args, common.load_model())
        return
    if not args.voices or not args.name:
        ap.error("need --voices and --name (or --anchor and --partners)")
    if len(args.voices) < 2:
        ap.error("need at least 2 voices")
    weights = args.weights or [1.0] * len(args.voices)
    if len(weights) != len(args.voices):
        ap.error("--weights must match --voices")
    if args.sweep and len(args.voices) != 2:
        ap.error("--sweep needs exactly 2 voices")

    model = common.load_model()
    latents = [common.load_voice(model, v) for v in args.voices]

    cond, emb = blend(latents, weights)
    path = ROOT / "latents" / f"{args.name}.pth"
    path.parent.mkdir(exist_ok=True)
    torch.save({"gpt_cond_latent": cond.cpu(), "speaker_embedding": emb.cpu(),
                "voices": args.voices, "weights": weights}, path)
    print(f"saved {path}")

    if args.sweep:
        for lang in ("en", "pl"):
            src = args.sweep_text or ROOT / f"texts/audition_{lang}.txt"
            text = common.read_paragraphs(src, lang)[0]
            for pct in (0, 25, 50, 75, 100):
                c, e = blend(latents, [100 - pct, pct])
                wav, dt = common.synth_long(model, text, lang, c, e)
                out = f"{args.out}/{args.name}_{lang}_{pct:03d}.wav"
                common.save_wav(out, wav)
                print(f"{out}: {len(wav) / common.SAMPLE_RATE:.1f}s audio, gen {dt:.1f}s", flush=True)


if __name__ == "__main__":
    main()
