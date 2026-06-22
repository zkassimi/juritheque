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
        "selectors": {"list": "a[href$='.pdf'], a[href$='.PDF']"},
        "base_url": "https://www.mcinet.gov.ma",
        "active": True,
    },
]

# Lookup rapide par id
SOURCES_BY_ID = {s["id"]: s for s in SOURCES}

# Sources désactivées temporairement (URL incorrecte ou accès bloqué)
SOURCES_OFFLINE = [
    {"id": "cdr",           "reason": "URL introuvable — structure du site changée"},
    {"id": "emploi",        "reason": "403 Forbidden"},
    {"id": "sante",         "reason": "404 — URL changée"},
    {"id": "mem",           "reason": "404 — URL changée"},
    {"id": "environnement", "reason": "404 — URL changée"},
    {"id": "interieur",     "reason": "DNS introuvable"},
    {"id": "agriculture",   "reason": "404 — URL changée"},
    {"id": "ammc",          "reason": "404 — URL changée"},
    {"id": "ism",           "reason": "404 — URL changée"},
    {"id": "wipo",          "reason": "404/403 — structure changée"},
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
