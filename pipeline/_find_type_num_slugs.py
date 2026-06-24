import os, re, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

TYPE_SLUGS = ["decret","loi","dahir","arrete","circulaire","texte-reglementaire",
              "code","reglement","convention","protocole","declaration","ordonnance"]
ALLOWED = set("abcdefghijklmnopqrstuvwxyz0123456789-")

all_rows, offset = [], 0
while True:
    r = requests.get(f"{URL}/rest/v1/laws",
        headers={**H, "Range": f"{offset}-{offset+999}"},
        params={"select":"id,number,title_fr,type,canonical_slug,source_name"}, timeout=20)
    if r.status_code not in (200,206): break
    chunk = r.json()
    if not chunk: break
    all_rows.extend(chunk)
    if len(chunk)<1000: break
    offset+=1000

def is_type_number_only(slug):
    for t in TYPE_SLUGS:
        if slug.startswith(t + "-"):
            rest = slug[len(t)+1:]
            if re.match(r"^[0-9][0-9\-]*$", rest):
                return True
    return False

type_num = [x for x in all_rows
    if x.get("canonical_slug") and
    all(c in ALLOWED for c in x["canonical_slug"]) and
    is_type_number_only(x["canonical_slug"])]

print(f"Slugs type-number sans mots-cles : {len(type_num)}")
for x in type_num[:40]:
    slug = x.get("canonical_slug","")
    src  = x.get("source_name","") or ""
    num  = x.get("number","") or ""
    title= (x.get("title_fr","") or "")[:50]
    print(f"  {slug:<40} | {src:<15} | {num:<20} | {title}")
