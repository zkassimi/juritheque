"""
fix_bad_slugs.py — Corrige les canonical_slug non conformes en base.

Convention cible : {type}-{number}-{mots-clés-titre}
  Ex : decret-2-16-800-agence-nationale-reglementation-telecommunications-anrt
       loi-103-12-protection-donnees-personnelles
       arrete-adala-3dfd795b-nomination-membres

Usage :
  python pipeline/fix_bad_slugs.py --dry-run   # aperçu sans écrire
  python pipeline/fix_bad_slugs.py --all       # applique en base
  python pipeline/fix_bad_slugs.py --limit 50  # test sur 50 textes
"""
import os, re, sys, argparse, unicodedata, requests
from dotenv import load_dotenv

load_dotenv()
load_dotenv("pipeline/.env", override=True)

URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")
H   = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

ALLOWED = set("abcdefghijklmnopqrstuvwxyz0123456789-")

STOPWORDS = {
    # Articles / prépositions
    'le','la','les','du','de','des','au','aux','et','ou','un','une',
    'n','no','par','sur','en','dans','pour','avec','sans','est','qui','que',
    # Verbes / qualificatifs génériques
    'relatif','relative','relatifs','relatives',
    'portant','fixant','instituant','modifiant','abrogeant','approuvant',
    'promulgation','promulguant','application','execution',
    # Types de textes (éviter répétition)
    'dahir','decret','loi','arrete','circulaire','texte','ordonnance',
    'code','reglement','avis','bulletin','projet','version','cadre',
    # Sources / références inutiles
    'sgg','adala','portail','officiel','bulletin','journal',
    # Mois hijri (bruit dans les titres)
    'muharram','safar','rabia','joumada','rajab','chaabane','ramadan',
    'chaoual','doulkaada','doulhijja','hija','hijja','awal','thani',
    # Mots datés inutiles
    'juillet','janvier','fevrier','mars','avril','mai','juin',
    'aout','septembre','octobre','novembre','decembre',
    # Numéros / abréviations
    'num','numero','ndeg','art','article',
}

# ─── Slugification ────────────────────────────────────────────────────────────

def _s(t: str) -> str:
    norm = unicodedata.normalize("NFD", (t or "").lower())
    norm = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", norm).strip("-")

def _clean_number(raw: str) -> str:
    """Extrait la partie numérique pure d'un champ number.
    Ex: 'Dahir n°1-19-08' → '1-19-08'
         '2.12.349'        → '2-12-349'
         'adala-d07fc359'  → 'adala-d07fc359'
    """
    raw = (raw or "").strip()
    # Si c'est déjà un ID adala, on le garde tel quel
    if re.match(r'^adala-[0-9a-f]+$', raw.lower()):
        return raw.lower()
    # Extraire le numéro au format marocain X.XX.XXX ou X-XX-XXX
    m = re.search(r'(\d[\d\.\-/]+)', raw)
    if m:
        num = m.group(1)
        # Normaliser séparateurs → tirets
        num = re.sub(r'[.\s/]+', '-', num).strip('-')
        return num
    return _s(raw)

def make_slug(law: dict) -> str:
    """Convention : {type}-{number_clean}-{mots-clés-titre}."""
    type_slug   = _s(law.get("type") or "texte")
    number_raw  = law.get("number") or ""
    number_slug = _s(_clean_number(number_raw))
    title       = (law.get("title_fr") or "").strip()

    # Tokens à exclure des keywords : type + number + stopwords
    type_tokens = set(type_slug.split("-"))
    num_tokens  = set(number_slug.split("-")) if number_slug else set()
    excluded    = STOPWORDS | type_tokens | num_tokens | {''}

    words = re.sub(r"[^a-zA-Z\xc0-\xff0-9\s]", " ", title).lower().split()
    keywords = []
    for w in words:
        sw = _s(w)
        # Ignorer les pures séquences numériques (années, etc.)
        if sw and w not in excluded and sw not in excluded and len(w) > 2 and not re.match(r'^\d+$', sw):
            keywords.append(sw)
        if len(keywords) >= 6:
            break
    kw_slug = "-".join(keywords)

    parts = [p for p in [type_slug, number_slug, kw_slug] if p]
    slug  = re.sub(r"-+", "-", "-".join(parts)).strip("-")[:100]
    return slug or f"texte-{law.get('id', 'unknown')[:8]}"

def is_bad(slug: str) -> bool:
    return bool(slug) and any(c not in ALLOWED for c in slug)

# ─── Supabase ─────────────────────────────────────────────────────────────────

def fetch_all() -> list:
    rows, offset = [], 0
    while True:
        r = requests.get(f"{URL}/rest/v1/laws",
            headers={**H, "Range": f"{offset}-{offset+999}"},
            params={"select": "id,number,title_fr,type,canonical_slug"},
            timeout=20)
        if r.status_code not in (200, 206):
            print(f"Erreur fetch {r.status_code}: {r.text[:200]}")
            break
        chunk = r.json()
        if not chunk: break
        rows.extend(chunk)
        if len(chunk) < 1000: break
        offset += 1000
    return rows

def slug_exists(slug: str, exclude_id: str) -> bool:
    r = requests.get(f"{URL}/rest/v1/laws",
        headers=H,
        params={"canonical_slug": f"eq.{slug}", "id": f"neq.{exclude_id}",
                "select": "id", "limit": "1"},
        timeout=10)
    return len(r.json()) > 0

def patch(law_id: str, new_slug: str) -> bool:
    r = requests.patch(f"{URL}/rest/v1/laws",
        headers={**H, "Content-Type": "application/json", "Prefer": "return=minimal"},
        params={"id": f"eq.{law_id}"},
        json={"canonical_slug": new_slug},
        timeout=10)
    return r.status_code in (200, 204)

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Aperçu sans écrire")
    ap.add_argument("--all",     action="store_true", help="Appliquer en base")
    ap.add_argument("--limit",   type=int, default=0,  help="Limite de corrections")
    args = ap.parse_args()

    if not args.dry_run and not args.all:
        print("Usage: --dry-run pour aperçu, --all pour appliquer")
        sys.exit(1)

    print("Chargement des textes…")
    rows = fetch_all()
    print(f"  {len(rows)} textes chargés")

    bad = [x for x in rows if is_bad(x.get("canonical_slug", ""))]
    print(f"  {len(bad)} slugs non conformes détectés\n")

    if args.limit:
        bad = bad[:args.limit]

    ok, errors, skipped = 0, 0, 0
    print(f"{'Avant':<50} {'Après':<60} Status")
    print("-" * 125)

    # Garder trace des slugs déjà générés dans cette session (évite doublons en lot)
    seen_in_session = set()

    for x in bad:
        old_slug = x.get("canonical_slug", "")
        new_slug = make_slug(x)

        # Unicité : suffixe -2, -3... si collision
        candidate = new_slug
        suffix = 2
        while (candidate in seen_in_session or
               (not args.dry_run and slug_exists(candidate, x["id"]))):
            candidate = f"{new_slug}-{suffix}"
            suffix += 1
            if suffix > 99:
                break
        new_slug = candidate
        seen_in_session.add(new_slug)

        status = "→ DRY" if args.dry_run else "?"
        if not args.dry_run:
            if patch(x["id"], new_slug):
                status = "✅ OK"
                ok += 1
            else:
                status = "❌ ERR"
                errors += 1
        else:
            ok += 1

        print(f"{old_slug:<50} {new_slug:<60} {status}")

    print(f"\n{'Aperçu' if args.dry_run else 'Résultat'} : {ok} corrigés, {errors} erreurs, {skipped} ignorés")

if __name__ == "__main__":
    main()
