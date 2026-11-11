r"""a_viewer.py - build the static proofreading viewer for notebook 2 (no server, no network).
Usage:  python tools/a_viewer.py [--images e1568]
Writes  Notebook2\viewer.html  (open it in a browser from its place on disk)
Shows the scan beside the transcript; uncertain words ([?], [...], [a|b?]) are highlighted.
Transcript sets found automatically: Notebook2\transcripts (label "draft"), every folder in
Notebook2\pilot\, and Notebook2\proofread (Jim's corrected files, <page>.txt).
Edit mode lets Jim correct the text; "Save corrected" downloads <page>.txt - move it into Notebook2\proofread\.
Edits are also kept in the browser (localStorage) until saved. Images are referenced, not embedded:
..\..\..\Assets\Diary\Notebook2\prep\<images>\<page>.jpg relative to the viewer.
"""
import argparse, html, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from a_paths import OUT, TRANSCRIPTS, PILOT, pages

TEMPLATE = r"""<!doctype html><html lang="pl"><head><meta charset="utf-8">
<title>Zeszyt 2 - proofreading</title>
<style>
:root{--bg:#f6f3ec;--ink:#1d1b16;--line:#cfc8b8;--hl:#ffe08a;--gap:#f7b2a8;--acc:#27507a}
*{box-sizing:border-box}body{margin:0;font:15px/1.5 Georgia,serif;background:var(--bg);color:var(--ink);height:100vh;display:flex;flex-direction:column}
header{display:flex;gap:10px;align-items:center;padding:6px 12px;border-bottom:1px solid var(--line);flex-wrap:wrap;font-family:system-ui,sans-serif;font-size:13px}
header select,header button,header input{font:inherit;padding:3px 8px}
button{cursor:pointer;border:1px solid var(--line);background:#fff;border-radius:4px}
button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
#stat{margin-left:auto;color:#555}
main{flex:1;display:flex;min-height:0}
#imgpane{flex:1 1 55%;overflow:auto;background:#2b2a27;cursor:grab}
#imgpane img{display:block;transform-origin:0 0}
#txtpane{flex:1 1 45%;overflow:auto;padding:14px 18px;border-left:1px solid var(--line);min-width:320px}
#view{white-space:pre-wrap;font-size:17px;line-height:1.75}
#edit{width:100%;height:100%;min-height:70vh;font:16px/1.7 Georgia,serif;padding:8px;border:1px solid var(--line);display:none;background:#fffdf7}
mark.u{background:var(--hl);border-radius:3px;padding:0 2px}
mark.g{background:var(--gap);border-radius:3px;padding:0 2px}
.tag{color:var(--acc);font-family:system-ui,sans-serif;font-size:12px;letter-spacing:.03em}
#meta{font-family:system-ui,sans-serif;font-size:12px;color:#555;margin-bottom:10px;border-bottom:1px dashed var(--line);padding-bottom:6px}
.edited{color:#a33;font-weight:600}
</style></head><body>
<header>
 <button id="prev" title="previous page (Alt+Left)">&#9664;</button>
 <select id="page"></select>
 <button id="next" title="next page (Alt+Right)">&#9654;</button>
 <label>set <select id="set"></select></label>
 <button id="zout">&minus;</button><button id="zfit">fit</button><button id="zin">+</button>
 <button id="mode">Edit</button>
 <button id="save">Save corrected</button>
 <button id="revert">Discard my edits</button>
 <span id="stat"></span>
</header>
<main><div id="imgpane"><img id="img" alt="scan"></div>
<div id="txtpane"><div id="meta"></div><div id="view"></div><textarea id="edit" spellcheck="false"></textarea></div></main>
<script>
const DATA=__DATA__;
const $=id=>document.getElementById(id);
let pi=0,si=0,zoom=1,editing=false;
const key=()=>'z2:'+DATA.pages[pi].id;
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function hl(t){
  return esc(t).split('\n').map(line=>{
    line=line.replace(/^\s*\[(\/?wycinek|margines|zdjęcie:[^\]]*)\]/,m=>'<span class="tag">'+m+'</span>');
    return line.split(/(\s+)/).map(w=>{
      if(/\[\.{3,}\]/.test(w)) return '<mark class="g">'+w+'</mark>';
      if(/\[\?\]|\[[^\]\s|]+\|[^\]]*\?\]/.test(w)) return '<mark class="u">'+w+'</mark>';
      return w}).join('')}).join('\n')}
function cur(){const p=DATA.pages[pi];const s=DATA.sets[si];return (p.text[s]??null)}
function render(){
  const p=DATA.pages[pi],s=DATA.sets[si];
  $('img').src=DATA.imgbase+p.id+'.jpg';
  const saved=localStorage.getItem(key());
  const base=cur();
  const t=saved!==null?saved:(base??'');
  $('view').innerHTML=base===null&&saved===null?'<i>no transcript for this page in set "'+s+'"</i>':hl(t);
  $('edit').value=t;
  const m=(p.meta[s]||{});
  const words=t.split(/\s+/).filter(Boolean),unc=words.filter(w=>/\[\?\]|\[\.{3,}\]|\|[^\]]*\?\]/.test(w)).length;
  $('meta').innerHTML='page <b>'+p.id+'</b> &middot; file '+esc(p.file)+' &middot; '+(m.type||p.type||'')+' '+(m.language||'')+
    (m.dates&&m.dates.length?' &middot; '+m.dates.join(', '):'')+(m.model?' &middot; '+esc(m.model)+' / '+esc(m.images||''):'')+
    (m.margin_notes?'<br>margin: '+esc(m.margin_notes):'')+(m.notes?'<br>note: '+esc(m.notes):'')+
    (saved!==null?'<br><span class="edited">showing your unsaved edits (kept in this browser)</span>':'');
  $('stat').textContent=words.length+' words, '+unc+' marked uncertain ('+(words.length?(100*unc/words.length).toFixed(1):0)+'%)';
  $('page').value=pi;$('set').value=si}
function setMode(e){editing=e;$('edit').style.display=e?'block':'none';$('view').style.display=e?'none':'block';
  $('mode').textContent=e?'Preview':'Edit';$('mode').classList.toggle('on',e);if(!e)render()}
function go(d){pi=Math.max(0,Math.min(DATA.pages.length-1,pi+d));render();$('imgpane').scrollTo(0,0)}
function z(f){zoom=f;const im=$('img');im.style.width=(im.naturalWidth*zoom)+'px'}
function fit(){const im=$('img');if(im.naturalWidth)z(($('imgpane').clientWidth-4)/im.naturalWidth)}
DATA.pages.forEach((p,i)=>$('page').add(new Option(p.id+(p.type&&p.type!=='handwriting'?' ('+p.type+')':''),i)));
DATA.sets.forEach((s,i)=>$('set').add(new Option(s,i)));
$('page').onchange=e=>{pi=+e.target.value;render()};$('set').onchange=e=>{si=+e.target.value;render()};
$('prev').onclick=()=>go(-1);$('next').onclick=()=>go(1);
$('zin').onclick=()=>z(zoom*1.2);$('zout').onclick=()=>z(zoom/1.2);$('zfit').onclick=fit;$('img').onload=fit;
$('mode').onclick=()=>setMode(!editing);
$('edit').oninput=()=>localStorage.setItem(key(),$('edit').value);
$('revert').onclick=()=>{if(confirm('Discard your unsaved edits for page '+DATA.pages[pi].id+'?')){localStorage.removeItem(key());render()}};
$('save').onclick=()=>{const t=$('edit').value;const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([t],{type:'text/plain;charset=utf-8'}));a.download=DATA.pages[pi].id+'.txt';a.click();
  alert('Downloaded '+a.download+'. Move it into Notebook2\\proofread\\ (it is the corrected text of this page).')};
document.onkeydown=e=>{if(e.altKey&&e.key==='ArrowRight')go(1);if(e.altKey&&e.key==='ArrowLeft')go(-1)};
let drag=null;const ip=$('imgpane');
ip.onmousedown=e=>{drag={x:e.clientX,y:e.clientY,l:ip.scrollLeft,t:ip.scrollTop};e.preventDefault()};
window.onmouseup=()=>drag=null;window.onmousemove=e=>{if(drag){ip.scrollLeft=drag.l-(e.clientX-drag.x);ip.scrollTop=drag.t-(e.clientY-drag.y)}};
const h=location.hash.slice(1).split(',');if(h[0]){const i=DATA.pages.findIndex(p=>p.id===h[0]);if(i>=0)pi=i}
if(h[1]){const i=DATA.sets.indexOf(h[1]);if(i>=0)si=i}
render();
</script></body></html>"""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--images", default="e1568"); a = ap.parse_args()
    sets = {}
    if (OUT / "proofread").is_dir() and any((OUT / "proofread").glob("*.txt")):
        sets["proofread"] = OUT / "proofread"
    if any(TRANSCRIPTS.glob("*.txt")):
        sets["draft"] = TRANSCRIPTS
    if PILOT.is_dir():
        for d in sorted(p for p in PILOT.iterdir() if p.is_dir() and any(p.glob("*.txt"))):
            sets[f"pilot/{d.name}"] = d
    survey = {}
    if (OUT / "survey.json").exists():
        survey = json.loads((OUT / "survey.json").read_text(encoding="utf-8"))
    plist = []
    for pid, src in pages():
        text, meta = {}, {}
        for name, d in sets.items():
            t = d / f"{pid}.txt"
            if t.exists():
                text[name] = t.read_text(encoding="utf-8")
                j = d / f"{pid}.json"
                if j.exists():
                    try: meta[name] = json.loads(j.read_text(encoding="utf-8"))
                    except Exception: pass
        plist.append({"id": pid, "file": src.name, "type": survey.get(pid, {}).get("type", ""), "text": text, "meta": meta})
    data = {"imgbase": f"../../../Assets/Diary/Notebook2/prep/{a.images}/", "sets": list(sets) or ["draft"], "pages": plist}
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    (OUT / "viewer.html").write_text(TEMPLATE.replace("__DATA__", blob), encoding="utf-8")
    print(f"sets={list(sets)} pages={len(plist)} -> {OUT / 'viewer.html'}")

if __name__ == "__main__":
    main()
