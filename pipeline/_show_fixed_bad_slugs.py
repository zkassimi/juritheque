import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# Chercher les dahirs 1-29-30, 1-15-134, 1-21-62 qu'on vient de corriger
numbers = ["1-29-30", "1-15-134", "1-21-62", "25"]
for num in numbers:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "number,title_fr,type,canonical_slug",
                "number": f"eq.{num}", "limit": "1"}, timeout=10)
    data = r.json()
    if data:
        x = data[0]
        print(f"[{x.get('type','?')}] n°{x.get('number')}")
        print(f"  titre : {x.get('title_fr','')}")
        print(f"  slug  : {x.get('canonical_slug','')}")
        print()
    else:
        print(f"n°{num} → non trouvé")
