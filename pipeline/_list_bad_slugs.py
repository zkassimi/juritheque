"""Liste tous les textes dont le slug ne respecte pas la convention {number}-{title} (lowercase kebab)."""
import os, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv("pipeline/.env", override=True)

URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

ALLOWED = set("abcdefghijklmnopqrstuvwxyz0123456789-")

all_rows, offset = [], 0
while True:
    r = requests.get(f"{URL}/rest/v1/laws",
        headers={**H, "Range": f"{offset}-{offset+999}"},
        params={"select": "number,title_fr,canonical_slug,source_name,type,date"},
        timeout=20)
    if r.status_code not in (200, 206): break
    chunk = r.json()
    if not chunk: break
    all_rows.extend(chunk)
    if len(chunk) < 1000: break
    offset += 1000

bad = [x for x in all_rows
       if x.get("canonical_slug") and
       any(c not in ALLOWED for c in x["canonical_slug"])]

print(f"Total textes non conformes : {len(bad)}\n")
print(f"{'N°':<25} {'Slug actuel':<55} {'Source':<12} {'Type':<20} {'Date'}")
print("-" * 140)
for x in sorted(bad, key=lambda r: r.get("canonical_slug", "")):
    num   = (x.get("number") or "—")[:23]
    slug  = (x.get("canonical_slug") or "")[:53]
    src   = (x.get("source_name") or "—")[:10]
    typ   = (x.get("type") or "—")[:18]
    date  = (x.get("date") or "—")[:10]
    print(f"{num:<25} {slug:<55} {src:<12} {typ:<20} {date}")
