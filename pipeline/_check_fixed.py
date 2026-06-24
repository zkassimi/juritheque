import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

r1 = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select":"number,title_fr,type,canonical_slug","number":"eq.adala-d07fc359"}, timeout=10)
r2 = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select":"number,title_fr,type,canonical_slug","number":"eq.100-13"}, timeout=10)
r3 = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select":"number,title_fr,type,canonical_slug","number":"eq.100_13"}, timeout=10)

for label, r in [("adala-d07fc359", r1), ("100-13", r2), ("100_13 (avant)", r3)]:
    data = r.json()
    if data:
        x = data[0]
        print(f"=== {label} ===")
        print(f"  type  : {x.get('type')}")
        print(f"  number: {x.get('number')}")
        print(f"  title : {x.get('title_fr')}")
        print(f"  slug  : {x.get('canonical_slug')}")
        print()
