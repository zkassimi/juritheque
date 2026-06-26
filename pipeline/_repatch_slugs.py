"""Repatche les 20 premiers records corrigés avec les slugs propres."""
import os, re, requests, unicodedata, time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
H   = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

# IDs des 20 records patchés au premier run
PATCHED_IDS = [5488,6211,5823,5829,974,5835,5534,5848,5632,5861,
               4215,5877,5881,4219,5888,4220,5897,5667,5910,5209]

STOPWORDS = {
    'le','la','les','du','de','des','au','aux','et','ou','n','sur',
    'relatif','relative','portant','fixant','instituant','modifiant',
    'dahir','decret','loi','arrete','circulaire','texte','par',
    'une','un','est','en','dans','pour','avec','sans',
    'moharrem','safar','rabii','joumada','rajab','chaabane','ramadan',
    'chaoual','kaada','hija','rejeb','chaaban','rebia','moharram',
    'janvier','fevrier','mars','avril','mai','juin','juillet','aout',
    'septembre','octobre','novembre','decembre',
    'promulgation','publication','promulguant','publiant','approbation',
    'portant','pris','faite','fait','signe','entre',
}

def normalize(t):
    norm = unicodedata.normalize("NFD", (t or "").lower())
    norm = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9\s]", " ", norm)

def make_slug(law_type, number, title_fr):
    def slugify(t): return re.sub(r"\s+", "-", normalize(t)).strip("-")
    type_slug   = slugify(law_type or "texte")
    number_slug = slugify(number or "")
    words       = normalize(title_fr or "").split()
    keywords    = [w for w in words if w not in STOPWORDS and len(w) > 2 and not re.match(r'^\d+$', w)][:7]
    kw_slug     = "-".join(keywords)
    parts       = [p for p in [type_slug, number_slug, kw_slug] if p]
    return re.sub(r"-+", "-", "-".join(parts)).strip("-")[:120]

# Fetch les 20 records
ids_filter = ",".join(str(i) for i in PATCHED_IDS)
r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,number,title_fr,type,canonical_slug,slug_history",
            "id": f"in.({ids_filter})"})
laws = r.json()
print(f"Fetched {len(laws)} records")

for law in laws:
    new_slug = make_slug(law.get("type",""), law.get("number",""), law.get("title_fr",""))
    old_slug = law.get("canonical_slug","")
    hist     = list(law.get("slug_history") or [])
    if old_slug and old_slug not in hist:
        hist.append(old_slug)

    patch = {"canonical_slug": new_slug, "slug_history": hist}
    pr = requests.patch(f"{URL}/rest/v1/laws?id=eq.{law['id']}", headers=H, json=patch, timeout=10)
    status = "✓" if pr.status_code in (200,204) else f"✗ {pr.status_code}"
    print(f"  {status} ID {law['id']}  {old_slug[:40]} → {new_slug[:50]}")
    time.sleep(0.2)

print("\nDone.")
