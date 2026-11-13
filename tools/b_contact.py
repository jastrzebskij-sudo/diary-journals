import csv,os,sys,glob
from PIL import Image,ImageDraw
P=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=[r for r in csv.DictReader(open(os.path.join(P,'Archival-Images','fetch-results.csv'),encoding='utf-8-sig')) if r['status']=='OK' and r['when']>=(sys.argv[1] if len(sys.argv)>1 else '')]
files=[]
for r in rows:
    f=os.path.join(P,*r['dest'].replace('\\','/').split('Diary/')[-1].split('/')) if 'Diary' in r['dest'] else r['dest']
    f=os.path.join(P,'Archival-Images',r['dest'].replace('\\','/').split('Archival-Images/')[-1])
    if os.path.exists(f) and f not in files: files.append(f)
TAG=sys.argv[2] if len(sys.argv)>2 else 'fetch'
W,H,L=480,340,34
for n in range(0,len(files),6):
    chunk=files[n:n+6]; sheet=Image.new('RGB',(W*3,(H+L)*2),'white'); d=ImageDraw.Draw(sheet)
    for i,f in enumerate(chunk):
        im=Image.open(f).convert('RGB'); im.thumbnail((W-6,H-6)); x,y=(i%3)*W,(i//3)*(H+L)
        sheet.paste(im,(x+3,y+3)); d.text((x+4,y+H),os.path.basename(f)[:62],fill='black'); d.text((x+4,y+H+14),'%s  %dx%d'%(os.path.basename(os.path.dirname(os.path.dirname(f))),*Image.open(f).size),fill='gray')
    out=os.path.join(P,'Archival-Images','contact-%s-%d.jpg'%(TAG,n//6+1)); sheet.save(out,quality=85); print(out,len(chunk))
