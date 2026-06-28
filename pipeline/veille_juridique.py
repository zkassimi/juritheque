"""
veille_juridique.py — Orchestrateur de veille juridique intelligente
=====================================================================
Surveille les sources officielles marocaines (URLs vérifiées).
Détecte : nouveaux textes, modifications, abrogations.

Usage :
  python pipeline/veille_juridique.py              # surveillance complète
  python pipeline/veille_juridique.py --dry-run    # aperçu sans écriture
  python pipeline/veille_juridique.py --source sgg_home
  python pipeline/veille_juridique.py --reset
"""

import os, sys, json, re, argparse, time
from pathlib import Path
from datetime import date, datetime
from urllib.parse import urljoin, urlparse

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Installe : pip install requests beautifulsoup4 lxml")
    sys.exit(1)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", ""))
STATE_FILE   = Path(__file__).parent / "veille_state.json"

HEADERS_SUPABASE = {
    "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json", "Prefer": "return=representation",
}
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-MA,fr;q=0.9,ar;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

console = Console()

sys.path.insert(0, str(Path(__file__).parent))
from veille_sources import SOURCES, SOURCES_BY_ID, SOURCES_OFFLINE, guess_domain
from veille_parser  import parse_relations, extract_law_number, extract_law_type, determine_action


# ── État persistant ─────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return _empty_state()

def _empty_state() -> dict:
    return {
        "last_bo_number": 7500,
        "last_run": None,
        "sources": {},
        "processed_urls": [],
        "stats": {"total_detected": 0, "total_queued": 0, "total_updated": 0, "total_repealed": 0},
    }

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

def reset_state():
    STATE_FILE.write_text(json.dumps(_empty_state(), indent=2), encoding="utf-8")
    console.print("[yellow]État réinitialisé.[/]")


# ── Supabase ────────────────────────────────────────────────────────────────────

def find_law_by_number(number: str) -> dict | None:
    if not number:
        return None
    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers=HEADERS_SUPABASE,
            params={"number": f"ilike.*{number}*", "select": "id,number,title_fr,status", "limit": "3"},
            timeout=10,
        )
        rows = resp.json() if resp.status_code == 200 and isinstance(resp.json(), list) else []
        return rows[0] if rows else None
    except Exception:
        return None

def url_in_queue(url: str) -> bool:
    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/import_queue",
            headers=HEADERS_SUPABASE,
            params={"pdf_url": f"eq.{url}", "select": "id", "limit": "1"},
            timeout=10,
        )
        rows = resp.json() if resp.status_code == 200 and isinstance(resp.json(), list) else []
        return len(rows) > 0
    except Exception:
        return False

def insert_queue(item: dict) -> bool:
    try:
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/import_queue",
            headers=HEADERS_SUPABASE,
            json=item,
            timeout=15,
        )
        return resp.status_code in (200, 201)
    except Exception:
        return False

def mark_needs_update(law_id: str, bo_ref: str) -> bool:
    try:
        resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers=HEADERS_SUPABASE,
            params={"id": f"eq.{law_id}"},
            json={"needs_update": True, "pending_bo": bo_ref, "last_checked": str(date.today())},
            timeout=15,
        )
        return resp.status_code in (200, 204)
    except Exception:
        return False


# ── Scraping ────────────────────────────────────────────────────────────────────

def fetch(url: str, timeout: int = 15) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=timeout, verify=False, allow_redirects=True)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "lxml")
        console.print(f"    [yellow]HTTP {resp.status_code}[/] {url[:60]}")
        return None
    except Exception as e:
        console.print(f"    [red]⚠️  {str(e)[:80]}[/]")
        return None


# Textes de liens génériques à ignorer (boutons "télécharger", "lire"...)
_GENERIC_LINK_TEXTS = {
    "تحميل", "إقرأ الآن", "télécharger", "download", "consulter",
    "lire", "voir", "pdf", "ouvrir", "accéder", "cliquer",
}

def _clean_title(el, full_url: str) -> str:
    """Extrait le meilleur titre disponible pour un lien PDF."""
    # 1. Attribut title
    t = (el.get("title") or "").strip()
    if t and t.lower() not in _GENERIC_LINK_TEXTS and len(t) > 5:
        return t[:250]
    # 2. Texte visible du lien (si non générique)
    txt = el.get_text(strip=True)
    if txt and txt.lower() not in _GENERIC_LINK_TEXTS and len(txt) > 5:
        return txt[:250]
    # 3. Texte du parent (td, li, div...)
    parent = el.find_parent(["td", "li", "div", "p", "span"])
    if parent:
        ptxt = parent.get_text(separator=" ", strip=True)
        if ptxt and len(ptxt) > 8:
            return ptxt[:250]
    # 4. Nom du fichier PDF
    filename = Path(urlparse(full_url).path).stem.replace("-", " ").replace("_", " ")
    return filename[:250] if filename else full_url


def extract_pdfs(soup: BeautifulSoup, base_url: str, selector: str = "a[href$='.pdf']") -> list[dict]:
    links = []
    seen  = set()
    try:
        elements = soup.select(selector)
    except Exception:
        elements = soup.find_all("a", href=re.compile(r"\.pdf$", re.I))

    for el in elements:
        href = el.get("href", "")
        if not href:
            continue
        full = urljoin(base_url, href)
        if full in seen or not full.startswith("http"):
            continue
        seen.add(full)
        title = _clean_title(el, full)
        links.append({"url": full, "title": title})
    return links


def scrape_pdf_list(source: dict, state: dict) -> list[dict]:
    """Scraper générique pour les pages avec liens PDF."""
    base = source.get("base_url", source["url"])
    soup = fetch(source["url"])
    if not soup:
        return []
    sel   = source.get("selectors", {}).get("list", "a[href$='.pdf']")
    links = extract_pdfs(soup, base, sel)

    # Filtres d'inclusion/exclusion par pattern URL (définis dans veille_sources.py)
    url_filter  = source.get("url_filter")
    url_exclude = source.get("url_exclude")
    if url_filter or url_exclude:
        before = len(links)
        if url_filter:
            links = [l for l in links if re.search(url_filter, l["url"])]
        if url_exclude:
            links = [l for l in links if not re.search(url_exclude, l["url"])]
        console.print(f"    Filtre URL : {before} → {len(links)} lien(s) retenus")
    else:
        console.print(f"    {len(links)} lien(s) PDF trouvé(s)")

    return _filter_new(links, state)


def scrape_bo_home(source: dict, state: dict) -> list[dict]:
    """SGG home page — extrait les liens BO récents."""
    soup = fetch(source["url"])
    if not soup:
        return []
    base  = source.get("base_url", "https://www.sgg.gov.ma")
    sel   = source.get("selectors", {}).get("pdf", "a[href*='/BO/']")
    links = extract_pdfs(soup, base, sel)
    console.print(f"    {len(links)} lien(s) BO récent(s) trouvé(s)")
    return _filter_new(links, state)


def scrape_bo_increment(source: dict, state: dict, dry_run: bool = False) -> list[dict]:
    """
    SGG — Essaie les numéros de BO depuis last_bo_number jusqu'au numéro actuel.
    URL template : https://www.sgg.gov.ma/BO/FR/{year}/BO_{number}_Fr.pdf
    """
    year       = date.today().year
    start      = state.get("last_bo_number", source.get("start_bo", 7500))
    found      = []
    processed  = set(state.get("processed_urls", []))

    console.print(f"    Vérification BOs depuis n°{start}...")

    for bo_num in range(start, start + 10):  # max 10 nouveaux par run
        url_fr = source["bo_url_fr"].format(year=year, number=bo_num)
        url_ar = source["bo_url_ar"].format(year=year, number=bo_num)

        if url_fr in processed:
            continue

        try:
            r = requests.head(url_fr, headers=HTTP_HEADERS, timeout=8, verify=False, allow_redirects=True)
            if r.status_code == 200:
                found.append({"url": url_fr, "title": f"Bulletin Officiel n° {bo_num} ({year}) — FR"})
                found.append({"url": url_ar, "title": f"Bulletin Officiel n° {bo_num} ({year}) — AR"})
                if not dry_run:
                    state["last_bo_number"] = bo_num + 1
                console.print(f"    ✅ BO {bo_num} trouvé !")
            elif r.status_code == 404:
                break  # numéro inexistant = fin des BOs disponibles
        except Exception:
            break
        time.sleep(0.3)

    return _filter_new(found, state)


def _filter_new(links: list[dict], state: dict) -> list[dict]:
    """Exclut les URLs déjà traitées."""
    processed = set(state.get("processed_urls", []))
    return [l for l in links if l["url"] not in processed]


# ── Traitement ─────────────────────────────────────────────────────────────────

def process_item(item: dict, state: dict, dry_run: bool) -> str:
    number   = item.get("law_number")
    action   = item.get("action", "new")
    existing = find_law_by_number(number) if number else None

    if existing and action in ("update", "repeal"):
        if not dry_run:
            mark_needs_update(existing["id"], item.get("pdf_url", "")[:50])
            state["stats"]["total_updated"] += 1
            if action == "repeal":
                state["stats"]["total_repealed"] += 1
        return f"⚠️  {action.upper()} → {existing.get('number', number)}"

    elif existing and action == "new":
        return f"⏭️  DOUBLON → {existing.get('number', number)}"

    else:
        queue_item = {
            "source":       item["source"],
            "pdf_url":      item.get("url"),
            "bo_url":       item.get("bo_url", item.get("url")),
            "title_fr":     item.get("title", "")[:300],
            "law_number":   number,
            "law_type":     item.get("law_type", ""),
            "domain_guess": item.get("domain", ""),
            "action":       "new",
            "status":       "pending",
        }
        if not dry_run and not url_in_queue(item.get("url", "")):
            insert_queue(queue_item)
            state["stats"]["total_queued"] += 1
        return f"🆕  NEW → {item.get('title', '')[:55]}"


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source",  help="ID source unique (ex: adala)")
    parser.add_argument("--reset",   action="store_true")
    args = parser.parse_args()

    console.print("\n[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    console.print("[bold]  🔍 Veille Juridique JuriThèque[/]")
    console.print("[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

    if args.reset:
        reset_state()
        return

    if args.dry_run:
        console.print("[yellow]Mode DRY-RUN — aucune écriture en base[/]\n")

    if not SUPABASE_URL or not SUPABASE_KEY:
        console.print("[red]❌ Variables SUPABASE_URL / SUPABASE_KEY manquantes[/]")
        sys.exit(1)

    state = load_state()
    state["last_run"] = datetime.now().isoformat()

    if args.source:
        sources = [SOURCES_BY_ID[args.source]] if args.source in SOURCES_BY_ID else []
        if not sources:
            console.print(f"[red]Source inconnue : {args.source}[/]")
            console.print("Disponibles : " + ", ".join(SOURCES_BY_ID.keys()))
            sys.exit(1)
    else:
        sources = [s for s in SOURCES if s.get("active", True)]

    console.print(f"  [bold]{len(sources)} source(s) active(s)[/]  |  "
                  f"[dim]{len(SOURCES_OFFLINE)} hors ligne[/]")
    console.print(f"  Dernier BO connu : n°{state.get('last_bo_number', '?')}")
    console.print(f"  URLs déjà traitées : {len(state.get('processed_urls', []))}\n")

    all_results = []

    for source in sources:
        sid   = source["id"]
        stype = source.get("type", "pdf_list")
        console.print(f"  [cyan]→ {source['label']}[/]")

        # Scraper selon le type
        if stype == "bo_home":
            raw_items = scrape_bo_home(source, state)
        elif stype == "bo_increment":
            raw_items = scrape_bo_increment(source, state, dry_run=args.dry_run)
        else:
            raw_items = scrape_pdf_list(source, state)

        # Enrichir chaque item
        for raw in raw_items:
            title     = raw.get("title", "")
            number    = extract_law_number(title)
            law_type  = extract_law_type(title)
            action    = determine_action(title)
            domain    = guess_domain(title)

            item = {**raw, "source": sid, "law_number": number,
                    "law_type": law_type, "action": action, "domain": domain}

            result = process_item(item, state, dry_run=args.dry_run)
            all_results.append((sid, title[:60], result))

            if raw.get("url"):
                urls = state.setdefault("processed_urls", [])
                if raw["url"] not in urls:
                    urls.append(raw["url"])

            state["stats"]["total_detected"] += 1
            time.sleep(0.2)

        state.setdefault("sources", {})[sid] = {
            "last_checked": str(date.today()),
            "items_found":  len(raw_items),
        }
        if not args.dry_run:
            save_state(state)

    # Limiter processed_urls à 5000
    state["processed_urls"] = list(set(state.get("processed_urls", [])))[-5000:]
    if not args.dry_run:
        save_state(state)

    # ── Rapport ────────────────────────────────────────────────────────────────
    console.print("\n[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    console.print("[bold]  Rapport de veille[/]")
    console.print("[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

    if all_results:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Source",  style="cyan", width=18)
        table.add_column("Titre",   width=55)
        table.add_column("Action",  width=30)
        for sid, title, result in all_results:
            table.add_row(sid, title, result)
        console.print(table)
    else:
        console.print("  Aucun nouveau texte détecté.")

    if SOURCES_OFFLINE:
        console.print(f"\n  [dim]⚠️  {len(SOURCES_OFFLINE)} source(s) hors ligne (URLs à corriger) :[/]")
        for s in SOURCES_OFFLINE:
            console.print(f"  [dim]   • {s['id']:20s} — {s['reason']}[/]")

    s = state["stats"]
    console.print(f"\n  Total détectés    : [bold]{s['total_detected']}[/]")
    console.print(f"  → Nouveaux (queue): [green]{s['total_queued']}[/]")
    console.print(f"  → À mettre à jour : [yellow]{s['total_updated']}[/]")
    console.print(f"  → Abrogés         : [red]{s['total_repealed']}[/]")
    if args.dry_run:
        console.print("\n  [yellow][DRY-RUN] Rien n'a été écrit en base.[/]")
    console.print()


if __name__ == "__main__":
    main()
