"""
slug_utils.py — Fonction partagée make_slug_from_law
Importée par fix_imported_titles.py et fix_bad_slugs.py.
"""
import re, unicodedata as _ud

_GENERIC_TYPES = {
    'texte-juridique', 'texte-reglementaire', 'texte', 'document', 'autre',
}

_SLUG_STOP = {
    'le','la','les','du','de','des','au','aux','et','ou','un','une',
    'n','no','par','sur','en','dans','pour','avec','sans',
    '1er','2eme','3eme','ier','ieme','premier','deuxieme','troisieme',
    'relatif','relative','relatifs','relatives',
    'portant','fixant','instituant','modifiant','abrogeant','approuvant',
    'promulgation','promulguant','application',
    'dahir','decret','loi','arrete','circulaire','texte','ordonnance',
    'code','reglement','avis','bulletin','projet','cadre',
    'sgg','adala','portail','officiel','journal',
    'muharram','safar','rabia','rabii','rabii','joumada','joumad','rajab','chaabane','ramadan',
    'chaoual','doulkaada','doulhijja','hija','hijja','moharrem','moharram','hicham',
    'jumada','rabi','safar',
    'juillet','janvier','fevrier','mars','avril','mai','juin',
    'aout','septembre','octobre','novembre','decembre',
    'juridique','reglementaire','legislatif','administratif',
    # Artefacts noms de fichiers
    'pdf','vf','vaf','fr','ar','doc','docx','version','consolide',
    'final','def','draft','ver','rev','copy','copie','var','num',
}

_BIGRAMS = [
    ('loi', 'organique'), ('donnees', 'personnelles'), ('droit', 'international'),
    ('cour', 'supreme'), ('cour', 'constitutionnelle'), ('haute', 'autorite'),
    ('conseil', 'superieur'), ('conseil', 'constitutionnel'), ('conseil', 'economique'),
    ('collectivites', 'territoriales'), ('marches', 'publics'), ('code', 'penal'),
    ('code', 'civil'), ('code', 'commerce'), ('code', 'travail'), ('code', 'famille'),
]


def _s(t: str) -> str:
    """Slugifie un token : minuscules, sans accents, caractères non-alphanumériques → tirets."""
    norm = _ud.normalize("NFD", (t or "").lower())
    norm = "".join(c for c in norm if _ud.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", norm).strip("-")


def make_slug_from_law(law_type: str, number: str, title_fr: str, date: str = "") -> str:
    """
    Génère un slug SEO complet : {type}-{number}-{prom_slug}-{keywords}-{year}

    Règles :
    - Types génériques (texte-juridique…) exclus
    - IDs internes adala exclus
    - Numéros artificiels year-index exclus
    - Loi promulguée extraite du titre (dahir portant promulgation loi n°…)
    - Bigrams importants préservés (loi-organique, données-personnelles…)
    - 8 mots-clés max
    - Année depuis date si absente du numéro
    - Longueur max 120 caractères
    """
    # ── Numéro ──────────────────────────────────────────────────────────────────
    raw_num = (number or "").strip()
    if re.match(r'^adala-[0-9a-f]+$', raw_num.lower()) or not raw_num:
        clean_num = ""
    else:
        m = re.search(r'(\d[\d\.\-/]+)', raw_num)
        clean_num = re.sub(r'[.\s/]+', '-', m.group(1)).strip('-') if m else _s(raw_num)

    # Numéros artificiels type "1997-1" → pas de sens dans slug
    if re.match(r'^(19|20)\d{2}-\d{1,2}$', clean_num or ''):
        clean_num = ""

    # ── Type ────────────────────────────────────────────────────────────────────
    raw_type_slug = _s(law_type or "")
    type_slug = "" if raw_type_slug in _GENERIC_TYPES else raw_type_slug

    # Éviter la répétition si le numéro contient déjà le type (ex: "loi-concurrence")
    if clean_num and type_slug and _s(clean_num).startswith(type_slug + "-"):
        clean_num = _s(clean_num)[len(type_slug) + 1:]

    number_slug = _s(clean_num)

    # ── Loi promulguée ──────────────────────────────────────────────────────────
    promulgated_num = ""
    promulgated_organic = False
    title_lower = (title_fr or "").lower()

    m_org = re.search(r'loi\s+organique\s+n[°o°]?\s*([\d][\d\.\-/]+)', title_lower)
    if m_org:
        promulgated_organic = True
        promulgated_num = re.sub(r'[.\s/]+', '-', m_org.group(1)).strip('-')
    else:
        m_prom = re.search(r'(?:promulgation\s+(?:de\s+)?)?loi\s+n[°o°]?\s*([\d][\d\.\-/]+)', title_lower)
        if m_prom:
            promulgated_num = re.sub(r'[.\s/]+', '-', m_prom.group(1)).strip('-')

    prom_slug = ""
    is_dahir = raw_type_slug in ('dahir', 'decret', 'arrete')
    if promulgated_num and promulgated_num != clean_num and is_dahir:
        prom_slug = ("loi-organique-" if promulgated_organic else "loi-") + _s(promulgated_num)

    # ── Keywords du titre ───────────────────────────────────────────────────────
    type_tokens = set(raw_type_slug.split("-"))
    num_tokens  = set(number_slug.split("-")) if number_slug else set()
    prom_tokens = set(prom_slug.split("-")) if prom_slug else set()
    excluded    = _SLUG_STOP | type_tokens | num_tokens | prom_tokens | {''}

    words  = re.sub(r"[^a-zA-Z\xc0-\xff0-9\s]", " ", title_fr or "").lower().split()
    slugged = [_s(w) for w in words]
    keywords = []
    i = 0
    while i < len(slugged) and len(keywords) < 8:
        sw = slugged[i]
        # Bigram
        if i + 1 < len(slugged):
            bigram = (sw, slugged[i + 1])
            if bigram in _BIGRAMS and sw not in excluded:
                keywords.append(f"{sw}-{slugged[i+1]}")
                i += 2
                continue
        if sw and sw not in excluded and len(sw) > 2 and not re.match(r'^\d+$', sw):
            keywords.append(sw)
        i += 1

    # ── Année ───────────────────────────────────────────────────────────────────
    year = ""
    if date:
        m = re.match(r"(\d{4})", str(date))
        if m:
            year = m.group(1)
    existing = number_slug + "-" + prom_slug
    if year and year not in keywords and year not in existing:
        keywords.append(year)

    # ── Assemblage ──────────────────────────────────────────────────────────────
    parts = [p for p in [type_slug, number_slug, prom_slug, "-".join(keywords)] if p]
    slug  = re.sub(r"-+", "-", "-".join(parts)).strip("-")[:120]
    return slug or f"texte-{number_slug or 'inconnu'}"
