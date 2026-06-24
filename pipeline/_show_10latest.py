import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

numbers = ["1-16-107","2-60-726","1919","1-00-312","2-22-85","1-18-22","1563-20"]
print(f"Résultats 10 exemples corrigés :\n")
for num in numbers:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "number,title_fr,type,canonical_slug,is_published",
                "number": f"eq.{num}", "limit": "1"}, timeout=8)
    data = r.json()
    if data:
        x = data[0]
        pub = "✅ publié" if x.get("is_published") != False else "🚫 masqué"
        print(f"  [{x.get('type','?')}] n°{x.get('number')} — {pub}")
        print(f"  titre : {x.get('title_fr','')}")
        print(f"  slug  : {x.get('canonical_slug','')}")
        print()
