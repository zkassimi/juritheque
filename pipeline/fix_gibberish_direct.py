"""
Fix residual bad records directly:
  1. The gibberish "decret cncp Ar" title_gibberish record — clear title_fr
  2. filename-as-title records like "2001-1-01-123-79-99-24-96-fr-loi-telecom (1)"
"""
import os, re, requests, unicodedata
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

SUPABASE_URL  = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY  = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}

def fetch(params: dict) -> list:
    r = requests.get(f"{SUPABASE_URL}/rest/v1/laws", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def patch(law_id: str, payload: dict) -> bool:
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={"id": f"eq.{law_id}"},
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 204):
        return True
    print(f"  PATCH error {r.status_code}: {r.text[:200]}")
    return False

def looks_like_filename(t: str) -> bool:
    t = (t or '').strip()
    if len(t) < 5:
        return False
    # slug-like: no spaces, has dashes+digits pattern
    if ' ' not in t and re.search(r'\d{4}[-_]\d', t):
        return True
    # ends with (1) or (2) etc — probably a duplicate filename
    if re.search(r'\(\d+\)$', t.strip()):
        return True
    return False

def humanize_filename(t: str) -> str:
    t = re.sub(r'\(\d+\)$', '', t).strip()
    t = t.replace('_', ' ').replace('-', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    return t.capitalize()

# ── 1. Fix the gibberish "decret cncp Ar" record ─────────────────────────────
print("=== Fix 1: gibberish title_gibberish record ===")
rows = fetch({
    "select": "id,number,title_fr,type",
    "title_fr": "like.%(2015_7%",
    "limit": "5",
})
if not rows:
    # Try by number
    rows = fetch({"select": "id,number,title_fr,type", "number": "eq.decret cncp Ar", "limit": "5"})
if not rows:
    print("  Record not found by title or number — trying broader search")
    rows = fetch({"select": "id,number,title_fr,type", "title_fr": "like.%(2015%", "limit": "10"})

for row in rows:
    print(f"  Found: id={row['id']} | number={row['number']} | title={row.get('title_fr','')[:60]}")
    # Clear the bad title so it shows as untitled (better than gibberish)
    ok = patch(row['id'], {"title_fr": None, "extraction_status": "pending"})
    if ok:
        print(f"  ✅ Cleared title_fr for {row['id']}")
    else:
        print(f"  ❌ Failed to clear")

# ── 2. Fix filename-as-title records ─────────────────────────────────────────
print("\n=== Fix 2: filename-as-title records ===")

# Fetch records where title looks like a slug/filename
# Strategy: fetch records with no spaces in title_fr that contain dashes and digits
page_size = 500
offset = 0
fixed = 0
skipped = 0

while True:
    rows = fetch({
        "select": "id,number,title_fr,title_ar,content_fr",
        "is_publicly_indexable": "eq.true",
        "limit": str(page_size),
        "offset": str(offset),
        "order": "created_at.asc",
    })
    if not rows:
        break

    for row in rows:
        t = (row.get('title_fr') or '').strip()
        if not looks_like_filename(t):
            continue

        print(f"  Filename-like: [{row['number']}] '{t}'")
        human = humanize_filename(t)
        if human and human != t and len(human) > 5:
            ok = patch(row['id'], {"title_fr": human})
            if ok:
                print(f"    ✅ → '{human}'")
                fixed += 1
            else:
                skipped += 1
        else:
            skipped += 1

    if len(rows) < page_size:
        break
    offset += page_size

print(f"\n=== DONE: {fixed} fixed, {skipped} skipped ===")
