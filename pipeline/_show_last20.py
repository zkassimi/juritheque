import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# Tous types confondus — récemment corrigés (pas de placeholder, pas de titre = numéro)
r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "number,title_fr,type,canonical_slug,date",
            "title_fr": "not.like.Texte N%",
            "canonical_slug": "not.like.texte-juridique-%",
            "canonical_slug": "not.like.texte-%",
            "order": "updated_at.desc",
            "limit": "20"},
    timeout=15)
results = r.json()
print(f"{len(results)} textes récemment mis à jour\n")
for x in results:
    print(f"  [{x.get('type','?')}] {x.get('number','?')}")
    print(f"  titre : {x.get('title_fr','')[:100]}")
    print(f"  slug  : {x.get('canonical_slug','')}")
    print()
