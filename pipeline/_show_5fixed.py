import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "number,title_fr,type,canonical_slug",
            "canonical_slug": "not.like.texte-juridique-%",
            "order": "updated_at.desc",
            "limit": "5"}, timeout=10)
print("5 derniers textes mis à jour :\n")
for x in r.json():
    print(f"  [{x.get('type','?')}] {x.get('number','?')}")
    print(f"  titre : {x.get('title_fr','')}")
    print(f"  slug  : {x.get('canonical_slug','')}")
    print()
