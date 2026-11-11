"""Batch render a text file to numbered WAVs plus a concatenated file in /srv/tts-out/render/<job>/.

  render.py texts/chapter1.txt --lang en --voice latents/calm_mix.pth --job chapter1
  render.py texts/rozdzial.txt --lang pl --voice "Claribel Dervla"
"""
import argparse

import common
from common import OUT_ROOT


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("textfile", help="UTF-8 file; paragraphs are blank-line separated, lines within one are joined")
    ap.add_argument("--lang", required=True, help="XTTS language code, e.g. en, pl")
    ap.add_argument("--voice", required=True, help="saved latent .pth, built-in speaker name, or reference WAV")
    ap.add_argument("--job", help="job name (default: text file stem)")
    ap.add_argument("--out", default=str(OUT_ROOT / "render"))
    ap.add_argument("--gap", type=float, default=common.SENTENCE_GAP_S, help="seconds of silence between sentences")
    ap.add_argument("--para-gap", type=float, default=common.PARAGRAPH_GAP_S, help="seconds of silence between paragraphs")
    ap.add_argument("--line-paragraphs", action="store_true", help="treat every line as its own paragraph")
    ap.add_argument("--whole-lines", action="store_true",
                    help="every line is one paragraph AND one chunk (no sentence splitting); use --para-gap between lines")
    args = ap.parse_args()

    from pathlib import Path

    job = args.job or Path(args.textfile).stem
    outdir = Path(args.out) / job
    paras = common.read_paragraphs(args.textfile, args.lang, args.line_paragraphs or args.whole_lines)
    if not paras:
        raise SystemExit("no text found")

    model = common.load_model()
    cond, emb = common.load_voice(model, args.voice)

    def log(i, n, wav, dt):
        print(f"{i:03d}/{n:03d}: {len(wav) / common.SAMPLE_RATE:.1f}s audio, gen {dt:.1f}s", flush=True)

    wavs, joined, _ = common.synth_paragraphs(model, paras, args.lang, cond, emb, args.gap, args.para_gap, log=log,
                                                 split=not args.whole_lines)
    for i, wav in enumerate(wavs, 1):
        common.save_wav(outdir / f"{i:03d}.wav", wav)
    common.save_wav(outdir / f"{job}_all.wav", joined)
    print(f"wrote {outdir}")


if __name__ == "__main__":
    main()
