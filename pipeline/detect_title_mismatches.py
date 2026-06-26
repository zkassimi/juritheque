"""
detect_title_mismatches.py — Détecte les records où title_fr ≠ title_ar (sujets différents)

Méthodes (sans API, basées sur heuristiques) :
  1. Titres FR dupliqués (même title_fr sur plusieurs records)
  2. Date FR ≠ date AR dans les titres (signe certain de mismatch)
  3. Numéro de loi dans title_ar ≠ number du record
"""
import os, re, sys, requests
from pathlib import Path
from collections import Counter
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
H   = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

LIMIT = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--limit=")), "10000"))

# ── Mois arabes → numéro ────────────────────────────────────────────────────
AR_MONTHS = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "أبريل": 4, "ماي": 5, "يونيو": 6,
    "يوليو": 7, "يوليوز": 7, "غشت": 8, "أغسطس": 8, "شتنبر": 9, "سبتمبر": 9,
    "أكتوبر": 10, "نونبر": 11, "نوفمبر": 11, "دجنبر": 12, "ديسمبر": 12,
}
FR_MONTHS = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12,
}

def extract_year_month(text: str, lang: str) -> tuple[int|None, int|None]:
    """Extrait (année, mois) depuis un titre de loi."""
    text = (text or "").lower()
    # Année : 4 chiffres entre 1800-2099
    years = re.findall(r'\b(1[89]\d\d|20\d\d)\b', text)
    year = int(years[0]) if years else None
    month = None
    months = FR_MONTHS if lang == "fr" else AR_MONTHS
    for m_name, m_num in months.items():
        if m_name in text:
            month = m_num
            break
    return year, month

def normalize_number(n: str) -> str:
    """Normalise 2.03.530 → 2-03-530."""
    return re.sub(r'[.\s/]+', '-', (n or "").strip().lower())

# ── Fetch toutes les lois ────────────────────────────────────────────────────
print(f"\n{'─'*70}")
print("detect_title_mismatches.py")
print(f"{'─'*70}\n")

all_laws = []
offset   = 0
page_size = 1000

while True:
    r = requests.get(f"{URL}/rest/v1/laws", headers={**H, "Prefer": "count=exact"},
        params={"select": "id,number,title_fr,title_ar,canonical_slug,type,date",
                "title_fr": "not.is.null",
                "title_ar": "not.is.null",
                "limit": str(page_size), "offset": str(offset)})
    batch = r.json()
    if not batch:
        break
    all_laws.extend(batch)
    offset += len(batch)
    if len(batch) < page_size:
        break

print(f"→ {len(all_laws)} lois avec title_fr ET title_ar\n")

mismatches = []

# ── CAS 1 : Titres FR dupliqués ──────────────────────────────────────────────
title_fr_counts = Counter(x["title_fr"] for x in all_laws)
duplicates = {t for t, c in title_fr_counts.items() if c >= 2}

dup_groups = {}
for x in all_laws:
    t = x["title_fr"]
    if t in duplicates:
        dup_groups.setdefault(t, []).append(x)

print(f"{'═'*70}")
print(f"CAS 1 — Titres FR dupliqués ({len(dup_groups)} groupes)")
print(f"{'═'*70}")

dup_count = 0
for t, group in sorted(dup_groups.items(), key=lambda x: -len(x[1])):
    if len(group) < 2:
        continue
    # Vérifier si les numéros sont différents (vrai doublon de contenu)
    numbers = [x["number"] for x in group]
    if len(set(numbers)) == 1:
        continue  # même numéro = vraie doublon de record (pas un problème de titre)
    dup_count += 1
    print(f"\n  [{dup_count}] title_fr dupliqué sur {len(group)} records différents :")
    print(f"      \"{t[:80]}\"")
    for x in group[:5]:
        print(f"      → ID {x['id']:5d}  n°={x['number']:20}  {(x['title_ar'] or '')[:60]}")
    for x in group:
        mismatches.append({"id": x["id"], "reason": "duplicate_title_fr",
                           "number": x["number"], "title_fr": t[:60],
                           "title_ar": (x["title_ar"] or "")[:60]})

print(f"\n  → {dup_count} groupes de doublons FR (≥2 records avec titres différents)")

# ── CAS 2 : Date FR ≠ Date AR ────────────────────────────────────────────────
print(f"\n{'═'*70}")
print("CAS 2 — Date FR ≠ Date AR dans les titres")
print(f"{'═'*70}")

date_mismatches = []
for x in all_laws:
    tfr = x.get("title_fr") or ""
    tar = x.get("title_ar") or ""

    yr_fr, mo_fr = extract_year_month(tfr, "fr")
    yr_ar, mo_ar = extract_year_month(tar, "ar")

    if not yr_fr or not yr_ar:
        continue  # pas de date extraite → skip

    year_diff  = abs(yr_fr - yr_ar) > 1   # tolérance 1 an (calendrier hégire)
    month_diff = (mo_fr and mo_ar and mo_fr != mo_ar and abs(yr_fr - yr_ar) == 0)

    if year_diff or month_diff:
        date_mismatches.append({
            "id":       x["id"],
            "number":   x["number"],
            "yr_fr":    yr_fr, "mo_fr": mo_fr,
            "yr_ar":    yr_ar, "mo_ar": mo_ar,
            "title_fr": tfr[:70],
            "title_ar": tar[:70],
            "slug":     x["canonical_slug"] or "",
        })

print(f"\n  → {len(date_mismatches)} records avec date FR ≠ date AR\n")
for i, x in enumerate(date_mismatches[:30], 1):
    print(f"  [{i:2d}] ID {x['id']:5d}  n°={x['number']:20}")
    mo_fr_str = f"{x['mo_fr']:02d}" if x['mo_fr'] else "??"
    print(f"        FR ({x['yr_fr']}/{mo_fr_str}): {x['title_fr'][:65]}")
    mo_ar_str = f"{x['mo_ar']:02d}" if x['mo_ar'] else "??"
    print(f"        AR ({x['yr_ar']}/{mo_ar_str}): {x['title_ar'][:65]}")

if len(date_mismatches) > 30:
    print(f"\n  ... et {len(date_mismatches)-30} autres")

for x in date_mismatches:
    mismatches.append({"id": x["id"], "reason": "date_mismatch_fr_ar",
                       "number": x["number"], "title_fr": x["title_fr"],
                       "title_ar": x["title_ar"]})

# ── CAS 3 : Numéro dans title_ar ≠ number du record ─────────────────────────
print(f"\n{'═'*70}")
print("CAS 3 — Numéro dans title_ar ≠ number du record")
print(f"{'═'*70}")

num_mismatches = []
for x in all_laws:
    tar  = x.get("title_ar") or ""
    num  = x.get("number") or ""
    if not num or not tar:
        continue
    norm_num = normalize_number(num)
    # Chercher un numéro de type X.XX.XXX ou X-XX-XXX dans le titre AR
    found = re.findall(r'\d{1,2}[.\-]\d{2,3}[.\-]\d{1,3}', tar)
    for f in found:
        if normalize_number(f) != norm_num:
            num_mismatches.append({
                "id":       x["id"],
                "number":   num,
                "found_in_ar": f,
                "title_fr": (x["title_fr"] or "")[:65],
                "title_ar": tar[:65],
            })
            break

print(f"\n  → {len(num_mismatches)} records avec numéro discordant dans title_ar\n")
for i, x in enumerate(num_mismatches[:20], 1):
    print(f"  [{i:2d}] ID {x['id']:5d}  record n°={x['number']:18}  AR n°={x['found_in_ar']}")
    print(f"        FR: {x['title_fr'][:65]}")
    print(f"        AR: {x['title_ar'][:65]}")

# ── RÉSUMÉ ───────────────────────────────────────────────────────────────────
all_ids = set(x["id"] for x in mismatches) | set(x["id"] for x in num_mismatches)
print(f"\n{'═'*70}")
print(f"RÉSUMÉ")
print(f"{'═'*70}")
print(f"  CAS 1 — titres FR dupliqués    : {dup_count} groupes")
print(f"  CAS 2 — date FR ≠ date AR      : {len(date_mismatches)} records")
print(f"  CAS 3 — numéro discordant AR   : {len(num_mismatches)} records")
print(f"  Total records suspects (uniq)  : {len(all_ids)}")
