import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Prefer": "count=exact"}

r1 = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id", "is_published": "eq.true", "limit": "0"}, timeout=10)
r2 = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id", "is_published": "eq.false", "limit": "0"}, timeout=10)

total_pub  = r1.headers.get("content-range", "?").split("/")[-1]
total_hide = r2.headers.get("content-range", "?").split("/")[-1]
print(f"✅ Publiés  : {total_pub}")
print(f"🚫 Masqués  : {total_hide}")

# Quelques exemples masqués
r3 = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "number,title_fr,type,canonical_slug",
            "is_published": "eq.false", "limit": "5"}, timeout=10)
print("\nExemples masqués :")
for x in r3.json():
    print(f"  [{x.get('type','?')}] {x.get('title_fr','')[:60]} → {x.get('canonical_slug','')[:50]}")
