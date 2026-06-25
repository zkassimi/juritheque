"""
Liste les textes masques (is_published=false) avec titres encore generiques.
Exporte un CSV pour recherche manuelle (ChatGPT, etc.)
"""
import os, re, csv, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)

URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H   = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

_NUMBER_AS_TITLE = re.compile(
    r'^(?:arrêté|arrete|décret|decret|dahir|loi|circulaire|décision|decision|ordonnance|texte)'
    r'\s*(?:n[°o]?\s*)?[\d][\d\.\-/]*\s*$',
    re.IGNORECASE
)

rows = []
offset = 0
while True:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H, params={
        "select": "id,number,title_fr,type,date,source_name",
        "is_published": "eq.false",
        "limit": "1000",
        "offset": str(offset),
        "order": "date.desc"
    }, timeout=15)
    chunk = r.json()
    if not chunk: break
    rows.extend(chunk)
    if len(chunk) < 1000: break
    offset += 1000

print(f"{len(rows)} textes masques trouves\n")

# Filtrer ceux qui ont encore un titre generique (number_as_title) ou vide
to_review = []
for x in rows:
    t = (x.get("title_fr") or "").strip()
    n = x.get("number") or ""
    if not t or _NUMBER_AS_TITLE.match(t):
        to_review.append(x)

print(f"{len(to_review)} textes avec titre manquant ou generique\n")

# Afficher
print(f"{'Type':<15} {'Numero':<15} {'Date':<12} {'Source':<20} Titre actuel")
print("-" * 90)
for x in to_review[:200]:
    t    = (x.get("type") or "?")[:14]
    n    = (x.get("number") or "?")[:14]
    d    = (x.get("date") or "")[:10]
    src  = (x.get("source_name") or "")[:19]
    titre= (x.get("title_fr") or "(vide)")[:40]
    print(f"{t:<15} {n:<15} {d:<12} {src:<20} {titre}")

if len(to_review) > 200:
    print(f"\n... et {len(to_review)-200} autres")

# Export CSV
csv_path = "pipeline/hidden_for_review.csv"
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["id", "type", "number", "date", "source_name", "title_fr"])
    for x in to_review:
        w.writerow([x.get("id",""), x.get("type",""), x.get("number",""),
                    x.get("date",""), x.get("source_name",""), x.get("title_fr","")])

print(f"\nCSV exporte : {csv_path} ({len(to_review)} lignes)")
print("Ouvre ce fichier Excel/Sheets pour copier les numeros vers ChatGPT.")
