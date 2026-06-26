"""
fix_types.py — Corrige les types non conformes en base (ex: "Texte Réglementaire" → "Décret")

Détecte le type correct à partir de title_fr / title_ar / number
et patche les enregistrements concernés.

Usage :
    python pipeline/fix_types.py --dry-run   # Aperçu sans modifier
    python pipeline/fix_types.py             # Applique les corrections
"""
import os, re, sys
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env", override=True)
load_dotenv()

URL = os.getenv("SUPABASE_URL", "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
H   = {"apikey": KEY, "Authorization": f"Bearer {KEY}",
       "Content-Type": "application/json", "Prefer": "return=representation"}

DRY_RUN = "--dry-run" in sys.argv

# ── Types valides ────────────────────────────────────────────────────────────
VALID_TYPES = {
    "Loi", "Loi organique",
    "Dahir", "Décret", "Décret royal",
    "Arrêté", "Arrêté conjoint",
    "Circulaire", "Code", "Jurisprudence",
    "Convention", "Traité",
    "Règlement", "Ordonnance",
    "Texte réglementaire", "Lettre Royale", "Discours Royal",
}

# ── Détection du type depuis le titre ────────────────────────────────────────
def detect_type(title_fr: str, title_ar: str = "", number: str = "") -> str | None:
    t  = (title_fr or "").lower()
    ta = (title_ar or "")
    n  = (number   or "").lower()

    # Titre français
    # Termes spécifiques à détecter en premier (avant dahir/décret)
    if re.search(r'\btraité\b|\btraite\b|\baccord\b|\bprotocole\b|\bconventionnel\b', t): return "Convention"

    if re.search(r'\bdahir\b', t):                    return "Dahir"
    if re.search(r'\bdécret\b|\bdecret\b', t):        return "Décret"
    if re.search(r'\barrêté\b|\barrete\b', t):        return "Arrêté"
    if re.search(r'\bcirculaire\b', t):               return "Circulaire"
    if re.search(r'\bcode\b', t):                     return "Code"
    if re.search(r'\bconvention\b', t):               return "Convention"
    if re.search(r'\bjurisprudence\b|\barrêt\b', t):  return "Jurisprudence"
    if re.search(r'\brèglement\b|\breglement\b', t):  return "Règlement"
    if re.search(r'\bordonnance\b', t):               return "Ordonnance"
    if re.search(r'\bloi\b', t):                      return "Loi"
    if re.search(r'\blettre royale\b', t):            return "Lettre Royale"

    # Titre arabe
    if 'ظهير' in ta:    return "Dahir"
    if 'مرسوم' in ta:   return "Décret"
    if 'قرار' in ta:    return "Arrêté"
    if 'منشور' in ta:   return "Circulaire"
    if 'مدونة' in ta:   return "Code"
    if 'قانون' in ta:   return "Loi"
    if 'اتفاقية' in ta: return "Convention"

    # Numéro (ex: "2-16-800" → Décret ; "1-XX-XXX" → Dahir)
    if re.match(r'^2[-.]', n):   return "Décret"
    if re.match(r'^1[-.]', n):   return "Dahir"
    if re.match(r'^3[-.]', n):   return "Arrêté"

    return None

# Types spécifiques à ne jamais écraser par détection automatique
TYPE_KEEP_AS_IS = {
    "Décret royal",    # historique (avant 1962)
    "Loi organique",   # procédure constitutionnelle spéciale
    "Arrêté conjoint", # multi-ministères
    "Traité",          # droit international
    "Discours Royal", "Lettre Royale",
    "Déclaration", "Avis", "Résolution", "Rapport", "Note", "Recommandation",
}

# ── Normaliser la casse des types existants ──────────────────────────────────
TYPE_ALIASES = {
    "texte réglementaire":    "Texte réglementaire",
    "texte reglementaire":    "Texte réglementaire",
    "texte réglementaire ":   "Texte réglementaire",
    "décret":                 "Décret",
    "dahir":                  "Dahir",
    "arrêté":                 "Arrêté",
    "loi":                    "Loi",
    "circulaire":             "Circulaire",
    "code":                   "Code",
    "convention":             "Convention",
    "règlement":              "Règlement",
    "ordonnance":             "Ordonnance",
}


# ── Chargement des lois ──────────────────────────────────────────────────────
print("Chargement des lois...", flush=True)
all_laws, offset = [], 0
while True:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "id,type,title_fr,title_ar,number,canonical_slug",
                "limit": "1000", "offset": str(offset)})
    batch = r.json()
    if not batch: break
    all_laws.extend(batch)
    offset += len(batch)
    if len(batch) < 1000: break

print(f"Total chargé : {len(all_laws)} lois\n")

# ── Analyse ──────────────────────────────────────────────────────────────────
to_fix = []

for law in all_laws:
    current_type = (law.get("type") or "").strip()

    # 1. Normaliser la casse si c'est un alias connu
    normalized = TYPE_ALIASES.get(current_type.lower())
    if normalized and normalized != current_type:
        to_fix.append({
            "id":       law["id"],
            "old_type": current_type,
            "new_type": normalized,
            "reason":   "normalisation casse",
            "title":    (law.get("title_fr") or "")[:60],
        })
        continue

    # 1b. Type spécifique → ne jamais écraser
    if current_type in TYPE_KEEP_AS_IS:
        continue

    # 2. Si type non valide → détecter depuis le titre
    if current_type not in VALID_TYPES:
        detected = detect_type(
            law.get("title_fr") or "",
            law.get("title_ar") or "",
            law.get("number") or "",
        )
        if detected:
            to_fix.append({
                "id":       law["id"],
                "old_type": current_type,
                "new_type": detected,
                "reason":   "type invalide → détecté",
                "title":    (law.get("title_fr") or "")[:60],
            })
        else:
            to_fix.append({
                "id":       law["id"],
                "old_type": current_type,
                "new_type": None,   # Indétectable
                "reason":   "type invalide — indétectable",
                "title":    (law.get("title_fr") or "")[:60],
            })
        continue

    # 3. Type "Texte réglementaire" générique → essayer de détecter quelque chose de plus précis
    if current_type == "Texte réglementaire":
        detected = detect_type(
            law.get("title_fr") or "",
            law.get("title_ar") or "",
            law.get("number") or "",
        )
        if detected and detected != "Texte réglementaire":
            to_fix.append({
                "id":       law["id"],
                "old_type": current_type,
                "new_type": detected,
                "reason":   "Texte réglementaire → plus précis",
                "title":    (law.get("title_fr") or "")[:60],
            })

SEP = "─" * 70

# ── Affichage ────────────────────────────────────────────────────────────────
fixable   = [x for x in to_fix if x["new_type"]]
unfixable = [x for x in to_fix if not x["new_type"]]

print(f"{'═'*70}")
print(f"CORRECTIONS DÉTECTÉES : {len(fixable)} corrigeables, {len(unfixable)} indétectables")
print(f"{'═'*70}\n")

# Grouper par transformation
from collections import Counter
changes = Counter(f"{x['old_type']} → {x['new_type']}" for x in fixable)
print("Transformations :")
for change, count in changes.most_common():
    print(f"  {count:4d}×  {change}")

print(f"\n{SEP}")
print("Exemples (20 premiers) :")
print(SEP)
for x in fixable[:20]:
    print(f"  ID={x['id']:5} | {x['old_type']:25} → {x['new_type']:20} | {x['title']}")

if unfixable:
    print(f"\n{SEP}")
    print(f"Indétectables ({len(unfixable)}) — type inchangé :")
    for x in unfixable[:10]:
        print(f"  ID={x['id']:5} | type='{x['old_type']}' | {x['title']}")

# ── Application ─────────────────────────────────────────────────────────────
if DRY_RUN:
    print(f"\n[DRY-RUN] Aucune modification. Relancez sans --dry-run pour appliquer.")
    sys.exit(0)

print(f"\n{'═'*70}")
print(f"APPLICATION des {len(fixable)} corrections...")
print(f"{'═'*70}")

ok = err = 0
for x in fixable:
    r = requests.patch(
        f"{URL}/rest/v1/laws?id=eq.{x['id']}",
        headers=H,
        json={"type": x["new_type"]},
        timeout=15,
    )
    if r.status_code in (200, 204):
        ok += 1
    else:
        err += 1
        print(f"  ✗ ID={x['id']} HTTP {r.status_code}")

    if ok % 100 == 0 and ok > 0:
        print(f"  ... {ok}/{len(fixable)} corrigés", flush=True)

print(f"\nDone : {ok} corrigés, {err} erreurs, {len(unfixable)} indétectables laissés tels quels.")
