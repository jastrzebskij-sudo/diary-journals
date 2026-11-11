"""c_listening_sheet.py - build a self-contained HTML listening sheet from candidate narration WAVs (workstream C, 2026-11-11).
Usage (Assets venv python; add --external-audio if the viewer will not play inline audio):
  python c_listening_sheet.py --text page1.txt --out sheet.html --title "Episode 1, page 1 (PL)" \
         --voice LABEL=path/to/file.wav [--voice LABEL=...] [--assets D:\\Claude\\Assets\\Diary]
Each WAV is converted to 64 kbit/s mono mp3 with ffmpeg (from <assets>\\bin) and embedded as base64, so the single
HTML file works anywhere. The sheet shows the narrated text, one player per voice (with duration), a rating row and a
'my pick' choice; the pick is kept in the browser (localStorage) and shown as a copy-pasteable line. The choice is Jim's."""
import argparse, base64, html, json, subprocess, tempfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--text", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--title", default="Listening sheet"); ap.add_argument("--voice", action="append", required=True)
ap.add_argument("--external-audio", action="store_true", help="write <out stem>-audio/<label>.mp3 beside the HTML and link them (for viewers that block inline data: audio)")
ap.add_argument("--assets", default=r"D:\Claude\Assets\Diary")
a = ap.parse_args()
ff = str(Path(a.assets) / "bin" / "ffmpeg.exe"); fp = str(Path(a.assets) / "bin" / "ffprobe.exe")
cards = []
with tempfile.TemporaryDirectory() as td:
    for v in a.voice:
        label, path = v.split("=", 1)
        mp3 = Path(td) / (label + ".mp3")
        subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", path, "-ac", "1", "-b:a", "64k", str(mp3)], check=True)
        dur = float(subprocess.check_output([fp, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)]))
        if a.external_audio:
            ext = Path(a.out).with_suffix("").with_name(Path(a.out).stem + "-audio"); ext.mkdir(exist_ok=True)
            (ext / (label + ".mp3")).write_bytes(mp3.read_bytes())
            cards.append((label, dur, None, ext.name + "/" + label + ".mp3"))
        else:
            cards.append((label, dur, base64.b64encode(mp3.read_bytes()).decode(), None))
text = Path(a.text).read_text(encoding="utf-8-sig").strip()
items = "".join(f"""<section class="card"><h2>{html.escape(l)}</h2><audio controls preload="metadata" src="{u if u else "data:audio/mpeg;base64," + b}"></audio>
<div class="row"><span>{d:.0f} s</span><label>Rating <select data-k="{html.escape(l)}"><option value="">-</option>{''.join(f'<option>{i}</option>' for i in range(1,6))}</select></label>
<label><input type="radio" name="pick" value="{html.escape(l)}"> my pick</label></div>
<textarea data-n="{html.escape(l)}" placeholder="notes (pace, warmth, Polish diction, artefacts)"></textarea></section>""" for l, d, b, u in cards)
page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Narrator choice</title><style>
:root{{--bg:#f6f2ea;--fg:#2b2620;--card:#fffdf8;--line:#d9d0bf;--acc:#7a4b22}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1d1a16;--fg:#ece6da;--card:#27231e;--line:#3e372e;--acc:#d6a36a}}}}
body{{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:16px/1.5 Georgia,serif;max-width:860px;margin-inline:auto}}
h1{{font-size:1.4rem}}h2{{font-size:1.05rem;margin:.2rem 0 .5rem;color:var(--acc)}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:12px 0}}
audio{{width:100%}}.row{{display:flex;gap:16px;flex-wrap:wrap;align-items:center;margin:.4rem 0;font:14px system-ui}}
textarea{{width:100%;min-height:48px;box-sizing:border-box;background:transparent;color:inherit;border:1px solid var(--line);border-radius:6px;padding:6px;font:14px system-ui}}
details{{margin:12px 0}}pre{{white-space:pre-wrap;font:15px/1.6 Georgia,serif}}#out{{font:14px ui-monospace,monospace;padding:8px;border:1px dashed var(--line);border-radius:6px}}
</style><h1>{html.escape(a.title)}: choose the narrator</h1>
<p>Same text, same settings, different XTTS-v2 voices. Listen with headphones; the choice is yours.</p>
<details><summary>Text read aloud</summary><pre>{html.escape(text)}</pre></details>{items}
<p id="out">no pick yet</p>
<script>
const S=(k,v)=>{{try{{localStorage.setItem('c-sheet-'+k,v)}}catch(e){{}}}},G=k=>{{try{{return localStorage.getItem('c-sheet-'+k)}}catch(e){{return null}}}};
function show(){{const p=document.querySelector('input[name=pick]:checked');const r={{}};document.querySelectorAll('select[data-k]').forEach(s=>{{if(s.value)r[s.dataset.k]=s.value}});
document.getElementById('out').textContent=(p?'PICK: '+p.value:'no pick yet')+'  ratings: '+JSON.stringify(r)}}
document.querySelectorAll('input,select,textarea').forEach(e=>{{const k=(e.dataset.k||e.dataset.n||e.value||'x')+e.tagName;
 if(e.type==='radio'){{if(G('pick')===e.value)e.checked=true;e.onchange=()=>{{S('pick',e.value);show()}}}}
 else{{const v=G(k);if(v)e.value=v;e.oninput=()=>{{S(k,e.value);show()}}}}}});show();
</script></html>"""
Path(a.out).write_text(page, encoding="utf-8")
print("wrote", a.out, f"{Path(a.out).stat().st_size/1e6:.1f} MB", [(l, round(d)) for l, d, _, _ in cards])
