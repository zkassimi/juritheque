import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# Chercher les textes récemment corrigés
for num in ["24-96", "1-72-255"]:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select":"number,title_fr,type,canonical_slug","number":f"eq.{num}"}, timeout=10)
    for x in r.json():
        print(f"number : {x.get('number')}")
        print(f"type   : {x.get('type')}")
        print(f"title  : {x.get('title_fr')}")
        print(f"slug   : {x.get('canonical_slug')}")
        print()
