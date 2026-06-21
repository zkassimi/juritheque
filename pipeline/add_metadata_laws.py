"""
JuriThèque — Ajout de lois avec métadonnées uniquement (sans PDF téléchargé)
════════════════════════════════════════════════════════════════════════════════
Permet d'ajouter dans la base de données des lois ou règlements qui existent
sur des sites officiels (SGG, Adala, Parlement…) sans en télécharger le contenu.

Ces fiches "metadata_only" apparaissent dans la recherche /base, ont leur page
/loi/[canonical_slug], et affichent un aperçu du PDF via Google Docs Viewer
(si source_url pointe vers un PDF public).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USAGE :

  Mode CSV (recommandé) :
    python -X utf8 pipeline/add_metadata_laws.py --source csv --file pipeline/laws_metadata_template.csv

  Mode scraping (listing HTML d'un site officiel) :
    python -X utf8 pipeline/add_metadata_laws.py --scrape https://adala.justice.gov.ma/FR/... --domain penal

  Options supplémentaires :
    --dry-run     : affiche ce qui serait inséré sans rien écrire en DB
    --limit N     : traite seulement les N premières entrées

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COLONNES CSV :
  number      - numéro de la loi (ex: "65-99")                              [obligatoire]
  title_fr    - titre en français                                            [obligatoire]
  title_ar    - titre en arabe                                               [optionnel]
  type        - Loi | Dahir | Décret | Arrêté | Circulaire | Code | Ordonnance [obligatoire]
  date        - date de promulgation YYYY-MM-DD                              [optionnel]
  domain_id   - travail | civil | penal | commercial | fiscal | etc.         [optionnel, auto-détecté]
  source_url  - URL du PDF officiel (pour aperçu Google Docs Viewer)        [recommandé]
  source_name - sgg | adala | anrt | bkam | mmsp | mem | cdr | finances     [optionnel]
  language    - Français | Arabe | Bilingue                                  [optionnel, défaut: Bilingue]
  bo_number   - numéro du Bulletin Officiel                                  [optionnel]
  bo_date     - date BO YYYY-MM-DD                                           [optionnel]
  status      - En vigueur | Abrogé | Modifié                               [optionnel, défaut: En vigueur]
  tags        - mots-clés séparés par ; (ex: "travail;salarié;contrat")     [optionnel]
"""

import argparse
import csv
import os
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
import httpx

try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    def log(msg, **kw): console.print(msg, **kw)
except ImportError:
    def log(msg, **kw): print(msg)

# ── Config ──────────────────────────────────────────────────────────────────────
load_dotenv()

SUPABASE_URL = (
    os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")
).rstrip("/")

SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("VITE_SUPABASE_ANON_KEY", "")
)

HEADERS = {
    "apikey":          SUPABASE_KEY,
    "Authorization":   f"Bearer {SUPABASE_KEY}",
    "Content-Type":    "application/json",
    "Prefer":          "return=representation",
}

SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# ── Domaines ────────────────────────────────────────────────────────────────────
DOMAIN_KEYWORDS = {
    "travail":       ["travail", "salarié", "emploi", "licenciement", "syndicat",
                      "grève", "rémunération", "smig", "convention collective",
                      "inspection du travail", "apprentissage"],
    "penal":         ["pénal", "pénitentiaire", "crime", "délit", "peine",
                      "détention", "procédure pénale", "infraction", "sanction pénale",
                      "tribunal correctionnel", "cour d'appel pénale"],
    "commercial":    ["commerce", "commercial", "société", "sarl", "sa ",
                      "fonds de commerce", "billet à ordre", "chèque", "lettre de change",
                      "faillite", "redressement judiciaire", "registre du commerce"],
    "civil":         ["civil", "famille", "mariage", "divorce", "succession",
                      "héritage", "contrat", "obligation", "prescription",
                      "responsabilité civile", "code civil", "état civil"],
    "administratif": ["administratif", "fonction publique", "fonctionnaire",
                      "concession", "marché public", "tribunal administratif",
                      "recours administratif", "contentieux administratif",
                      "décentralisation", "établissement public"],
    "fiscal":        ["fiscal", "impôt", "taxe", "tva", "ir ", "is ",
                      "patente", "contribution", "recouvrement fiscal",
                      "douane", "droits de douane", "trésor"],
    "international": ["international", "traité", "convention internationale",
                      "coopération", "extradition", "arbitrage international"],
    "numerique":     ["numérique", "télécommunication", "internet", "données personnelles",
                      "cybersécurité", "anrt", "agence nationale", "communication électronique",
                      "protection des données"],
    "constitutionnel":["constitution", "constitutionnel", "parlement", "chambre",
                       "représentants", "conseillers", "élection", "gouvernement",
                       "conseil constitutionnel"],
    "bancaire":      ["bancaire", "banque", "bank al-maghrib", "crédit",
                      "établissement de crédit", "monétaire", "bkam",
                      "blanchiment", "finance islamique", "microfinance"],
    "finances_publiques": ["budget", "finances publiques", "loi de finances",
                            "comptabilité publique", "trésorerie", "dette publique",
                            "contrôle financier", "cour des comptes"],
}

DEFAULT_DOMAIN = "civil"

TYPE_KEYWORDS = {
    "Dahir":       ["dahir"],
    "Loi":         ["loi n°", "loi n ", "loi du", "loi relative", "loi organique"],
    "Décret":      ["décret", "decree"],
    "Arrêté":      ["arrêté"],
    "Circulaire":  ["circulaire", "note circulaire"],
    "Ordonnance":  ["ordonnance"],
    "Code":        ["code du", "code de", "code pénal", "code civil"],
    "Règlement":   ["règlement", "règlement intérieur"],
}

# ── Helpers ──────────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Génère un slug SEO-friendly depuis un titre français."""
    if not text:
        return ""
    # Normalisation unicode (supprime les accents)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    # Remplacer tout ce qui n'est pas alphanumérique par un tiret
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    # Limiter à 80 caractères max (sans couper au milieu d'un mot)
    if len(text) > 80:
        text = text[:80].rsplit("-", 1)[0]
    return text


def detect_domain(title: str) -> str:
    """Détecte le domaine juridique depuis le titre."""
    title_lower = title.lower()
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in title_lower)
        if score > 0:
            scores[domain] = score
    if scores:
        return max(scores, key=scores.get)
    return DEFAULT_DOMAIN


def detect_type(title: str) -> str:
    """Détecte le type juridique depuis le titre."""
    title_lower = title.lower()
    for law_type, keywords in TYPE_KEYWORDS.items():
        if any(kw in title_lower for kw in keywords):
            return law_type
    return "Texte juridique"


def check_duplicate(canonical_slug: str) -> bool:
    """Vérifie si un canonical_slug existe déjà dans la DB."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    try:
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers=HEADERS,
            params={"canonical_slug": f"eq.{canonical_slug}", "select": "id"},
            timeout=10,
        )
        r.raise_for_status()
        return len(r.json()) > 0
    except Exception as e:
        log(f"[yellow]⚠ Impossible de vérifier le doublon : {e}[/]")
        return False


def insert_law(law_data: dict, dry_run: bool = False) -> dict | None:
    """Insère une loi dans Supabase. Retourne le record créé ou None."""
    if dry_run:
        log(f"  [dim][DRY-RUN] Insérerait : {law_data['canonical_slug']}[/]")
        return {"id": "DRY_RUN"}

    if not SUPABASE_URL or not SUPABASE_KEY:
        log("[red]✗ SUPABASE_URL ou SUPABASE_SERVICE_KEY manquant dans .env[/]")
        return None

    try:
        r = httpx.post(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers=HEADERS,
            json=law_data,
            timeout=15,
        )
        r.raise_for_status()
        result = r.json()
        return result[0] if isinstance(result, list) else result
    except httpx.HTTPStatusError as e:
        body = e.response.text[:300]
        log(f"[red]✗ HTTP {e.response.status_code} : {body}[/]")
        return None
    except Exception as e:
        log(f"[red]✗ Erreur : {e}[/]")
        return None


# ── Préparation d'un record ──────────────────────────────────────────────────────

def prepare_record(row: dict) -> dict | None:
    """Valide et complète un dictionnaire de données de loi."""
    # Champs obligatoires
    title_fr = (row.get("title_fr") or "").strip()
    number   = (row.get("number")   or "").strip()
    law_type = (row.get("type")     or "").strip()

    if not title_fr:
        log(f"[red]  ✗ title_fr manquant — ligne ignorée[/]")
        return None
    if not number:
        log(f"[red]  ✗ number manquant pour '{title_fr[:40]}' — ligne ignorée[/]")
        return None
    if not law_type:
        law_type = detect_type(title_fr)
        log(f"[dim]  → type auto-détecté : {law_type}[/]")

    # Champs optionnels
    title_ar    = (row.get("title_ar")    or "").strip() or None
    domain_id   = (row.get("domain_id")  or "").strip()
    source_url  = (row.get("source_url") or "").strip() or None
    source_name = (row.get("source_name")or "").strip() or None
    language    = (row.get("language")   or "Bilingue").strip()
    bo_number   = (row.get("bo_number")  or "").strip() or None
    bo_date     = (row.get("bo_date")    or "").strip() or None
    status      = (row.get("status")     or "En vigueur").strip()
    raw_date    = (row.get("date")       or "").strip() or None
    tags_raw    = (row.get("tags")       or "").strip()

    # Auto-détection domaine
    if not domain_id:
        domain_id = detect_domain(title_fr + " " + (title_ar or ""))
        log(f"[dim]  → domaine auto-détecté : {domain_id}[/]")

    # Tags
    tags = [t.strip() for t in tags_raw.split(";") if t.strip()] if tags_raw else []

    # Canonical slug
    slug_base = f"{number}-{title_fr}"
    canonical_slug = slugify(slug_base)
    if not canonical_slug:
        canonical_slug = slugify(title_fr)

    return {
        "number":                    number,
        "title_fr":                  title_fr,
        "title_ar":                  title_ar,
        "type":                      law_type,
        "status":                    status,
        "date":                      raw_date,
        "language":                  language,
        "domain_id":                 domain_id,
        "source_url":                source_url,
        "source_name":               source_name,
        "bo_number":                 bo_number,
        "bo_date":                   bo_date,
        "tags":                      tags,
        "canonical_slug":            canonical_slug,
        "extraction_status":         "metadata_only",
        "extraction_confidence_score": 10,
        "is_publicly_indexable":     True,
        "needs_human_review":        False,
    }


# ── Mode CSV ─────────────────────────────────────────────────────────────────────

def run_csv(csv_path: Path, dry_run: bool, limit: int | None):
    log(f"\n[bold gold1]📄 Mode CSV — lecture de : {csv_path}[/]")

    if not csv_path.exists():
        log(f"[red]✗ Fichier non trouvé : {csv_path}[/]")
        sys.exit(1)

    stats = {"inserted": 0, "duplicate": 0, "error": 0, "skipped": 0}
    rows_processed = 0

    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if limit and rows_processed >= limit:
                break
            rows_processed += 1

            title_fr = (row.get("title_fr") or "").strip()
            log(f"\n[cyan]→ Traitement[/] : {title_fr[:60] or '(sans titre)'}")

            record = prepare_record(row)
            if not record:
                stats["skipped"] += 1
                continue

            slug = record["canonical_slug"]
            log(f"  [dim]slug : {slug}[/]")

            if check_duplicate(slug):
                log(f"  [yellow]⚠ Doublon ignoré (canonical_slug existe déjà)[/]")
                stats["duplicate"] += 1
                continue

            result = insert_law(record, dry_run=dry_run)
            if result:
                log(f"  [green]✅ Insérée (ID: {result.get('id', '?')})[/]")
                stats["inserted"] += 1
            else:
                stats["error"] += 1

    _print_summary(stats, dry_run)


# ── Mode Scraping ────────────────────────────────────────────────────────────────

def run_scrape(url: str, domain: str | None, dry_run: bool, limit: int | None):
    log(f"\n[bold gold1]🌐 Mode scraping — URL : {url}[/]")
    log("[dim]Tentative de récupération de la page HTML...[/]")

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        log("[red]✗ beautifulsoup4 requis : pip install beautifulsoup4[/]")
        sys.exit(1)

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; JuriThequeBot/1.0)"}
        r = httpx.get(url, headers=headers, follow_redirects=True, timeout=20)
        r.raise_for_status()
    except Exception as e:
        log(f"[red]✗ Erreur HTTP : {e}[/]")
        sys.exit(1)

    soup = BeautifulSoup(r.text, "html.parser")
    stats = {"inserted": 0, "duplicate": 0, "error": 0, "skipped": 0}

    # Extraction heuristique des liens vers des PDFs / pages de lois
    # On cherche les liens qui ressemblent à des titres de lois
    candidates = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]
        if not text or len(text) < 15:
            continue
        # Filtrer les liens qui ressemblent à des lois
        text_lower = text.lower()
        is_law = any(kw in text_lower for kw in [
            "dahir", "loi n°", "loi n ", "décret", "arrêté", "circulaire",
            "code ", "ordonnance", "arrêt", "décision"
        ])
        if not is_law:
            continue
        # Construire l'URL absolue
        if href.startswith("http"):
            full_href = href
        elif href.startswith("/"):
            from urllib.parse import urlparse
            parsed = urlparse(url)
            full_href = f"{parsed.scheme}://{parsed.netloc}{href}"
        else:
            full_href = href

        candidates.append({"title_fr": text, "source_url": full_href if full_href.endswith(".pdf") else None,
                            "source_name": urlparse_hostname(full_href)})

    if not candidates:
        log("[yellow]⚠ Aucune loi détectée dans la page. Vérifiez l'URL ou utilisez le mode CSV.[/]")
        return

    log(f"[dim]→ {len(candidates)} candidats détectés[/]")

    rows_done = 0
    for candidate in candidates:
        if limit and rows_done >= limit:
            break
        rows_done += 1

        title_fr = candidate["title_fr"]
        log(f"\n[cyan]→[/] {title_fr[:60]}")

        # Enrichir avec des données manquantes
        candidate["number"]    = extract_number_from_title(title_fr)
        candidate["type"]      = detect_type(title_fr)
        candidate["domain_id"] = domain or detect_domain(title_fr)
        candidate["language"]  = "Français"
        candidate["status"]    = "En vigueur"

        record = prepare_record(candidate)
        if not record:
            stats["skipped"] += 1
            continue

        slug = record["canonical_slug"]
        if check_duplicate(slug):
            log(f"  [yellow]⚠ Doublon ignoré[/]")
            stats["duplicate"] += 1
            continue

        result = insert_law(record, dry_run=dry_run)
        if result:
            log(f"  [green]✅ Insérée (ID: {result.get('id', '?')})[/]")
            stats["inserted"] += 1
        else:
            stats["error"] += 1

    _print_summary(stats, dry_run)


def extract_number_from_title(title: str) -> str:
    """Tente d'extraire un numéro de loi depuis le titre."""
    # Patterns communs : "65-99", "1-04-22", "n°1.04.22", etc.
    patterns = [
        r'n[°\s]*(\d+[-\.]\d+[-\.]?\d*)',   # n°65-99 or n°1.04.22
        r'(\d{1,2}-\d{2,3})',                # 65-99
        r'(\d{1,2}\.\d{2,3})',               # 65.99
        r'n[°\s]*(\d+)',                     # n°65
    ]
    for pattern in patterns:
        m = re.search(pattern, title, re.IGNORECASE)
        if m:
            return m.group(1)
    return "N/A"


def urlparse_hostname(url: str) -> str:
    """Extrait le hostname d'une URL pour source_name."""
    from urllib.parse import urlparse
    host = urlparse(url).hostname or ""
    if "sgg.gov.ma" in host:          return "sgg"
    if "adala.justice.gov.ma" in host: return "adala"
    if "anrt.ma" in host:             return "anrt"
    if "bkam.ma" in host:             return "bkam"
    if "mmsp.gov.ma" in host:         return "mmsp"
    if "mem.gov.ma" in host:          return "mem"
    if "chambredesrepresentants" in host: return "cdr"
    if "finances.gov.ma" in host:     return "finances"
    if "ism.ma" in host:              return "ism"
    if "wipo.int" in host:            return "wipo"
    return host.split(".")[0] if host else "externe"


# ── Résumé ──────────────────────────────────────────────────────────────────────

def _print_summary(stats: dict, dry_run: bool):
    mode = "[bold yellow][DRY-RUN][/] " if dry_run else ""
    log(f"\n{mode}[bold]━━━ Résumé ━━━[/]")
    log(f"  [green]✅ Insérées   : {stats['inserted']}[/]")
    log(f"  [yellow]⚠  Doublons   : {stats['duplicate']}[/]")
    log(f"  [dim]↷  Ignorées   : {stats['skipped']}[/]")
    log(f"  [red]✗  Erreurs    : {stats['error']}[/]")

    if not dry_run and stats["inserted"] > 0:
        log(f"\n[bold green]✔ Relancez le sitemap pour inclure les nouvelles lois :[/]")
        log(f"  [dim]python -X utf8 pipeline/generate_sitemap.py[/]")
        log(f"  [dim]npm run build[/]")


# ── Point d'entrée ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="JuriThèque — Ajouter des lois avec métadonnées uniquement (sans PDF)"
    )
    parser.add_argument("--source", choices=["csv"], default="csv",
                        help="Source des données (pour l'instant: csv)")
    parser.add_argument("--file", type=Path,
                        default=SCRIPT_DIR / "laws_metadata_template.csv",
                        help="Chemin vers le fichier CSV")
    parser.add_argument("--scrape", metavar="URL",
                        help="URL d'une page listant des lois à scraper")
    parser.add_argument("--domain", help="Domaine juridique (si --scrape)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simule sans écrire en base de données")
    parser.add_argument("--limit", type=int,
                        help="Traiter seulement les N premières entrées")
    args = parser.parse_args()

    log("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log("[bold gold1]  JuriThèque — Ajout de lois par métadonnées      [/]")
    log("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")

    if not SUPABASE_URL or not SUPABASE_KEY:
        log("[red]✗ SUPABASE_URL et SUPABASE_SERVICE_KEY sont requis dans .env[/]")
        sys.exit(1)

    if args.dry_run:
        log("[bold yellow]  [DRY-RUN] Aucune donnée ne sera écrite en base[/]")

    if args.scrape:
        run_scrape(args.scrape, args.domain, args.dry_run, args.limit)
    else:
        run_csv(args.file, args.dry_run, args.limit)


if __name__ == "__main__":
    main()
