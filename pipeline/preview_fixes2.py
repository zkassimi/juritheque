"""Aperçu complet 5 exemples par cas — sans modification."""
import os, re, unicodedata, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()
URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

STOPWORDS = {'le','la','les','du','de','des','au','aux','et','ou','un','une',
             'n','relatif','relative','portant','fixant','instituant','modifiant',
             'dahir','decret','loi','arrete','circulaire','texte','code'}

def slugify(t):
    n = unicodedata.normalize("NFD", (t or "").lower())
    n = "".join(c for c in n if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", n).strip("-")

def make_slug(law_type, number, title_fr):
    type_s = slugify(law_type or "texte")
    num_s  = slugify(number or "")
    words  = re.sub(r"[^a-zA-Z0-9\s]", " ", title_fr or "").lower().split()
    kws    = [w for w in words if w not in STOPWORDS and len(w) > 2][:7]
    kw_s   = "-".join(kws)
    parts  = [p for p in [type_s, num_s, kw_s] if p]
    return re.sub(r"-+", "-", "-".join(parts))[:100].strip("-")

def clean_number(n):
    return re.sub(r"^n[°º\s.]+\s*", "", (n or "").strip(), flags=re.IGNORECASE).strip()

SEP = "─" * 68

# ══════════════════════════════════════════════════════════════════════
print(f"\n{'═'*68}")
print("CAS 1 — 17 numbers avec préfixe 'n°' → double H1")
print(f"{'═'*68}")
r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,number,type,title_fr,canonical_slug",
            "number": "like.n%", "limit": "5"})
for i, x in enumerate(r.json(), 1):
    old_num  = x["number"]
    new_num  = clean_number(old_num)
    old_slug = x["canonical_slug"] or ""
    new_slug = make_slug(x["type"], new_num, x["title_fr"])
    print(f"\n  [{i}] ID {x['id']}")
    print(f"  number  AVANT : {old_num!r:30}  →  APRÈS : {new_num!r}")
    print(f"  H1      AVANT : {x['type']} n° {old_num}")
    print(f"  H1      APRÈS : {x['type']} n° {new_num}")
    print(f"  slug    AVANT : {old_slug[:60]}")
    print(f"  slug    APRÈS : {new_slug[:60]}")

# ══════════════════════════════════════════════════════════════════════
print(f"\n\n{'═'*68}")
print("CAS 2 — Vrais titres filename (sans espace OU < 3 espaces + tirets)")
print(f"{'═'*68}")
# Correct filter: title has fewer than 2 spaces AND contains multiple dashes
r2 = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,number,type,title_fr,canonical_slug",
            "title_fr": "like.*-*-*-*", "limit": "200"})
filename_rows = []
for x in r2.json():
    t = x.get("title_fr") or ""
    space_count = t.count(" ")
    # Real filename: few/no spaces, mostly dashes/underscores
    if space_count <= 1 and len(t) > 8:
        filename_rows.append(x)

print(f"  → {len(filename_rows)} vrais titres-filenames détectés\n")
for i, x in enumerate(filename_rows[:5], 1):
    t = x["title_fr"] or ""
    # Humanize: replace dashes/underscores with spaces, capitalize
    cleaned = re.sub(r"[-_]+", " ", t)
    cleaned = re.sub(r"\s+", " ", cleaned).strip().capitalize()
    # Try to add type+number prefix if not already there
    typ = x.get("type","")
    num = x.get("number","")
    if typ and num and typ.lower() not in cleaned.lower()[:15]:
        fixed = f"{typ} n° {num} — {cleaned[:60]}"
    else:
        fixed = cleaned[:80]
    print(f"  [{i}] ID {x['id']} — type={x['type']} n°={x['number']}")
    print(f"  title AVANT : {t[:75]!r}")
    print(f"  title APRÈS : {fixed!r}")
    print()

# ══════════════════════════════════════════════════════════════════════
print(f"\n{'═'*68}")
print("CAS 3 — 2 records cassés (re-patch direct)")
print(f"{'═'*68}")
fixes = [
    (7770, "Loi n° 2001-1 relative aux télécommunications"),
    (4041, None),
]
for law_id, fix_title in fixes:
    r3 = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "id,number,type,title_fr,canonical_slug", "id": f"eq.{law_id}"})
    x = r3.json()[0] if r3.json() else {}
    print(f"\n  ID {law_id} — {x.get('canonical_slug','')}")
    print(f"  title AVANT : {x.get('title_fr','')!r}")
    if fix_title:
        new_slug = make_slug(x.get("type",""), x.get("number",""), fix_title)
        print(f"  title APRÈS : {fix_title!r}")
        print(f"  slug  APRÈS : {new_slug}")
    else:
        print(f"  title APRÈS : NULL (vider — gibberish irréparable sans PDF)")
        print(f"  slug  APRÈS : inchangé (déjà corrigé)")

print(f"\n{'═'*68}")
print("RÉSUMÉ")
print(f"{'═'*68}")
print(f"  CAS 1 : 17 PATCHs number + régénération slug")
print(f"  CAS 2 : {len(filename_rows)} PATCHs title_fr (humanize)")
print(f"  CAS 3 : 2 PATCHs title_fr directs")
print(f"  TOTAL : {17 + len(filename_rows) + 2} enregistrements à corriger")
