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
sys.path.insert(0, os.path.dirname(__file__))
from slug_utils import make_slug_from_law as _make_slug_full, _s, _GENERIC_TYPES

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
    'juridique','reglementaire','legislatif','administrative',
    'code','reglement','avis','bulletin','projet','version','cadre',
    # Sources / références inutiles
    'sgg','adala','portail','officiel','bulletin','journal',
    # Mois hijri (bruit dans les titres)
    'muharram','safar','rabia','joumada','rajab','chaabane','ramadan',
    'chaoual','doulkaada','doulhijja','hija','hijja','awal','thani',
    # Mois grégoriens inutiles
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

_GENERIC_TYPES = {'texte-juridique', 'texte-reglementaire', 'texte', 'document', 'autre'}

def _infer_type_from_number(number: str, current_type: str) -> str:
    """Déduit le type légal depuis le format du numéro marocain standard."""
    ct = (current_type or "").strip().lower()
    if ct and ct not in ('texte juridique', 'texte réglementaire', 'texte', 'document', ''):
        return current_type  # Type déjà précis → garder
    n = re.sub(r'[\s_\.\s]+', '-', (number or '').strip())
    if re.match(r'^1-\d{2}-\d+$', n):   return "Dahir"    # 1-xx-xxx
    if re.match(r'^2-\d{2}-\d+$', n):   return "Décret"   # 2-xx-xxx
    if re.match(r'^\d{2,3}-\d{2}$', n): return "Loi"      # xx-xx (loi)
    if re.match(r'^\d{4}-\d+$', n):     return "Arrêté"   # xxxx-x
    return current_type or ""

def make_slug(law: dict) -> str:
    """Convention : {type}-{number_clean}-{mots-clés-titre}."""
    current_type = (law.get("type") or "").strip()
    number_raw   = law.get("number") or ""
    # Tenter d'inférer le vrai type depuis le numéro si type générique
    inferred     = _infer_type_from_number(_clean_number(number_raw), current_type)
    raw_type     = _s(inferred or current_type or "")
    # Toujours exclure les types génériques du slug
    type_slug    = "" if raw_type in _GENERIC_TYPES else raw_type
    number_raw  = law.get("number") or ""
    # Ignorer les IDs internes adala dans le slug
    if re.match(r'^adala-[0-9a-f]+$', number_raw.lower()) or not number_raw:
        number_slug = ""
    else:
        number_slug = _s(_clean_number(number_raw))
    title       = (law.get("title_fr") or "").strip()
    date        = (law.get("date") or "")

    # Tokens à exclure des keywords : type + number + stopwords
    type_tokens = set(raw_type.split("-"))
    num_tokens  = set(number_slug.split("-")) if number_slug else set()
    excluded    = STOPWORDS | type_tokens | num_tokens | {''}

    words = re.sub(r"[^a-zA-Z\xc0-\xff0-9\s]", " ", title).lower().split()
    keywords = []
    for w in words:
        sw = _s(w)
        if sw and w not in excluded and sw not in excluded and len(w) > 2 and not re.match(r'^\d+$', sw):
            keywords.append(sw)
        if len(keywords) >= 6:
            break

    # Ajouter l'année depuis le champ date (important pour loi de finances, etc.)
    year = ""
    if date:
        m = re.match(r"(\d{4})", str(date))
        if m:
            year = m.group(1)
    if year and year not in keywords:
        keywords.append(year)

    kw_slug = "-".join(keywords)

    parts = [p for p in [type_slug, number_slug, kw_slug] if p]
    slug  = re.sub(r"-+", "-", "-".join(parts)).strip("-")[:100]
    return slug or f"sans-titre-{law.get('id', 'unknown')[:8]}"

def is_bad(slug: str) -> bool:
    """Slug non conforme : majuscules, ou préfixe générique sans valeur SEO."""
    if not slug:
        return False
    if any(c not in ALLOWED for c in slug):
        return True  # Caractères invalides (majuscules, accents)
    if slug.startswith("texte-juridique-") or slug.startswith("texte-reglementaire-"):
        return True  # Type générique sans valeur SEO
    return False

# ─── Supabase ─────────────────────────────────────────────────────────────────

def fetch_all() -> list:
    rows, offset = [], 0
    while True:
        r = requests.get(f"{URL}/rest/v1/laws",
            headers={**H, "Range": f"{offset}-{offset+999}"},
            params={"select": "id,number,title_fr,type,canonical_slug,date"},
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

    def _has_real_title(x):
        t = (x.get("title_fr") or "").strip()
        if not t: return False
        # Placeholder adala → pas encore de vrai titre, skip
        if re.match(r'^Texte\s+N[°o]?\s+adala-[0-9a-f]+\s*$', t, re.IGNORECASE): return False
        # Titre = juste chiffres → skip
        if re.match(r'^[\d\s\-_\.]+$', t): return False
        return True

    bad = [x for x in rows if is_bad(x.get("canonical_slug", "")) and _has_real_title(x)]
    print(f"  {len(bad)} slugs non conformes détectés (titres valides uniquement)\n")

    if args.limit:
        bad = bad[:args.limit]

    ok, errors, skipped = 0, 0, 0
    print(f"{'Avant':<50} {'Après':<60} Status")
    print("-" * 125)

    # Garder trace des slugs déjà générés dans cette session (évite doublons en lot)
    seen_in_session = set()

    for x in bad:
        old_slug = x.get("canonical_slug", "")
        # Inférer le vrai type depuis le numéro si le type DB est générique
        inferred_type = _infer_type_from_number(
            _clean_number(x.get("number") or ""),
            x.get("type") or ""
        )
        new_slug = _make_slug_full(
            inferred_type or x.get("type") or "",
            x.get("number") or "",
            x.get("title_fr") or "",
            x.get("date") or "",
        )

        # Rejeter si le slug généré est trop court ou ressemble à un hash seul
        if len(new_slug) < 4 or re.match(r'^[0-9a-f]{6,}$', new_slug):
            skipped += 1
            print(f"  {'[SKIP hash/court]':<50} {new_slug:<60} → SKIP")
            continue

        # Rejeter si le nouveau slug n'a pas de type identifiable — ambiguë sans contexte
        # (ex: "declaration-patrimoine" seul ne dit pas si c'est loi/dahir/circulaire)
        has_type = any(new_slug.startswith(t + "-")
                       for t in ["dahir","decret","loi","arrete","circulaire","rapport",
                                 "lettre-royale","discours-royal","message-royal","avis","code"])
        has_number = bool(re.search(r'-\d+-\d', new_slug))  # contient un numéro
        if not has_type and not has_number:
            skipped += 1
            print(f"  {'[SKIP sans type]':<50} {new_slug:<60} → SKIP (besoin IA)")
            continue

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
