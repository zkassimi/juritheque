"""
fix_title_ar.py — Corrige les title_ar manquants ou incorrects

3 cas traités :
  CAS 1 : title_ar en français (pas de caractères arabes) → traduire title_fr → arabe
  CAS 2 : title_ar absent (NULL) → traduire title_fr → arabe
  CAS 3 : title_fr = title_ar (copie française) → traduire title_fr → arabe

Auto-resumable : les records déjà corrigés ne réapparaissent plus.

Usage :
  python pipeline/fix_title_ar.py --preview 10
  python pipeline/fix_title_ar.py --apply
  python pipeline/fix_title_ar.py --apply --limit 100
"""

import os, re, sys, time, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
OR  = os.getenv("OPENROUTER_API_KEY", "")
H   = {"apikey": KEY, "Authorization": f"Bearer {KEY}",
       "Content-Type": "application/json", "Prefer": "return=representation"}

apply     = "--apply" in sys.argv
preview_n = 10
for a in sys.argv:
    if a.startswith("--preview="):  preview_n = int(a.split("=")[1])
    if a.startswith("--limit="):    limit_arg = int(a.split("=")[1])
if "--preview" in sys.argv and not any(a.startswith("--preview=") for a in sys.argv):
    idx = sys.argv.index("--preview")
    if idx + 1 < len(sys.argv) and sys.argv[idx+1].isdigit():
        preview_n = int(sys.argv[idx+1])
limit_arg = 0
for a in sys.argv:
    if a.startswith("--limit="): limit_arg = int(a.split("=")[1])

def has_arabic(t):
    return bool(re.search(r'[؀-ۿ]', t or ""))

def translate_fr_to_ar(title_fr, law_type="", number=""):
    if not OR or not title_fr:
        return None
    prompt = (
        "Tu es un juriste marocain expert en traduction juridique officielle. "
        "Traduis ce titre français de texte juridique marocain en arabe, dans le style du Bulletin Officiel marocain.\n"
        "Réponds UNIQUEMENT avec le titre traduit en arabe, sans explication ni ponctuation supplémentaire.\n\n"
        f"Type : {law_type or 'Texte juridique'}\n"
        f"Numéro : {number or 'inconnu'}\n"
        f"Titre français : {title_fr}"
    )
    for attempt in range(3):
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OR}", "Content-Type": "application/json"},
                json={"model": "google/gemini-2.5-flash", "max_tokens": 300, "temperature": 0.1,
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=30,
            )
            if r.status_code == 200:
                title = r.json()["choices"][0]["message"]["content"].strip().split("\n")[0]
                title = title.strip("\"'«».,")
                if len(title) > 5 and has_arabic(title):
                    return title[:300]
        except Exception as e:
            if attempt < 2:
                print(f"    Réseau: {e} — retry {attempt+2}/3", flush=True)
                time.sleep(4)
            else:
                print(f"    ✗ Erreur traduction: {e}", flush=True)
    return None

# ── Fetch toutes les lois ──────────────────────────────────────────────────
print("Chargement des lois...", flush=True)
all_laws, offset = [], 0
while True:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "id,number,title_fr,title_ar,type,canonical_slug",
                "limit": "1000", "offset": str(offset)})
    batch = r.json()
    if not batch: break
    all_laws.extend(batch)
    offset += len(batch)
    if len(batch) < 1000: break
print(f"→ {len(all_laws)} lois chargées", flush=True)

# ── Catégoriser ───────────────────────────────────────────────────────────
to_fix = []
stats = {"cas1": 0, "cas2": 0, "cas3": 0}

for x in all_laws:
    tfr = (x.get("title_fr") or "").strip()
    tar = (x.get("title_ar") or "").strip()

    # Ignorer si title_fr absent ou en arabe (problème différent)
    if not tfr or has_arabic(tfr):
        continue

    cas = None
    if not tar:
        cas = 2  # title_ar absent
        stats["cas2"] += 1
    elif not has_arabic(tar):
        if tfr.lower() == tar.lower():
            cas = 3  # copie exacte
            stats["cas3"] += 1
        else:
            cas = 1  # title_ar en français (mais différent)
            stats["cas1"] += 1

    if cas:
        to_fix.append({**x, "_cas": cas})

print(f"\n{'═'*60}", flush=True)
print(f"RECORDS À CORRIGER", flush=True)
print(f"{'═'*60}", flush=True)
print(f"  CAS 1 — title_ar en français (≠ title_fr) : {stats['cas1']}", flush=True)
print(f"  CAS 2 — title_ar absent                   : {stats['cas2']}", flush=True)
print(f"  CAS 3 — title_fr = title_ar (copie)       : {stats['cas3']}", flush=True)
print(f"  TOTAL                                      : {len(to_fix)}", flush=True)
print(flush=True)

if not to_fix:
    print("✅ Rien à corriger !", flush=True)
    sys.exit(0)

# Appliquer la limite
if apply:
    to_process = to_fix[:limit_arg] if limit_arg else to_fix
else:
    to_process = to_fix[:preview_n]

mode = "APPLY" if apply else f"PREVIEW ({preview_n})"
print(f"Mode : {mode} — {len(to_process)} records à traiter\n", flush=True)

ok_count = 0
err_count = 0

for i, law in enumerate(to_process, 1):
    lid      = law["id"]
    number   = law.get("number") or ""
    law_type = law.get("type") or "Texte juridique"
    title_fr = law.get("title_fr") or ""
    title_ar = law.get("title_ar") or ""
    cas      = law["_cas"]
    slug     = law.get("canonical_slug") or ""

    cas_label = ["", "AR en FR", "AR absent", "FR=AR"][cas]
    print(f"  [{i}/{len(to_process)}] CAS{cas} ({cas_label}) | n°={number}", flush=True)
    print(f"    title_fr : {title_fr[:80]}", flush=True)
    if title_ar:
        print(f"    title_ar : {title_ar[:80]}  ← À REMPLACER", flush=True)

    new_ar = translate_fr_to_ar(title_fr, law_type, number)

    if not new_ar:
        print(f"    ✗ Traduction échouée — skip", flush=True)
        err_count += 1
        time.sleep(0.5)
        continue

    print(f"    → Nouveau title_ar : {new_ar[:80]}", flush=True)

    if apply:
        patched = False
        for attempt in range(3):
            try:
                r = requests.patch(
                    f"{URL}/rest/v1/laws?id=eq.{lid}",
                    headers=H, json={"title_ar": new_ar}, timeout=20,
                )
                if r.status_code in (200, 204):
                    print(f"    ✓ PATCHÉ", flush=True)
                    ok_count += 1
                    patched = True
                else:
                    print(f"    ✗ PATCH échoué: {r.status_code} {r.text[:80]}", flush=True)
                    err_count += 1
                break
            except Exception as e:
                if attempt < 2:
                    print(f"    Réseau: {e} — retry {attempt+2}/3", flush=True)
                    time.sleep(5)
                else:
                    print(f"    ✗ Abandon: {e}", flush=True)
                    err_count += 1
    else:
        ok_count += 1

    time.sleep(0.3)

print(f"\n{'═'*60}", flush=True)
if apply:
    print(f"✅ {ok_count} records corrigés", flush=True)
    if err_count:
        print(f"⚠  {err_count} erreurs — relancer pour les records manquants", flush=True)
else:
    print(f"PREVIEW terminé — {ok_count} corrections prêtes", flush=True)
    print(f"→ Lancer : python pipeline/fix_title_ar.py --apply", flush=True)
