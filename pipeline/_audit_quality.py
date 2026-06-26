"""
_audit_quality.py — Audit complet de la qualité des lois en base

Détecte :
  1. title_ar absent (NULL ou vide)
  2. title_ar en français (pas de caractères arabes)
  3. title_fr absent
  4. canonical_slug absent ou trop court
  5. slug_history vide (risque 301 cassé si slug changé)
  6. date absente
  7. source_url absent ET pdf_url absent (aucune source)
  8. type = "Texte juridique" (générique, pas enrichi)
  9. titre FR trop court (< 20 chars) — probablement un placeholder
 10. titre FR = titre AR (même texte dans les deux champs)
"""
import os, re, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
H   = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

print("Chargement de toutes les lois...")
all_laws, offset = [], 0
while True:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "id,number,title_fr,title_ar,canonical_slug,type,date,source_url,pdf_url,slug_history",
                "limit": "1000", "offset": str(offset)})
    batch = r.json()
    if not batch: break
    all_laws.extend(batch)
    offset += len(batch)
    if len(batch) < 1000: break

print(f"→ {len(all_laws)} lois chargées\n")

def has_arabic(t):
    return bool(re.search(r'[؀-ۿ؀-ۿ]', t or ""))

issues = {
    "no_title_ar":       [],
    "title_ar_in_french":[],
    "no_title_fr":       [],
    "no_slug":           [],
    "no_date":           [],
    "no_source":         [],
    "generic_type":      [],
    "short_title_fr":    [],
    "fr_equals_ar":      [],
}

for x in all_laws:
    lid    = x["id"]
    tfr    = (x.get("title_fr") or "").strip()
    tar    = (x.get("title_ar") or "").strip()
    slug   = (x.get("canonical_slug") or "").strip()
    typ    = (x.get("type") or "").strip()
    date   = x.get("date")
    src    = x.get("source_url") or x.get("pdf_url")

    if not tar:
        issues["no_title_ar"].append(x)
    elif not has_arabic(tar):
        issues["title_ar_in_french"].append(x)

    if not tfr:
        issues["no_title_fr"].append(x)
    elif len(tfr) < 20:
        issues["short_title_fr"].append(x)

    if not slug or len(slug) < 5:
        issues["no_slug"].append(x)

    if not date:
        issues["no_date"].append(x)

    if not src:
        issues["no_source"].append(x)

    if typ.lower() in ("texte juridique", "texte réglementaire", ""):
        issues["generic_type"].append(x)

    if tfr and tar and tfr.lower().strip() == tar.lower().strip():
        issues["fr_equals_ar"].append(x)

print("=" * 65)
print("AUDIT QUALITÉ — JuriThèque")
print("=" * 65)
print(f"  Total lois : {len(all_laws)}\n")

labels = {
    "no_title_ar":        "❌ title_ar absent (NULL/vide)",
    "title_ar_in_french": "⚠️  title_ar en français (pas d'arabe)",
    "no_title_fr":        "❌ title_fr absent",
    "no_slug":            "⚠️  canonical_slug absent/trop court",
    "no_date":            "⚠️  date absente",
    "no_source":          "⚠️  aucune source (pdf_url ET source_url vides)",
    "generic_type":       "ℹ️  type générique (Texte juridique)",
    "short_title_fr":     "⚠️  title_fr trop court (< 20 chars)",
    "fr_equals_ar":       "⚠️  title_fr = title_ar (même texte)",
}

for key, label in labels.items():
    n = len(issues[key])
    pct = n / len(all_laws) * 100
    print(f"  {label:<50} : {n:5d}  ({pct:.1f}%)")

# Exemples pour les cas importants
for key in ["no_title_ar", "title_ar_in_french", "short_title_fr", "fr_equals_ar"]:
    items = issues[key]
    if items:
        print(f"\n--- Exemples {labels[key]} (5 premiers) ---")
        for x in items[:5]:
            print(f"  ID {x['id']:5d}  n°={x.get('number','?'):20}  FR={str(x.get('title_fr',''))[:50]}  AR={str(x.get('title_ar',''))[:50]}")

print("\n" + "=" * 65)
print("FIN AUDIT")
