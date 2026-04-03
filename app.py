import re, requests, time, os
from collections import defaultdict
from flask import Flask, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

FARMACI = [
    {"id":"1","nome":"Dailyvit B12 flaconcini",     "qty":4,"url":"https://www.trovaprezzi.it/prezzo_integratori-coadiuvanti_984984308.aspx"},
    {"id":"2","nome":"Collirio Plus 10ml",           "qty":5,"url":"https://www.trovaprezzi.it/prezzo_prodotti-salute_984158865.aspx"},
    {"id":"3","nome":"Alfa Collirio Idratante 10ml", "qty":5,"url":"https://www.trovaprezzi.it/prezzo_prodotti-salute_987055872.aspx"},
    {"id":"4","nome":"Norsan 120 Arktis",            "qty":5,"url":"https://www.trovaprezzi.it/prezzo_integratori-coadiuvanti_981499054.aspx"},
    {"id":"5","nome":"Dailyvit Senior",              "qty":5,"url":"https://www.trovaprezzi.it/prezzo_integratori-coadiuvanti_930629934.aspx"},
    {"id":"6","nome":"Essaven Gel 80g",              "qty":1,"url":"https://www.trovaprezzi.it/prezzo_farmaci-da-banco_036193023.aspx"},
    {"id":"7","nome":"Aximagnesio 20 bustine",       "qty":2,"url":"https://www.trovaprezzi.it/prezzo_integratori-coadiuvanti_972069633.aspx"},
    {"id":"8","nome":"Fluimucil 600mg bustine",      "qty":1,"url":"https://www.trovaprezzi.it/prezzo_farmaci-da-banco_034936169.aspx"},
    {"id":"9","nome":"Apropos Vita+ Mag+Pot",        "qty":2,"url":"https://www.trovaprezzi.it/prezzo_integratori-coadiuvanti_979043116.aspx"},
]

HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146.0.0.0 Safari/537.36","Accept-Language":"it-IT,it;q=0.9"}
_cache, _cache_time, CACHE_TTL = {}, {}, 600

def float_da_testo(t):
    t = t.replace("Tot.","").replace("+ Sped.","").replace("Sped.","").strip()
    m = re.search(r"(\d+)[.,](\d{2})\s*\u20ac|\u20ac\s*(\d+)[.,](\d{2})", t)
    if not m: return 0.0
    a,b = (m.group(1),m.group(2)) if m.group(1) else (m.group(3),m.group(4))
    return float(f"{a}.{b}")

def scarica_offerte(url):
    offerte = []
    for pu in [url, url+"?page=2"]:
        try:
            r = requests.get(pu, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text,"html.parser")
            items = soup.find_all("li", class_="listing_item")
            if not items: break
            for item in items:
                s=item.find("span",class_="merchant_name")
                p=item.find("div",class_="item_basic_price")
                sh=item.find("div",class_="item_delivery_price")
                b=item.find("a",href=lambda h:h and "/goto" in h)
                if not s or not p: continue
                prezzo=float_da_testo(p.get_text())
                sped=float_da_testo(sh.get_text()) if sh else 0.0
                if prezzo==0: continue
                offerte.append({"shop":s.get_text(strip=True),"prezzo":prezzo,"sped":sped,"totale":round(prezzo+sped,2),"url":("https://www.trovaprezzi.it"+b["href"]) if b else ""})
            time.sleep(1.0)
        except Exception as e: print(f'ERR {pu}: {e}')
    seen,unici=[],[]
    seen_set=set()
    for o in offerte:
        k=o["shop"].lower()
        if k not in seen_set: seen_set.add(k);unici.append(o)
    return sorted(unici,key=lambda x:x["totale"])[:40]

def get_offerte(fid):
    now=time.time()
    if fid not in _cache or (now-_cache_time.get(fid,0))>=CACHE_TTL:
        f=next((x for x in FARMACI if x["id"]==fid),None)
        if not f: return []
        _cache[fid]=scarica_offerte(f["url"]); _cache_time[fid]=now
    return _cache[fid]

HTML = open('index.html', encoding='utf-8').read()

@app.route("/")
def index(): return HTML

@app.route("/api/farmaci")
def api_farmaci(): return jsonify([{"id":x["id"],"nome":x["nome"],"qty":x["qty"]} for x in FARMACI])

@app.route("/api/prezzi/<fid>")
def api_prezzi(fid):
    f=next((x for x in FARMACI if x["id"]==fid),None)
    if not f: return jsonify({"error":"non trovato"}),404
    return jsonify({"farmaco":f["nome"],"qty":f["qty"],"offerte":get_offerte(fid)})

@app.route("/api/confronto")
def api_confronto():
    farmacie=defaultdict(lambda:{"totale":0.0,"trovati":0,"dettaglio":[]})
    for f in FARMACI:
        for o in get_offerte(f["id"]):
            farmacie[o["shop"]]["trovati"]+=1
            farmacie[o["shop"]]["totale"]+=round(o["totale"]*f["qty"],2)
            farmacie[o["shop"]]["dettaglio"].append({"farmaco":f["nome"],"qty":f["qty"],"prezzo":o["prezzo"],"sped":o["sped"],"totale_qty":round(o["totale"]*f["qty"],2)})
    result=sorted([{"shop":k,"trovati":v["trovati"],"totale":round(v["totale"],2),"dettaglio":v["dettaglio"]} for k,v in farmacie.items()],key=lambda x:(-x["trovati"],x["totale"]))
    return jsonify(result)

@app.route("/ping")
def ping(): return jsonify({"status":"ok"})

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)
