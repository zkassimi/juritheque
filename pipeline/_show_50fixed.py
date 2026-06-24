import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Prefer": "count=exact"}

r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "number,title_fr,type,canonical_slug",
            "canonical_slug": "not.like.texte-juridique-%",
            "canonical_slug": "not.like.texte-reglementaire-%",
            "order": "updated_at.desc",
            "limit": "50"}, timeout=15)
rows = r.json()
print(f"50 derniers textes enrichis (titre + slug) :\n")
print(f"{'N°':<15} {'Type':<12} {'Titre (80 car)':<80} {'Slug'}")
print("-"*170)
for x in rows:
    num   = (x.get('number') or '')[:14]
    typ   = (x.get('type') or '')[:11]
    titre = (x.get('title_fr') or '')[:79]
    slug  = (x.get('canonical_slug') or '')
    print(f"{num:<15} {typ:<12} {titre:<80} {slug}")
