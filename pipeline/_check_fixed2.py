import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

for num in ["adala-d74d3f35", "adala-d07fc359"]:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select":"number,title_fr,type,canonical_slug","number":f"eq.{num}"}, timeout=10)
    for x in r.json():
        print(f"=== {num} ===")
        print(f"  type  : {x.get('type')}")
        print(f"  title : {x.get('title_fr')}")
        print(f"  slug  : {x.get('canonical_slug')}")
        print()
