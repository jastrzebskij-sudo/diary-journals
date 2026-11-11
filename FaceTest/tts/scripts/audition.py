"""Render the audition texts once per built-in speaker -> /srv/tts-out/audition/<speaker>_{en,pl}.wav + index.csv."""
import argparse
import csv

import common
from common import ROOT, OUT_ROOT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--speakers", nargs="*", help="subset of speakers (default: all)")
    ap.add_argument("--out", default=str(OUT_ROOT / "audition"))
    args = ap.parse_args()

    model = common.load_model()
    speakers = args.speakers or common.builtin_speakers(model)
    texts = {
        "en": common.read_paragraphs(ROOT / "texts/audition_en.txt", "en"),
        "pl": common.read_paragraphs(ROOT / "texts/audition_pl.txt", "pl"),
    }
    rows = []
    for sp in speakers:
        cond, emb = common.load_voice(model, sp)
        for lang, paras in texts.items():
            name = f"{sp.replace(' ', '_')}_{lang}.wav"
            wav, dt = common.synth_long(model, " ".join(paras), lang, cond, emb)
            common.save_wav(f"{args.out}/{name}", wav)
            dur = len(wav) / common.SAMPLE_RATE
            vram = common.vram_mb()
            rows.append([sp, lang, name, f"{dur:.1f}", f"{dt:.1f}", f"{dt / dur:.2f}", f"{vram:.0f}"])
            print(f"{name}: audio {dur:.1f}s, gen {dt:.1f}s (RTF {dt / dur:.2f}), peak VRAM {vram:.0f} MiB", flush=True)
    with open(f"{args.out}/index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["speaker", "lang", "file", "audio_s", "gen_s", "rtf", "peak_vram_mib"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
