"""
JuriThèque Web Scraper
═══════════════════════════════════════════════════════════════════
Scrape official Moroccan legal websites and feed content into
the JuriThèque database (same Supabase structure as extract.py).

Supported sources:
  --source sgg         → sgg.gov.ma           Textes consolidés         (~63 PDFs)
  --source sgg-lois    → sgg.gov.ma           Lois importantes          (~74 PDFs)
  --source mmsp        → mmsp.gov.ma          Fonction publique         (~47 PDFs)
  --source anrt        → anrt.ma              Télécom & numérique       (~33 PDFs)
  --source bkam        → bkam.ma              Réglementation bancaire   (~68 PDFs)
  --source finances    → lof/mef/dgi/cdr      Finances publiques, CGI   (~72 PDFs)
  --source cdr         → chambredesrepresentants.ma  Projets de loi     (~27 PDFs)
  --source mem         → mem.gov.ma           Énergie, mines, EnR       (~88 PDFs)
  --source environnement → environnement.gov.ma  Droit de l'environnement (~55 PDFs)
  --source wipo        → wipolex/unodc/maroclear  PI, commerce, codes   (~18 PDFs)
  --source ism         → ism.ma              ISM — 13 domaines en arabe (~170 PDFs)
  --source all         → Toutes les sources ci-dessus                  (~706 PDFs)
  --source adala       → justice.gov.ma       Textes HTML
  --source ilo         → ilo.org/natlex       Droit du travail (HTML)

Usage:
  python scraper.py --source bkam                  # Réglementation bancaire
  python scraper.py --source mem                   # Énergie & mines
  python scraper.py --source environnement         # Droit environnemental
  python scraper.py --source cdr                   # Projets de loi CDR
  python scraper.py --source all                   # Tout télécharger
  python scraper.py --source sgg --dry-run         # Preview, aucun téléchargement
  python scraper.py --source bkam --limit 20       # Max 20 PDFs

Requirements:
  pip install requests beautifulsoup4 httpx python-dotenv rich lxml
"""

import os, sys, re, time, json, hashlib
from pathlib import Path
from datetime import datetime
import httpx
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich import print as rprint

load_dotenv()
console = Console()

# ── Config ────────────────────────────────────────────────────────────────────
SUPABASE_URL  = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY  = os.getenv("SUPABASE_SERVICE_KEY", "")
DRY_RUN       = "--dry-run" in sys.argv
LIMIT         = int(next((sys.argv[sys.argv.index("--limit") + 1] for i, a in enumerate(sys.argv) if a == "--limit"), 9999))
YEAR_FILTER   = next((sys.argv[sys.argv.index("--year") + 1] for i, a in enumerate(sys.argv) if a == "--year"), None)
SOURCE        = next((sys.argv[sys.argv.index("--source") + 1] for i, a in enumerate(sys.argv) if a == "--source"), "adala")
DELAY         = 1.5   # seconds between requests (be polite)
PDF_FOLDER    = Path("./pdfs")
PDF_FOLDER.mkdir(exist_ok=True)

HEADERS_SB = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; JuriTheque-Bot/1.0; +https://juritheque.com)",
    "Accept-Language": "fr-MA,fr;q=0.9,ar;q=0.8",
}

# ── Supabase helpers ──────────────────────────────────────────────────────────
def sb_exists(number: str) -> bool:
    """Return True if a law with this number already exists."""
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS_SB,
        params={"number": f"eq.{number}", "select": "id", "limit": "1"},
        timeout=10,
    )
    return len(r.json()) > 0

def sb_insert(record: dict) -> dict:
    r = httpx.post(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS_SB,
        json=record,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()[0] if r.json() else {}

# ── Type detector ─────────────────────────────────────────────────────────────
def detect_type(title: str) -> str:
    t = title.lower()
    if "dahir"       in t: return "Dahir"
    if "décret"      in t: return "Décret"
    if "arrêté"      in t: return "Arrêté"
    if "circulaire"  in t: return "Circulaire"
    if "loi"         in t: return "Loi"
    if "ordonnance"  in t: return "Ordonnance"
    if "code"        in t: return "Code"
    return "Loi"

def detect_domain(title: str) -> str:
    t = title.lower()
    if any(w in t for w in ["travail","emploi","salarié","syndi"]): return "travail"
    if any(w in t for w in ["pénal","criminel","infraction","sanction","peine","prison"]): return "penal"
    if any(w in t for w in ["commercial","société","entreprise","commerce","concurrence",
                             "consommateur","marque","brevet","propriété industrielle",
                             "propriété intellectuelle","droit d'auteur","copyright"]): return "commercial"
    if any(w in t for w in ["fiscal","impôt","impot","taxe","tva","douane","cgi","contribuable",
                             "code général des impôts","code general des impots"]): return "fiscal"
    if any(w in t for w in ["loi de finances","loi organique","budget","dépense","recette",
                             "finances publiques","tresorerie","trésorerie","comptabilité publique",
                             "marches publics","marchés publics","contrôle financier",
                             "ordonnancement","programmation budgétaire","dette publique"]): return "finances_publiques"
    if any(w in t for w in ["administratif","fonction publique","collectivité","service public",
                             "mine","minier","carrière","hydrocarbure","énergie","électricité",
                             "renouvelable","masen","onee","pétrol","gaz","explosif"]): return "administratif"
    if any(w in t for w in ["environnement","pollution","déchet","déchets","air","eau","littoral",
                             "biodiversité","évaluation environnementale","éie","eie","forêt",
                             "milieu naturel","changement climatique"]): return "administratif"
    if any(w in t for w in ["civil","famille","mariage","divorce","héritage","succession",
                             "procédure civile","état civil","filiation"]): return "civil"
    if any(w in t for w in ["constitution","constitutionnel","parlement","organique"]): return "constitutionnel"
    if any(w in t for w in ["numérique","informatique","données","cyber","digital",
                             "télécom","communication","audiovisuel","internet"]): return "numerique"
    if any(w in t for w in ["international","traité","convention","accord"]): return "international"
    if any(w in t for w in ["bancaire","banque","crédit","paiement","monétaire","financier",
                             "microfinance","participatif","circulaire","wali","intérêt"]): return "bancaire"
    return "civil"

def clean_text(text: str) -> str:
    """Normalize whitespace."""
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

# ══════════════════════════════════════════════════════════════════════════════
# SOURCE 1 — adala.justice.gov.ma
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# SOURCE: mmsp.gov.ma — Ministère de la Transformation Numérique et Réforme Admin
# Fonction Publique : ~50 PDFs (Dahirs, Décrets, Circulaires, Lois)
# ══════════════════════════════════════════════════════════════════════════════

BASE_MMSP = "https://mmsp.gov.ma"

MMSP_PDF_URLS = [
    # ── Statut Général de la Fonction Publique ──────────────────────────────
    f"{BASE_MMSP}/sites/default/files/2024-09/SGFP_06092024_Ar.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/Rapport_general_refonte_SGFP_ar.pdf",
    # ── Statuts particuliers ────────────────────────────────────────────────
    f"{BASE_MMSP}/sites/default/files/2025-03/ListeStatutsParticuliers_07032025_Ar.pdf",
    # ── Recrutement / التوظيف ────────────────────────────────────────────────
    f"{BASE_MMSP}/sites/default/files/2022-05/article_31_constitution.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_02_349_0.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_92_231_0.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_11_621_0.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/circulaire_14_2012_0.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_12_90_0.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/loi_cadre_97_13.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/Circulaire_CG_N132017_0.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_01_96.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_01_94.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/Decret_N_2-17-635_24092018_Ar.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_64_389.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_15_770_0.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/circulaire_9_2009_0.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/arretes-contractualisation-BO3.pdf_0.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/arretes-contractualisation-BO1.pdf_0.pdf",
    # ── Promotion / الترقي ──────────────────────────────────────────────────
    f"{BASE_MMSP}/sites/default/files/2022-12/Decret_N_2-04-403_23122022.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/circulaire_2_2006.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/circulaire_2_2007.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/circulaire_9_11.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_62_344.pdf",
    # ── Régime disciplinaire / النظام التأديبي ───────────────────────────────
    f"{BASE_MMSP}/sites/default/files/2024-09/ExtraitsDahir_N_1-58-008_13092024_Ar.pdf",
    f"{BASE_MMSP}/sites/default/files/2024-09/Regime%20disciplinaire_13092024_Ar.pdf",
    f"{BASE_MMSP}/sites/default/files/2024-09/Loi_N_12-81_13092024_Ar.pdf",
    f"{BASE_MMSP}/sites/default/files/2024-09/Decret_N_2-99-1216_18092024_Ar.pdf",
    f"{BASE_MMSP}/sites/default/files/2024-09/Circulaire_N_26-2012_18092024.pdf",
    # ── Congés / الرخص ──────────────────────────────────────────────────────
    f"{BASE_MMSP}/sites/default/files/2024-09/CirculaireChefGouvernement_N_8.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_99_1219.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/circulaire_5_11.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2-05-01_fr.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/circulaire_3_2015.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/circulaire_12_1979.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_99_1215.pdf",
    # ── Mobilité / الحركية ───────────────────────────────────────────────────
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_13_436.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/circulaire_1_2016.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_99_1218.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_13_422.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_13_423.pdf",
    # ── Notation & Évaluation / التنقيط والتقييم ─────────────────────────────
    f"{BASE_MMSP}/sites/default/files/2022-05/decret_2_05_1367.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/arrete_1725_06.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/guide_notation.pdf",
    # ── Sécurité sociale / الاحتياط الاجتماعي ────────────────────────────────
    f"{BASE_MMSP}/sites/default/files/2022-05/loi_011_71.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/loi_72_14.pdf",
    f"{BASE_MMSP}/sites/default/files/2022-05/loi_013_71.pdf",
]


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE: anrt.ma — Agence Nationale de Réglementation des Télécommunications
# Numérique, télécom, cybersécurité, données personnelles (~38 PDFs)
# ══════════════════════════════════════════════════════════════════════════════

BASE_ANRT = "https://www.anrt.ma"

ANRT_PDF_URLS = [
    # ── Lois télécommunications ─────────────────────────────────────────────
    f"{BASE_ANRT}/sites/default/files/2024-09/Loi%2024-96%20consolid%C3%A9e%20%28site%20web%20anrt%29%20-2019%20%20%20-%20V7%20compil%C3%A9e.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/loi_121.12_modifiant_loi_24.96_vf_0.pdf",
    f"{BASE_ANRT}/sites/default/files/2013-1-13-57-93-12-24-96-loi-telecom-fr_0.pdf",
    f"{BASE_ANRT}/sites/default/files/2011-1-11-86-59-10-24-96-loi-telecom-fr.pdf",
    f"{BASE_ANRT}/sites/default/files/2007-1-07-43-29-06-24-96-loi-telecom-fr_0.pdf",
    f"{BASE_ANRT}/sites/default/files/2004-1-04-154-55-01-24-96-loi-telecom-fr.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/2001-1-01-123-79-99-24-96-fr-loi-telecom%20%281%29.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/1997-1-97-162-24-96-loi-telecom-fr.pdf",
    # ── Autres lois (cybersécurité, données perso, concurrence, audiovisuel) ─
    f"{BASE_ANRT}/sites/default/files/2024-06/loi%2040.21%20modifiant%20et%20compl%C3%A9tant%20la%20loi%20n%20104-12relative%20%C3%A0%20la%20libert%C3%A9%20des%20prix%20et%20de%20la%20concurrence.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/loi_16.18_modifiant_la_loi_77.03_relative_a_la_communication_audiovisuelle_vf.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/loi_05-20_cybersecurite_fr.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/loi-haca.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/loi-_com-audiosuelle-fr.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/la_loi_96-14_modifiant_et_completant_la_loi_77-03_fr.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/loi-concurrence.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/2011-1-11-03-31-08-protec-conso-fr.pdf",
    f"{BASE_ANRT}/sites/default/files/2009-1-09-15-09-08-protec-pers-physique-donnees-caractere-personnel-fr_0.pdf",
    f"{BASE_ANRT}/sites/default/files/2007-1-07-129-53-05-echang-elect-donnees-jurid-fr.pdf",
    # ── Décrets réglementaires ──────────────────────────────────────────────
    f"{BASE_ANRT}/sites/default/files/2022-02/decret_relatif_a_la_procedures_de_traitement_de_litiges-2-05-772-version_consolidee.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/decret_1026_version.consolide.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/decret_1025_version.consolide.pdf",
    f"{BASE_ANRT}/sites/default/files/2024-07/decret_1024_consolide-_vf-3-7-24__0.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/2016-2-16-800-pnf-fr.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/decret_2-16-347_revision_du_decret_2-05-772_-_mai_2016_bo-fr.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-02/decret_2-05-772_-_litiges_et_saisines_-_juillet_2005_bo_fr.pdf",
    # ── Arrêtés ─────────────────────────────────────────────────────────────
    f"{BASE_ANRT}/sites/default/files/2024-07/arrete-modif_liste_sva-vf.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-03/arrete_2045-18_redevance_frequence_-_vffr_mention_bo.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-03/arrete_2045-18_frequence_vf_bo.pdf",
    f"{BASE_ANRT}/sites/default/files/2024-06/2016-3291-16-redevance-frequences-fr.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-03/2012-1604-12-redev-assign-freq-radio-fr.pdf",
    f"{BASE_ANRT}/sites/default/files/2024-06/2008-977-08-mod-promot-service-telecom-fr.pdf",
    f"{BASE_ANRT}/sites/default/files/2022-03/2008-623-08-redev-assign-freq-radio-fr_0.pdf",
]


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE: bkam.ma — Bank Al-Maghrib (Réglementation bancaire & financière)
# Lois bancaires, circulaires, arrêtés, banque participative (~68 PDFs)
# ══════════════════════════════════════════════════════════════════════════════

BASE_BKAM = "https://www.bkam.ma"

# List of (url, filename) tuples — explicit names for Liferay CMS URLs without .pdf
BKAM_PDF_URLS = [
    # ── Loi bancaire & textes fondamentaux ─────────────────────────────────
    (f"{BASE_BKAM}/content/download/757666/8545663/loi bancaire fr 22.pdf",
     "bkam_loi_103-12_bancaire.pdf"),
    (f"{BASE_BKAM}/content/download/746515/8468377/Dahir n%C2%B01-20-74 du 25 juillet 2020 portant promulgation de la loi n%C2%B044-20 modifiant et compl%C3%A9tant la loi n%C2%B0103-12.pdf",
     "bkam_dahir_1-20-74_loi-44-20.pdf"),
    (f"{BASE_BKAM}/content/download/746516/8468379/Dahir n%C2%B01-21-76 du 14 juillet 2021 portant promulgation de la loi n%C2%B050-20 relative %C3%A0 la microfinance.pdf",
     "bkam_dahir_1-21-76_loi-50-20_microfinance.pdf"),
    (f"{BASE_BKAM}/content/download/746517/8468381/Dahir n%C2%B01-21-77 du 14 juillet 2021 portant promulgation de la loi n%C2%B051-20.pdf",
     "bkam_dahir_1-21-77_loi-51-20.pdf"),
    (f"{BASE_BKAM}/content/download/746518/8468383/D%C3%A9cret n%C2%B0 2-17-31 du 27 septembre 2017.pdf",
     "bkam_decret_2-17-31_conseil-credit.pdf"),
    (f"{BASE_BKAM}/content/download/746519/8468385/D%C3%A9cret n%C2%B02-17-32 du 14 septembre 2017.pdf",
     "bkam_decret_2-17-32_comite-coord.pdf"),
    (f"{BASE_BKAM}/content/download/498911/4962989/decret_2-06-223.pdf",
     "bkam_decret_2-06-223.pdf"),
    (f"{BASE_BKAM}/content/download/498913/4962993/arrete_29-07.pdf",
     "bkam_arrete_29-07.pdf"),
    (f"{BASE_BKAM}/content/download/498914/4962995/arrete_30-07.pdf",
     "bkam_arrete_30-07.pdf"),
    (f"{BASE_BKAM}/content/download/498915/4962997/6%20-%20Arr%C3%AAt%C3%A9%20Associations%20de%20micro-cr%C3%A9dit.pdf",
     "bkam_arrete_31-07_microcredit.pdf"),
    (f"{BASE_BKAM}/content/download/498918/4963003/arrete_32-07_avoirs.pdf",
     "bkam_arrete_32-07_avoirs.pdf"),
    (f"{BASE_BKAM}/content/download/498916/4962999/7%20-%20Arr%C3%AAt%C3%A9%20banques%20offshore.pdf",
     "bkam_arrete_33-07_banques-offshore.pdf"),
    (f"{BASE_BKAM}/content/download/498917/4963001/8%20-%20Arr%C3%AAt%C3%A9%20transfert%20de%20fonds%20.pdf",
     "bkam_arrete_transfert-fonds.pdf"),
    # ── Recueil complet (170+ textes) ───────────────────────────────────────
    (f"{BASE_BKAM}/content/download/814412/8935685/Recueil des textes l%C3%A9gislatifs et r%C3%A9glementaires de BAM _ VF.pdf",
     "bkam_recueil_textes_legislatifs_2023.pdf"),
    # ── Banque participative ────────────────────────────────────────────────
    (f"{BASE_BKAM}/content/download/780551/8703992/directive n 7w2021 du 1er mars 2023 - avis CSO.pdf",
     "bkam_directive_7w2021_participatif.pdf"),
    (f"{BASE_BKAM}/content/download/746780/8469832/Circulaire n%C2%B01 W 2019.pdf",
     "bkam_circ_1w2019_participatif.pdf"),
    (f"{BASE_BKAM}/content/download/746686/8469237/Circulaire n%C2%B02 W 2019.pdf",
     "bkam_circ_2w2019_ijara.pdf"),
    (f"{BASE_BKAM}/content/download/746685/8469235/Circulaire n%C2%B0 16 W 16.pdf",
     "bkam_circ_16w16_conformite.pdf"),
    (f"{BASE_BKAM}/content/download/746684/8469233/Circulaire n%C2%B09 W 2018.pdf",
     "bkam_circ_9w2018_fonds-propres-risques.pdf"),
    (f"{BASE_BKAM}/content/download/746683/8469231/Circulaire n%C2%B03W2021.pdf",
     "bkam_circ_3w2021_fonds-propres.pdf"),
    (f"{BASE_BKAM}/content/download/746682/8469229/Circulaire n%C2%B010W2018.pdf",
     "bkam_circ_10w2018_fonds-propres-participatif.pdf"),
    (f"{BASE_BKAM}/content/download/746681/8469227/Circulaire n%C2%B04W2021.pdf",
     "bkam_circ_4w2021_fonds-propres.pdf"),
    (f"{BASE_BKAM}/content/download/512856/5154536/circulaire_3w17_participatif.pdf",
     "bkam_circ_3w17_banques-participatives.pdf"),
    (f"{BASE_BKAM}/content/download/512855/5154534/circulaire_2w17_depots.pdf",
     "bkam_circ_2w17_depots-participatifs.pdf"),
    (f"{BASE_BKAM}/content/download/512854/5154532/circulaire_1w17_produits.pdf",
     "bkam_circ_1w17_produits-participatifs.pdf"),
    # ── Activité des établissements de crédit ───────────────────────────────
    (f"{BASE_BKAM}/content/download/817419/8955908/", "bkam_circ_2w2024_paiement.pdf"),
    (f"{BASE_BKAM}/content/download/817418/8955906/", "bkam_circ_1w2024_art22.pdf"),
    (f"{BASE_BKAM}/content/download/761414/8571425/", "bkam_circ_2w2022_paiement.pdf"),
    (f"{BASE_BKAM}/content/download/761412/8571421/", "bkam_circ_1w2022_art22.pdf"),
    (f"{BASE_BKAM}/content/download/746522/8468391/", "bkam_circ_2w2018_offshore.pdf"),
    (f"{BASE_BKAM}/content/download/746521/8468389/", "bkam_circ_3w2018_microcredit.pdf"),
    (f"{BASE_BKAM}/content/download/746523/8468393/", "bkam_circ_8w16_capital.pdf"),
    (f"{BASE_BKAM}/content/download/746525/8468397/", "bkam_circ_7w16_paiement.pdf"),
    (f"{BASE_BKAM}/content/download/746524/8468395/", "bkam_circ_6w2016_art22.pdf"),
    (f"{BASE_BKAM}/content/download/746526/8468399/", "bkam_circ_30g2006_societes-financement.pdf"),
    (f"{BASE_BKAM}/content/download/499023/4963418/", "bkam_circ_20g2006_capital-min.pdf"),
    (f"{BASE_BKAM}/content/download/499027/4963426/", "bkam_circ_27g2006_conseil-admin.pdf"),
    (f"{BASE_BKAM}/content/download/499029/4963430/", "bkam_circ_39g2007_banques-etrangeres.pdf"),
    (f"{BASE_BKAM}/content/download/499028/4963428/", "bkam_circ_36g2004_bureaux-representation.pdf"),
    (f"{BASE_BKAM}/content/download/499025/4963422/", "bkam_circ_10g2012_transferts-fonds.pdf"),
    (f"{BASE_BKAM}/content/download/499024/4963420/", "bkam_circ_1g11_capital-modif.pdf"),
    (f"{BASE_BKAM}/content/download/499022/4963416/", "bkam_circ_5w2015_agrement.pdf"),
    (f"{BASE_BKAM}/content/download/499026/4963424/", "bkam_directive_3g12_intermediaires.pdf"),
    # ── Microfinance ────────────────────────────────────────────────────────
    (f"{BASE_BKAM}/content/download/778494/8689658/", "bkam_circ_5w2023_prov-microfinance.pdf"),
    (f"{BASE_BKAM}/content/download/778493/8689656/", "bkam_circ_4w2023_assoc-microfinance.pdf"),
    (f"{BASE_BKAM}/content/download/778492/8689654/", "bkam_circ_3w2023_loi50-20.pdf"),
    (f"{BASE_BKAM}/content/download/778491/8689652/", "bkam_circ_2w2023_imf-credit.pdf"),
    (f"{BASE_BKAM}/content/download/778490/8689650/", "bkam_circ_1w2023_capital-min.pdf"),
    # ── Systèmes et moyens de paiement ─────────────────────────────────────
    (f"{BASE_BKAM}/content/download/498836/4962757/Circulaire%20numro%205-G-97.pdf",
     "bkam_circ_5g97_cheques.pdf"),
    (f"{BASE_BKAM}/content/download/498837/4962759/Circulaire%20numero%206-G-97.pdf",
     "bkam_circ_6g97_incidents-paiement.pdf"),
    (f"{BASE_BKAM}/content/download/498838/4962761/Circulaire%2012G06.pdf",
     "bkam_circ_12g06_normalisation-cheque.pdf"),
    (f"{BASE_BKAM}/content/download/498839/4962763/decision_20G2007_LCN.pdf",
     "bkam_decision_20g2007_LCN.pdf"),
    (f"{BASE_BKAM}/content/download/498840/4962765/circulaire_1w15_effets-commerce.pdf",
     "bkam_circ_1w15_effets-commerce.pdf"),
    (f"{BASE_BKAM}/content/download/498841/4962767/circulaire_2w15_impayés.pdf",
     "bkam_circ_2w15_impayes.pdf"),
    (f"{BASE_BKAM}/content/download/498842/4962769/BO_6388_Fr_3_W_comptes_bancaires.pdf",
     "bkam_circ_3w15_comptes-bancaires.pdf"),
    (f"{BASE_BKAM}/content/download/498843/4962771/LC%2041-DOMC-2007.pdf",
     "bkam_lc_41-domc-2007_LCN.pdf"),
    (f"{BASE_BKAM}/content/download/498844/4962773/2013_Circ-11-G-13-communication-SCI-sur-LCN.pdf",
     "bkam_circ_11g13_LCN.pdf"),
    (f"{BASE_BKAM}/content/download/498845/4962775/CIRCULAIRE_SRBM_14-G-06.pdf",
     "bkam_circ_14g06_SRBM.pdf"),
    (f"{BASE_BKAM}/content/download/498846/4962777/circulaire_17G05_pension.pdf",
     "bkam_circ_17g05_pension.pdf"),
    (f"{BASE_BKAM}/content/download/612250/6778237/version/1/file/D%C3%A9cision+N%C2%B0392-W-2018.pdf",
     "bkam_decision_392w2018_paiement-mobile.pdf"),
    (f"{BASE_BKAM}/content/download/612251/6778239/version/1/file/LC-BKAM-2018-70.pdf",
     "bkam_lc_70-2018_paiement-mobile.pdf"),
    (f"{BASE_BKAM}/content/download/834939/9078080/version/1/file/De%CC%81cision+Re%CC%81glementaire+Commission+d%27interchange_DCOM.pdf",
     "bkam_decision_interchange_DCOM.pdf"),
    # ── Taux d'intérêt ──────────────────────────────────────────────────────
    (f"{BASE_BKAM}/content/download/18657/149169/Circulaire_2G2011_interets-crediteurs.pdf",
     "bkam_circ_2g2011_interets-crediteurs.pdf"),
    (f"{BASE_BKAM}/content/download/18656/149167/Circulaire_modif_19g2006_taux-max.pdf",
     "bkam_circ_modif_19g2006_taux-max.pdf"),
    (f"{BASE_BKAM}/content/download/18655/149165/Circulaire_4G2010_interets-credit.pdf",
     "bkam_circ_4g2010_interets-credit.pdf"),
    # ── Activité fiduciaire ─────────────────────────────────────────────────
    (f"{BASE_BKAM}/content/download/498921/4963018/decret_2-03-547_retrait-billets.pdf",
     "bkam_decret_2-03-547_retrait-billets-2003.pdf"),
    (f"{BASE_BKAM}/content/download/498922/4963020/decret_2-97-965_retrait-billets.pdf",
     "bkam_decret_2-97-965_retrait-billets-1998.pdf"),
]


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE: finances.gov.ma + lof.finances.gov.ma + chambredesrepresentants.ma
# Finances publiques : LOF, CGI, lois de finances annuelles, notes circulaires DGI
# (~72 PDFs)
# ══════════════════════════════════════════════════════════════════════════════

BASE_LOF  = "https://lof.finances.gov.ma"
BASE_MEF  = "https://www.finances.gov.ma"
BASE_CDR  = "https://www.chambredesrepresentants.ma"
BASE_DGI  = "https://www.tax.gov.ma"

FINANCES_PDF_URLS = [
    # ── Loi organique 130-13 + Constitution ────────────────────────────────
    (f"{BASE_LOF}/sites/default/files/loi_organique_130-30_fr18.pdf",
     "lof_loi-organique_130-13_loi-finances.pdf"),
    (f"{BASE_LOF}/sites/default/files/constitution_2011_fr_17.pdf",
     "lof_constitution_2011.pdf"),
    # ── Décrets d'exécution LOF ─────────────────────────────────────────────
    (f"{BASE_LOF}/sites/default/files/decret_ndeg_2-15-426_relatif_a_lelaboration_et_a_lexecution_des_lois_de_finances_version_consolidee_fr.pdf",
     "lof_decret_2-15-426_consolidee.pdf"),
    (f"{BASE_LOF}/sites/default/files/decret_ndeg_2-15-426_du_28_ramadan_1436_15_juillet_2015.pdf",
     "lof_decret_2-15-426_original.pdf"),
    (f"{BASE_LOF}/sites/default/files/decret_2_17_607_elaboration_execution_lf_19_12_2017_fr.pdf",
     "lof_decret_2-17-607.pdf"),
    (f"{BASE_LOF}/sites/default/files/decret_ndeg_2-22-580_cdg_bo_7200_fr.pdf",
     "lof_decret_2-22-580_controle-gestion.pdf"),
    # ── Arrêtés LOF ────────────────────────────────────────────────────────
    (f"{BASE_LOF}/sites/default/files/bo_7066_fr_arrete_eep_pbt.pdf",
     "lof_arrete_314-22_eep.pdf"),
    (f"{BASE_LOF}/sites/default/files/arrete_679_20_eep_pbt_vf.pdf",
     "lof_arrete_679-20_eep.pdf"),
    (f"{BASE_LOF}/sites/default/files/arete_du_ministre_mefra_eep_pbt_fr.pdf",
     "lof_arrete_551-18_eep.pdf"),
    (f"{BASE_LOF}/sites/default/files/arrete_audit_de_performance_version_francaise_bo.pdf",
     "lof_arrete_740-18_audit-performance.pdf"),
    (f"{BASE_LOF}/sites/default/files/arrete_fixant_les_modalites_dexecution_relatives_aux_remboursements_degrevements_et_restitutions_fiscaux_fr.pdf",
     "lof_arrete_193-16_remboursements-fiscaux.pdf"),
    (f"{BASE_LOF}/sites/default/files/arrete_811e_annexe.pdf",
     "lof_arrete_811-17_personnel.pdf"),
    (f"{BASE_LOF}/sites/default/files/arrete_personnel_decembre_2016.pdf",
     "lof_arrete_3-221-16_personnel.pdf"),
    # ── Circulaires LOF 2024-2026 ───────────────────────────────────────────
    (f"{BASE_LOF}/sites/default/files/circulaire_pbt_2027-2029_signee.pdf",
     "lof_circ_03-2026_pbt-2027-2029.pdf"),
    (f"{BASE_LOF}/sites/default/files/circ_pbt_2026-2028.pdf",
     "lof_circ_5-2025_pbt-2026-2028.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_9-2024_relative_aux_modalites_de_mise_en_place_du_dispositif_de_controle_de_gestion_au_sein_des_departements_ministeriels.pdf",
     "lof_circ_9-2024_controle-gestion.pdf"),
    (f"{BASE_LOF}/sites/default/files/circ_pbt_2025-2027.pdf",
     "lof_circ_4-2024_pbt-2025-2027.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_cg_pbt_2024-2026.pdf",
     "lof_circ_6-2023_pbt-2024-2026.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_pbt_2023_2025_signee.pdf",
     "lof_circ_5bis-2022_pbt-2023-2025.pdf"),
    # ── Circulaires LOF 2021-2019 ───────────────────────────────────────────
    (f"{BASE_LOF}/sites/default/files/circ_cg_12-2021_26072021.pdf",
     "lof_circ_12-2021_programmation.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_rdp_2020.pdf",
     "lof_circ_3724-2021_rapports-perf.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_09_2021_role_et_et_attribution_du_rprog.pdf",
     "lof_circ_9-2021_rprog.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_04-2021.pdf",
     "lof_circ_4-2021_pbt-2022-2024.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_actualisation_propositions_pbt_2021-2023.pdf",
     "lof_circ_9-2020_pbt-2021-2023.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_cg_022020_11032020_pbt_2021-2023.pdf",
     "lof_circ_2-2020_pbt-2021-2023.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_02_oct_pdp_cachete.pdf",
     "lof_circ_17-2019_projets-perf.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_cg_propositions_pbt_2020-2022_28032019.pdf",
     "lof_circ_3-2019_pbt-2020-2022.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_diffusion_rdp_signee.pdf",
     "lof_circ_724-2019_rapports-perf.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_procedures_annulation-creditreport.pdf",
     "lof_circ_2019_annulation-credits.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_mef_poste_budgetaires_tab_effectifs_17012019.pdf",
     "lof_circ_2019_postes-budgetaires.pdf"),
    # ── Circulaires LOF 2018-2016 ───────────────────────────────────────────
    (f"{BASE_LOF}/sites/default/files/circulaire_cg_5-2018_budget2019.pdf",
     "lof_circ_5-2018_pbt-2019-2021.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_mef_modalites_application_virements_credits_entre_programmes.pdf",
     "lof_circ_7787-2018_virements-credits.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_mef_nouveau_calendrier_des_reunions_du_ccf.pdf",
     "lof_circ_8906-2018_ccf.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_procedure_report_2021-2022.pdf",
     "lof_circ_2022_report-credits.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_dematerialisation_du_visa_des_documents.pdf",
     "lof_circ_dematerialisation-visa.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_823-e_report_2017-2018.pdf",
     "lof_circ_823-2018_report-credits.pdf") if False else
    (f"{BASE_LOF}/sites/default/files/circulaire_mef_generalisation_ebudget2_ep_enregistre_14112018.pdf",
     "lof_lettre_8596-2018_ebudget2.pdf"),
    (f"{BASE_LOF}/sites/default/files/circ_mef_nomenclature_budgetaire_19072017.pdf",
     "lof_circ_4973-2017_nomenclature.pdf"),
    (f"{BASE_LOF}/sites/default/files/circ_min_gestion_fin_eep_10072017.pdf",
     "lof_circ_4509-2017_gestion-eep.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaires_maquettepdp_avecannexe.pdf",
     "lof_circ_1693-2017_projets-perf.pdf"),
    (f"{BASE_LOF}/sites/default/files/circulaire_de_m._le_ministre_de_leconomie_et_des_finances_noi_5165_en_date_du_19_07_2016_portant_application_de_larticle_5_du_decret_relatif_a_lelaboration_et_lexecution_des_lois_de_finances.pdf",
     "lof_circ_5165-2016_art5.pdf"),
    # ── Code Général des Impôts (CGI) ───────────────────────────────────────
    (f"{BASE_MEF}/Publication/dgi/2025/CGI-2026-FR.pdf",
     "dgi_CGI_2026_fr.pdf"),
    (f"{BASE_MEF}/Publication/dgi/2024/cgi-2025-fr.pdf",
     "dgi_CGI_2025_fr.pdf"),
    (f"{BASE_MEF}/Publication/dgi/2024/CG-2024-fr.pdf",
     "dgi_CGI_2024_fr.pdf"),
    # ── Notes Circulaires DGI ───────────────────────────────────────────────
    (f"{BASE_DGI}/wps/wcm/connect/ad04626f-6168-40d0-8f70-8e453a925bdc/Note+Circulaire++n%C2%B0+736+relative+aux+mesures+fiscales+de+la+LF+2025.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-ad04626f-6168-40d0-8f70-8e453a925bdc-plIELLR",
     "dgi_note-circulaire_736_LF2025.pdf"),
    (f"{BASE_DGI}/wps/wcm/connect/eeb72abe-f989-4037-87e4-220c97a4708b/Note+Circulaire++N%C2%B0+735+LF+2024.pdf?MOD=AJPERES&CACHEID=ROOTWORKSPACE-eeb72abe-f989-4037-87e4-220c97a4708b-oSe93IK",
     "dgi_note-circulaire_735_LF2024.pdf"),
    # ── Notes synthétiques mesures fiscales ────────────────────────────────
    (f"{BASE_MEF}/Publication/dgi/2025/note-synthetique-mesures-fiscalesLF20265.pdf",
     "dgi_note-synthetique_LF2026.pdf"),
    (f"{BASE_MEF}/Publication/dgi/2024/synthetique-mesures-fiscaleslF2025.pdf",
     "dgi_note-synthetique_LF2025.pdf"),
    (f"{BASE_MEF}/Publication/dgi/2024/Note-Synthetique-MesuresFiscales2024.pdf",
     "dgi_note-synthetique_LF2024.pdf"),
    # ── Lois de finances annuelles ──────────────────────────────────────────
    (f"{BASE_CDR}/sites/default/files/01-%20Projet%20loi%20de%20Finances%202026_Fr.pdf",
     "lf_2026_PLF_fr.pdf"),
    (f"{BASE_CDR}/sites/default/files/loi/01-%20Projet%20loi%20de%20Finances%202025_Fr.pdf",
     "lf_2025_PLF_fr.pdf"),
    (f"{BASE_CDR}/sites/default/files/2024-10/01-%20Projet%20loi%20de%20Finances%202025_Ar.pdf",
     "lf_2025_PLF_ar.pdf"),
    (f"{BASE_MEF}/Maliya%20tawassol/SLF-23%20Fr-2025.pdf",
     "lf_2025_adoptee_fr.pdf"),
    (f"{BASE_MEF}/Maliya%20tawassol/SLF-22-2024.pdf",
     "lf_2024_adoptee_fr.pdf"),
    (f"{BASE_MEF}/Maliya%20tawassol/SLF2022.pdf",
     "lf_2022_adoptee_fr.pdf"),
    (f"{BASE_MEF}/Publication/db/2023/01-Corps-la-Loi_Fr.pdf",
     "lf_2023_corps_fr.pdf"),
    # ── Rapports sur les dépenses fiscales ─────────────────────────────────
    (f"{BASE_CDR}/sites/default/files/09-%20Rapport%20De%CC%81penses%20Fiscales_Fr.pdf",
     "lf_2026_rapport-depenses-fiscales_fr.pdf"),
    (f"{BASE_CDR}/sites/default/files/2024-10/07-%20Rapport%20de%CC%81penses%20fiscales_Fr.pdf",
     "lf_2025_rapport-depenses-fiscales_fr.pdf"),
    (f"{BASE_MEF}/Publication/db/2026/Rapport-depenses-fiscales_Fr.pdf",
     "mef_rapport-depenses-fiscales-2026_fr.pdf"),
    # ── Circulaires MEF délais de paiement ─────────────────────────────────
    (f"{BASE_MEF}/Publication/depp/2023/note-circulaire734.pdf",
     "mef_circ_734_loi-69-21_delais-paiement.pdf"),
    (f"{BASE_MEF}/Publication/depp/2023/Circulaire-D-1265.pdf",
     "mef_circ_1265_loi-69-21_ar.pdf"),
    (f"{BASE_MEF}/Publication/depp/2023/Loi%2069-21%20code%20de%20commerce%20d%C3%A9lais%20de%20paiement.pdf",
     "mef_loi_69-21_delais-paiement.pdf"),
    (f"{BASE_MEF}/Publication/depp/2019/CirculaireD%C3%A9laisPaiement_Juin2019_fr.pdf",
     "mef_circ_1632-2019_delais-paiement.pdf"),
    (f"{BASE_MEF}/Publication/depp/2018/4%20-MEF-Circulaire%20Delaispaiement%20EEP_18092018.pdf",
     "mef_circ_2467-2018_delais-paiement-eep.pdf"),
    (f"{BASE_MEF}/Publication/depp/2018/decretn2-17-696_fr.pdf",
     "mef_decret_2-17-696_observatoire-delais.pdf"),
    (f"{BASE_MEF}/Publication/depp/2018/decretn2-16-344_fr.pdf",
     "mef_decret_2-16-344_delais-paiement.pdf"),
    # ── Incitations fiscales sectorielles ──────────────────────────────────
    (f"{BASE_MEF}/Publication/dgi/2025/secteur-transport-incitations-fiscales2025.pdf",
     "dgi_incitations-fiscales_transport_2025.pdf"),
    # ── Rapport économique et financier ────────────────────────────────────
    (f"{BASE_MEF}/Publication/db/2026/Rapport-economique-financier_Fr.pdf",
     "mef_rapport-economique-financier_2026.pdf"),
]


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE: chambredesrepresentants.ma — Projets & textes de loi adoptés
# Droit civil, pénal, commercial, organisationnel, social (~27 PDFs)
# ══════════════════════════════════════════════════════════════════════════════

BASE_CDR_LOIS = "https://www.chambredesrepresentants.ma"

CDR_PDF_URLS = [
    # ── Procédure civile & pénale ───────────────────────────────────────────
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/rapport_lec1_p1_02.23_MAJ_compressed.pdf",
     "cdr_rapport_loi-02.23_procedure-civile_p1.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/Rapport-lec1-p2UPL03.23_0.pdf",
     "cdr_rapport_loi-03.23_procedure-penale_p2.pdf"),
    # ── Organisation judiciaire ─────────────────────────────────────────────
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/38.15-3.pdf",
     "cdr_loi_38.15_organisation-judiciaire.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/106.13.pdf",
     "cdr_loi_106.13.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/70.15.pdf",
     "cdr_loi_70.15.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/70.14.pdf",
     "cdr_loi_70.14.pdf"),
    # ── Droit civil & famille ───────────────────────────────────────────────
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/projet_loi_36.21.pdf",
     "cdr_projet-loi_36.21_etat-civil.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/27.14.pdf",
     "cdr_loi_27.14.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/02.13.pdf",
     "cdr_loi_02.13.pdf"),
    # ── Droit pénal & sécurité ──────────────────────────────────────────────
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/97.15.pdf",
     "cdr_loi_97.15.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/33.15.pdf",
     "cdr_loi_33.15.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/94.12_0.pdf",
     "cdr_loi_94.12.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/88.13_2.pdf",
     "cdr_loi_88.13.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/59.13.pdf",
     "cdr_loi_59.13.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/lec_1_59.13.pdf",
     "cdr_lec1_loi_59.13.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/lec_2_83.13.pdf",
     "cdr_lec2_loi_83.13.pdf"),
    # ── Droit commercial & entreprises ─────────────────────────────────────
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/11.16.pdf",
     "cdr_loi_11.16.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/projet_loi_44.20.pdf",
     "cdr_projet-loi_44.20.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/projet_loi_43.20_0.pdf",
     "cdr_projet-loi_43.20.pdf"),
    # ── Droit social & protection ────────────────────────────────────────────
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/projet_loi_06.21.pdf",
     "cdr_projet-loi_06.21.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/projet_loi_04.21_0.pdf",
     "cdr_projet-loi_04.21.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/projet_loi_1_82.21.pdf",
     "cdr_projet-loi_82.21.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/projet_loi_96.21.pdf",
     "cdr_projet-loi_96.21.pdf"),
    # ── Education & numérique ────────────────────────────────────────────────
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/Projet_loi_59.21.pdf",
     "cdr_projet-loi_59.21_enseignement.pdf"),
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/Projet_loi_16.22.pdf",
     "cdr_projet-loi_16.22.pdf"),
    # ── Lois organiques & constitutionnelles ─────────────────────────────────
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/projet_loi_1_66.19.pdf",
     "cdr_projet-loi_66.19.pdf"),
    # ── Propositions de loi récentes (2024) ──────────────────────────────────
    (f"{BASE_CDR_LOIS}/sites/default/files/loi/prop_loi_288_2024.pdf",
     "cdr_prop-loi_288_2024.pdf"),
]


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE: ism.ma — Institut Supérieur de la Magistrature
# Textes de loi en arabe : 13 domaines, ~170 PDFs
# Droit civil, pénal, commercial, famille, foncier, santé, environnement...
# ══════════════════════════════════════════════════════════════════════════════

BASE_ISM = "https://ism.ma/pdf/ARABE/Textesdeloiarabe"

ISM_PDF_URLS = [
    # ── Constitution ────────────────────────────────────────────────────────
    ("https://ism.ma/pdf/constitution.pdf",
     "ism_constitution_ar.pdf"),
    (f"{BASE_ISM}/const/3.pdf",  "ism_const_3.pdf"),
    (f"{BASE_ISM}/const/4.pdf",  "ism_const_4.pdf"),
    (f"{BASE_ISM}/const/5.pdf",  "ism_const_5.pdf"),
    # ── Droit civil ──────────────────────────────────────────────────────────
    (f"{BASE_ISM}/civil/1.pdf",  "ism_civil_1.pdf"),
    (f"{BASE_ISM}/civil/2.pdf",  "ism_civil_2.pdf"),
    (f"{BASE_ISM}/civil/3.pdf",  "ism_civil_3.pdf"),
    (f"{BASE_ISM}/civil/4.pdf",  "ism_civil_4.pdf"),
    (f"{BASE_ISM}/civil/5.pdf",  "ism_civil_5.pdf"),
    (f"{BASE_ISM}/civil/6.pdf",  "ism_civil_6.pdf"),
    (f"{BASE_ISM}/civil/7.pdf",  "ism_civil_7.pdf"),
    (f"{BASE_ISM}/civil/8.pdf",  "ism_civil_8.pdf"),
    # ── Droit de la famille ──────────────────────────────────────────────────
    (f"{BASE_ISM}/famille/1.pdf", "ism_famille_1.pdf"),
    (f"{BASE_ISM}/famille/2.pdf", "ism_famille_2.pdf"),
    (f"{BASE_ISM}/famille/3.pdf", "ism_famille_3.pdf"),
    (f"{BASE_ISM}/famille/4.pdf", "ism_famille_4.pdf"),
    (f"{BASE_ISM}/famille/5.pdf", "ism_famille_5.pdf"),
    # ── Droit du bail / loyer ────────────────────────────────────────────────
    (f"{BASE_ISM}/loyer/1.pdf",  "ism_loyer_1.pdf"),
    (f"{BASE_ISM}/loyer/2.pdf",  "ism_loyer_2.pdf"),
    (f"{BASE_ISM}/loyer/3.pdf",  "ism_loyer_3.pdf"),
    (f"{BASE_ISM}/loyer/4.pdf",  "ism_loyer_4.pdf"),
    # ── Droit foncier & immobilier ───────────────────────────────────────────
    (f"{BASE_ISM}/foncier/1.pdf",  "ism_foncier_1.pdf"),
    (f"{BASE_ISM}/foncier/2.pdf",  "ism_foncier_2.pdf"),
    (f"{BASE_ISM}/foncier/3.pdf",  "ism_foncier_3.pdf"),
    (f"{BASE_ISM}/foncier/4.pdf",  "ism_foncier_4.pdf"),
    (f"{BASE_ISM}/foncier/5.pdf",  "ism_foncier_5.pdf"),
    (f"{BASE_ISM}/foncier/6.pdf",  "ism_foncier_6.pdf"),
    (f"{BASE_ISM}/foncier/7.pdf",  "ism_foncier_7.pdf"),
    (f"{BASE_ISM}/foncier/8.pdf",  "ism_foncier_8.pdf"),
    (f"{BASE_ISM}/foncier/9.pdf",  "ism_foncier_9.pdf"),
    (f"{BASE_ISM}/foncier/10.pdf", "ism_foncier_10.pdf"),
    (f"{BASE_ISM}/foncier/11.pdf", "ism_foncier_11.pdf"),
    (f"{BASE_ISM}/foncier/12.pdf", "ism_foncier_12.pdf"),
    (f"{BASE_ISM}/foncier/13.pdf", "ism_foncier_13.pdf"),
    (f"{BASE_ISM}/foncier/14.pdf", "ism_foncier_14.pdf"),
    (f"{BASE_ISM}/foncier/15.pdf", "ism_foncier_15.pdf"),
    (f"{BASE_ISM}/foncier/16.pdf", "ism_foncier_16.pdf"),
    # ── Droit social & travail ───────────────────────────────────────────────
    (f"{BASE_ISM}/social/1.pdf",  "ism_social_1.pdf"),
    (f"{BASE_ISM}/social/2.pdf",  "ism_social_2.pdf"),
    (f"{BASE_ISM}/social/3.pdf",  "ism_social_3.pdf"),
    # ── Droit pénal ──────────────────────────────────────────────────────────
    (f"{BASE_ISM}/penal/1.pdf",   "ism_penal_1.pdf"),
    (f"{BASE_ISM}/penal/2.pdf",   "ism_penal_2.pdf"),
    (f"{BASE_ISM}/penal/3.pdf",   "ism_penal_3.pdf"),
    (f"{BASE_ISM}/penal/4.pdf",   "ism_penal_4.pdf"),
    (f"{BASE_ISM}/penal/5.pdf",   "ism_penal_5.pdf"),
    (f"{BASE_ISM}/penal/6.pdf",   "ism_penal_6.pdf"),
    (f"{BASE_ISM}/penal/7.pdf",   "ism_penal_7.pdf"),
    (f"{BASE_ISM}/penal/8.pdf",   "ism_penal_8.pdf"),
    (f"{BASE_ISM}/penal/9.pdf",   "ism_penal_9.pdf"),
    (f"{BASE_ISM}/penal/10.pdf",  "ism_penal_10.pdf"),
    (f"{BASE_ISM}/penal/11.pdf",  "ism_penal_11.pdf"),
    (f"{BASE_ISM}/penal/12.pdf",  "ism_penal_12.pdf"),
    (f"{BASE_ISM}/penal/13.pdf",  "ism_penal_13.pdf"),
    (f"{BASE_ISM}/penal/14.pdf",  "ism_penal_14.pdf"),
    # ── Droit commercial ─────────────────────────────────────────────────────
    (f"{BASE_ISM}/comercial/1.pdf",  "ism_commercial_1.pdf"),
    (f"{BASE_ISM}/comercial/2.pdf",  "ism_commercial_2.pdf"),
    (f"{BASE_ISM}/comercial/3.pdf",  "ism_commercial_3.pdf"),
    (f"{BASE_ISM}/comercial/4.pdf",  "ism_commercial_4.pdf"),
    (f"{BASE_ISM}/comercial/5.pdf",  "ism_commercial_5.pdf"),
    (f"{BASE_ISM}/comercial/6.pdf",  "ism_commercial_6.pdf"),
    (f"{BASE_ISM}/comercial/7.pdf",  "ism_commercial_7.pdf"),
    (f"{BASE_ISM}/comercial/8.pdf",  "ism_commercial_8.pdf"),
    (f"{BASE_ISM}/comercial/9.pdf",  "ism_commercial_9.pdf"),
    (f"{BASE_ISM}/comercial/10.pdf", "ism_commercial_10.pdf"),
    (f"{BASE_ISM}/comercial/11.pdf", "ism_commercial_11.pdf"),
    (f"{BASE_ISM}/comercial/12.pdf", "ism_commercial_12.pdf"),
    (f"{BASE_ISM}/comercial/13.pdf", "ism_commercial_13.pdf"),
    (f"{BASE_ISM}/comercial/14.pdf", "ism_commercial_14.pdf"),
    (f"{BASE_ISM}/comercial/15.pdf", "ism_commercial_15.pdf"),
    (f"{BASE_ISM}/comercial/16.pdf", "ism_commercial_16.pdf"),
    (f"{BASE_ISM}/comercial/17.pdf", "ism_commercial_17.pdf"),
    (f"{BASE_ISM}/comercial/18.pdf", "ism_commercial_18.pdf"),
    (f"{BASE_ISM}/comercial/19.pdf", "ism_commercial_19.pdf"),
    (f"{BASE_ISM}/comercial/20.pdf", "ism_commercial_20.pdf"),
    (f"{BASE_ISM}/comercial/21.pdf", "ism_commercial_21.pdf"),
    (f"{BASE_ISM}/comercial/22.pdf", "ism_commercial_22.pdf"),
    (f"{BASE_ISM}/comercial/23.pdf", "ism_commercial_23.pdf"),
    (f"{BASE_ISM}/comercial/24.pdf", "ism_commercial_24.pdf"),
    (f"{BASE_ISM}/comercial/25.pdf", "ism_commercial_25.pdf"),
    (f"{BASE_ISM}/comercial/26.pdf", "ism_commercial_26.pdf"),
    (f"{BASE_ISM}/comercial/27.pdf", "ism_commercial_27.pdf"),
    # ── Droit administratif & financier ──────────────────────────────────────
    (f"{BASE_ISM}/administratif/1.pdf",  "ism_admin_1.pdf"),
    (f"{BASE_ISM}/administratif/2.pdf",  "ism_admin_2.pdf"),
    (f"{BASE_ISM}/administratif/3.pdf",  "ism_admin_3.pdf"),
    (f"{BASE_ISM}/administratif/4.pdf",  "ism_admin_4.pdf"),
    # note: /5.pdf absent
    (f"{BASE_ISM}/administratif/6.pdf",  "ism_admin_6.pdf"),
    (f"{BASE_ISM}/administratif/7.pdf",  "ism_admin_7.pdf"),
    (f"{BASE_ISM}/administratif/8.pdf",  "ism_admin_8.pdf"),
    (f"{BASE_ISM}/administratif/9.pdf",  "ism_admin_9.pdf"),
    (f"{BASE_ISM}/administratif/10.pdf", "ism_admin_10.pdf"),
    (f"{BASE_ISM}/administratif/11.pdf", "ism_admin_11.pdf"),
    (f"{BASE_ISM}/administratif/12.pdf", "ism_admin_12.pdf"),
    (f"{BASE_ISM}/administratif/13.pdf", "ism_admin_13.pdf"),
    (f"{BASE_ISM}/administratif/14.pdf", "ism_admin_14.pdf"),
    (f"{BASE_ISM}/administratif/15.pdf", "ism_admin_15.pdf"),
    (f"{BASE_ISM}/administratif/16.pdf", "ism_admin_16.pdf"),
    # ── Droit de l'environnement ─────────────────────────────────────────────
    (f"{BASE_ISM}/environnement/1.pdf",  "ism_env_1.pdf"),
    (f"{BASE_ISM}/environnement/2.pdf",  "ism_env_2.pdf"),
    (f"{BASE_ISM}/environnement/3.pdf",  "ism_env_3.pdf"),
    (f"{BASE_ISM}/environnement/4.pdf",  "ism_env_4.pdf"),
    (f"{BASE_ISM}/environnement/5.pdf",  "ism_env_5.pdf"),
    (f"{BASE_ISM}/environnement/6.pdf",  "ism_env_6.pdf"),
    (f"{BASE_ISM}/environnement/7.pdf",  "ism_env_7.pdf"),
    (f"{BASE_ISM}/environnement/8.pdf",  "ism_env_8.pdf"),
    (f"{BASE_ISM}/environnement/9.pdf",  "ism_env_9.pdf"),
    (f"{BASE_ISM}/environnement/10.pdf", "ism_env_10.pdf"),
    (f"{BASE_ISM}/environnement/11.pdf", "ism_env_11.pdf"),
    (f"{BASE_ISM}/environnement/12.pdf", "ism_env_12.pdf"),
    (f"{BASE_ISM}/environnement/13.pdf", "ism_env_13.pdf"),
    (f"{BASE_ISM}/environnement/14.pdf", "ism_env_14.pdf"),
    (f"{BASE_ISM}/environnement/15.pdf", "ism_env_15.pdf"),
    (f"{BASE_ISM}/environnement/16.pdf", "ism_env_16.pdf"),
    (f"{BASE_ISM}/environnement/17.pdf", "ism_env_17.pdf"),
    (f"{BASE_ISM}/environnement/18.pdf", "ism_env_18.pdf"),
    (f"{BASE_ISM}/environnement/19.pdf", "ism_env_19.pdf"),
    (f"{BASE_ISM}/environnement/20.pdf", "ism_env_20.pdf"),
    (f"{BASE_ISM}/environnement/21.pdf", "ism_env_21.pdf"),
    (f"{BASE_ISM}/environnement/22.pdf", "ism_env_22.pdf"),
    # ── Droit sanitaire / santé ──────────────────────────────────────────────
    (f"{BASE_ISM}/sanitaire/1.pdf",  "ism_sante_1.pdf"),
    (f"{BASE_ISM}/sanitaire/2.pdf",  "ism_sante_2.pdf"),
    (f"{BASE_ISM}/sanitaire/3.pdf",  "ism_sante_3.pdf"),
    (f"{BASE_ISM}/sanitaire/4.pdf",  "ism_sante_4.pdf"),
    (f"{BASE_ISM}/sanitaire/5.pdf",  "ism_sante_5.pdf"),
    (f"{BASE_ISM}/sanitaire/6.pdf",  "ism_sante_6.pdf"),
    (f"{BASE_ISM}/sanitaire/7.pdf",  "ism_sante_7.pdf"),
    (f"{BASE_ISM}/sanitaire/8.pdf",  "ism_sante_8.pdf"),
    (f"{BASE_ISM}/sanitaire/9.pdf",  "ism_sante_9.pdf"),
    (f"{BASE_ISM}/sanitaire/10.pdf", "ism_sante_10.pdf"),
    (f"{BASE_ISM}/sanitaire/11.pdf", "ism_sante_11.pdf"),
    (f"{BASE_ISM}/sanitaire/12.pdf", "ism_sante_12.pdf"),
    (f"{BASE_ISM}/sanitaire/13.pdf", "ism_sante_13.pdf"),
    (f"{BASE_ISM}/sanitaire/14.pdf", "ism_sante_14.pdf"),
    (f"{BASE_ISM}/sanitaire/15.pdf", "ism_sante_15.pdf"),
    (f"{BASE_ISM}/sanitaire/16.pdf", "ism_sante_16.pdf"),
    (f"{BASE_ISM}/sanitaire/17.pdf", "ism_sante_17.pdf"),
    (f"{BASE_ISM}/sanitaire/18.pdf", "ism_sante_18.pdf"),
    (f"{BASE_ISM}/sanitaire/19.pdf", "ism_sante_19.pdf"),
    # ── Organisation judiciaire & professions juridiques ─────────────────────
    (f"{BASE_ISM}/OrgaJuri/OrgaJuri.pdf",         "ism_orga-judiciaire.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/LoiMinJust.pdf", "ism_loi-min-justice.pdf"),
    (f"{BASE_ISM}/TribAdmin/TribAdmin.pdf",        "ism_trib-admin.pdf"),
    (f"{BASE_ISM}/TribAppelAdmin/TribAppelAdmin.pdf", "ism_trib-appel-admin.pdf"),
    (f"{BASE_ISM}/CreaTribComm/CreaTribComm.pdf",  "ism_creation-trib-commerciaux.pdf"),
    (f"{BASE_ISM}/JustProx/JustProx.pdf",          "ism_justice-proximite.pdf"),
    (f"{BASE_ISM}/TribCass/TribCass.pdf",          "ism_cour-cassation.pdf"),
    (f"{BASE_ISM}/StatMagis/StatMagis.pdf",        "ism_statut-magistrats.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/ElecMagis.pdf",  "ism_election-magistrats.pdf"),
    (f"{BASE_ISM}/MetieAvoc/MetieAvoc.pdf",        "ism_metier-avocat.pdf"),
    (f"{BASE_ISM}/SocAvoc/SocAvoc.pdf",            "ism_societe-avocats.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/Notaria.pdf",    "ism_notariat.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/LoiAdala.pdf",   "ism_loi-adala.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/Adala.pdf",      "ism_adala.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/Huiss.pdf",      "ism_huissiers.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/Traduct.pdf",    "ism_traducteurs.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/Expert.pdf",     "ism_experts-judiciaires.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/LoiNassakha.pdf","ism_loi-nassakha.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/OrganiNassakha.pdf","ism_organi-nassakha.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/InstitMoham.pdf","ism_instit-mohammed.pdf"),
    ("https://ism.ma/pdf/ARABE/Textesdeloiarabe/ChargJuri.pdf",  "ism_charg-juridique.pdf"),
    # ── Droits de l'Homme ────────────────────────────────────────────────────
    (f"{BASE_ISM}/droitdelhome/1.pdf", "ism_droits-homme_1.pdf"),
    (f"{BASE_ISM}/droitdelhome/2.pdf", "ism_droits-homme_2.pdf"),
]


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE: mem.gov.ma — Ministère de l'Énergie et des Mines
# Mines, hydrocarbures, électricité, énergies renouvelables, sécurité industrielle
# (~90 PDFs directs via SharePoint attachments)
# ══════════════════════════════════════════════════════════════════════════════

BASE_MEM = "https://mem.gov.ma"

MEM_PDF_URLS = [
    # ── Énergies renouvelables & électricité ────────────────────────────────
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/53/loi%2058-15%20_BO6436Fr.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/52/Loi%2037-16%20relative%20à%20MASEN%20VFr.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/51/13-09%20energies%20renv.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/4/2016%20BO_6480_Fr%20Loi%2048-15%20régulation%20du%20secteur%20de%20l%27électricité%20.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/23/ficheLoi%2038%20-%2016%20ONEE%20Fr.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/47/BO_6266_Fr_cahier%20de%20charge%20EnR%2028-30.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/45/BO_5984_fr%20zoning%20eolien%2075-81.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/172/Décret%20d%27application%20loi%2013-09%20.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/171/2015%20Decret%20de%20la%20MT%20Pages%20de%20BO_6414_Fr.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/3/2015%20Decret%20de%20la%20MT%20Pages%20de%20BO_6414_Fr.pdf",
    # ── Mines & carrières ────────────────────────────────────────────────────
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/174/Loi%2033.13%20sur%20les%20Mines%20francais.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/184/Loi%2074.15.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/94/loi%2067-15.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/8/loi-142-12.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/24/Loi%2054-14%20FR.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/176/Décret%202-15-807%20version_Francaise.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/27/Statut%20mineur.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/28/REGLEMENT%20GENERAL%20SUR%20L%27EXPLOITATION.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/34/reglglsurexploi.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/33/ARRETE%20VIZIRIEL%202%20JAN%2032_CARIE_MINES.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/10/Dahir%20portant%20loi%20n°%201-72-255.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/18/Décret%20n°2-72-622.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/17/Loi%20n°%20009-71%20.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/7/151-176.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/201/AEO-RecueilJuridique201120.pdf",
    # ── Hydrocarbures ────────────────────────────────────────────────────────
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/126/LOI_Hydrocarbures_2003.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/92/Dahir%201995%20hc.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/91/Dahir%2022%20février%201973%20HC.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/96/Décret%20d%27application%201996%20%20loi%2022%20%20février%201973.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/95/Décret%20d%27application%20de%20la%20loi%2022%20fev%201973%20hc.pdf",
    # ── Sécurité industrielle & nucléaire ────────────────────────────────────
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/9/Decret_2-90-352_CNEN_BO_4205_fr%20(002).pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/216/Décret-Cavités.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/215/Décret%202.19.543%20+Arrêté%20conjoint.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/186/2.18.705%20-%20Décret%20relatif%20aux%20documents%20dont%20la%20tenue%20est%20obligatoire.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/185/Arrêté%20Modèles%20de%20rapports_FR.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/179/Arrêté%20Modèles%20de%20rapports_FR.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/165/Décret%20IGM%202011.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/166/Arrêté%20DIV-SERV%20IG%202014.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/170/Decret-n-2-97-30.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/169/controle%20inst%20decret%202%2094%20666.pdf",
    # ── GPL & hydrocarbures liquéfiés ─────────────────────────────────────────
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/69/Dahir%2012%20janvier%201955.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/80/Arrêté%2029Dec1953_récipients%20d%27emmagasinage%20d%27hydrocarbures%20liquéfiés.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/79/Arrêté%201993%20approuvant%20le%20règlement%20général%20relatif%20aux%20normes%20de%20sécurité%20CE-Dépôts%20GPL.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/131/Arrêté%202Jan1962_Caractéristiques%20des%20GPL.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/130/arrêté%20du%2028%20décembre%201951%20installations%20qui%20mettent%20en%20oeuvre%20des%20cpourants%20électriques%20d.pdf",
    # ── Explosifs & matières dangereuses ────────────────────────────────────
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/32/Dahir%202MARS1938_manutention%20et%20transport%20par%20voies%20de%20terre%20des%20matières%20dangereuses%20etc.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/30/DAHIR%20DU%2014%20AVRIL%201914%20FABRIQUE.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/29/DAHIR%20DU%2014%20JANVIER%201914.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/39/circulaire%204546%202006-explosifs.pdf",
    # ── Appareils à pression & vapeur ────────────────────────────────────────
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/44/DAHIR%2022%20juillet%201953_Règlement%20sur%20l%27emploi%20des%20APV.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/65/Arrêté%2019-08-1953%20modalités%20d%27application%20du%20dahir%20du%2022-07-1953_%20APV.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/64/Arrêté%201953_Construction-entretien%20et%20établissement_APV.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/63/Décret%20n°%202-97-341%20du%2030%20juin%201997%20rémunérations%20des%20services%20épreuves%20d%27appareils%20à%20vapeur.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/75/Arrêté%2011Avr1957_Extincteurs%20d%27incendie.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/74/Arrêté%2015Jan1955_Générateurs%20d%27acétylène.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/73/Arrêté%2014Jan1955_Modalités%20d%27application%20du%20Dahir%2012jan1955.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/72/Arrêté%2013Jan1955_Construction%20et%20emploi%20des%20APG.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/71/ARRETE%20VIZIRIEL%20DU%2012%20JANVIER%201955%20FIXANT%20LES%20TAXES%20PERÇUES%20A%20.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/70/Arrêté%2017-12-1953_emploi%20de%20la%20soudure_art%205.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/66/Arrêté%2017-12-1953_emploi%20de%20la%20soudure_art%205.pdf",
    # ── Géologie & permis ────────────────────────────────────────────────────
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/217/BO%20Fr%20Arreté%20n°1924-20%20dated-2020-08-20-no-6910.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/214/Agrément%20géologues3_BO_7141_Ar.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/208/BO_7119_Ar.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/207/BO_7022_Fr.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/205/Arrêté%202138.22%20du%2029%20Dhu%20al-Hijjah%201443%20(29%20juillet%202022).pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/204/Arrete%20n3851-21.VFr.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/196/Arrete_delegation_pouvoirs.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/195/BO_6813_Haldes%20et%20terrils.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/194/Décret%20Gisements%20du%20Sel.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/193/%D9%85%D8%B1%D8%B3%D9%88%D9%85%20%D8%B1%D9%82%D9%85%202.18.442.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/187/%D9%85%D8%B1%D8%B3%D9%88%D9%85%20%D8%B1%D9%82%D9%85%202.19.583.pdf",
    # ── Importation & commerce ───────────────────────────────────────────────
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/38/10.Autorisation%20d%27importation%20des%20matières%20premieres.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/37/10%20Homologation%20limiteur%20de%20débit.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/36/8.Licences%20d%27importation.pdf",
    # ── Circulaires ──────────────────────────────────────────────────────────
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/85/circulaire%20n°236%20du%202006.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/82/Circulaire%20n°%201%20du%2013-3-17.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/81/Circulaire%20n°%2001-09%20du%2008-01-09.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/77/CIRCULAIRE%20n°%206359%20du%2010%2010%202018%20OCA.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/76/circulaire02dec2005.pdf",
    # ── Arrêtés divers ───────────────────────────────────────────────────────
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/22/Arrêté%20du%20ministre%20du%20commerce%2c%20de%20l%27industrie%2c%20des%20mines%2c%20de%20l%27artisanat%20et%20de%20la%20marine%20marchande%20n°%20053-62.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/21/Arrêté%20du%20ministre%20de%20l%27énergie%20et%20des%20mines%20n°1546-07%20.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/20/Arrêté%20du%20ministre%20de%20l%27énergie%20et%20des%20mines%20n°%20484-81.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/19/Arrêté%20du%20ministre%20du%20commerce%2c%20de%20l%27industrie%2c%20des%20mines%20et%20de%20la%20marine%20marchande%20n°%20393-76%20.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/16/Arrêté%20du%20ministre%20du%20commerce%2c%20de%20l%27industrie%2c%20des%20mines%20et%20de%20la%20marine%20marchande%20n°%20773-73.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/14/Arrêté%20%20n°%201263-91%20du%209%20chaoual%201413%20(1er%20avril%201993)%20.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/13/Arrêté%20du%20ministre%20du%20commerce%2c%20de%20l%27artisanat%2c%20de%20l%27industrie%2c%20des%20mines%20et%20de%20la%20marine%20marchande%20n°%20345-68.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/12/Arrêté%20n°%201282-06.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/11/Décret%20n°%202-72-513%20.pdf",
    f"{BASE_MEM}/Lists/Lst_Textes_Reglementaires/Attachments/132/BO_5566_Fr%20arrete%20Grands%20PP%201546%203-08-2007.pdf",
]


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE: environnement.gov.ma — Ministère de la Transition Énergétique
# Environnement, eau, déchets, air, littoral, EIE, biodiversité (~55 PDFs)
# ══════════════════════════════════════════════════════════════════════════════

BASE_ENV = "https://www.environnement.gov.ma"

ENVIRO_PDF_URLS = [
    # ── Loi-cadre & textes fondamentaux ─────────────────────────────────────
    f"{BASE_ENV}/PDFs/LETTRE_ROYALE.pdf",
    f"{BASE_ENV}/PDFs/decretCNE.pdf",
    (f"{BASE_ENV}/images/2022/avril/d1.pdf",
     "env_loi-cadre_99-12_environnement.pdf"),
    (f"{BASE_ENV}/images/2022/avril/Dahir_n_1-03-59_du_10_rabii_I_1424__12_mai_2003__portant_promulgation_de_la_loi_n_11-03_relative_à_la_protection_et_à_la_mise_en_valeur_de_lenvironnement.pdf",
     "env_loi_11-03_protection-environnement.pdf"),
    # ── Évaluation environnementale (EIE) ────────────────────────────────────
    (f"{BASE_ENV}/images/2022/November/loi_n_49_17_relative_a_evaluation_environnementale.pdf",
     "env_loi_49-17_evaluation-environnementale.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Dahir_1-03-60.pdf",
     "env_dahir_1-03-60.pdf"),
    (f"{BASE_ENV}/images/2022/avril/D%C3%A9cret_n_2-04-563_du_5_kaada_1429_4_novembre_2008_relatif_aux_attributions_et_au_fonctionnement_du_comit%C3%A9_national_et_des_comit%C3%A9s_r%C3%A9gionaux_des_%C3%A9tudes_dimpact.pdf",
     "env_decret_2-04-563_eie-comites.pdf"),
    (f"{BASE_ENV}/images/2022/avril/D%C3%A9cret_n_2-04-564_du_5_kaada_1429_4_novembre_2008_fixant_les_modalit%C3%A9s_dorganisation_et_de_d%C3%A9roulement_de_lenqu%C3%AAte_publique_relative_aux_projets_soumis_aux_%C3%A9tudes_dimpa.pdf",
     "env_decret_2-04-564_enquete-publique.pdf"),
    (f"{BASE_ENV}/images/2022/Arr%C3%AAt%C3%A9_n_636-10_du_7_rabii_I_1431__22_f%C3%A9vrier_2010_.pdf",
     "env_arrete_636-10_eie.pdf"),
    f"{BASE_ENV}/arabe/PDFs/instruments/D1998.pdf",
    # ── Police de l'environnement ─────────────────────────────────────────────
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-14-782_du_30_rejeb_1436__19_mai_2015__relatif_%C3%A0_lorganisation_et_aux_modalit%C3%A9s_de_fonctionnement_de_la_police_de_lenvironnement.pdf",
     "env_decret_2-14-782_police-environnement.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Decret_2-19-721.pdf",
     "env_decret_2-19-721_police.pdf"),
    # ── Qualité de l'air ─────────────────────────────────────────────────────
    (f"{BASE_ENV}/images/2022/Lois/Dahir_n_1-15-87_du_29_ramadan_1436_16_juillet_2015_portant_promulgation_de_la_loi_n_81-12_relative_au_littoral.pdf",
     "env_loi_81-12_littoral.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/Dahir_n_1-03-61_du_10_rabii_I_1424__12_mai_2003__portant_promulgation_de_la_loi_n_13-03_relative_%C3%A0_la_lutte_contre_la_pollution_de_lair.pdf",
     "env_loi_13-03_pollution-air.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-09-286_du_20_hija_1430__8_d%C3%A9cembre_2009__fixant_les_normes_de_qualit%C3%A9_de_lair_et_les_modalit%C3%A9s_de_surveillance_de_lair.pdf",
     "env_decret_2-09-286_qualite-air.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-09-631_du_23_rejeb_1431_6_juillet_2010_fixant_les_valeurs_limites_de_d%C3%A9gagement_d%C3%A9mission_ou_de_rejet_de_polluants_dans_lair_%C3%A9manant_de_sources_de.pdf",
     "env_decret_2-09-631_valeurs-limites-polluants.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Arrete_2304-22.pdf",
     "env_arrete_2304-22_air.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/2835-10.pdf",
     "env_arrete_2835-10_air.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Arrete_3399-12.pdf",
     "env_arrete_3399-12_air.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Arrete_2251-21.pdf",
     "env_arrete_2251-21_air.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/Arr%C3%AAt%C3%A9_n_2323-20_du_18_moharrem_1442_7_septembre_2020.pdf",
     "env_arrete_2323-20_air.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Decret_2-21-965.pdf",
     "env_decret_2-21-965_littoral.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-15-769_du_3_rabii_I_1437_15_d%C3%A9cembre_2015_fixant_la_composition_le_nombre_des_membres_les_attributions_et_les_modalit%C3%A9s.pdf",
     "env_decret_2-15-769_commission-littorale.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-95-717_du_10_rejeb_1417__22_novembre_1996__relatif_%C3%A0_la_pr%C3%A9paration_et_%C3%A0_la_lutte_contre_les_pollutions_marines_accidentelles.pdf",
     "env_decret_2-95-717_pollutions-marines.pdf"),
    # ── Gestion des déchets ──────────────────────────────────────────────────
    (f"{BASE_ENV}/images/2022/847-25.pdf",
     "env_arrete_847-25_dechets.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/844-25.pdf",
     "env_arrete_844-25_dechets.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/Dahir_n_1-12-25_du_13_ramadan_1433__2_ao%C3%BBt_2012__portant_promulgation_de_la_loi_n_23-12_modifiant_la_loi_n_28-00_relative_%C3%A0_la_gestion_des_d%C3%A9chets_et_%C3%A0_leur_%C3%A9limination.pdf",
     "env_loi_23-12_gestion-dechets.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Dahir_1-06-153.pdf",
     "env_dahir_1-06-153_dechets.pdf"),
    (f"{BASE_ENV}/images/D%C3%A9chets/6.D%C3%A9cret_n_2-17-587_FR_D%C3%A9cret_2-17-587_relatif_%C3%A0_la_fixation_des_conditions_et_modalit%C3%A9s_dimportation_dexportation_et_de_transit_des_d%C3%A9chets-pages.pdf",
     "env_decret_2-17-587_dechets-import-export.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Decret_2-14-85.pdf",
     "env_decret_2-14-85_dechets.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-12-172_du_12_joumada_II_1433__4_mai_2012__fixant_les_prescriptions_techniques_relatives_%C3%A0_l%C3%A9limination_et_aux_proc%C3%A9d%C3%A9s_de_valorisation_des_d%C3%A9chets_par_incinc%C3%A9ra.pdf",
     "env_decret_2-12-172_incineration-dechets.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Decret_2-09-85.pdf",
     "env_decret_2-09-85_dechets.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-09-284_du_20_hija_1430__8_d%C3%A9cembre_2009__fixant_les_proc%C3%A9dures_administratives_et_les_prescriptions_techniques_relatives_aux_d%C3%A9charges_contr%C3%B4l%C3%A9es.pdf",
     "env_decret_2-09-284_decharges-controlees.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-09-538_du_5_rabii_II_1431__22_mars_2010__fixant_les_modalit%C3%A9s_d%C3%A9laboration_du_plan_directeur_national_de_gestion_des_d%C3%A9chets_dangereux.pdf",
     "env_decret_2-09-538_plan-dechets-dangereux.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-09-285_du_23_rejeb_1431__6_juillet_2010__fixant_les_modalit%C3%A9s_d%C3%A9laboration_du_plan_directeur_pr%C3%A9fectoral_ou_provincial_de_gestion_des_d%C3%A9chets_m%C3%A9nagers.pdf",
     "env_decret_2-09-285_plan-dechets-menagers.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-09-683_du_23_rejeb_1431__6_juillet_2010__fixant_les_modalit%C3%A9s_d%C3%A9laboration_du_plan_directeur_r%C3%A9gional_de_gestion_des_d%C3%A9chets_industriels.pdf",
     "env_decret_2-09-683_plan-dechets-industriels.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-07-253_du_14_rejeb_1429__18_juillet_2008__portant_classification_des_d%C3%A9chets_et_fixant_la_liste_des_d%C3%A9chets_dangereux.pdf",
     "env_decret_2-07-253_classification-dechets.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-09-139_du_25_joumada_I_1430__21_mai_2009__relatif_%C3%A0_la_gestion_des_d%C3%A9ch%C3%AAts_m%C3%A9dicaux_et_pharmaceutiques.pdf",
     "env_decret_2-09-139_dechets-medicaux.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/D%C3%A9cret_n_2-08-243_du_30_rabii_I_1431__17_mars_2010__institutant_la_Commission_des_polychlorobiphn%C3%A8les__PCB_.pdf",
     "env_decret_2-08-243_PCB.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/491.23.pdf", "env_arrete_491-23_dechets.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/492.23.pdf", "env_arrete_492-23_dechets.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/493.23.pdf", "env_arrete_493-23_dechets.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/495.23.pdf", "env_arrete_495-23_dechets.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/501.23.pdf", "env_arrete_501-23_dechets.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/1-15-148.PDF", "env_dahir_1-15-148_biodiversite.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Dahir_1-19-126.pdf", "env_dahir_1-19-126.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Decret_2-16-174.pdf", "env_decret_2-16-174.pdf"),
    (f"{BASE_ENV}/images/2023/Lois/Decret_2-20-641.pdf", "env_decret_2-20-641.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/Arr%C3%AAt%C3%A9_conjoint__n_2817-10_du_15_joumada_I_1432_19_avril_2011.pdf",
     "env_arrete_2817-10_dechets.pdf"),
    (f"{BASE_ENV}/images/Mde_PDFs/Fr/Actualisation_Cadre_Legislatif_05082016/2_Arrete_publie_BO_Batteries_Usagees.pdf",
     "env_arrete_batteries-usagees.pdf"),
    (f"{BASE_ENV}/images/Mde_PDFs/Fr/Actualisation_Cadre_Legislatif_05082016/3_Arrt_publi_BO_relatif_aux_Dchets_Dangereux.pdf",
     "env_arrete_dechets-dangereux-bo.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/Arr%C3%AAt%C3%A9_conjoint__n_3413-11_du_6_safar_1434_20_d%C3%A9cembre_2012.pdf",
     "env_arrete_3413-11_dechets.pdf"),
    (f"{BASE_ENV}/images/2022/Lois/Arr%C3%AAt%C3%A9_n_782-21_du_8_joumada_I_1443_13_d%C3%A9cembre_2021.pdf",
     "env_arrete_782-21_dechets.pdf"),
]


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE: WIPO Lex — Propriété intellectuelle & droit commercial marocain
# Lois PI (brevets, marques, droits d'auteur), code de commerce (~18 PDFs)
# ══════════════════════════════════════════════════════════════════════════════

BASE_WIPO = "https://wipolex-res.wipo.int"

WIPO_PDF_URLS = [
    # ── Propriété industrielle (Loi 17-97) ──────────────────────────────────
    (f"{BASE_WIPO}/edocs/lexdocs/laws/ar/ma/ma074ar_1.pdf",
     "wipo_loi_17-97_propriete-industrielle_ar.pdf"),
    (f"{BASE_WIPO}/edocs/lexdocs/laws/fr/ma/ma074fr_1.pdf",
     "wipo_loi_17-97_propriete-industrielle_fr.pdf"),
    # ── Droit d'auteur (Loi 2-00) ────────────────────────────────────────────
    (f"{BASE_WIPO}/edocs/lexdocs/laws/ar/ma/ma073ar_1.pdf",
     "wipo_loi_2-00_droit-auteur_ar.pdf"),
    (f"{BASE_WIPO}/edocs/lexdocs/laws/fr/ma/ma073fr_1.pdf",
     "wipo_loi_2-00_droit-auteur_fr.pdf"),
    # ── BMDA (Loi 25-19) ─────────────────────────────────────────────────────
    (f"{BASE_WIPO}/edocs/lexdocs/laws/ar/ma/ma200ar_1.pdf",
     "wipo_loi_25-19_bmda_ar.pdf"),
    (f"{BASE_WIPO}/edocs/lexdocs/laws/fr/ma/ma200fr_1.pdf",
     "wipo_loi_25-19_bmda_fr.pdf"),
    # ── OMPIC (Loi 13-99) ────────────────────────────────────────────────────
    (f"{BASE_WIPO}/edocs/lexdocs/laws/ar/ma/ma075ar_1.pdf",
     "wipo_loi_13-99_ompic_ar.pdf"),
    # ── Indications géographiques (Loi 25-06) ────────────────────────────────
    (f"{BASE_WIPO}/edocs/lexdocs/laws/ar/ma/ma072ar_1.pdf",
     "wipo_loi_25-06_indications-geographiques_ar.pdf"),
    (f"{BASE_WIPO}/edocs/lexdocs/laws/fr/ma/ma072fr_1.pdf",
     "wipo_loi_25-06_indications-geographiques_fr.pdf"),
    # ── Obtentions végétales (Loi 09-94) ─────────────────────────────────────
    (f"{BASE_WIPO}/edocs/lexdocs/laws/fr/ma/ma001fr_1.pdf",
     "wipo_loi_09-94_obtentions-vegetales_fr.pdf"),
    # ── Concurrence (Loi 104-12) ──────────────────────────────────────────────
    (f"{BASE_WIPO}/edocs/lexdocs/laws/ar/ma/ma076ar.pdf",
     "wipo_loi_104-12_concurrence_ar.pdf"),
    (f"{BASE_WIPO}/edocs/lexdocs/laws/fr/ma/ma076fr.pdf",
     "wipo_loi_104-12_concurrence_fr.pdf"),
    # ── Code de Commerce (Loi 15-95) ──────────────────────────────────────────
    (f"{BASE_WIPO}/edocs/lexdocs/laws/ar/ma/ma086ar.pdf",
     "wipo_loi_15-95_code-commerce_ar.pdf"),
    (f"{BASE_WIPO}/edocs/lexdocs/laws/fr/ma/ma086fr.pdf",
     "wipo_loi_15-95_code-commerce_fr.pdf"),
    # ── Protection du consommateur (Loi 31-08) ───────────────────────────────
    (f"{BASE_WIPO}/edocs/lexdocs/laws/ar/ma/ma077ar.pdf",
     "wipo_loi_31-08_protection-consommateur_ar.pdf"),
    (f"{BASE_WIPO}/edocs/lexdocs/laws/fr/ma/ma077fr.pdf",
     "wipo_loi_31-08_protection-consommateur_fr.pdf"),
    # ── Textes complémentaires (UNODC) ───────────────────────────────────────
    ("https://www.unodc.org/cld/uploads/res/document/mar/code-penal-version-consolidee-du-2014_html/Morocco_Code_Penal_v2014.pdf",
     "unodc_code-penal_2014_fr.pdf"),
    ("https://www.maroclear.com/sites/default/files/2024-09/DGRQ_FIC_RLR21_20220202_V1.0%20V%20PUBLIC.pdf",
     "maroclear_recueil-textes-legislatifs_2021.pdf"),
]


def scrape_adala(limit=50):
    """
    Scrape justice.gov.ma (portail du Ministère de la Justice) for Moroccan legal texts.
    Returns list of law dicts ready for Supabase.
    """
    BASE = "https://justice.gov.ma"
    results = []

    console.print(f"\n[bold cyan]📡 Scraping justice.gov.ma...[/bold cyan]")

    # Try the resources/documents page
    pages_to_try = [
        f"{BASE}/resources",
        f"{BASE}/fr/resources",
        f"{BASE}/projects-of-laws",
        f"{BASE}/new_releases",
        f"{BASE}/themes",
    ]

    all_links = []
    for url in pages_to_try:
        try:
            resp = requests.get(url, headers=HTTP_HEADERS, timeout=15)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "lxml")
            # Find links to individual law pages
            found = [a for a in soup.find_all("a", href=True)
                     if len(a.get_text(strip=True)) > 15
                     and any(kw in a.get_text().lower() for kw in
                             ["loi","dahir","décret","arrêté","code","قانون","مرسوم","ظهير"])]
            if found:
                console.print(f"  [dim]{url}: {len(found)} liens trouvés[/dim]")
                all_links.extend(found)
        except Exception as e:
            console.print(f"  [dim]{url}: {e}[/dim]")
        time.sleep(DELAY * 0.5)

    if not all_links:
        console.print("[yellow]Aucun lien trouvé sur justice.gov.ma[/yellow]")
        console.print("[cyan]→ Recommandation: utilisez --source sgg pour les PDFs officiels[/cyan]")
        return []

    seen = set()
    for link in all_links:
        if len(results) >= limit:
            break
        href = link.get("href", "")
        if not href.startswith("http"):
            href = BASE + href
        if href in seen:
            continue
        seen.add(href)
        law = scrape_adala_detail(href)
        if law:
            results.append(law)
            console.print(f"  ✓ [green]{law['number']}[/green] — {law['title_fr'][:60]}...")
        time.sleep(DELAY)

    return results

def scrape_adala_detail(url: str) -> dict | None:
    """Scrape a single law page on adala."""
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Title
        title_el = soup.select_one("h1, h2.law-title, .page-title h1")
        title_fr = clean_text(title_el.get_text()) if title_el else ""
        if not title_fr:
            return None

        # Content — main article body
        content_el = soup.select_one("article, .law-content, .content-body, main .content, #content")
        content_fr = clean_text(content_el.get_text()) if content_el else ""

        # Date
        date_el = soup.select_one(".date, time, .publication-date, .law-date")
        date_str = None
        if date_el:
            raw = date_el.get_text(strip=True)
            m = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{1,2}\s+\w+\s+\d{4})', raw)
            if m:
                try:
                    for fmt in ["%Y-%m-%d", "%d/%m/%Y"]:
                        try:
                            date_str = datetime.strptime(m.group(1), fmt).strftime("%Y-%m-%d")
                            break
                        except: pass
                except: pass

        # Law number from title or URL
        number = extract_number(title_fr) or extract_number(url) or f"adala-{hashlib.md5(url.encode()).hexdigest()[:8]}"

        return {
            "number":     number,
            "title_fr":   title_fr[:500],
            "title_ar":   None,
            "type":       detect_type(title_fr),
            "status":     "En vigueur",
            "date":       date_str,
            "domain_id":  detect_domain(title_fr),
            "language":   "Français",
            "content_fr": content_fr[:100_000] if content_fr else None,
            "content_ar": None,
            "source_url": url,
            "tags":       [],
        }
    except Exception as e:
        console.print(f"  [red]✗ Erreur {url}: {e}[/red]")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# SOURCE 2 — sgg.gov.ma (Textes consolidés — PDFs officiels)
# ══════════════════════════════════════════════════════════════════════════════

# Liste complète des textes consolidés officiels (sgg.gov.ma/arabe/textesconsolides.aspx)
SGG_PDF_URLS = [
    # Lois organiques
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/64_14.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/44_14.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/02_12.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/27_11.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/28_11.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/29_11.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/59_11.pdf",
    # Lois
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/100_13.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/106_13.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/41_05.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/12_90.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/16_09.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/25_90.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/60_22.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/86_12.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/97_12.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/52_05.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/45_12.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/98_15.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/69_00.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/99_15.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/104_12.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/20_13.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/7_81.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/01_09.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/1_72_255.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/24_96.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/13_09.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/131_13.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/1_58_376.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/1_58_377.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/22_80.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/28_00.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/103_12.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/17_04.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/38_15.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/57_11.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/39_08.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/47_18.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/48_15.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/52_20.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/47_06.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/18_00.pdf",
    # Décrets
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/1_09_236.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/31_08.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/36_15_ar.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_14_867.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_15_426.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_19_67.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_23_1067.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_13_820.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_10_421.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_97_1039.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_19_971.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_14_791.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_77_169.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_10_313.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_18_622.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_02_177.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_12_666.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_23_690.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_22_797.pdf",
    "https://www.sgg.gov.ma/Portals/1/textesconsolides/2_14_782.pdf",
]

# ══════════════════════════════════════════════════════════════════════════════
# SOURCE 2b — sgg.gov.ma/textesimportants (Lois organiques, lois-cadres, décrets)
# ══════════════════════════════════════════════════════════════════════════════

BASE_SGG = "https://www.sgg.gov.ma"

SGG_LOIS_PDF_URLS = [
    # Constitution
    f"{BASE_SGG}/Portals/1/lois/constitution_2011_Ar.pdf",
    # Lois organiques
    f"{BASE_SGG}/Portals/1/lois/Loi_organique_54.25_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_07.21_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_06.21_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_05.21_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_organique_53.25_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_04.21_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_085.13_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_30.24_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_48.22_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_51.21_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_08.21_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_57.20_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_organique_36.24_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_066.13_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_128.12_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_065.13_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_111.14_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_112.14_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_113.14_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_13.22_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_14.22_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_106.13_AR.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_90.15_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_70.21_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_44.14_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_71.21_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-organique_64.14_Ar.pdf",
    # Lois ordinaires
    f"{BASE_SGG}/Portals/1/lois/Loi_26.16_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_CNLCM_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_org_droit_greve_97_15_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-cadre_69.19_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-cadre_50.21_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-cadre_06.22_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_09.21.pdf",
    f"{BASE_SGG}/Portals/1/lois/charte_invest_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-cadre_03.22_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_99.12_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Dahir_1.16.52_ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi-cadre_51.17_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_40-17.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_43-12.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_11-15.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_64-12.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_121-12.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_93-12.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_59-10.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_29-06.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_55-01.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_79-99.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_24-96.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_48-15.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_104.12_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_76.00_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Dahir_173284T_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Dahir_158377_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_88.13_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_108.13_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_01.12_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_47-18.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_46-18.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_86.12_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_60-16.pdf",
    f"{BASE_SGG}/Portals/1/lois/Loi_55-19.pdf",
    # Décrets
    f"{BASE_SGG}/Portals/1/lois/decret_2.17.618_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/decret_2.17.585_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/decret_2.22.431.pdf",
    f"{BASE_SGG}/Portals/1/lois/decret_2.22.335.pdf",
    f"{BASE_SGG}/Portals/1/lois/decret_2.19.591_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/decret_2.18.934_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/decret_cncp_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/D_2.15.426_Ar.pdf",
    f"{BASE_SGG}/Portals/1/lois/Decret_2-20-528.pdf",
]


def download_pdf_list(pdf_urls: list, label: str, limit: int) -> list:
    """Generic PDF downloader — downloads from a list of URLs (or (url, name) tuples) into ./pdfs/"""
    console.print(f"\n[bold cyan]📡 {label}[/bold cyan]")
    console.print(f"  {len(pdf_urls)} PDFs disponibles (limite: {limit})")

    def _resolve(item):
        """Return (url, filename_stem) from either a plain URL string or (url, name) tuple."""
        if isinstance(item, (tuple, list)):
            href, name = item[0], item[1]
        else:
            href = item
            from urllib.parse import unquote
            raw = Path(unquote(href)).name
            name = raw if raw else href.split("/")[-1]
        # Ensure .pdf extension
        if not name.lower().endswith(".pdf"):
            name = name + ".pdf"
        return href, name

    if DRY_RUN:
        console.print("\n[yellow]Mode dry-run — voici ce qui serait téléchargé :[/yellow]")
        for item in pdf_urls[:limit]:
            href, name = _resolve(item)
            filepath = PDF_FOLDER / name
            status = "[dim]déjà présent[/dim]" if filepath.exists() else "[green]à télécharger[/green]"
            console.print(f"  {status} — {name}")
        console.print(f"\n[yellow]Total: {min(limit, len(pdf_urls))} — aucun téléchargement effectué.[/yellow]")
        return []

    downloaded = []
    for i, item in enumerate(pdf_urls[:limit], 1):
        href, name = _resolve(item)
        filename = PDF_FOLDER / name
        if filename.exists():
            console.print(f"  [dim]({i}/{min(limit,len(pdf_urls))}) Déjà téléchargé: {filename.name}[/dim]")
            continue
        console.print(f"  [dim]({i}/{min(limit,len(pdf_urls))}) Téléchargement: {name[:60]}...[/dim]")
        try:
            # timeout=(connexion, lecture) — évite les blocages infinis
            r = requests.get(
                href,
                headers=HTTP_HEADERS,
                timeout=(10, 30),   # 10s connexion, 30s lecture max
                stream=True,
                verify=False,       # ignore SSL errors sur certains sites gov
            )
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            size_kb = filename.stat().st_size // 1024
            console.print(f"  ✓ [green]{name[:60]}[/green] ({size_kb} KB)")
            downloaded.append(str(filename))
            time.sleep(DELAY)
        except requests.exceptions.Timeout:
            console.print(f"  [yellow]⏱ Timeout — ignoré: {Path(href).name[:50]}[/yellow]")
        except requests.exceptions.SSLError:
            console.print(f"  [yellow]🔒 SSL error — ignoré: {Path(href).name[:50]}[/yellow]")
        except Exception as e:
            console.print(f"  [red]✗ {Path(href).name[:50]}: {str(e)[:60]}[/red]")

    if downloaded:
        console.print(f"\n[bold green]✅ {len(downloaded)} PDFs téléchargés dans ./pdfs/[/bold green]")
        console.print("[yellow]→ Lancez maintenant: python extract.py[/yellow]")
    else:
        console.print("[yellow]Aucun nouveau PDF. Tous déjà téléchargés.[/yellow]")
    return downloaded


def scrape_sgg_pdfs(year=None, limit=20):
    """
    Download official consolidated legal texts from sgg.gov.ma.
    Files go to ./pdfs/ — then run extract.py to process them.
    Also re-scrapes the page to catch newly added PDFs.
    """
    BASE     = "https://www.sgg.gov.ma"
    PAGE_URL = f"{BASE}/arabe/textesconsolides.aspx"

    console.print(f"\n[bold cyan]📡 Téléchargement textes consolidés depuis sgg.gov.ma...[/bold cyan]")

    # Try to scrape fresh list from the page first
    pdf_urls = list(SGG_PDF_URLS)  # start with known list
    try:
        resp = requests.get(PAGE_URL, headers=HTTP_HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "lxml")
        fresh = [a["href"] for a in soup.find_all("a", href=True) if ".pdf" in a["href"].lower()]
        for href in fresh:
            if not href.startswith("http"):
                href = BASE + "/" + href.lstrip("/")
            if href not in pdf_urls:
                pdf_urls.append(href)
                console.print(f"  [dim]Nouveau PDF trouvé: {Path(href).name}[/dim]")
    except Exception as e:
        console.print(f"  [yellow]Impossible de rafraîchir la liste: {e} — utilisation de la liste statique[/yellow]")

    return download_pdf_list(pdf_urls, "Textes consolidés sgg.gov.ma", limit)

# ══════════════════════════════════════════════════════════════════════════════
# SOURCE 3 — ILO NATLEX (droit du travail marocain)
# ══════════════════════════════════════════════════════════════════════════════
def scrape_ilo(limit=30):
    """
    Scrape ILO NATLEX database for Moroccan labor law.
    Returns list of law dicts ready for Supabase.
    """
    BASE = "https://www.ilo.org"
    url  = f"{BASE}/dyn/natlex/natlex4.listAll?p_lang=fr&p_country=MAR&p_classification=01&p_origin=COUNTRY&p_sortby=SORTBY_COUNTRY"

    console.print(f"\n[bold cyan]📡 Scraping ILO NATLEX (Maroc)...[/bold cyan]")

    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        console.print(f"[red]Erreur ILO: {e}[/red]")
        return []

    soup    = BeautifulSoup(resp.text, "lxml")
    results = []

    rows = soup.select("table.natlex tr")[1:]  # skip header
    for row in rows[:limit]:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        link_el  = cells[0].find("a")
        if not link_el:
            continue
        href     = BASE + link_el.get("href", "")
        title_fr = clean_text(link_el.get_text())
        date_str = clean_text(cells[1].get_text()) if len(cells) > 1 else None

        law = {
            "number":    extract_number(title_fr) or f"ilo-{hashlib.md5(href.encode()).hexdigest()[:8]}",
            "title_fr":  title_fr[:500],
            "title_ar":  None,
            "type":      detect_type(title_fr),
            "status":    "En vigueur",
            "date":      parse_date(date_str),
            "domain_id": "travail",
            "language":  "Français",
            "content_fr": None,  # fetch detail if needed
            "source_url": href,
            "tags":      ["travail", "ILO"],
        }
        results.append(law)
        console.print(f"  ✓ [green]{law['number']}[/green] — {law['title_fr'][:60]}...")
        time.sleep(DELAY * 0.5)

    return results

# ══════════════════════════════════════════════════════════════════════════════
# Utilities
# ══════════════════════════════════════════════════════════════════════════════
def extract_number(text: str) -> str | None:
    """Try to extract a law number like 'n° 15-95', '2-24-100', etc."""
    patterns = [
        r'n[°o]\s*(\d[\d\-\.]+)',
        r'loi\s+(\d[\d\-\.]+)',
        r'dahir\s+n[°o]?\s*(\d[\d\-\.]+)',
        r'décret\s+n[°o]?\s*(\d[\d\-\.]+)',
        r'(\d{1,2}-\d{2,3}-\d{2,4})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None

def parse_date(text: str) -> str | None:
    if not text: return None
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]:
        try:
            return datetime.strptime(text.strip(), fmt).strftime("%Y-%m-%d")
        except: pass
    m = re.search(r'(\d{4})', text)
    if m: return f"{m.group(1)}-01-01"
    return None

# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════
def main():
    console.print(f"[bold]JuriThèque Scraper[/bold] — source=[cyan]{SOURCE}[/cyan] dry_run=[yellow]{DRY_RUN}[/yellow]")

    if not SUPABASE_URL or not SUPABASE_KEY:
        console.print("[red]⚠ SUPABASE_URL / SUPABASE_SERVICE_KEY manquants dans .env[/red]")
        sys.exit(1)

    # ── Run selected source ──
    if SOURCE == "adala":
        laws = scrape_adala(limit=LIMIT)
    elif SOURCE == "sgg":
        scrape_sgg_pdfs(limit=LIMIT)
        return  # PDFs → handled by extract.py
    elif SOURCE == "sgg-lois":
        download_pdf_list(SGG_LOIS_PDF_URLS, "Lois importantes sgg.gov.ma", LIMIT)
        return  # PDFs → handled by extract.py
    elif SOURCE == "mmsp":
        download_pdf_list(MMSP_PDF_URLS, "Fonction Publique — mmsp.gov.ma", LIMIT)
        return
    elif SOURCE == "anrt":
        download_pdf_list(ANRT_PDF_URLS, "Télécom & Numérique — anrt.ma", LIMIT)
        return
    elif SOURCE == "bkam":
        download_pdf_list(BKAM_PDF_URLS, "Réglementation bancaire — bkam.ma", LIMIT)
        return
    elif SOURCE == "finances":
        download_pdf_list(FINANCES_PDF_URLS, "Finances publiques — lof/mef/dgi/cdr", LIMIT)
        return
    elif SOURCE == "cdr":
        download_pdf_list(CDR_PDF_URLS, "Projets de loi — chambredesrepresentants.ma", LIMIT)
        return
    elif SOURCE == "mem":
        download_pdf_list(MEM_PDF_URLS, "Energie & Mines — mem.gov.ma", LIMIT)
        return
    elif SOURCE == "environnement":
        download_pdf_list(ENVIRO_PDF_URLS, "Droit environnemental — environnement.gov.ma", LIMIT)
        return
    elif SOURCE == "wipo":
        download_pdf_list(WIPO_PDF_URLS, "PI & codes — WIPO/UNODC/Maroclear", LIMIT)
        return
    elif SOURCE == "ism":
        download_pdf_list(ISM_PDF_URLS, "Textes juridiques arabes — ism.ma (Institut Superieur Magistrature)", LIMIT)
        return
    elif SOURCE == "all":
        console.print("[bold green]Telechargement de TOUTES les sources...[/bold green]")
        # Merge — deduplicate by resolved name
        all_items = (SGG_PDF_URLS + SGG_LOIS_PDF_URLS + MMSP_PDF_URLS +
                     ANRT_PDF_URLS + BKAM_PDF_URLS + FINANCES_PDF_URLS +
                     CDR_PDF_URLS + MEM_PDF_URLS + ENVIRO_PDF_URLS +
                     WIPO_PDF_URLS + ISM_PDF_URLS)
        seen_names, deduped = set(), []
        for item in all_items:
            name = item[1] if isinstance(item, (tuple, list)) else item.split("/")[-1]
            if name not in seen_names:
                seen_names.add(name)
                deduped.append(item)
        console.print(f"  Total: {len(deduped)} PDFs uniques")
        download_pdf_list(deduped, f"Toutes sources ({len(deduped)} PDFs)", LIMIT)
        return
    elif SOURCE == "ilo":
        laws = scrape_ilo(limit=LIMIT)
    else:
        console.print(f"[red]Source inconnue: {SOURCE}[/red]")
        console.print("Sources: adala, sgg, sgg-lois, mmsp, anrt, bkam, finances, cdr, mem, environnement, wipo, ism, all, ilo")
        sys.exit(1)

    if not laws:
        console.print("[yellow]Aucune loi trouvée.[/yellow]")
        return

    # ── Preview table ──
    table = Table(title=f"{len(laws)} lois trouvées", show_lines=False)
    table.add_column("N°",       style="cyan",  width=18)
    table.add_column("Titre",    style="white", width=50)
    table.add_column("Type",     style="yellow",width=12)
    table.add_column("Domaine",  style="green", width=14)
    table.add_column("Date",     style="dim",   width=12)
    table.add_column("Contenu",  style="dim",   width=10)
    for law in laws:
        has_content = "✓ oui" if law.get("content_fr") else "✗ non"
        table.add_row(
            law["number"][:18],
            (law["title_fr"] or "")[:50],
            law["type"],
            law["domain_id"],
            law.get("date") or "—",
            has_content,
        )
    console.print(table)

    if DRY_RUN:
        console.print("[yellow]Mode dry-run — aucune insertion.[/yellow]")
        return

    # ── Insert into Supabase ──
    inserted = skipped = errors = 0
    for law in track(laws, description="Insertion Supabase..."):
        if sb_exists(law["number"]):
            skipped += 1
            continue
        try:
            # Remove source_url if column doesn't exist in your schema
            record = {k: v for k, v in law.items() if k != "source_url"}
            sb_insert(record)
            inserted += 1
        except Exception as e:
            errors += 1
            console.print(f"  [red]✗ {law['number']}: {e}[/red]")

    console.print(f"\n[bold green]✅ Terminé![/bold green]")
    console.print(f"   Insérées : [green]{inserted}[/green]")
    console.print(f"   Ignorées (déjà présentes) : [yellow]{skipped}[/yellow]")
    console.print(f"   Erreurs  : [red]{errors}[/red]")

if __name__ == "__main__":
    main()
