"""
veille_sources.py — Configuration des sources surveillées (URLs vérifiées)
==========================================================================
Toutes les URLs ont été testées et validées le 2026-06-22.
"""

# Sources avec URLs vérifiées et fonctionnelles
SOURCES = [

    # ── Tier 1 — Sources primaires ────────────────────────────────────────────

    {
        "id":    "sgg_home",
        "label": "SGG — Page d'accueil (BOs récents)",
        "url":   "https://www.sgg.gov.ma/arabe/Accueil.aspx",
        "type":  "bo_home",
        "freq":  "daily",
        "mode":  "auto",   # SGG = source officielle de référence → auto
        "selectors": {"pdf": "a[href*='/BO/']"},
        "base_url": "https://www.sgg.gov.ma",
        "active": True,
    },
    {
        "id":    "sgg_bo_increment",
        "label": "SGG — BOs par numéro incrémental",
        "url":   "https://www.sgg.gov.ma/BO/FR/",
        "type":  "bo_increment",
        "freq":  "daily",
        "mode":  "auto",   # SGG incrémental → fiabilité maximale → auto
        # URL template : https://www.sgg.gov.ma/BO/FR/{year}/BO_{number}_Fr.pdf
        "bo_url_fr": "https://www.sgg.gov.ma/BO/FR/{year}/BO_{number}_Fr.pdf",
        "bo_url_ar": "https://www.sgg.gov.ma/BO/AR/{year}/BO_{number}_Ar.pdf",
        "start_bo":  7500,   # numéro de départ (mis à jour par veille_state.json)
        "active": True,
    },
    {
        "id":    "adala",
        "label": "Adala Justice — Textes juridiques",
        "url":   "https://adala.justice.gov.ma/",
        "type":  "pdf_list",
        "freq":  "weekly",
        "mode":  "semi",   # Adala : fiable mais titres parfois en format arabe → validation
        "selectors": {"list": "a[href*='/api/uploads/']"},
        "base_url": "https://adala.justice.gov.ma",
        "active": True,
    },

    # ── Tier 2 — Ministères (URLs vérifiées) ─────────────────────────────────

    {
        "id":    "finances",
        "label": "Ministère des Finances — Textes juridiques",
        "url":   "https://www.finances.gov.ma/fr/Pages/Textes-juridiques.aspx",
        "type":  "pdf_list",
        "freq":  "weekly",
        "mode":  "semi",   # Finances : bonne source mais périmètre variable
        "selectors": {"list": "a[href$='.pdf']"},
        "base_url": "https://www.finances.gov.ma",
        "active": True,
    },
    {
        "id":    "lof",
        "label": "Loi Organique des Finances (LOF)",
        "url":   "https://lof.finances.gov.ma/",
        "type":  "pdf_list",
        "freq":  "monthly",
        "mode":  "auto",   # LOF : périmètre très bien défini → auto
        "selectors": {"list": "a[href$='.pdf']"},
        "base_url": "https://lof.finances.gov.ma",
        "active": True,
    },

    # ── Tier 3 — Régulateurs (URLs vérifiées) ────────────────────────────────

    {
        "id":    "bkam",
        "label": "Bank Al-Maghrib — Recueil des textes",
        "url":   "https://www.bkam.ma/Supervision-bancaire/Recueil-des-textes-legislatifs-et-reglementaires",
        "type":  "pdf_list",
        "freq":  "monthly",
        "mode":  "semi",   # BKAM : fiable, mais textes souvent bilingues complexes
        "selectors": {"list": "a[href$='.pdf']"},
        "base_url": "https://www.bkam.ma",
        "active": True,
    },
    {
        "id":    "anrt_lois_telecom",
        "label": "ANRT — Lois Télécommunications",
        "url":   "https://www.anrt.ma/reglementation/lois/telecommunications",
        "type":  "pdf_list",
        "freq":  "monthly",
        "mode":  "semi",
        "selectors": {"list": "a[href$='.pdf']"},
        "base_url": "https://www.anrt.ma",
        "active": True,
    },
    {
        "id":    "anrt_lois_autres",
        "label": "ANRT — Autres lois",
        "url":   "https://www.anrt.ma/reglementation/lois/autres-lois",
        "type":  "pdf_list",
        "freq":  "monthly",
        "mode":  "semi",
        "selectors": {"list": "a[href$='.pdf']"},
        "base_url": "https://www.anrt.ma",
        "active": True,
    },
    {
        "id":    "anrt_decrets",
        "label": "ANRT — Décrets réglementaires",
        "url":   "https://www.anrt.ma/reglementation/decrets-reglementaires/telecommunications",
        "type":  "pdf_list",
        "freq":  "monthly",
        "mode":  "semi",
        "selectors": {"list": "a[href$='.pdf']"},
        "base_url": "https://www.anrt.ma",
        "active": True,
    },
    {
        "id":    "cndp",
        "label": "CNDP — Textes fondateurs",
        "url":   "https://www.cndp.ma/commission/textes-fondateurs.html",
        "type":  "pdf_list",
        "freq":  "monthly",
        "mode":  "semi",
        "selectors": {"list": "a[href$='.pdf']"},
        "base_url": "https://www.cndp.ma",
        "active": True,
    },
    {
        "id":    "mcinet",
        "label": "Ministère du Commerce — Textes juridiques",
        "url":   "https://www.mcinet.gov.ma/fr/content/textes-juridiques",
        "type":  "pdf_list",
        "freq":  "monthly",
        "mode":  "semi",   # Commerce : périmètre commercial bien défini
        "selectors": {"list": "a[href$='.pdf'], a[href$='.PDF']"},
        "base_url": "https://www.mcinet.gov.ma",
        "active": True,
    },

    # ── Tier 4 — Sources ajoutées après audit 2026-06-28 ─────────────────────

    {
        "id":    "sgg_consolid",
        "label": "SGG — Textes consolidés",
        "url":   "https://www.sgg.gov.ma/textesconsolides.aspx",
        "type":  "pdf_list",
        "freq":  "monthly",
        "mode":  "auto",   # Textes consolidés SGG = très haute fiabilité
        "selectors": {"list": "a[href$='.pdf']"},
        "base_url": "https://www.sgg.gov.ma",
        "active": True,
    },
    {
        "id":    "loi_finances",
        "label": "Ministère des Finances — Lois de finances",
        "url":   "https://www.finances.gov.ma/fr/vous-orientez/Pages/lois-finances.aspx",
        "type":  "pdf_list",
        "freq":  "monthly",
        "mode":  "manual",  # Filtres complexes → validation manuelle recommandée
        "selectors": {"list": "a[href$='.pdf']"},
        "base_url": "https://www.finances.gov.ma",
        # Exclure rapports de performance (pdp_*), notes budgétaires, circulaires.
        # Accepter uniquement les vraies lois de finances : PLF*, LF*, loi*finances*, loi-de-finances*
        "url_filter": r"(?i)(PLF|LF_|loi.?finances|loi.?de.?finances|loi-finances|\bLF\d)",
        "url_exclude": r"(?i)(pdp_|Tome\d|dep_fisc|nrri|segma|foncier|lettre_cadrage|Circ_CG|note_|Synth|Rapport_PB|Genre|reprtition|np_fr|ncc_fr)",
        "active": True,
    },
]

# Lookup rapide par id
SOURCES_BY_ID = {s["id"]: s for s in SOURCES}

# Sources désactivées — audit 2026-06-28
# Légende : JS = requiert navigateur headless (Playwright), 403 = accès bloqué
SOURCES_OFFLINE = [
    {
        "id": "cdr",
        "label": "Chambre des représentants",
        "reason": "Rendu JS — 0 PDF accessible statiquement. Nécessite Playwright.",
        "urls_tested": [
            "https://www.chambredesrepresentants.ma/fr/legislation/projets-de-loi",
            "https://www.chambredesrepresentants.ma/fr/legislation/propositions-de-loi",
            "https://www.chambredesrepresentants.ma/fr/legislation/textes-votes-chambre-representants",
        ],
        "fix": "Implémenter un adapter Playwright pour rendre le JS avant extraction PDF.",
    },
    {
        "id": "emploi",
        "label": "Ministère de l'Emploi",
        "reason": "403 Forbidden — accès bloqué par le serveur.",
        "urls_tested": ["https://www.emploi.gov.ma/fr/"],
        "fix": "Rotation User-Agent ou scraping via cache Google/archive.org.",
    },
    {
        "id": "sante",
        "label": "Ministère de la Santé",
        "reason": "Page textes juridiques introuvable. Page d'accueil accessible (200) mais 1 seul PDF non juridique.",
        "urls_tested": ["https://www.sante.gov.ma/Pages/Textes-juridiques.aspx", "https://www.sante.gov.ma/"],
        "fix": "Trouver la nouvelle URL de la rubrique textes juridiques.",
    },
    {
        "id": "mem",
        "label": "Ministère de l'Énergie et des Mines",
        "reason": "Page textes juridiques introuvable (404). Accueil accessible mais 0 PDF.",
        "urls_tested": ["https://www.mem.gov.ma/fr/Pages/Textes-juridiques.aspx", "https://www.mem.gov.ma/"],
        "fix": "Trouver la nouvelle URL de la rubrique textes juridiques sur mem.gov.ma.",
    },
    {
        "id": "environnement",
        "label": "Ministère de l'Environnement",
        "reason": "403 Forbidden sur toutes les URLs testées.",
        "urls_tested": ["https://www.environnement.gov.ma/", "https://www.environnement.gov.ma/fr/"],
        "fix": "Scraping indirect via SGG (BO) ou cache.",
    },
    {
        "id": "interieur",
        "label": "Ministère de l'Intérieur",
        "reason": "DNS introuvable (mininterieur.gov.ma). URL officielle à confirmer.",
        "urls_tested": [],
        "fix": "Vérifier l'URL officielle sur le portail du gouvernement marocain.",
    },
    {
        "id": "agriculture",
        "label": "Ministère de l'Agriculture",
        "reason": "Rendu JS — page textes juridiques accessible (200) mais 0 PDF extrait statiquement.",
        "urls_tested": ["https://www.agriculture.gov.ma/fr/Pages/textes-juridiques.aspx"],
        "fix": "Implémenter un adapter Playwright.",
    },
    {
        "id": "ammc",
        "label": "AMMC — Autorité des Marchés des Capitaux",
        "reason": "Rendu JS — page réglementation accessible mais 0 PDF extrait.",
        "urls_tested": ["https://www.ammc.ma/fr/reglementation"],
        "fix": "Implémenter un adapter Playwright.",
    },
    {
        "id": "ism",
        "label": "Institut Supérieur de la Magistrature",
        "reason": "Rendu JS — page textes juridiques accessible (200) mais 0 PDF extrait.",
        "urls_tested": ["https://www.ism.ma/fr/textes-juridiques"],
        "fix": "Implémenter un adapter Playwright.",
    },
    {
        "id": "wipo",
        "label": "WIPO — Wipolex Maroc",
        "reason": "Structure changée — anciennes URLs inexistantes (404).",
        "urls_tested": ["https://www.wipo.int/wipolex/en/members/MA"],
        "fix": "Trouver la nouvelle URL Wipolex pour le Maroc.",
    },
]

# Détection domaine par mots-clés dans le titre
DOMAIN_KEYWORDS = {
    "civil":              ["civil", "obligations", "contrats", "propriété", "succession", "famille", "mariage"],
    "penal":              ["pénal", "criminel", "sanctions", "infractions", "prison", "correctionnel"],
    "commercial":         ["commercial", "sociétés", "entreprises", "commerce", "fonds de commerce", "SARL", "SA"],
    "administratif":      ["administratif", "administration", "fonction publique", "fonctionnaires", "marchés publics"],
    "travail":            ["travail", "emploi", "salarié", "licenciement", "SMIG", "syndicat", "convention collective"],
    "fiscal":             ["fiscal", "impôt", "TVA", "IS", "IR", "douane", "taxe", "CGI"],
    "constitutionnel":    ["constitution", "constitutionnel", "droits fondamentaux", "libertés"],
    "collectivites":      ["commune", "région", "collectivité", "territoriale", "province", "arrondissement"],
    "finances_publiques": ["finances publiques", "budget", "LOF", "comptabilité publique", "trésorerie"],
    "bancaire":           ["bancaire", "banque", "crédit", "financier", "assurance", "BKAM", "capitaux"],
    "environnement":      ["environnement", "eau", "déchets", "pollution", "carrières", "mines"],
    "energie":            ["énergie", "électricité", "renouvelable", "pétrolier", "mines"],
    "numerique":          ["numérique", "digital", "télécom", "données personnelles", "cybersécurité", "ANRT"],
    "urbanisme":          ["urbanisme", "construction", "lotissement", "permis", "foncier", "agence urbaine"],
    "international":      ["international", "traité", "convention", "extradition", "diplomatique"],
    "sante":              ["santé", "médecine", "pharmacie", "médicament", "hôpital", "clinique"],
}


def guess_domain(title_fr: str, title_ar: str = "") -> str:
    text = (title_fr + " " + title_ar).lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw.lower() in text for kw in keywords):
            return domain
    return "administratif"
