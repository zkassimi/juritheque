"""Fix rapide : 2 titres non conformes + 6 slugs courts."""
import os, re, unicodedata, requests
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

URL = os.getenv("SUPABASE_URL","").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}",
     "Content-Type": "application/json", "Prefer": "return=representation"}

def slugify(t):
    norm = unicodedata.normalize("NFD", (t or "").lower())
    norm = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", norm).strip("-")

def patch(law_id, data):
    r = requests.patch(f"{URL}/rest/v1/laws?id=eq.{law_id}", headers=H, json=data, timeout=15)
    ok = r.status_code in (200, 204)
    print(f"  {'✓' if ok else '✗'} ID={law_id} → {data}")
    return ok

# ── Fetch les 8 records problématiques ───────────────────────────────
ids = [7779, 7780, 7768, 7767, 7766, 7771, 7769, 4905]
ids_str = ",".join(str(i) for i in ids)
r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,number,title_fr,title_ar,type,canonical_slug,slug_history",
            "id": f"in.({ids_str})"})
laws = {x["id"]: x for x in r.json()}
print(f"Fetched {len(laws)} records\n")

# ── FIX 1 : titres filename ───────────────────────────────────────────
print("=== FIX 1 — Titres non conformes ===")
for lid in [7779, 7780]:
    x = laws.get(lid)
    if not x:
        print(f"  ID={lid} non trouvé")
        continue
    # Essayer de construire un titre propre depuis title_ar ou number
    tar = (x.get("title_ar") or "").strip()
    num = (x.get("number") or "").strip()
    typ = (x.get("type") or "Décret").strip()
    tfr = x.get("title_fr","")
    print(f"  ID={lid} | number={num} | title_fr={tfr} | title_ar={tar[:60]}")
    # Ces 2 records semblent être des doublons du décret 2-16-800
    # On peut améliorer le titre en ajoutant "(version consolidée)"
    if "version.consolide" in tfr.lower() or "version.consolide" in (x.get("canonical_slug","")).lower():
        new_tfr = f"{typ} n° {num.replace('_',' ').replace('version.consolide','').strip()} (version consolidée)"
        new_slug = slugify(new_tfr)[:80]
        hist = list(x.get("slug_history") or [])
        old = x.get("canonical_slug","")
        if old and old not in hist:
            hist.append(old)
        patch(lid, {"title_fr": new_tfr, "canonical_slug": new_slug, "slug_history": hist})

# ── FIX 2 : slugs trop courts ─────────────────────────────────────────
print("\n=== FIX 2 — Slugs mal formés ===")
STOPWORDS = {
    "le","la","les","du","de","des","au","aux","et","ou","n","sur",
    "relatif","relative","portant","fixant","instituant","modifiant",
    "dahir","decret","loi","arrete","circulaire","texte","par",
    "une","un","est","en","dans","pour","avec","sans","promulgation",
    "janvier","fevrier","mars","avril","mai","juin","juillet","aout",
    "septembre","octobre","novembre","decembre",
}

def make_slug(law):
    def norm(t):
        n = unicodedata.normalize("NFD", (t or "").lower())
        n = "".join(c for c in n if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z0-9\s]", " ", n)
    type_s   = re.sub(r"\s+", "-", norm(law.get("type","texte"))).strip("-")
    num_s    = re.sub(r"\s+", "-", norm(law.get("number",""))).strip("-")
    title    = norm(law.get("title_fr",""))
    words    = [w for w in title.split() if w not in STOPWORDS and len(w) > 2 and not re.match(r"^\d+$",w)][:7]
    kw_s     = "-".join(words)
    parts    = [p for p in [type_s, num_s, kw_s] if p]
    slug     = re.sub(r"-+", "-", "-".join(parts)).strip("-")[:120]
    return slug or f"texte-{law['id']}"

for lid in [7768, 7767, 7766, 7771, 7769, 4905]:
    x = laws.get(lid)
    if not x:
        print(f"  ID={lid} non trouvé")
        continue
    old_slug = x.get("canonical_slug","")
    new_slug = make_slug(x)
    hist = list(x.get("slug_history") or [])
    if old_slug and old_slug not in hist:
        hist.append(old_slug)
    print(f"  ID={lid} : {old_slug} → {new_slug}")
    if new_slug != old_slug:
        patch(lid, {"canonical_slug": new_slug, "slug_history": hist})
    else:
        print(f"    → slug inchangé")

print("\nDone.")
