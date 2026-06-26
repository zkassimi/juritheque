"""Aperçu des corrections avant/après sans rien modifier."""
import os, re, unicodedata, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True)
load_dotenv()
URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

def slugify(t):
    n = unicodedata.normalize("NFD", (t or "").lower())
    n = "".join(c for c in n if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", n).strip("-")

def clean_number(n):
    """Supprime le préfixe nº / n° / N° du champ number."""
    return re.sub(r"^n[°º\s.]+\s*", "", (n or "").strip(), flags=re.IGNORECASE).strip()

def humanize(t):
    """Titre filename → lisible (remplace tirets/underscores par espaces)."""
    t = re.sub(r"[-_]+", " ", t).strip()
    t = re.sub(r"\s+", " ", t)
    return t.capitalize()

print("\n" + "="*70)
print("CAS 1 — 17 numbers avec préfixe 'n°' (double affichage dans le H1)")
print("="*70)
r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,number,type,title_fr,canonical_slug",
            "number": "like.n%", "limit": "17"})
for x in r.json():
    old_num = x["number"]
    new_num = clean_number(old_num)
    old_h1  = f"{x['type']} n° {old_num}"
    new_h1  = f"{x['type']} n° {new_num}"
    print(f"\n  ID {x['id']} — {x['canonical_slug'][:50]}")
    print(f"  number AVANT : {old_num!r}")
    print(f"  number APRÈS : {new_num!r}")
    print(f"  H1 AVANT     : {old_h1}")
    print(f"  H1 APRÈS     : {new_h1}")

print("\n" + "="*70)
print("CAS 2 — 10 exemples de titres style filename (sur 155 total)")
print("="*70)
r2 = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,number,type,title_fr,canonical_slug",
            "title_fr": "like.*-*-*-*-*", "limit": "10",
            "order": "id.asc"})
for x in r2.json():
    old_t = x["title_fr"] or ""
    new_t = humanize(old_t)
    print(f"\n  ID {x['id']} — n° {x['number']} ({x['type']})")
    print(f"  title AVANT : {old_t[:80]!r}")
    print(f"  title APRÈS : {new_t[:80]!r}")

print("\n" + "="*70)
print("CAS 3 — Les 2 records cassés (2001-1 et decret cncp Ar)")
print("="*70)
for id_, fix_title in [(7770, "Loi n° 2001-1 relative aux télécommunications"),
                       (4041, None)]:
    r3 = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "id,number,type,title_fr,canonical_slug", "id": f"eq.{id_}"})
    x = r3.json()[0] if r3.json() else {}
    print(f"\n  ID {id_} — {x.get('canonical_slug','')}")
    print(f"  title AVANT : {x.get('title_fr','')!r}")
    if fix_title:
        print(f"  title APRÈS : {fix_title!r}")
    else:
        print(f"  title APRÈS : None (vider → sera ignoré ou corrigé par AI lookup)")
