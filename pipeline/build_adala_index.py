"""
build_adala_index.py — Crawle toutes les pages Adala et construit adala_index.json

Index : { "2.03.530": { "title_ar": "...", "pdf_url": "...", "type_ar": "..." }, ... }

Usage :
  python build_adala_index.py           # crawl complet (~392 pages, ~45 min)
  python build_adala_index.py --resume  # reprend où on s'est arrêtés
  python build_adala_index.py --pages 1-50  # pages spécifiques seulement
"""

import json, re, sys, time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

import requests
from bs4 import BeautifulSoup

try:
    import urllib3; urllib3.disable_warnings()
except ImportError:
    pass

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn
    console = Console()
    def log(m): console.print(m)
except ImportError:
    def log(m): print(m)

BASE        = "https://adala.justice.gov.ma"
INDEX_PATH  = Path(__file__).parent / "adala_index.json"
STATE_PATH  = Path(__file__).parent / "adala_index_state.json"
DELAY       = 1.2   # secondes entre pages (poli)
MAX_PAGES   = 450   # sécurité
HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ar,fr;q=0.8,en;q=0.5",
}


def normalize_num(n: str) -> str:
    """2-03-530 / 2/03/530 → 2.03.530"""
    n = re.sub(r"[\-\s/]+", ".", n.strip().lower())
    n = re.sub(r"\.+", ".", n).strip(".")
    return n


def parse_page(html: str) -> list[dict]:
    """Extrait les entrées d'une page Adala."""
    soup   = BeautifulSoup(html, "html.parser")
    items  = []
    seen   = set()

    pdf_links = soup.find_all("a", href=re.compile(r"/api/uploads/.*\.pdf"))

    # Dédupliquer par href
    unique = []
    seen_hrefs = set()
    for a in pdf_links:
        h = a.get("href", "").split("#")[0]
        if h and h not in seen_hrefs:
            seen_hrefs.add(h)
            unique.append(a)

    processed = set()
    for a_tag in unique:
        # Remonter jusqu'au div.group (carte)
        card = a_tag.parent
        for _ in range(8):
            if card is None: break
            if card.name == "div" and "group" in (card.get("class") or []):
                break
            card = getattr(card, "parent", None)

        if card is None or id(card) in processed:
            continue
        processed.add(id(card))

        # PDF
        a_pdf = card.find("a", href=re.compile(r"/api/uploads/.*\.pdf"))
        if not a_pdf:
            continue
        pdf_href = a_pdf["href"].split("#")[0]
        pdf_url  = BASE + pdf_href if pdf_href.startswith("/") else pdf_href

        # Titre arabe
        title_ar = a_pdf.get_text(strip=True)
        if not title_ar or len(title_ar) < 5:
            continue

        # Type (span badge)
        type_span = card.find("span", class_=lambda c: c and "rounded-full" in " ".join(c))
        type_ar   = type_span.get_text(strip=True) if type_span else ""

        # Numéro explicite dans <p>رقم:</p>
        number_raw = ""
        for p in card.find_all("p"):
            t = p.get_text(strip=True)
            if t.startswith("رقم:"):
                number_raw = t.replace("رقم:", "").strip()
                break

        # Si pas de numéro explicit → extraire du titre
        if not number_raw:
            m = re.search(r'(\d{1,2}[.\-]\d{2,3}[.\-]\d+)', title_ar)
            if m:
                number_raw = m.group(1)

        if not number_raw:
            continue  # sans numéro, inutilisable pour le matching

        number_key = normalize_num(number_raw)
        if not number_key or number_key in seen:
            continue
        seen.add(number_key)

        items.append({
            "number_key": number_key,
            "number_raw": number_raw,
            "title_ar":   title_ar,
            "type_ar":    type_ar,
            "pdf_url":    pdf_url,
        })

    return items


def count_pages(session: requests.Session) -> int:
    """Détecte le nombre total de pages."""
    r = session.get(f"{BASE}/search?page=1", headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    # Chercher la dernière page dans la pagination
    page_links = soup.find_all("a", href=re.compile(r"[?&]page=\d+"))
    max_p = 1
    for a in page_links:
        m = re.search(r"page=(\d+)", a["href"])
        if m:
            max_p = max(max_p, int(m.group(1)))
    # Fallback : chercher le texte "Total X"
    if max_p == 1:
        text = soup.get_text()
        m = re.search(r'(\d+)\s*(?:نتيجة|résultats?|results?)', text)
        if m:
            total = int(m.group(1))
            max_p = (total // 20) + 1
    return max_p or 400


# ── Parse args ────────────────────────────────────────────────────────────────
resume     = "--resume" in sys.argv
pages_arg  = next((a for a in sys.argv if a.startswith("--pages=")), None)
page_start, page_end = 1, MAX_PAGES

if pages_arg:
    parts = pages_arg.replace("--pages=", "").split("-")
    page_start = int(parts[0])
    page_end   = int(parts[1]) if len(parts) > 1 else page_start

# ── Charger index existant ────────────────────────────────────────────────────
index: dict = {}
last_page   = 0

if INDEX_PATH.exists():
    with open(INDEX_PATH, encoding="utf-8") as f:
        index = json.load(f)
    log(f"[dim]→ Index existant chargé : {len(index)} entrées[/]")

if resume and STATE_PATH.exists():
    with open(STATE_PATH) as f:
        state   = json.load(f)
        last_page = state.get("last_page", 0)
    log(f"[dim]→ Reprise depuis la page {last_page + 1}[/]")
    page_start = max(page_start, last_page + 1)

# ── Crawl ─────────────────────────────────────────────────────────────────────
log(f"\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
log(f"[bold gold1]  build_adala_index.py  pages {page_start}–{page_end}[/]")
log(f"[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

session = requests.Session()
session.verify = False

# Détecter nb pages réel
log("[dim]Détection du nombre de pages...[/]")
try:
    total_pages = count_pages(session)
    page_end    = min(page_end, total_pages)
    log(f"[dim]→ {total_pages} pages détectées[/]\n")
except Exception:
    log("[yellow]⚠ Impossible de détecter le nb de pages, on utilisera {MAX_PAGES} max[/]")

new_count    = 0
empty_streak = 0

for page_num in range(page_start, page_end + 1):
    try:
        r = session.get(f"{BASE}/search?page={page_num}", headers=HEADERS, timeout=25)
        r.raise_for_status()
    except Exception as e:
        log(f"  [red]✗ Page {page_num} erreur: {e}[/]")
        empty_streak += 1
        if empty_streak >= 5:
            log("[red]5 erreurs consécutives → arrêt[/]")
            break
        time.sleep(5)
        continue

    items = parse_page(r.text)

    if not items:
        empty_streak += 1
        if empty_streak >= 3:
            log(f"  [dim]Page {page_num} vide (streak={empty_streak}) → fin du contenu[/]")
            if empty_streak >= 5:
                break
        time.sleep(DELAY)
        continue

    empty_streak = 0
    added = 0
    for item in items:
        key = item["number_key"]
        if key not in index:
            index[key] = {
                "title_ar": item["title_ar"],
                "type_ar":  item["type_ar"],
                "pdf_url":  item["pdf_url"],
                "number_raw": item["number_raw"],
            }
            new_count += 1
            added += 1

    # Log progression toutes les 10 pages
    if page_num % 10 == 0 or added > 0:
        log(f"  p{page_num:3d} → +{added:2d} nouvelles entrées  total={len(index)}")

    # Sauvegarde toutes les 20 pages
    if page_num % 20 == 0:
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        with open(STATE_PATH, "w") as f:
            json.dump({"last_page": page_num, "total_entries": len(index)}, f)
        log(f"  [dim]💾 Sauvegarde : {len(index)} entrées (page {page_num})[/]")

    time.sleep(DELAY)

# Sauvegarde finale
with open(INDEX_PATH, "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)
with open(STATE_PATH, "w") as f:
    json.dump({"last_page": page_num, "total_entries": len(index)}, f)

log(f"\n[bold green]✅ Index complet : {len(index)} lois indexées[/]")
log(f"   Nouvelles entrées ce run : {new_count}")
log(f"   Fichier : {INDEX_PATH}")
