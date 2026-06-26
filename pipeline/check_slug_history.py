import os, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True)
load_dotenv()
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# Count non-empty slug_history
r = requests.get(f"{URL}/rest/v1/laws",
    headers={**H, "Prefer": "count=exact"},
    params={"select": "id", "slug_history": "not.eq.{}", "limit": "1"})
print("Lois avec slug_history non vide:", r.headers.get("content-range","?"))

# Show 3 examples
r2 = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "canonical_slug,number,type,slug_history",
            "slug_history": "not.eq.{}", "limit": "3"})
for law in r2.json():
    print(f"  canonical: {law['canonical_slug']}")
    print(f"  history:   {law['slug_history']}")
    print()

# Test: verify old slug works for lookup
print("--- Test lookup par ancien slug ---")
test_slug = "texte-juridique-2-22-431"
r3 = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "canonical_slug,number,title_fr",
            "slug_history": f'cs.{{"{test_slug}"}}', "limit": "1"})
print(f"Recherche '{test_slug}':", r3.json())
