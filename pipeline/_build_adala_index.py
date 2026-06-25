"""
Construit un index local Adala : {number_normalisé: title_ar}
Sauvegarde dans pipeline/adala_index.json

Usage : python pipeline/_build_adala_index.py
Durée estimée : ~5 minutes (525 pages, délai 0.5s entre pages)
"""
import json, re, requests, time, os, sys

OUTPUT = os.path.join(os.path.dirname(__file__), "adala_index.json")
ADALA_SEARCH = "https://adala.justice.gov.ma/search"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
           "Accept-Language": "ar,fr;q=0.8"}
_NEXT_RE = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL)

def normalize_num(n: str) -> str:
    """2.72.274 / 2-72-274 → 2-72-274 (format canonique tirets)"""
    return re.sub(r'[\.\s]+', '-', (n or "").strip()).strip('-').lower()

def fetch_page(page: int, session: requests.Session) -> list[dict]:
    for attempt in range(3):
        try:
            r = session.get(ADALA_SEARCH, params={"page": str(page)}, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                return []
            m = _NEXT_RE.search(r.text)
            if not m:
                return []
            nd = json.loads(m.group(1))
            return nd["props"]["pageProps"]["searchResult"]["data"]
        except Exception as e:
            if attempt < 2:
                time.sleep(5)
            else:
                print(f"  Page {page} erreur: {e}", flush=True)
                return []
    return []

def main():
    # Charger l'index existant si disponible (reprise)
    index = {}
    if os.path.exists(OUTPUT):
        with open(OUTPUT, encoding="utf-8") as f:
            index = json.load(f)
        print(f"Index existant chargé : {len(index)} entrées. Reprise...", flush=True)

    session = requests.Session()

    # Obtenir le total
    r0 = session.get(ADALA_SEARCH, params={"page": "1"}, headers=HEADERS, timeout=20)
    m0 = _NEXT_RE.search(r0.text)
    if not m0:
        print("Erreur : impossible de lire la page 1 d'Adala", flush=True)
        sys.exit(1)
    sr = json.loads(m0.group(1))["props"]["pageProps"]["searchResult"]
    total = sr["total"]
    page_size = len(sr["data"]) or 15
    total_pages = (total + page_size - 1) // page_size
    print(f"Total textes Adala : {total} | Pages : {total_pages}", flush=True)

    new_count = 0
    for page in range(1, total_pages + 1):
        items = fetch_page(page, session)
        for item in items:
            fm = item.get("fileMeta") or {}
            raw_num = (fm.get("lawNumber") or "").strip()
            title_ar = (item.get("name") or fm.get("object") or "").strip()
            if raw_num and len(title_ar) > 5:
                key = normalize_num(raw_num)
                if key and key not in index:
                    index[key] = title_ar
                    new_count += 1

        if page % 50 == 0 or page == total_pages:
            pct = int(page * 100 / total_pages)
            print(f"[{page}/{total_pages} {pct}%] index={len(index)} (+{new_count} nouveaux)", flush=True)
            # Sauvegarde intermédiaire toutes les 50 pages
            with open(OUTPUT, "w", encoding="utf-8") as f:
                json.dump(index, f, ensure_ascii=False, indent=None)
            new_count = 0

        time.sleep(0.4)  # respecter Adala

    # Sauvegarde finale
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=None)
    print(f"\nIndex Adala sauvegardé : {OUTPUT}", flush=True)
    print(f"Total entrées : {len(index)}", flush=True)

if __name__ == "__main__":
    main()
