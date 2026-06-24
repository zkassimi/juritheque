"""Affiche des exemples du nouveau format de slug — validation avant application."""
import os, re, unicodedata, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)

URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

STOPWORDS = {
    'le','la','les','du','de','des','au','aux','et','ou','un','une',
    'n','no','par','sur','en','dans','pour','avec','sans',
    'relatif','relative','relatifs','relatives',
    'portant','fixant','instituant','modifiant','abrogeant','approuvant',
    'dahir','decret','loi','arrete','circulaire','texte','ordonnance',
    'code','reglement','avis','bulletin','version','arabe',
}

def _s(t):
    norm = unicodedata.normalize("NFD", (t or "").lower())
    norm = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", norm).strip("-")

def make_slug(law):
    type_slug   = _s(law.get("type") or "texte")
    number_slug = _s(law.get("number") or "")
    title       = (law.get("title_fr") or "").strip()
    num_tokens  = set(number_slug.split("-")) if number_slug else set()
    words = re.sub(r"[^a-zA-Z\xc0-\xff0-9\s]", " ", title).lower().split()
    keywords = []
    for w in words:
        sw = _s(w)
        if sw and w not in STOPWORDS and len(w) > 2 and sw not in num_tokens:
            keywords.append(sw)
        if len(keywords) >= 6:
            break
    kw_slug = "-".join(keywords)
    parts = [p for p in [type_slug, number_slug, kw_slug] if p]
    return re.sub(r"-+", "-", "-".join(parts)).strip("-")[:100]

# Fetch textes variés avec de vrais titres
rows = []
for src in ["ANRT", "sgg", "Adala"]:
    r = requests.get(f"{URL}/rest/v1/laws",
        headers={**H, "Range": "0-9"},
        params={"select":"number,title_fr,type,canonical_slug,source_name",
                "source_name": f"eq.{src}", "title_fr": "not.is.null",
                "order": "created_at.desc"},
        timeout=15)
    if r.status_code in (200,206):
        rows.extend(r.json()[:5])

print(f"{'TYPE':<20} {'N°':<20} {'TITRE (extrait)':<45}")
print(f"{'SLUG ACTUEL':<50} → {'SLUG NOUVEAU'}")
print("=" * 110)

for x in rows:
    new = make_slug(x)
    old = x.get("canonical_slug","")
    typ = (x.get("type") or "")[:18]
    num = (x.get("number") or "")[:18]
    tit = (x.get("title_fr") or "")[:43]
    print(f"\n{typ:<20} {num:<20} {tit:<45}")
    print(f"  AVANT : {old}")
    print(f"  APRÈS : {new}")
