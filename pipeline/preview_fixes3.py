"""
Preview complet des corrections — même règle que fix_imported_titles.py
Utilise make_slug_from_law() de slug_utils.py + get_best_title() de title_lookup.py
"""
import os, re, sys, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))
from slug_utils import make_slug_from_law
from title_lookup import get_best_title

URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

def clean_number(n):
    """Retire le préfixe n° / nº du champ number."""
    return re.sub(r"^n[°º\s.]+\s*", "", (n or "").strip(), flags=re.IGNORECASE).strip()

SEP = "═" * 70

# ══════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("CAS 1 — 5 exemples : number avec préfixe n° (17 au total)")
print(SEP)

r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,number,type,title_fr,canonical_slug,date",
            "number": "like.n%", "limit": "5"})

for i, x in enumerate(r.json(), 1):
    old_num  = x["number"] or ""
    new_num  = clean_number(old_num)
    old_slug = x["canonical_slug"] or ""
    new_slug = make_slug_from_law(
        law_type=x["type"] or "",
        number=new_num,
        title_fr=x["title_fr"] or "",
        date=str(x["date"] or ""),
    )
    print(f"\n  [{i}] ID {x['id']} — type: {x['type']}")
    print(f"       number  AVANT : {old_num!r}")
    print(f"       number  APRÈS : {new_num!r}")
    print(f"       title_fr      : {(x['title_fr'] or '')[:80]}")
    print(f"       slug    AVANT : /{old_slug}")
    print(f"       slug    APRÈS : /{new_slug}")

# ══════════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("CAS 3 — 2 records cassés : lookup AI + make_slug_from_law()")
print(SEP)

bad_records = [
    {"id": 7770, "number": "2001-1",      "type": "Loi",    "date": ""},
    {"id": 4041, "number": "decret cncp Ar", "type": "Décret", "date": ""},
]

for x in bad_records:
    # Fetch current state from DB
    r2 = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "id,number,type,title_fr,canonical_slug,date",
                "id": f"eq.{x['id']}"})
    row = r2.json()[0] if r2.json() else {}
    old_title = row.get("title_fr") or ""
    old_slug  = row.get("canonical_slug") or ""
    num       = row.get("number") or ""
    typ       = row.get("type") or ""
    dt        = str(row.get("date") or "")

    print(f"\n  ID {x['id']} — number={num!r} type={typ!r}")
    print(f"  title AVANT : {old_title!r}")
    print(f"  slug  AVANT : /{old_slug}")

    print(f"  → Appel get_best_title()...")
    new_title = get_best_title(law_type=typ, number=num, date=dt)

    if new_title:
        new_slug = make_slug_from_law(law_type=typ, number=num,
                                       title_fr=new_title, date=dt)
        print(f"  title APRÈS : {new_title!r}")
        print(f"  slug  APRÈS : /{new_slug}")
    else:
        print(f"  title APRÈS : NULL (AI n'a pas trouvé → vider en base)")
        print(f"  slug  APRÈS : inchangé")
