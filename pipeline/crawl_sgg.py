"""
JuriThèque — Crawleur complet SGG (sgg.gov.ma)
════════════════════════════════════════════════════════════════════════════════
Découvre dynamiquement tous les textes juridiques sur sgg.gov.ma,
télécharge les PDFs, extrait le texte et insère dans Supabase.

Sources crawlées :
  1. Textes consolidés  → sgg.gov.ma/arabe/textesconsolides.aspx  (~67 PDFs)
  2. Textes importants  → sgg.gov.ma/arabe/textesimportants.aspx  (~74 PDFs)

Usage :
  python -X utf8 pipeline/crawl_sgg.py                    # tout crawler
  python -X utf8 pipeline/crawl_sgg.py --dry-run          # simuler sans insérer
  python -X utf8 pipeline/crawl_sgg.py --limit 10         # seulement 10 PDFs
  python -X utf8 pipeline/crawl_sgg.py --discover-only    # lister les PDFs sans télécharger

Prérequis :
  pip install httpx beautifulsoup4 pymupdf python-dotenv rich requests

Variables .env :
  SUPABASE_URL  (ou VITE_SUPABASE_URL)
  SUPABASE_SERVICE_KEY
"""

import argparse
import hashlib
import os
import re
import sys
import time
import unicodedata
from pathlib import Path
from datetime import date

from dotenv import load_dotenv
import httpx
import requests
import urllib3
from bs4 import BeautifulSoup

# Supprimer les warnings SSL (sgg.gov.ma a un cert auto-signé)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from rich.console import Console
    from rich.progress import track, Progress, SpinnerColumn, TextColumn, BarColumn
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

HEADERS_SB = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}

HTTP_HEADERS = {
    "User-Agent":      "Mozilla/5.0 (compatible; JuriTheque-Bot/1.0; +https://juritheque.com)",
    "Accept-Language": "ar;q=0.9,fr;q=0.8",
    "Accept":          "text/html,application/xhtml+xml,*/*",
}

BASE_SGG = "https://www.sgg.gov.ma"
DELAY    = 2.0   # secondes entre les requêtes (pour respecter le serveur)

SCRIPT_DIR   = Path(__file__).parent
PDF_DIR      = SCRIPT_DIR / "pdfs" / "sgg"
PDF_DIR.mkdir(parents=True, exist_ok=True)

# Pages SGG à crawler
SGG_PAGES = [
    ("textes-consolides", f"{BASE_SGG}/arabe/textesconsolides.aspx"),
    ("textes-importants", f"{BASE_SGG}/arabe/textesimportants.aspx"),
]

TODAY = date.today().isoformat()

# ── Helpers domaine/type (mêmes règles que scraper.py) ─────────────────────────
def detect_type(title: str) -> str:
    t = title.lower()
    if "dahir"       in t: return "Dahir"
    if "décret"      in t: return "Décret"
    if "arrêté"      in t: return "Arrêté"
    if "circulaire"  in t: return "Circulaire"
    if "loi organique" in t: return "Loi organique"
    if "loi-cadre"   in t or "loi cadre" in t: return "Loi-cadre"
    if "loi"         in t: return "Loi"
    if "ordonnance"  in t: return "Ordonnance"
    if "code"        in t: return "Code"
    if "constitution" in t: return "Constitution"
    return "Texte juridique"


def detect_domain(title: str) -> str:
    t = title.lower()
    if any(w in t for w in ["travail","emploi","salarié","syndi"]): return "travail"
    if any(w in t for w in ["pénal","criminel","infraction","sanction","peine"]): return "penal"
    if any(w in t for w in ["commercial","société","entreprise","commerce","concurrence","consommateur","marque","brevet","propriété industrielle"]): return "commercial"
    if any(w in t for w in ["fiscal","impôt","taxe","tva","douane","contribuable","code général des impôts"]): return "fiscal"
    if any(w in t for w in ["loi de finances","budget","finances publiques","comptabilité publique"]): return "finances_publiques"
    if any(w in t for w in ["environnement","pollution","déchet","air","eau","biodiversité","forêt"]): return "administratif"
    if any(w in t for w in ["administratif","fonction publique","service public","mine","énergie","électricité"]): return "administratif"
    if any(w in t for w in ["civil","famille","mariage","divorce","héritage","succession","procédure civile"]): return "civil"
    if any(w in t for w in ["constitution","constitutionnel","parlement","organique"]): return "constitutionnel"
    if any(w in t for w in ["numérique","télécom","communication","données","cyber"]): return "numerique"
    if any(w in t for w in ["international","traité","convention internationale"]): return "international"
    if any(w in t for w in ["bancaire","banque","crédit","paiement","monétaire"]): return "bancaire"
    return "civil"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    if len(text) > 80:
        text = text[:80].rsplit("-", 1)[0]
    return text


def extract_number_from_title(title: str) -> str:
    """Extrait le numéro de loi depuis un titre ou nom de fichier."""
    # Patterns communs : "n°65-99", "n°1-04-22", "1.04.22", etc.
    patterns = [
        r'n[°\s.]*(\d+[-\.]\d+[-\.]?\d*)',   # n°65-99 or n°1.04.22
        r'(\d{1,2}-\d{2,3}-\d+)',             # 1-04-22 (Dahir format)
        r'(\d{2,3}[.\-]\d{2,3})',             # 65-99 or 65.99 or 103.12
        r'n[°\s]*(\d+)',                      # n°65
    ]
    for pattern in patterns:
        m = re.search(pattern, title, re.IGNORECASE)
        if m:
            return m.group(1)
    return "N/A"


def extract_info_from_url(url: str, filename: str) -> dict:
    """
    Extrait le numéro et le type de loi directement depuis l'URL SGG.
    C'est la source la plus fiable car SGG nomme ses fichiers selon la convention.

    Exemples :
      textesconsolides/64_14.pdf         → number=64-14, type=Texte juridique
      lois/Loi-organique_04.21_ar.pdf    → number=04.21, type=Loi organique
      lois/Loi_40-17.pdf                 → number=40-17, type=Loi
      lois/Loi-cadre_03.22_Ar.pdf        → number=03.22, type=Loi-cadre
      lois/constitution_2011_Ar.pdf      → number=2011, type=Constitution
      lois/decret_2.17.618_Ar.pdf        → number=2.17.618, type=Décret
      lois/Dahir_1.16.52_ar.pdf          → number=1.16.52, type=Dahir
      lois/charte_invest_ar.pdf          → number=N/A, type=Charte
    """
    fname = url.split("/")[-1].split("?")[0]          # Loi-organique_04.21_ar.pdf
    fname_lower = fname.lower().replace("_ar.pdf","").replace("_fr.pdf","").replace(".pdf","")
    # → loi-organique_04.21

    # Détecter le type depuis le nom de fichier
    law_type = "Texte juridique"
    if re.search(r'loi.?organique|loi_org', fname_lower, re.I): law_type = "Loi organique"
    elif re.search(r'loi.?cadre',           fname_lower, re.I): law_type = "Loi-cadre"
    elif re.search(r'^loi',                  fname_lower, re.I): law_type = "Loi"
    elif re.search(r'dahir',                fname_lower, re.I): law_type = "Dahir"
    elif re.search(r'decret|décret',        fname_lower, re.I): law_type = "Décret"
    elif re.search(r'constitution',         fname_lower, re.I): law_type = "Constitution"
    elif re.search(r'charte',              fname_lower, re.I): law_type = "Charte"
    elif "textesconsolides" in url:
        law_type = "Loi"   # textesconsolides sont toujours des lois

    # Extraire le numéro depuis le nom de fichier
    # Patterns dans l'ordre de priorité
    number_patterns = [
        r'(\d{1,3}[._]\d{2,3}[._]\d+)',  # 1.16.52 ou 2_17_618
        r'(\d{1,3}[._]\d{2,3})',          # 04.21 ou 64_14 ou 2_00
        r'(\d{4})',                        # 2011 (constitution)
    ]
    number = "N/A"
    # Retirer le préfixe type (Loi-organique_, Loi_, Dahir_, decret_...)
    cleaned = re.sub(r'^(loi[._-]?(?:organique|cadre)?[._-]?|dahir[._-]?|decret[._-]?|constitution[._-]?|charte[._-]?)', '', fname_lower, flags=re.I)
    # Retirer les suffixes lingue (_ar, _fr, t ar, ...)
    cleaned = re.sub(r'[._-](ar|fr|t)$', '', cleaned, flags=re.I)

    for pat in number_patterns:
        m = re.search(pat, cleaned)
        if m:
            number = m.group(1).replace("_", ".").replace("-", ".")
            break

    return {"number": number, "type": law_type}


def extract_date_from_title(title: str) -> str | None:
    """Tente d'extraire une date depuis le titre."""
    # Patterns : "du 11 septembre 2003", "du 1er août 1996"
    months = {
        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12',
    }
    pattern = r'du\s+(\d{1,2})(?:er|ème)?\s+(' + '|'.join(months.keys()) + r')\s+(\d{4})'
    m = re.search(pattern, title.lower())
    if m:
        day, month_str, year = m.groups()
        month = months.get(month_str, '01')
        return f"{year}-{month}-{int(day):02d}"
    return None


# ── PDF text extraction ─────────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_path: Path) -> tuple[str, str]:
    """Extrait le texte d'un PDF. Retourne (content_ar, title_ar)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        log("[yellow]⚠ PyMuPDF non installé. Exécutez : pip install pymupdf[/]")
        return "", ""

    content = ""
    try:
        doc = fitz.open(str(pdf_path))
        pages_text = []
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages_text.append(text)
        content = "\n\n".join(pages_text)
        doc.close()
    except Exception as e:
        log(f"  [yellow]⚠ Erreur extraction PDF : {e}[/]")

    # Nettoyer
    content = re.sub(r'\r\n', '\n', content)
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    content = re.sub(r'[ \t]{2,}', ' ', content)
    content = content.strip()

    # Extraire titre depuis première page
    title = ""
    if content:
        lines = [l.strip() for l in content.split('\n') if l.strip() and len(l.strip()) > 5]
        # Chercher une ligne qui ressemble à un titre (FR ou AR)
        arabic_keywords = ['ظهير', 'قانون', 'مرسوم', 'قرار', 'دستور', 'منشور', 'نظام', 'مدونة', 'المملكة']
        french_keywords = ['dahir', 'loi', 'décret', 'arrêté', 'constitution', 'ordonnance', 'circulaire']
        for line in lines[:25]:
            ll = line.lower()
            if (any(kw in ll for kw in french_keywords)
                    or any(kw in line for kw in arabic_keywords)):
                if len(line) >= 10:   # Ignorer les lignes trop courtes
                    title = line[:200]
                    break
        if not title and lines:
            # Prendre la première ligne non-vide raisonnablement longue
            for line in lines[:5]:
                if len(line) >= 10:
                    title = line[:200]
                    break

    return content, title


# ── Supabase ────────────────────────────────────────────────────────────────────
def sb_number_exists(number: str) -> bool:
    """Vérifie si une loi avec ce numéro existe déjà."""
    if not SUPABASE_URL or number == "N/A":
        return False
    try:
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            params={"number": f"eq.{number}", "select": "id", "limit": "1"},
            timeout=10,
        )
        return len(r.json()) > 0
    except:
        return False


def sb_slug_exists(slug: str) -> bool:
    """Vérifie si un canonical_slug existe déjà."""
    if not SUPABASE_URL or not slug:
        return False
    try:
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            params={"canonical_slug": f"eq.{slug}", "select": "id", "limit": "1"},
            timeout=10,
        )
        return len(r.json()) > 0
    except:
        return False


def sb_insert(record: dict) -> dict | None:
    """Insère une loi dans Supabase."""
    try:
        r = httpx.post(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers=HEADERS_SB,
            json=record,
            timeout=30,
        )
        r.raise_for_status()
        result = r.json()
        return result[0] if isinstance(result, list) else result
    except httpx.HTTPStatusError as e:
        log(f"  [red]✗ HTTP {e.response.status_code} : {e.response.text[:200]}[/]")
        return None
    except Exception as e:
        log(f"  [red]✗ Erreur insertion : {e}[/]")
        return None


# ── Phase 1 : Découverte des PDFs sur SGG ──────────────────────────────────────
def discover_pdfs() -> list[dict]:
    """Crawle les pages SGG et retourne la liste de tous les PDFs avec leur titre."""
    all_pdfs = []
    seen_urls = set()

    log("\n[bold cyan]━━━ Phase 1 : Découverte des PDFs sur SGG ━━━[/]")

    for source_name, page_url in SGG_PAGES:
        log(f"\n[dim]→ Crawl : {page_url}[/]")
        soup = None
        for attempt in range(3):
            try:
                r = requests.get(
                    page_url,
                    headers=HTTP_HEADERS,
                    timeout=30,
                    verify=False,
                )
                soup = BeautifulSoup(r.text, "html.parser")
                break
            except Exception as e:
                wait = (attempt + 1) * 5
                log(f"  [yellow]⚠ Tentative {attempt+1}/3 échouée ({e.__class__.__name__}). Attente {wait}s...[/]")
                time.sleep(wait)
        if soup is None:
            log(f"  [red]✗ Impossible de charger {page_url} après 3 tentatives[/]")
            continue

        page_pdfs = 0
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if ".pdf" not in href.lower():
                continue

            # Normaliser l'URL
            if href.startswith("/"):
                url = BASE_SGG + href
            elif href.startswith("http"):
                url = href.replace("http://www.sgg.gov.ma", BASE_SGG)
            else:
                continue

            # Nettoyer les query strings (version params)
            url_clean = url.split("?")[0]

            if url_clean in seen_urls:
                continue
            seen_urls.add(url_clean)

            # Titre visible dans le lien
            title_from_link = a.get_text(strip=True)
            # Titre depuis l'élément parent (td, li, div)
            parent_text = ""
            parent = a.parent
            if parent:
                parent_text = parent.get_text(separator=" ", strip=True)[:300]

            # Nom du fichier comme indice
            filename = url_clean.split("/")[-1].replace(".pdf", "").replace("_", " ").replace("-", " ")

            all_pdfs.append({
                "url":        url,
                "url_clean":  url_clean,
                "filename":   filename,
                "title_hint": title_from_link or parent_text or filename,
                "source":     source_name,
            })
            page_pdfs += 1

        log(f"  → {page_pdfs} PDFs trouvés sur {source_name}")
        time.sleep(DELAY)

    log(f"\n[bold green]✔ Total PDFs découverts : {len(all_pdfs)}[/]")
    return all_pdfs


# ── Phase 2 : Téléchargement ────────────────────────────────────────────────────
def download_pdf(url: str, filename: str) -> Path | None:
    """Télécharge un PDF et le sauvegarde localement. Retourne le chemin ou None."""
    safe_name = re.sub(r'[^\w.-]', '_', filename) + ".pdf"
    pdf_path = PDF_DIR / safe_name

    if pdf_path.exists() and pdf_path.stat().st_size > 1000:
        return pdf_path  # Déjà téléchargé

    for attempt in range(3):
        try:
            r = requests.get(
                url,
                headers=HTTP_HEADERS,
                timeout=45,
                verify=False,
                stream=True,
            )
            r.raise_for_status()
            content_type = r.headers.get("content-type", "")
            if "pdf" not in content_type.lower() and "application" not in content_type.lower():
                log(f"  [yellow]⚠ Pas un PDF ({content_type}), ignoré[/]")
                return None

            with open(pdf_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            size_kb = pdf_path.stat().st_size // 1024
            log(f"  [dim]↓ Téléchargé ({size_kb} KB)[/]")
            return pdf_path

        except Exception as e:
            wait = (attempt + 1) * 5
            if attempt < 2:
                log(f"  [yellow]⚠ Tentative {attempt+1}/3 ({e.__class__.__name__}). Attente {wait}s...[/]")
                time.sleep(wait)
            else:
                log(f"  [red]✗ Échec téléchargement après 3 tentatives : {e}[/]")
                return None
    return None


# ── Phase 3 : Traitement complet d'un PDF ─────────────────────────────────────
def process_pdf(pdf_info: dict, dry_run: bool = False) -> str:
    """
    Pipeline complet pour un PDF SGG :
    1. Télécharge le PDF
    2. Extrait le texte
    3. Dérive les métadonnées
    4. Vérifie les doublons
    5. Insère dans Supabase

    Retourne : 'inserted' | 'duplicate' | 'skipped' | 'error'
    """
    url      = pdf_info["url"]
    filename = pdf_info["filename"]
    hint     = pdf_info["title_hint"]

    log(f"\n[cyan]→[/] {filename[:60]}")
    log(f"  [dim]URL: {url}[/]")

    # ── Téléchargement ────────────────────────────────────────────────────────
    pdf_path = download_pdf(url, filename)
    if not pdf_path:
        return "error"

    time.sleep(0.5)  # Petite pause entre downloads et extraction

    # ── Extraction du texte ───────────────────────────────────────────────────
    content_raw, title_extracted = extract_text_from_pdf(pdf_path)

    # Choisir le meilleur titre disponible
    title_raw = title_extracted or hint or filename
    # Nettoyer le titre (retirer le contenu trop long ou trop court)
    if len(title_raw) > 250:
        title_raw = title_raw[:250]
    if len(title_raw) < 5:
        title_raw = f"Texte SGG — {filename}"

    # ── Détection des métadonnées ─────────────────────────────────────────────
    # Priorité : URL/filename (plus fiable) → titre → fallback
    url_info  = extract_info_from_url(url, filename)
    number    = url_info["number"]
    if number == "N/A":
        number = extract_number_from_title(title_raw) or extract_number_from_title(filename)
    law_type  = url_info["type"]
    if law_type == "Texte juridique":
        law_type = detect_type(title_raw)
    domain_id = detect_domain(title_raw)
    law_date  = extract_date_from_title(title_raw)

    # ── Séparation titre FR/AR (title_fr est NOT NULL en DB) ─────────────────
    has_arabic = bool(re.search(r'[؀-ۿ]', content_raw))
    if has_arabic and not re.search(r'[a-zA-Z]{5,}', content_raw):
        # PDF purement arabe → title_ar = titre extrait, title_fr = généré (obligatoire)
        title_ar = title_raw if len(title_raw) > 5 else None
        num_label = f" n°{number}" if number != "N/A" else ""
        title_fr = f"{law_type}{num_label} — version arabe (SGG)"
    else:
        title_fr = title_raw
        title_ar = None

    # Langue
    language   = "Arabe" if has_arabic and not re.search(r'[a-zA-Z]{5,}', content_raw) else "Bilingue"

    # ── Vérification des doublons ─────────────────────────────────────────────
    if number != "N/A" and sb_number_exists(number):
        log(f"  [yellow]⚠ Doublon — loi n°{number} déjà dans la DB[/]")
        return "duplicate"

    # Générer le canonical_slug : préférer le type + numéro (court, stable)
    if number != "N/A":
        type_short = (law_type.lower()
                      .replace("loi organique", "loi-organique")
                      .replace("loi-cadre", "loi-cadre")
                      .replace(" ", "-"))
        slug_base = f"{type_short}-{number}"
    elif not has_arabic and title_fr:
        # Titre en français utilisable directement
        slug_base = title_fr
    else:
        # Pour un PDF purement arabe sans numéro, utiliser le nom de fichier (plus stable)
        slug_base = filename
    canonical_slug = slugify(slug_base)
    if not canonical_slug or len(canonical_slug) < 4:
        canonical_slug = slugify(filename)
    if not canonical_slug:
        canonical_slug = re.sub(r'[^a-z0-9]+', '-', url.split("/")[-1].split("?")[0].lower().replace(".pdf",""))

    if sb_slug_exists(canonical_slug):
        log(f"  [yellow]⚠ Doublon slug — {canonical_slug} déjà dans la DB[/]")
        return "duplicate"

    log(f"  [dim]→ Type: {law_type} | Domaine: {domain_id} | n°{number}[/]")
    log(f"  [dim]→ Slug: {canonical_slug}[/]")
    log(f"  [dim]→ Contenu extrait: {len(content_raw):,} caractères[/]")

    if dry_run:
        log(f"  [dim yellow][DRY-RUN] Insérerait dans Supabase[/]")
        return "inserted"

    # ── Insertion dans Supabase ───────────────────────────────────────────────
    # Contenu en arabe si détecté, sinon en français
    content_ar = content_raw if has_arabic else None
    content_fr = content_raw if not has_arabic else None

    record = {
        "number":                     number if number != "N/A" else filename,
        "title_fr":                   title_fr,   # toujours non-null (NOT NULL en DB)
        "title_ar":                   title_ar,   # null si PDF non arabe
        "type":                       law_type,
        "status":                     "En vigueur",
        "date":                       law_date,
        "language":                   language,
        "domain_id":                  domain_id,
        "content_fr":                 content_fr,
        "content_ar":                 content_ar,
        "source_name":                "sgg",
        "source_url":                 url,
        "canonical_slug":             canonical_slug,
        "extraction_status":          "success" if content_raw else "metadata_only",
        "extraction_confidence_score": 55 if content_raw else 10,
        "is_publicly_indexable":      True,
        "needs_human_review":         len(content_raw) < 500 if content_raw else True,
        "tags":                       [],
    }

    result = sb_insert(record)
    if result:
        law_id = result.get("id", "?")
        log(f"  [green]✅ Inséré (ID: {law_id})[/]")
        return "inserted"
    else:
        return "error"


# ── Point d'entrée ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="JuriThèque — Crawler complet SGG (découverte + extraction + insertion)"
    )
    parser.add_argument("--dry-run",        action="store_true",
                        help="Simuler sans écrire en base de données")
    parser.add_argument("--limit",          type=int, default=None,
                        help="Traiter seulement les N premiers PDFs")
    parser.add_argument("--discover-only",  action="store_true",
                        help="Lister les PDFs trouvés sans les télécharger")
    parser.add_argument("--skip-existing",  action="store_true", default=True,
                        help="Ignorer les PDFs déjà téléchargés localement")
    args = parser.parse_args()

    log("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log("[bold gold1]  JuriThèque — Crawleur SGG (sgg.gov.ma)            [/]")
    log("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")

    if not SUPABASE_URL or not SUPABASE_KEY:
        log("[red]✗ SUPABASE_URL et SUPABASE_SERVICE_KEY sont requis dans .env[/]")
        sys.exit(1)

    if args.dry_run:
        log("[bold yellow]  [DRY-RUN] Aucune donnée ne sera écrite[/]")

    # Phase 1 : Découverte
    pdfs = discover_pdfs()

    if not pdfs:
        log("[red]✗ Aucun PDF trouvé sur SGG. Vérifiez votre connexion internet.[/]")
        sys.exit(1)

    if args.discover_only:
        log("\n[bold]Liste des PDFs découverts :[/]")
        for i, p in enumerate(pdfs, 1):
            log(f"  {i:3}. [{p['source']}] {p['filename'][:60]}")
            log(f"       {p['url']}")
        log(f"\n[bold green]✔ {len(pdfs)} PDFs disponibles sur SGG[/]")
        return

    # Appliquer la limite
    if args.limit:
        pdfs = pdfs[:args.limit]
        log(f"\n[dim]→ Traitement limité aux {args.limit} premiers PDFs[/]")

    # Phase 2+3 : Téléchargement, extraction, insertion
    log(f"\n[bold cyan]━━━ Phase 2-3 : Téléchargement + Extraction + Insertion ━━━[/]")
    log(f"[dim]PDFs à traiter : {len(pdfs)} | Dossier local : {PDF_DIR}[/]\n")

    stats = {"inserted": 0, "duplicate": 0, "error": 0}

    for i, pdf_info in enumerate(pdfs, 1):
        log(f"[dim][{i}/{len(pdfs)}][/]", end=" ")
        status = process_pdf(pdf_info, dry_run=args.dry_run)
        stats[status if status in stats else "error"] += 1
        time.sleep(DELAY)  # Politesse envers le serveur SGG

    # Résumé final
    log(f"\n[bold]━━━ Résumé ━━━[/]")
    log(f"  [green]✅ Insérées   : {stats['inserted']}[/]")
    log(f"  [yellow]⚠  Doublons   : {stats['duplicate']}[/]")
    log(f"  [red]✗  Erreurs    : {stats['error']}[/]")

    if not args.dry_run and stats["inserted"] > 0:
        log(f"\n[bold green]✔ Étapes suivantes :[/]")
        log(f"  [dim]1. Enrichissement AI (optionnel, lent) :[/]")
        log(f"     [dim]python -X utf8 pipeline/enrich.py --only-missing --force[/]")
        log(f"  [dim]2. Regénérer le sitemap :[/]")
        log(f"     [dim]python -X utf8 pipeline/generate_sitemap.py[/]")
        log(f"  [dim]3. Rebuilder et uploader :[/]")
        log(f"     [dim]npm run build[/]")


if __name__ == "__main__":
    main()
