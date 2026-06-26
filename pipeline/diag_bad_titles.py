import os, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True)
load_dotenv()
URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# 1. Check 2001-1
r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,number,title_fr,canonical_slug", "number": "eq.2001-1"})
print("=== number=2001-1 ===")
for x in r.json():
    print(f"  id={x['id']} slug={x['canonical_slug']}")
    print(f"  title_fr={repr(x['title_fr'])[:100]}")

# 2. Check decret cncp Ar
r2 = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,number,title_fr,canonical_slug", "number": "like.*cncp*"})
print("\n=== number like cncp ===")
for x in r2.json():
    print(f"  id={x['id']} slug={x['canonical_slug']}")
    print(f"  title_fr={repr(x['title_fr'])[:100]}")

# 3. Count numbers with n° prefix
r3 = requests.get(f"{URL}/rest/v1/laws",
    headers={**H, "Prefer": "count=exact"},
    params={"select": "id", "number": "like.n%", "limit": "1"})
print(f"\nNumbers avec préfixe 'n': {r3.headers.get('content-range','?')}")

# 4. Count titles looking like filenames (no spaces, with digits and dashes)
r4 = requests.get(f"{URL}/rest/v1/laws",
    headers={**H, "Prefer": "count=exact"},
    params={"select": "id", "title_fr": "like.*-*-*-*-*", "limit": "1"})
print(f"Titres style filename (A-B-C-D): {r4.headers.get('content-range','?')}")
