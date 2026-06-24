import os, re, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv("pipeline/.env", override=True)

URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

r = requests.get(f"{URL}/rest/v1/laws", headers={**H, "Range": "0-1999"},
    params={"select": "canonical_slug,number,title_fr"}, timeout=30)
rows = r.json()

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")[:100]

BAD_TITLES = {"texte juridique", "loi", "decret", "arrete", "dahir", "circulaire"}

bad = [(x["canonical_slug"], x.get("number", "") or "", x.get("title_fr", "") or "")
       for x in rows
       if x.get("canonical_slug") and
       any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in x["canonical_slug"])]

print(f"{'Avant':<44} {'Apres':<44} {'(title_fr)'}")
print("-" * 120)
for slug, num, title in bad[:20]:
    m = re.search(r"-(\d{4,})$", slug)
    suffix = m.group(1) if m else ""
    if title and title.lower() not in BAD_TITLES:
        base = slugify(title[:70])
    elif num:
        base = slugify("texte-n-" + num)
    else:
        base = slug.lower()
    new_slug = base + ("-" + suffix if suffix else "")
    print(f"{slug:<44} {new_slug:<44} ({title[:30]})")
