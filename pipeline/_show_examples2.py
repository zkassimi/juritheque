"""Affiche exemples complets : lien + titre complet + changement proposé."""
import os, re, requests, time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

URL  = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY  = os.getenv("SUPABASE_SERVICE_KEY", "")
OR   = os.getenv("OPENROUTER_API_KEY", "")
H    = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
SITE = "https://juritheque.com/loi"

def has_arabic(t):
    return bool(re.search(r'[؀-ۿ]', t or ""))

def translate_fr_to_ar(title_fr, law_type="", number=""):
    if not OR: return "❓ (traduction non disponible sans API)"
    prompt = (
        "Traduis ce titre juridique marocain du français en arabe officiel (style Bulletin Officiel).\n"
        "Réponds UNIQUEMENT avec le titre traduit, sans explication.\n\n"
        f"Titre : {title_fr}"
    )
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OR}", "Content-Type": "application/json"},
            json={"model": "google/gemini-2.5-flash", "max_tokens": 250, "temperature": 0.1,
                  "messages": [{"role": "user", "content": prompt}]}, timeout=25)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip().split("\n")[0]
    except: pass
    return "❓ (erreur traduction)"

# ── Fetch ──────────────────────────────────────────────────────────────────
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

print(f"→ {len(all_laws)} lois chargées\n")

no_ar, ar_in_fr, fr_eq_ar = [], [], []
for x in all_laws:
    tfr  = (x.get("title_fr") or "").strip()
    tar  = (x.get("title_ar") or "").strip()
    slug = x.get("canonical_slug") or ""
    if not slug: continue
    if not tar:
        no_ar.append(x)
    elif not has_arabic(tar):
        ar_in_fr.append(x)
    if tfr and tar and not has_arabic(tar) and tfr.lower() == tar.lower():
        fr_eq_ar.append(x)

SEP = "═" * 75

# ══ CAS 1 : title_ar en français ══════════════════════════════════════════
print(f"\n{SEP}")
print("CAS 1 — title_ar EN FRANÇAIS (750 records)")
print("  Problème : la page arabe affiche un titre français au lieu de l'arabe")
print("  Correction : traduire title_fr → arabe pour remplacer title_ar")
print(SEP)

for i, x in enumerate(ar_in_fr[:3], 1):
    slug   = x.get("canonical_slug","")
    tfr    = x.get("title_fr","")
    tar    = x.get("title_ar","")
    new_ar = translate_fr_to_ar(tfr, x.get("type",""), x.get("number",""))
    time.sleep(0.3)
    print(f"\n  [{i}] n° {x['number']}")
    print(f"  URL      : {SITE}/{slug}")
    print(f"  title_fr : {tfr}")
    print(f"  title_ar : {tar}  ← FAUX (français)")
    print(f"  → NOUVEAU title_ar : {new_ar}")

# ══ CAS 2 : title_ar absent ═══════════════════════════════════════════════
print(f"\n\n{SEP}")
print("CAS 2 — title_ar ABSENT (353 records)")
print("  Problème : aucun titre arabe → page arabe vide")
print("  Correction : traduire title_fr → arabe")
print(SEP)

for i, x in enumerate([x for x in no_ar if x.get("canonical_slug") and x.get("title_fr") and not has_arabic(x.get("title_fr",""))][:3], 1):
    slug   = x.get("canonical_slug","")
    tfr    = x.get("title_fr","")
    new_ar = translate_fr_to_ar(tfr, x.get("type",""), x.get("number",""))
    time.sleep(0.3)
    print(f"\n  [{i}] n° {x['number']}")
    print(f"  URL      : {SITE}/{slug}")
    print(f"  title_fr : {tfr}")
    print(f"  title_ar : NULL")
    print(f"  → NOUVEAU title_ar : {new_ar}")

# ══ CAS 3 : title_fr = title_ar ═══════════════════════════════════════════
print(f"\n\n{SEP}")
print("CAS 3 — title_fr = title_ar (39 records)")
print("  Problème : title_ar est une copie du title_fr (en français)")
print("  Correction : traduire title_fr → arabe pour remplacer title_ar")
print(SEP)

for i, x in enumerate(fr_eq_ar[:3], 1):
    slug   = x.get("canonical_slug","")
    tfr    = x.get("title_fr","")
    new_ar = translate_fr_to_ar(tfr, x.get("type",""), x.get("number",""))
    time.sleep(0.3)
    print(f"\n  [{i}] n° {x['number']}")
    print(f"  URL      : {SITE}/{slug}")
    print(f"  title_fr : {tfr}")
    print(f"  title_ar : {x.get('title_ar','')}  ← COPIE DU FRANÇAIS")
    print(f"  → NOUVEAU title_ar : {new_ar}")

print(f"\n\n{SEP}")
print("RÉSUMÉ")
print(SEP)
print(f"  CAS 1 — title_ar en français : {len(ar_in_fr)} records")
print(f"  CAS 2 — title_ar absent      : {len(no_ar)} records")
print(f"  CAS 3 — title_fr = title_ar  : {len(fr_eq_ar)} records")
print(f"  TOTAL à corriger             : {len(ar_in_fr) + len(no_ar) + len(fr_eq_ar)} records")
