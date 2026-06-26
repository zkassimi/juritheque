"""
fix_types_ai.py — Corrige les types indétectables via Gemini AI

Usage:
    python pipeline/fix_types_ai.py --test      # 10 premiers, aperçu uniquement
    python pipeline/fix_types_ai.py --dry-run   # Tous, aperçu sans modifier
    python pipeline/fix_types_ai.py             # Applique toutes les corrections
"""
import os, re, json, sys, time, requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env", override=True)
load_dotenv()

URL    = os.getenv("SUPABASE_URL", "").rstrip("/")
KEY    = os.getenv("SUPABASE_SERVICE_KEY", "")
OR_KEY = os.getenv("OPENROUTER_API_KEY", "")
H      = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

TEST    = "--test"    in sys.argv
DRY_RUN = "--dry-run" in sys.argv
LIMIT   = 10 if TEST else None

VALID_TYPES = [
    "Loi", "Loi organique", "Dahir", "Décret", "Décret royal",
    "Arrêté", "Arrêté conjoint", "Circulaire", "Code", "Convention",
    "Traité", "Règlement", "Ordonnance", "Jurisprudence",
    "Texte réglementaire", "Lettre Royale", "Discours Royal",
    "Déclaration", "Avis", "Rapport", "Note", "Charte",
    "Bulletin officiel",
]

# Alias : types renvoyés par l'IA mais non dans VALID_TYPES
TYPE_ALIASES_AI = {
    "Journal officiel": "Bulletin officiel",
    "Revue":            "Rapport",
    "Guide":            "Rapport",
    "Recueil":          "Code",
}

# ── Fetch les enregistrements à corriger ─────────────────────────────────────
print("Chargement des enregistrements...", flush=True)
all_laws, offset = [], 0
while True:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "id,type,title_fr,title_ar,number",
                "limit": "1000", "offset": str(offset)})
    batch = r.json()
    if not batch: break
    # Garder uniquement les types indétectables
    for x in batch:
        if x.get("type") in ("Autre", "Texte réglementaire", "Texte juridique"):
            all_laws.append(x)
    offset += len(batch)
    if len(batch) < 1000: break

target = all_laws[:LIMIT] if LIMIT else all_laws
print(f"{len(all_laws)} enregistrements trouvés — traitement de {len(target)}\n")

# ── Appel IA ─────────────────────────────────────────────────────────────────
def detect_with_ai(law: dict) -> tuple[str | None, float, str]:
    title_fr = (law.get("title_fr") or "").strip()
    title_ar = (law.get("title_ar") or "").strip()
    number   = (law.get("number")   or "").strip()

    prompt = (
        "Tu es un expert en droit marocain.\n"
        "Détermine le type juridique exact de ce texte.\n\n"
        f"Titre FR : {title_fr}\n"
        f"Titre AR : {title_ar}\n"
        f"Numéro   : {number}\n\n"
        f"Types possibles : {', '.join(VALID_TYPES)}\n\n"
        "Réponds UNIQUEMENT avec un objet JSON (sans markdown) :\n"
        '{"type": "...", "confidence": 0.0-1.0, "reason": "..."}\n'
        "Si impossible à déterminer, utilise \"Texte réglementaire\" avec confidence < 0.5."
    )

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OR_KEY}", "Content-Type": "application/json"},
            json={"model": "google/gemini-2.5-flash",
                  "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": 300},
            timeout=25,
        )
        if resp.status_code != 200:
            return None, 0.0, f"HTTP {resp.status_code}"

        raw = resp.json()["choices"][0]["message"]["content"].strip()
        # Nettoyer les fences markdown
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw).strip()
        # Extraire le JSON
        m = re.search(r"\{[\s\S]*\}", raw)
        if not m:
            return None, 0.0, f"no JSON in: {raw[:80]}"
        data = json.loads(m.group())
        t    = data.get("type", "").strip()
        conf = float(data.get("confidence", 0))
        reason = data.get("reason", "")
        # Appliquer les alias
        if t in TYPE_ALIASES_AI:
            t = TYPE_ALIASES_AI[t]
        if t not in VALID_TYPES:
            return None, conf, f"type inconnu '{t}'"
        return t, conf, reason

    except Exception as e:
        return None, 0.0, str(e)

# ── Boucle principale ────────────────────────────────────────────────────────
SEP = "─" * 72
results = []

print(SEP)
print(f"{'ID':>6}  {'TYPE ACTUEL':20}  {'→':1}  {'TYPE DÉTECTÉ':20}  {'CONF':5}  TITRE")
print(SEP)

for i, law in enumerate(target):
    new_type, conf, reason = detect_with_ai(law)
    title = (law.get("title_fr") or law.get("title_ar") or "")[:55]

    keep = new_type and conf >= 0.6 and new_type != law["type"]
    results.append({"law": law, "new_type": new_type, "conf": conf,
                    "reason": reason, "apply": keep})

    marker = "✓" if keep else "✗"
    print(f"{marker} {law['id']:5}  {law['type']:20}  →  {str(new_type or '?'):20}  {int(conf*100):3}%  {title}")
    if not keep:
        print(f"         ↳ {reason[:80]}")

    # Pause pour éviter le rate limiting
    time.sleep(0.3)

# ── Résumé ───────────────────────────────────────────────────────────────────
fixable = [x for x in results if x["apply"]]
print(f"\n{SEP}")
print(f"Corrigeables (conf ≥ 60%) : {len(fixable)}/{len(results)}")
print(SEP)

if TEST or DRY_RUN:
    print("\n[TEST/DRY-RUN] Aucune modification appliquée.")
    sys.exit(0)

# ── Application ──────────────────────────────────────────────────────────────
print(f"\nApplication de {len(fixable)} corrections...")
ok = err = 0
for x in fixable:
    r = requests.patch(
        f"{URL}/rest/v1/laws?id=eq.{x['law']['id']}",
        headers=H,
        json={"type": x["new_type"]},
        timeout=15,
    )
    if r.status_code in (200, 204):
        ok += 1
    else:
        err += 1
        print(f"  ✗ ID={x['law']['id']} HTTP {r.status_code}")

print(f"\nDone : {ok} corrigés, {err} erreurs.")
