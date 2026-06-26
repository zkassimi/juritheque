"""Diagnostique les 3 problèmes visibles sur le site."""
import os, re, requests
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

URL = os.getenv("SUPABASE_URL","").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

print("Chargement...", flush=True)
all_laws, offset = [], 0
while True:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select":"id,number,title_fr,title_ar,canonical_slug,type,pdf_url,source_url",
                "limit":"1000","offset":str(offset)})
    batch = r.json()
    if not batch: break
    all_laws.extend(batch)
    offset += len(batch)
    if len(batch) < 1000: break
print(f"Total: {len(all_laws)}\n")

SEP = "─" * 65

# ── PROBLÈME 1 : titres non conformes ──────────────────────────────
bad_titles = []
for x in all_laws:
    tfr = (x.get("title_fr") or "").strip()
    if not tfr:
        continue
    is_bad = (
        "version.consolide" in tfr.lower()
        or ("_" in tfr and " " not in tfr[:20])  # underscore sans espace
        or re.match(r"^[A-Z][a-z]+ \d{3,4} ", tfr)  # "Decret 1025 ..."
        or "portail adala" in tfr.lower()
        or ("—" in tfr and "adala" in tfr.lower())
        or re.match(r"^\d{4}-\d+-\w", tfr)  # commence par date-slug
        or tfr.lower().startswith("decret_")
        or tfr.lower().startswith("arrete_")
        or tfr.lower().startswith("loi_")
    )
    if is_bad:
        bad_titles.append(x)

print(f"PROBLÈME 1 — Titres non conformes (filename/adala style) : {len(bad_titles)}")
print(SEP)
for x in bad_titles[:15]:
    print(f"  ID={x['id']:5} n={str(x['number'])[:20]:20} | {x['title_fr'][:65]}")

# ── PROBLÈME 2 : slugs adala ou mal formés ──────────────────────────
bad_slugs = []
for x in all_laws:
    slug = (x.get("canonical_slug") or "").strip()
    if not slug:
        continue
    is_bad = (
        re.match(r"^adala-[a-f0-9]{6,}", slug)  # adala-xxxxxxxx
        or "_" in slug  # underscore dans slug
        or "version.consolide" in slug
        or re.match(r"^\d{4}-\d$", slug)  # juste "2016-2"
        or re.match(r"^[a-z]+-\d{4}-\d+$", slug)  # "decret-2016-2" trop court
    )
    if is_bad:
        bad_slugs.append(x)

print(f"\nPROBLÈME 2 — Slugs mal formés (adala-hash/underscore/court) : {len(bad_slugs)}")
print(SEP)
for x in bad_slugs[:15]:
    print(f"  ID={x['id']:5} slug={x['canonical_slug'][:60]}")

# ── PROBLÈME 3 : viewer — source externe (Adala bloque iframe) ──────
adala_source = [x for x in all_laws if
    "adala.justice.gov.ma" in (x.get("source_url") or "")
    or "adala.justice.gov.ma" in (x.get("pdf_url") or "")
]
no_local_pdf = [x for x in all_laws if
    not x.get("pdf_url") or
    (x.get("pdf_url") and "adala.justice.gov.ma" in x["pdf_url"])
]

print(f"\nPROBLÈME 3 — Viewer bloqué")
print(SEP)
print(f"  Sources Adala (iframe bloqué par X-Frame-Options) : {len(adala_source)}")
print(f"  Sans PDF local (Storage Supabase)                 : {len(no_local_pdf)}")

print(f"\n{'═'*65}")
print("RÉSUMÉ")
print(f"{'═'*65}")
print(f"  1. Titres non conformes    : {len(bad_titles):5}")
print(f"  2. Slugs mal formés        : {len(bad_slugs):5}")
print(f"  3. Viewer Adala bloqué     : {len(adala_source):5}")
