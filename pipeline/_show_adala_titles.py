"""Montre les titres réels des textes Adala avec mauvais slugs."""
import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)

URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

ALLOWED = set("abcdefghijklmnopqrstuvwxyz0123456789-")

all_rows, offset = [], 0
while True:
    r = requests.get(f"{URL}/rest/v1/laws",
        headers={**H, "Range": f"{offset}-{offset+999}"},
        params={"select":"number,title_fr,title_ar,type,canonical_slug,source_name"}, timeout=20)
    if r.status_code not in (200,206): break
    chunk = r.json()
    if not chunk: break
    all_rows.extend(chunk)
    if len(chunk)<1000: break
    offset+=1000

bad = [x for x in all_rows
       if x.get("canonical_slug") and
       any(c not in ALLOWED for c in x["canonical_slug"])]

print(f"30 premiers textes parmi les 701 — titres actuels en base\n")
print(f"{'TYPE':<20} {'N°':<20} {'SLUG ACTUEL':<40}")
print(f"  title_fr  | title_ar")
print("=" * 100)

for x in bad[:30]:
    print(f"\n{(x.get('type') or '')[:18]:<20} {(x.get('number') or '')[:18]:<20} {(x.get('canonical_slug') or '')[:38]}")
    print(f"  FR: {(x.get('title_fr') or 'VIDE')[:80]}")
    print(f"  AR: {(x.get('title_ar') or 'VIDE')[:80]}")
