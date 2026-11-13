import sys,json,urllib.parse,urllib.request,csv
sys.path.insert(0,'tools')
rows=[r for r in csv.DictReader(open('Archival-Images/fetch-queue.csv',encoding='utf-8-sig')) if any(k in r['url_or_title'] for k in ('Pulk','Chorale','Drapeau','183-1987-1210-502','BA-10','Belgische'))]
titles="|".join(r['url_or_title'] if r['url_or_title'].lower().startswith('file:') else 'File:'+r['url_or_title'] for r in rows)
q=dict(action="query",format="json",formatversion="2",maxlag="5",redirects="1",titles=titles,prop="imageinfo",iiprop="url|size",iiurlwidth="1920")
req=urllib.request.Request("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(q),headers={"User-Agent":"DiaryFamilyArchive/1.0 (private, non-commercial family archive; debug; contact: jastrzebskij@gmail.com)"})
d=json.load(urllib.request.urlopen(req,timeout=60))
for p in d["query"]["pages"]:
    i=(p.get("imageinfo") or [{}])[0]
    print(p["title"][:60],"|",i.get("width"),"|",i.get("url"),"|",i.get("thumburl"))
