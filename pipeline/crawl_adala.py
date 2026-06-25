"""
JuriThèque — Crawleur Adala (adala.justice.gov.ma)
════════════════════════════════════════════════════════════════════════════════
Extrait les 7 867 textes juridiques du portail du Ministère de la Justice
marocain et les insère dans Supabase en mode metadata_only.

Les PDFs restent sur le serveur Adala — les visiteurs les voient via
Google Docs Viewer déjà intégré dans LawDetail.jsx.

Usage :
  python -X utf8 pipeline/crawl_adala.py                   # tout crawler
  python -X utf8 pipeline/crawl_adala.py --dry-run         # simuler sans écrire
  python -X utf8 pipeline/crawl_adala.py --pages 1-10      # pages 1 à 10 seulement
  python -X utf8 pipeline/crawl_adala.py --limit 50        # max 50 textes insérés
  python -X utf8 pipeline/crawl_adala.py --discover        # compter sans insérer

Prérequis :
  pip install httpx beautifulsoup4 python-dotenv rich requests

Variables .env :
  SUPABASE_URL  (ou VITE_SUPABASE_URL)
  SUPABASE_SERVICE_KEY
"""

import argparse
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
from bs4 import BeautifulSoup

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    console = Console()
    def log(msg, **kw): console.print(msg, **kw)
except ImportError:
    def log(msg, **kw): print(msg)

try:
    from title_lookup import get_best_title as _get_best_title
    from slug_utils import make_slug_from_law as _make_slug
    _LOOKUP_AVAILABLE = True
except ImportError:
    _LOOKUP_AVAILABLE = False
    def _get_best_title(*a, **kw): return None  # type: ignore
    def _make_slug(law_type, number, title_fr, date=""): return f"{law_type}-{number}".lower()  # type: ignore

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

ADALA_BASE = "https://adala.justice.gov.ma"
DELAY      = 1.5   # secondes entre les pages (politesse)
TODAY      = date.today().isoformat()

HTTP_HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ar,fr;q=0.8,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
}

# ── Correspondances arabes → français ──────────────────────────────────────────

TYPE_AR_TO_FR = {
    "ظهير": "Dahir",
    "ظهير شريف": "Dahir",
    "قانون تنظيمي": "Loi organique",
    "قانون إطار": "Loi-cadre",
    "قانون": "Loi",
    "مرسوم ملكي": "Décret royal",
    "مرسوم": "Décret",
    "قرار وزاري": "Arrêté ministériel",
    "قرار مشترك": "Arrêté conjoint",
    "قرار": "Arrêté",
    "دورية": "Circulaire",
    "منشور": "Circulaire",
    "مذكرة": "Note circulaire",
    "اتفاقية": "Convention",
    "معاهدة": "Traité",
    "بروتوكول": "Protocole",
    "رسالة ملكية": "Lettre royale",
    "خطاب ملكي": "Discours royal",
    "نظام": "Règlement",
    "مقرر": "Décision",
    "إعلان": "Déclaration",
}

DOMAIN_KEYWORDS_AR = {
    "travail":            ["الشغل", "العمل", "التشغيل", "العمال", "الأجراء", "النقابات", "الحوادث"],
    "penal":              ["الجنائي", "العقوبات", "الجرائم", "المسطرة الجنائية", "السجن", "الإجرام"],
    "commercial":         ["التجارة", "الشركات", "الأعمال", "التجاري", "البورصة", "الاستثمار", "الملكية"],
    "fiscal":             ["الضريبة", "الجبائي", "الجمارك", "الضرائب", "المالية العامة", "الميزانية"],
    "finances_publiques": ["المالية", "الميزانية", "المحاسبة العمومية", "الخزينة"],
    "administratif":      ["الإداري", "الوظيفة العمومية", "التنظيم", "المرافق العمومية", "البيئة", "التعمير"],
    "civil":              ["المدني", "الأسرة", "الزواج", "الطلاق", "الإرث", "العقار", "المسطرة المدنية"],
    "constitutionnel":    ["الدستور", "الدستوري", "البرلمان", "الانتخابات", "الأحزاب"],
    "numerique":          ["الرقمي", "الاتصالات", "التكنولوجيا", "الإنترنت", "البيانات", "المعلوميات"],
    "international":      ["الدولي", "المعاهدات", "الاتفاقيات الدولية", "القانون الدولي"],
    "bancaire":           ["البنوك", "المصارف", "الائتمان", "النقدي", "التأمين", "المالي"],
}


def detect_type_from_ar(type_ar: str, title_ar: str = "") -> str:
    """Convertit le type arabe en type français."""
    t = type_ar.strip()
    # Match exact
    if t in TYPE_AR_TO_FR:
        return TYPE_AR_TO_FR[t]
    # Match partiel
    for ar, fr in sorted(TYPE_AR_TO_FR.items(), key=lambda x: -len(x[0])):
        if ar in t or ar in title_ar:
            return fr
    return "Texte juridique"


def detect_domain_from_ar(title_ar: str, type_fr: str = "") -> str:
    """Détecte le domaine depuis un titre en arabe."""
    for domain, keywords in DOMAIN_KEYWORDS_AR.items():
        if any(kw in title_ar for kw in keywords):
            return domain
    # Fallback selon le type
    if type_fr in ("Dahir", "Loi organique", "Constitution"):
        return "constitutionnel"
    if type_fr in ("Convention", "Traité", "Protocole"):
        return "international"
    return "administratif"  # défaut pour Adala (beaucoup de textes administratifs)


def extract_number_from_ar(title_ar: str) -> str:
    """Extrait le numéro depuis un titre arabe."""
    # Patterns arabes : رقم 2.80.603, ن° 65.99, etc.
    patterns = [
        r'رقم\s+(\d[\d\.\-]+)',          # رقم 2.80.603
        r'رقم\s+(\d+)',                   # رقم 65
        r'(\d{1,3}[.\-]\d{2,3}[.\-]\d+)', # 1.04.22
        r'(\d{2,3}[.\-]\d{2,3})',         # 65.99
    ]
    for pattern in patterns:
        m = re.search(pattern, title_ar)
        if m:
            return m.group(1)
    return "N/A"


def extract_date_from_ar(title_ar: str) -> str | None:
    """Extrait la date depuis un titre arabe (format grégorien ou hégire → approximation)."""
    # Date grégorienne : يناير, فبراير, etc.
    months_ar = {
        'يناير': '01', 'فبراير': '02', 'مارس': '03', 'أبريل': '04',
        'ماي': '05', 'يونيو': '06', 'يوليوز': '07', 'غشت': '08',
        'شتنبر': '09', 'أكتوبر': '10', 'نونبر': '11', 'دجنبر': '12',
        'محرم': None, 'صفر': None,  # Hégire — pas de conversion simple
    }
    pattern = r'(\d{1,2})\s+(' + '|'.join(months_ar.keys()) + r')\s+(\d{4})'
    m = re.search(pattern, title_ar)
    if m:
        day, month_str, year = m.groups()
        month = months_ar.get(month_str)
        if month:
            return f"{year}-{month}-{int(day):02d}"
    # Juste l'année
    m2 = re.search(r'\b(19|20)\d{2}\b', title_ar)
    if m2:
        return f"{m2.group(0)}-01-01"
    return None


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:80].rsplit("-", 1)[0] if len(text) > 80 else text


# ── Supabase ────────────────────────────────────────────────────────────────────

def sb_number_exists(number: str) -> bool:
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
        log(f"    [red]✗ HTTP {e.response.status_code}: {e.response.text[:150]}[/]")
        return None
    except Exception as e:
        log(f"    [red]✗ Erreur: {e}[/]")
        return None


# ── Scraping d'une page Adala ──────────────────────────────────────────────────

def fetch_page(page_num: int, session: requests.Session) -> list[dict]:
    """
    Récupère une page de résultats Adala et retourne la liste des textes trouvés.

    Structure HTML confirmée :
      <div class="group w-full min-h-[200px] grid grid-cols-12 ...">   ← CARTE
        <div class="col-span-12 md:col-span-8 ...">
          <span class="...rounded-full...text-yellow-600">TYPE</span>  ← badge type
          <a href="/api/uploads/...pdf">TITRE COMPLET</a>              ← titre + lien
          <ul>
            <p>المادة: المادة الإدارية</p>    ← matière/domaine
            <p>رقم: 2.80.603</p>              ← numéro extrait
          </ul>
        </div>
        <div>إقرأ الآن</div>   ← bouton lecture (ignoré)
      </div>
    """
    url = f"{ADALA_BASE}/search?page={page_num}"
    for attempt in range(3):
        try:
            r = session.get(url, headers=HTTP_HEADERS, timeout=30)
            r.raise_for_status()
            break
        except Exception as e:
            wait = (attempt + 1) * 5
            if attempt < 2:
                time.sleep(wait)
            else:
                log(f"  [red]✗ Page {page_num} inaccessible après 3 tentatives: {e}[/]")
                return []

    soup  = BeautifulSoup(r.text, "html.parser")
    items = []
    seen_urls = set()

    # Partir des liens PDF uniques et remonter vers le div.group (carte)
    all_pdf_links = soup.find_all("a", href=re.compile(r"/api/uploads/.*\.pdf"))

    # Dédupliquer par href
    seen_hrefs = set()
    unique_pdf_links = []
    for a in all_pdf_links:
        href = a.get("href", "").split("#")[0]
        if href and href not in seen_hrefs:
            seen_hrefs.add(href)
            unique_pdf_links.append(a)

    # Pour chaque lien, remonter vers la carte parente (div avec class "group")
    processed_cards = set()
    for a_tag in unique_pdf_links:
        # Remonter jusqu'au div.group
        card = a_tag.parent
        for _ in range(8):
            if card is None:
                break
            classes = card.get("class", []) if hasattr(card, "get") else []
            if card.name == "div" and "group" in classes:
                break
            card = card.parent if hasattr(card, "parent") else None

        if card is None or id(card) in processed_cards:
            continue
        processed_cards.add(id(card))

        # ── Lien PDF (1er dans la carte) ──────────────────────────────────────
        a_tag = card.find("a", href=re.compile(r"/api/uploads/.*\.pdf"))
        if not a_tag:
            continue

        pdf_href   = a_tag.get("href", "").split("#")[0]
        if pdf_href in seen_urls:
            continue
        seen_urls.add(pdf_href)

        source_url = ADALA_BASE + pdf_href if pdf_href.startswith("/") else pdf_href

        # ── Titre (texte du lien) ──────────────────────────────────────────────
        title_ar = a_tag.get_text(strip=True)
        if not title_ar or len(title_ar) < 5:
            continue

        # ── Type (span badge jaune arrondi) ────────────────────────────────────
        type_span = card.find(
            "span",
            class_=lambda c: c and "rounded-full" in " ".join(c)
        )
        type_ar = type_span.get_text(strip=True) if type_span else ""

        # ── Numéro (depuis <p> contenant "رقم:") ───────────────────────────────
        number_explicit = ""
        for p_el in card.find_all("p"):
            txt = p_el.get_text(strip=True)
            if txt.startswith("رقم:"):
                number_explicit = txt.replace("رقم:", "").strip()
                break

        # ── Matière (depuis <p> contenant "المادة:") ───────────────────────────
        matiere_ar = ""
        for p_el in card.find_all("p"):
            txt = p_el.get_text(strip=True)
            if txt.startswith("المادة:"):
                matiere_ar = txt.replace("المادة:", "").strip()
                break

        items.append({
            "title_ar":       title_ar[:300],
            "type_ar":        type_ar,
            "number_explicit": number_explicit,   # déjà extrait depuis la fiche HTML
            "matiere_ar":     matiere_ar,
            "source_url":     source_url,
        })

    return items


def get_total_pages(session: requests.Session) -> int:
    """Récupère le nombre total de pages depuis la page 1."""
    try:
        r = session.get(f"{ADALA_BASE}/search?page=1", headers=HTTP_HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Chercher "X de Y résultats" ou pagination numérotée
        text = soup.get_text()

        # Pattern : "عرض 15 من 7867 عناصر" = affichage 15 de 7867 éléments
        m = re.search(r'من\s+([\d,]+)\s+عناصر', text)
        if m:
            total = int(m.group(1).replace(",", ""))
            return (total + 14) // 15  # 15 par page

        # Chercher la dernière page dans la pagination
        page_links = soup.find_all("a", href=re.compile(r"page=\d+"))
        if page_links:
            max_page = max(int(re.search(r'page=(\d+)', a["href"]).group(1))
                           for a in page_links if re.search(r'page=(\d+)', a.get("href", "")))
            return max_page

    except Exception as e:
        log(f"  [yellow]⚠ Impossible de déterminer le nombre de pages: {e}[/]")

    return 525  # fallback basé sur 7867 / 15


# ── Traitement d'un texte ───────────────────────────────────────────────────────

def process_item(item: dict, dry_run: bool, fast: bool = False) -> str:
    """
    Traite un texte Adala et l'insère dans Supabase.
    Retourne : 'inserted' | 'duplicate' | 'skipped' | 'error'
    """
    title_ar   = item["title_ar"]
    type_ar    = item.get("type_ar", "")
    source_url = item["source_url"]
    matiere_ar = item.get("matiere_ar", "")

    # Extraire métadonnées — priorité au numéro extrait par la fiche HTML
    number    = item.get("number_explicit") or extract_number_from_ar(title_ar)
    law_date  = extract_date_from_ar(title_ar)
    type_fr   = detect_type_from_ar(type_ar, title_ar)
    domain_id = detect_domain_from_ar(matiere_ar or title_ar, type_fr)

    # Vérification doublon par numéro
    if number != "N/A" and sb_number_exists(number):
        return "duplicate"

    # ── Title FR : lookup AI par numéro (plus de placeholder "— portail Adala") ─
    num_label = f" n°{number}" if number != "N/A" else ""
    title_fr  = None

    if not fast and _LOOKUP_AVAILABLE and number != "N/A":
        title_fr = _get_best_title(
            law_type=type_fr,
            number=number,
            date=law_date or "",
            title_ar=title_ar,
        )
        if title_fr:
            log(f"  [green]→ Titre lookup: {title_fr[:70]}[/]")

    if not title_fr:
        # Fallback : titre arabe traduit ou placeholder minimal
        title_fr = f"{type_fr}{num_label}" if num_label else f"{type_fr} (Adala)"

    # ── Canonical slug avec titre réel (meilleure qualité SEO) ──────────────
    import hashlib as _hl
    if number != "N/A":
        canonical_slug = _make_slug(type_fr, number, title_fr, law_date or "")
    else:
        h = _hl.md5(source_url.encode()).hexdigest()[:8]
        type_slug_fb = slugify(type_fr)
        canonical_slug = f"{type_slug_fb}-adala-{h}"

    if sb_slug_exists(canonical_slug):
        return "duplicate"

    if dry_run:
        return "inserted"

    record = {
        "number":                     number if number != "N/A" else f"adala-{canonical_slug[-8:]}",
        "title_fr":                   title_fr,
        "title_ar":                   title_ar,
        "type":                       type_fr,
        "status":                     "En vigueur",
        "date":                       law_date,
        "language":                   "Arabe",
        "domain_id":                  domain_id,
        "source_name":                "Adala",
        "source_url":                 source_url,
        "canonical_slug":             canonical_slug,
        "extraction_status":          "metadata_only",
        "extraction_confidence_score": 10,
        "is_publicly_indexable":      True,
        "needs_human_review":         True,
        "tags":                       [],
    }

    result = sb_insert(record)
    return "inserted" if result else "error"


# ── Point d'entrée ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="JuriThèque — Crawleur Adala (adala.justice.gov.ma)"
    )
    parser.add_argument("--dry-run",   action="store_true",
                        help="Simuler sans écrire en DB")
    parser.add_argument("--pages",     type=str, default=None,
                        help="Plage de pages à crawler, ex: '1-50' ou '10'")
    parser.add_argument("--limit",     type=int, default=None,
                        help="Arrêter après N insertions réussies")
    parser.add_argument("--discover",  action="store_true",
                        help="Compter les textes sans insérer")
    parser.add_argument("--fast",      action="store_true",
                        help="Mode rapide : pas de lookup AI pour les titres (titre placeholder conservé)")
    args = parser.parse_args()

    log("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log("[bold gold1]  JuriThèque — Crawleur Adala (justice.gov.ma)       [/]")
    log("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")

    if not SUPABASE_URL or not SUPABASE_KEY:
        log("[red]✗ SUPABASE_URL et SUPABASE_SERVICE_KEY requis dans .env[/]")
        sys.exit(1)

    if args.dry_run:
        log("[bold yellow]  [DRY-RUN] Aucune donnée ne sera écrite[/]")

    session = requests.Session()

    # Déterminer la plage de pages
    log("\n[dim]→ Détection du nombre total de pages...[/]")
    total_pages = get_total_pages(session)
    log(f"[dim]→ {total_pages} pages détectées (≈{total_pages * 15:,} textes)[/]")

    if args.pages:
        if "-" in args.pages:
            p_start, p_end = map(int, args.pages.split("-"))
        else:
            p_start = p_end = int(args.pages)
        page_range = range(p_start, min(p_end + 1, total_pages + 1))
    else:
        page_range = range(1, total_pages + 1)

    if args.discover:
        log(f"\n[bold]Mode découverte — {len(page_range)} pages à analyser[/]")
        total_found = 0
        for p in page_range:
            items = fetch_page(p, session)
            total_found += len(items)
            log(f"  Page {p}: {len(items)} textes")
            time.sleep(DELAY)
        log(f"\n[bold green]✔ Total trouvé : {total_found} textes sur {len(page_range)} pages[/]")
        return

    # Crawl principal
    log(f"\n[bold cyan]━━━ Crawl des pages {page_range.start} à {page_range.stop - 1} ━━━[/]")

    stats = {"inserted": 0, "duplicate": 0, "error": 0, "skipped": 0}
    total_processed = 0

    for page_num in page_range:
        items = fetch_page(page_num, session)

        if not items:
            log(f"  [dim]Page {page_num}: 0 textes (vide ou erreur)[/]")
            time.sleep(DELAY)
            continue

        new_on_page = 0
        for item in items:
            status = process_item(item, dry_run=args.dry_run, fast=args.fast)
            stats[status if status in stats else "error"] += 1
            total_processed += 1

            if status == "inserted":
                new_on_page += 1
                log(f"  [green]✅[/] {item['title_ar'][:70]}")

            if args.limit and stats["inserted"] >= args.limit:
                log(f"\n[yellow]→ Limite de {args.limit} insertions atteinte, arrêt.[/]")
                break

        log(f"  [dim]Page {page_num}/{page_range.stop-1} : "
            f"{new_on_page} nouveaux | {stats['duplicate']} doublons cumulés[/]")

        if args.limit and stats["inserted"] >= args.limit:
            break

        time.sleep(DELAY)

    # Résumé
    log(f"\n[bold]━━━ Résumé final ━━━[/]")
    log(f"  [green]✅ Insérés    : {stats['inserted']:,}[/]")
    log(f"  [yellow]⚠  Doublons   : {stats['duplicate']:,}[/]")
    log(f"  [red]✗  Erreurs    : {stats['error']:,}[/]")
    log(f"  [dim]   Traités    : {total_processed:,}[/]")

    if not args.dry_run and stats["inserted"] > 0:
        log(f"\n[bold green]✔ Étapes suivantes :[/]")
        log(f"  [dim]1. Regénérer le sitemap :[/]")
        log(f"     [dim]python -X utf8 pipeline/generate_sitemap.py[/]")
        log(f"  [dim]2. Rebuilder et uploader :[/]")
        log(f"     [dim]npm run build[/]")


if __name__ == "__main__":
    main()
