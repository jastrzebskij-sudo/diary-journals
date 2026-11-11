r"""a_stamp.py - record model, settings and date in the per-page JSON files of a transcript folder,
and recount words / uncertain words from the .txt (the reader's own counts are not trusted).
Usage:  python tools/a_stamp.py <folder> --model "claude-..." --images e1568 [--date 2026-11-11]
                                 [--prompt "a_transcribe_prompt.md v1"] [--pages 01 02 ...] [--force]
Without --pages every page in the folder that has no model recorded is stamped; --force restamps.
"""
import argparse, datetime, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from a_paths import count

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--model", required=True); ap.add_argument("--images", required=True)
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--prompt", default="a_transcribe_prompt.md v1")
    ap.add_argument("--pages", nargs="*"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    d = Path(a.folder); n = 0
    for txt in sorted(d.glob("*.txt")):
        pid = txt.stem
        if a.pages and pid not in a.pages:
            continue
        jp = d / f"{pid}.json"
        try:
            meta = json.loads(jp.read_text(encoding="utf-8")) if jp.exists() else {}
        except Exception as e:
            meta = {"notes": f"unreadable json from reader: {e}"}
        w, u = count(txt.read_text(encoding="utf-8"))
        meta.update(page=pid, words=w, uncertain=u)
        if a.force or a.pages or not meta.get("model"):
            meta.update(model=a.model, images=a.images, prompt=a.prompt, transcribed_on=a.date)
            n += 1
        jp.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"stamped={n} folder={d}")

if __name__ == "__main__":
    main()
