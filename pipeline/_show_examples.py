"""Affiche des exemples concrets avec URLs pour chaque catégorie de problème."""
import os, re, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
H   = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
SITE = "https://juritheque.com/loi"

def has_arabic(t):
    return bool(re.search(r'[؀-ۿ]', t or ""))

all_laws, offset = [], 0
while True:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "id,number,title_fr,title_ar,canonical_slug,type",
                "limit": "1000", "offset": str(offset)})
    batch = r.json()
    if not batch: break
    all_laws.extend(batch)
    offset += len(batch)
    if len(batch) < 1000: break

no_ar, ar_in_fr, fr_in_ar, fr_eq_ar = [], [], [], []

for x in all_laws:
    tfr = (x.get("title_fr") or "").strip()
    tar = (x.get("title_ar") or "").strip()
    slug = x.get("canonical_slug") or ""
    if not slug: continue

    if not tar:
        no_ar.append(x)
    elif not has_arabic(tar):
        ar_in_fr.append(x)

    if tfr and not has_arabic(tfr) and tar and not has_arabic(tar) and tfr.lower() == tar.lower():
        fr_eq_ar.append(x)

    if tfr and has_arabic(tfr) and not tar:
        fr_in_ar.append(x)

SEP = "─" * 70

print(f"\n{'═'*70}")
print("EXEMPLES À VÉRIFIER SUR LE SITE")
print(f"{'═'*70}")

print(f"\n[CAS 1] title_ar EN FRANÇAIS (750 records) — page arabe affiche du français")
print(SEP)
for x in ar_in_fr[:5]:
    slug = x.get("canonical_slug","")
    print(f"  n°={x['number']}")
    print(f"  title_fr : {x.get('title_fr','')[:70]}")
    print(f"  title_ar : {x.get('title_ar','')[:70]}  ← EN FRANÇAIS !")
    print(f"  URL      : {SITE}/{slug}")
    print()

print(f"\n[CAS 2] title_ar ABSENT (353 records) — page arabe sans titre")
print(SEP)
for x in [x for x in no_ar if x.get("canonical_slug")][:5]:
    slug = x.get("canonical_slug","")
    print(f"  n°={x['number']}")
    print(f"  title_fr : {x.get('title_fr','')[:70]}")
    print(f"  title_ar : NULL")
    print(f"  URL      : {SITE}/{slug}")
    print()

print(f"\n[CAS 3] title_fr = title_ar (39 records) — même texte français dans les 2 champs")
print(SEP)
for x in fr_eq_ar[:5]:
    slug = x.get("canonical_slug","")
    print(f"  n°={x['number']}")
    print(f"  title_fr : {x.get('title_fr','')[:70]}")
    print(f"  title_ar : {x.get('title_ar','')[:70]}  ← IDENTIQUE")
    print(f"  URL      : {SITE}/{slug}")
    print()
