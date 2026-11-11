r"""a_viewer.py - build the static proofreading viewer for notebook 2 (no server, no network).
Usage:  python tools/a_viewer.py [--images e1568]
Writes  Notebook2\viewer.html  (open it in a browser from its place on disk)
Shows the scan beside the transcript; uncertain words ([?], [...], [a|b?]) are highlighted.
Transcript sets found automatically: Notebook2\transcripts (label "draft"), every folder in
Notebook2\pilot\, and Notebook2\proofread (Jim's corrected files, <page>.txt).
Where the transcript sets in Notebook2\pilot\ read a word differently, the word is marked blue (hover shows the other
sets' readings); line-end hyphens are rejoined, crossed-out words and margin notes are left out of that comparison.
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
mark.d{background:#bfdcff;box-shadow:inset 0 -2px 0 var(--acc);border-radius:3px;padding:0 2px;cursor:help}
mark.d.u,mark.d.g{background:linear-gradient(90deg,var(--hl) 50%,#bfdcff 50%)}
#legend{font-family:system-ui,sans-serif;font-size:12px;color:#555}
#legend mark{padding:0 4px}
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
 <button id="dis" class="on" title="mark words the other pilot sets read differently">Disagreements</button>
 <span id="legend"><mark class="u">[?]</mark> <mark class="g">[...]</mark> <mark class="d">differs</mark></span>
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
let pi=0,si=0,zoom=1,editing=false,showD=true;
const key=()=>'z2:'+DATA.pages[pi].id;
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
const SKIPLINE=/^\s*\[(\/?wycinek|zdjęcie:|mapa:)/;
const TAGCHUNK=/^\[margines[\]:]/;
const ATTR=x=>x.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const short=n=>n.split('/').pop().replace(/-e\d+c?$/,'');
function norm(w){const m=w.match(/^\[([^|\]\s]+)\|/);if(m)w=m[1];
  return w.replace(/\[\?\]/g,'').replace(/[\[\]?.,;:„”"'()—|<>…\-]/g,'').toLowerCase()}
/* tokens for comparison: main-text stream T and margin-note stream M. Skips markup lines, crossed-out words and
   gaps; rejoins a word split by a line-end hyphen. Each token keeps the [line,chunk] positions it came from. */
function toks(text){
  const T=[],M=[];let skr=false,pend=null;
  const flush=()=>{if(pend){(pend.m?M:T).push({n:pend.n,raw:pend.raw,pos:pend.pos});pend=null}};
  const lines=text.split('\n');
  lines.forEach((line,li)=>{
    const blank=!line.trim(),skip=SKIPLINE.test(line),isM=/^\s*\[margines[\]:]/.test(line);
    if(pend&&(blank||skip||isM!==pend.m))flush();
    if(skip)return;
    const parts=line.split(/(\s+)/);let last=-1;
    parts.forEach((w,ci)=>{if(ci%2===0&&w&&!TAGCHUNK.test(w))last=ci});
    parts.forEach((w,ci)=>{
      if(ci%2||!w||TAGCHUNK.test(w))return;
      if(w.startsWith('<skreślone:'))skr=true;
      if(skr){if(w.endsWith('>'))skr=false;return}
      let n=norm(w);
      if(pend){const p=pend;pend=null;
        (isM?M:T).push({n:p.n+n,raw:p.raw+w,pos:p.pos.concat([[li,ci]])});return}
      if(!n)return;
      if(ci===last&&/\p{L}-(\[\?\])?$/u.test(w)&&li+1<lines.length&&lines[li+1].trim()&&!SKIPLINE.test(lines[li+1])){
        pend={n:n,raw:w.replace(/-(\[\?\])?$/,''),pos:[[li,ci]],m:isM};return}
      (isM?M:T).push({n:n,raw:w,pos:[[li,ci]]})});
  });
  flush();return {T:T,M:M}}
function lcsPairs(a,b){
  const n=a.length,m=b.length,L=[];
  for(let i=0;i<=n;i++)L.push(new Uint16Array(m+1));
  for(let i=n-1;i>=0;i--)for(let j=m-1;j>=0;j--)
    L[i][j]=a[i].n===b[j].n?L[i+1][j+1]+1:Math.max(L[i+1][j],L[i][j+1]);
  const out=[];let i=0,j=0;
  while(i<n&&j<m){if(a[i].n===b[j].n){out.push([i,j]);i++;j++}else if(L[i+1][j]>=L[i][j+1])i++;else j++}
  return out}
/* words of `text` that another pilot set reads differently: {map:"line:chunk"->[{set,alt}], n:token count, others:[names]} */
function dis(text,curName){
  const p=DATA.pages[pi],others=DATA.sets.filter(s=>s!==curName&&s.indexOf('pilot/')===0&&p.text[s]!=null);
  const map=new Map();let n=0;if(!others.length)return {map:map,n:0,others:others};
  const A=toks(text);
  others.forEach(name=>{
    const B=toks(p.text[name]);
    ['T','M'].forEach(k=>{
      const a=A[k],b=B[k],pr=lcsPairs(a,b);pr.unshift([-1,-1]);pr.push([a.length,b.length]);
      for(let x=0;x+1<pr.length;x++){
        const i0=pr[x][0],j0=pr[x][1],i1=pr[x+1][0],j1=pr[x+1][1];
        if(i1-i0<2)continue;
        const alt=b.slice(j0+1,j1).map(t=>t.raw).join(' ')||'∅';
        for(let i=i0+1;i<i1;i++){
          if(!a[i]._d){a[i]._d=1;n++}
          a[i].pos.forEach(q=>{const key=q[0]+':'+q[1];if(!map.has(key))map.set(key,[]);map.get(key).push({set:short(name),alt:alt})})}}})});
  return {map:map,n:n,others:others}}
function hl(t,dm){
  return t.split('\n').map((line,li)=>{
    if(SKIPLINE.test(line))return '<span class="tag">'+esc(line)+'</span>';
    return line.split(/(\s+)/).map((w,ci)=>{
      if(ci%2||!w)return esc(w);
      const e=esc(w);
      if(TAGCHUNK.test(w))return '<span class="tag">'+e+'</span>';
      const cls=[];
      if(/\[\.{3,}\]/.test(w))cls.push('g');
      else if(/\[\?\]|\[[^\]\s|]+\|[^\]]*\?\]/.test(w))cls.push('u');
      const d=dm&&dm.get(li+':'+ci);
      if(d)cls.push('d');
      if(!cls.length)return e;
      return '<mark class="'+cls.join(' ')+'"'+(d?' title="'+ATTR(d.map(x=>x.set+': '+x.alt).join('  |  '))+'"':'')+'>'+e+'</mark>'
    }).join('')}).join('\n')}
function cur(){const p=DATA.pages[pi];const s=DATA.sets[si];return (p.text[s]??null)}
function render(){
  const p=DATA.pages[pi],s=DATA.sets[si];
  $('img').src=DATA.imgbase+p.id+'.jpg';
  const saved=localStorage.getItem(key());
  const base=cur();
  const t=saved!==null?saved:(base??'');
  const dd=showD&&(base!==null||saved!==null)?dis(t,s):{map:null,n:0,others:[]};
  $('view').innerHTML=base===null&&saved===null?'<i>no transcript for this page in set "'+s+'"</i>':hl(t,dd.map);
  $('edit').value=t;
  const m=(p.meta[s]||{});
  const words=t.split(/\s+/).filter(Boolean),unc=words.filter(w=>/\[\?\]|\[\.{3,}\]|\|[^\]]*\?\]/.test(w)).length;
  $('meta').innerHTML='page <b>'+p.id+'</b> &middot; file '+esc(p.file)+' &middot; '+(m.type||p.type||'')+' '+(m.language||'')+
    (m.dates&&m.dates.length?' &middot; '+m.dates.join(', '):'')+(m.model?' &middot; '+esc(m.model)+' / '+esc(m.images||''):'')+
    (m.margin_notes?'<br>margin: '+esc(m.margin_notes):'')+(m.notes?'<br>note: '+esc(m.notes):'')+
    (saved!==null?'<br><span class="edited">showing your unsaved edits (kept in this browser)</span>':'');
  $('stat').textContent=words.length+' words, '+unc+' marked uncertain ('+(words.length?(100*unc/words.length).toFixed(1):0)+'%)'+
    (dd.others.length?' \u00b7 '+dd.n+' differ from '+dd.others.map(short).join(', '):'');
  $('page').value=pi;$('set').value=si}
function setMode(e){editing=e;$('edit').style.display=e?'block':'none';$('view').style.display=e?'none':'block';
  $('mode').textContent=e?'Preview':'Edit';$('mode').classList.toggle('on',e);if(!e)render()}
function go(d){pi=Math.max(0,Math.min(DATA.pages.length-1,pi+d));render();$('imgpane').scrollTo(0,0)}
function z(f){zoom=f;const im=$('img');im.style.width=(im.naturalWidth*zoom)+'px'}
function fit(){const im=$('img');if(im.naturalWidth)z(($('imgpane').clientWidth-4)/im.naturalWidth)}
function pageDelta(i){const save=pi;pi=i;let best=null;
  const ps=DATA.sets.filter(x=>x.indexOf('pilot/')===0&&DATA.pages[i].text[x]!=null);
  if(ps.length>1)ps.forEach(x=>{const r=dis(DATA.pages[i].text[x],x).n;if(best===null||r>best)best=r});
  pi=save;return best}
DATA.pages.forEach((p,i)=>{const d=pageDelta(i);
  $('page').add(new Option(p.id+(p.type&&p.type!=='handwriting'?' ('+p.type+')':'')+(d!==null?'  \u0394'+d:''),i))});
$('dis').onclick=()=>{showD=!showD;$('dis').classList.toggle('on',showD);render()};
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
