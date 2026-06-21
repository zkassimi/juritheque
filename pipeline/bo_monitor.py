"""
JuriThèque — Bulletin Officiel Monitor
════════════════════════════════════════════════════════════════════
Vérifie automatiquement les nouveaux numéros du Bulletin Officiel
sur sgg.gov.ma, télécharge les PDFs et les insère dans Supabase
via le pipeline extract.py existant.

Usage:
  python bo_monitor.py              # Vérifie + télécharge les nouveaux BOs
  python bo_monitor.py --dry-run    # Affiche ce qui serait téléchargé
  python bo_monitor.py --force      # Re-télécharge même si déjà vu
  python bo_monitor.py --install    # Installe la tâche planifiée Windows (hebdo)
  python bo_monitor.py --uninstall  # Supprime la tâche planifiée

Requirements:
  pip install requests beautifulsoup4 lxml python-dotenv rich
"""

import os, sys, json, time, subprocess, re
from pathlib import Path
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import print as rprint

load_dotenv()
console = Console()

# ── Config ─────────────────────────────────────────────────────────────────
PDF_FOLDER   = Path("./pdfs")
STATE_FILE   = Path("./bo_state.json")   # tracks which BOs we've already downloaded
DRY_RUN      = "--dry-run"   in sys.argv
FORCE        = "--force"     in sys.argv
INSTALL      = "--install"   in sys.argv
UNINSTALL    = "--uninstall" in sys.argv
PDF_FOLDER.mkdir(exist_ok=True)

BASE_URL  = "https://www.sgg.gov.ma"
BO_PAGE   = f"{BASE_URL}/arabe/BulletinOfficiel.aspx"
DELAY     = 2.0

HTTP_HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "fr-MA,fr;q=0.9,ar;q=0.8",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer":         BASE_URL,
}

# ── State management ────────────────────────────────────────────────────────
def load_state() -> dict:
    """Load the list of already-downloaded BO issue numbers."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {"downloaded": [], "last_check": None}

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

# ── ASP.NET form handler ────────────────────────────────────────────────────
def get_form_state(session: requests.Session) -> dict:
    """Fetch the BO page and extract ASP.NET hidden form fields."""
    try:
        resp = session.get(BO_PAGE, headers=HTTP_HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        fields = {}
        for hidden in soup.find_all("input", {"type": "hidden"}):
            name = hidden.get("name", "")
            val  = hidden.get("value", "")
            if name:
                fields[name] = val
        return fields
    except Exception as e:
        console.print(f"[red]Erreur lors du chargement de la page BO: {e}[/red]")
        return {}

def search_bo_issues(session: requests.Session, form_state: dict) -> list[dict]:
    """
    Submit the search form to get the list of BO issues.
    Returns a list of {number, date, url_ar, url_fr} dicts.
    """
    # Build POST payload — ASP.NET WebForms requires all hidden fields
    payload = dict(form_state)

    # Trigger the search button via __doPostBack
    payload["__EVENTTARGET"]   = "dnn$ctr3108$Aggregator$ctr3109$View$searchBt"
    payload["__EVENTARGUMENT"] = ""

    # Optional: search last 30 days
    date_from = (datetime.now() - timedelta(days=60)).strftime("%d/%m/%Y")
    date_to   = datetime.now().strftime("%d/%m/%Y")

    # Try to find the date field names in the form
    for key in payload:
        if "date" in key.lower() and "from" in key.lower():
            payload[key] = date_from
        if "date" in key.lower() and "to" in key.lower():
            payload[key] = date_to

    try:
        resp = session.post(BO_PAGE, data=payload, headers=HTTP_HEADERS, timeout=30)
        resp.raise_for_status()
        return parse_bo_results(resp.text)
    except Exception as e:
        console.print(f"[yellow]POST search failed ({e}) — trying direct page parse[/yellow]")
        # Fallback: parse the original GET response for any PDF links
        try:
            resp2 = session.get(BO_PAGE, headers=HTTP_HEADERS, timeout=20)
            return parse_bo_results(resp2.text)
        except:
            return []

def parse_bo_results(html: str) -> list[dict]:
    """Extract BO issue list from the page HTML."""
    soup    = BeautifulSoup(html, "lxml")
    results = []

    # Look for table rows containing BO info
    # Typical structure: | عدد | تاريخ | تحميل (PDF link) |
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        # Try to find issue number and PDF links
        pdf_links = row.find_all("a", href=lambda h: h and ".pdf" in h.lower())
        if not pdf_links:
            # Also look for links with BO in the URL
            pdf_links = row.find_all("a", href=lambda h: h and (
                "BO" in (h or "") or "bulletin" in (h or "").lower()
            ))

        if not pdf_links:
            continue

        issue_num = None
        issue_date = None
        # Extract issue number from cells
        for cell in cells:
            text = cell.get_text(strip=True)
            if re.match(r'^\d{4,5}$', text):
                issue_num = text
            date_match = re.search(r'\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}', text)
            if date_match:
                issue_date = date_match.group()

        for link in pdf_links:
            href = link.get("href", "")
            if not href.startswith("http"):
                href = BASE_URL + "/" + href.lstrip("/")
            lang = "ar" if any(x in href.lower() for x in ["_ar", "arab"]) else "fr"
            results.append({
                "number": issue_num or Path(href).stem,
                "date":   issue_date,
                "url":    href,
                "lang":   lang,
            })

    # Deduplicate by URL
    seen = set()
    unique = []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    return unique


def try_known_url_patterns(issue_num: int, year: int) -> list[str]:
    """
    Try known URL patterns for BO PDFs.
    sgg.gov.ma changes patterns over time — we try several.
    """
    patterns = [
        f"{BASE_URL}/BO/Bo_ar/{year}/BO{issue_num}_Ar.pdf",
        f"{BASE_URL}/BO/Bo_fr/{year}/BO{issue_num}_Fr.pdf",
        f"{BASE_URL}/Portals/0/BO/{year}/BO{issue_num}_ar.pdf",
        f"{BASE_URL}/Portals/1/BO/BO{issue_num}_ar.pdf",
        f"{BASE_URL}/Portals/0/BO/BO{issue_num}.pdf",
        f"{BASE_URL}/arabe/LinkClick.aspx?fileticket=BO{issue_num}",
    ]
    valid = []
    for url in patterns:
        try:
            r = requests.head(url, headers=HTTP_HEADERS, timeout=8, allow_redirects=True)
            if r.status_code == 200:
                valid.append(url)
        except:
            pass
    return valid


def scan_recent_bo_numbers(start: int = None, count: int = 10) -> list[dict]:
    """
    Scan recent BO issue numbers by trying URL patterns.
    BO issues are published ~2x per week, numbered sequentially.
    """
    if start is None:
        start = 7500  # approximate current number (May 2026)

    found = []
    year  = datetime.now().year

    console.print(f"\n[dim]Scanning BO #{start} to #{start + count}...[/dim]")
    for num in range(start, start + count):
        urls = try_known_url_patterns(num, year)
        if urls:
            found.append({"number": str(num), "date": None, "urls": urls})
            console.print(f"  [green]✓ BO #{num} trouvé: {len(urls)} fichier(s)[/green]")
        time.sleep(0.3)

    return found


# ── Download ────────────────────────────────────────────────────────────────
def download_bo(issue: dict, state: dict) -> list[str]:
    """Download a BO issue. Returns list of downloaded file paths."""
    num = str(issue.get("number", ""))

    if not FORCE and num in state["downloaded"]:
        console.print(f"  [dim]BO #{num} déjà téléchargé — ignoré[/dim]")
        return []

    urls = issue.get("urls") or ([issue["url"]] if issue.get("url") else [])
    downloaded = []

    for url in urls:
        filename = PDF_FOLDER / f"BO_{num}_{Path(url).name}"
        if filename.exists() and not FORCE:
            downloaded.append(str(filename))
            continue
        try:
            r = requests.get(url, headers=HTTP_HEADERS, timeout=120, stream=True)
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            size_kb = filename.stat().st_size // 1024
            console.print(f"  ✓ [green]{filename.name}[/green] ({size_kb} KB)")
            downloaded.append(str(filename))
            time.sleep(DELAY)
        except Exception as e:
            console.print(f"  [red]✗ {url}: {e}[/red]")

    if downloaded:
        state["downloaded"].append(num)

    return downloaded


# ── Windows Task Scheduler ──────────────────────────────────────────────────
def install_scheduled_task():
    """Install a weekly Windows Task Scheduler job to run this script."""
    script_path = Path(__file__).resolve()
    python_path = sys.executable
    task_name   = "JuriTheque_BO_Monitor"

    # Run every Monday at 08:00
    xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-01T08:00:00</StartBoundary>
      <ScheduleByWeek>
        <WeeksInterval>1</WeeksInterval>
        <DaysOfWeek><Monday /></DaysOfWeek>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>"{script_path}"</Arguments>
      <WorkingDirectory>{script_path.parent}</WorkingDirectory>
    </Exec>
  </Actions>
  <Settings>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
  </Settings>
</Task>"""

    xml_file = Path("./bo_task.xml")
    xml_file.write_text(xml, encoding="utf-16")

    result = subprocess.run(
        ["schtasks", "/Create", "/TN", task_name, "/XML", str(xml_file), "/F"],
        capture_output=True, text=True
    )
    xml_file.unlink(missing_ok=True)

    if result.returncode == 0:
        console.print(f"[bold green]✅ Tâche planifiée installée:[/bold green]")
        console.print(f"   Nom : {task_name}")
        console.print(f"   Fréquence : chaque lundi à 08:00")
        console.print(f"   Script : {script_path}")
    else:
        console.print(f"[red]Erreur: {result.stderr}[/red]")
        console.print("[yellow]Essayez en mode Administrateur[/yellow]")


def uninstall_scheduled_task():
    task_name = "JuriTheque_BO_Monitor"
    result = subprocess.run(
        ["schtasks", "/Delete", "/TN", task_name, "/F"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        console.print(f"[green]✅ Tâche '{task_name}' supprimée[/green]")
    else:
        console.print(f"[red]{result.stderr}[/red]")


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    console.print("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    console.print("[bold gold1]  JuriThèque — Bulletin Officiel Monitor [/]")
    console.print(f"[bold gold1]  {datetime.now().strftime('%Y-%m-%d %H:%M')}[/]")
    console.print("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

    if INSTALL:
        install_scheduled_task()
        return
    if UNINSTALL:
        uninstall_scheduled_task()
        return

    state = load_state()
    state["last_check"] = datetime.now().isoformat()

    # ── Step 1: Try ASP.NET form scraping ──────────────────────────────────
    console.print("[cyan]1. Tentative scraping formulaire ASP.NET...[/cyan]")
    session    = requests.Session()
    form_state = get_form_state(session)
    issues     = []

    if form_state:
        issues = search_bo_issues(session, form_state)
        console.print(f"   → {len(issues)} issues trouvées via formulaire")

    # ── Step 2: Fallback — scan sequential BO numbers ──────────────────────
    if not issues:
        console.print("[cyan]2. Fallback: scan des numéros récents...[/cyan]")
        already = [int(n) for n in state["downloaded"] if n.isdigit()]
        start   = max(already) + 1 if already else 7490
        found   = scan_recent_bo_numbers(start=start, count=20)
        for f in found:
            issues.append(f)

    if not issues:
        console.print("[yellow]Aucun nouveau Bulletin Officiel trouvé.[/yellow]")
        console.print("[dim]Le site sgg.gov.ma utilise un formulaire dynamique difficile à scraper.[/dim]")
        console.print("[dim]→ Téléchargement manuel sur https://www.sgg.gov.ma/arabe/BulletinOfficiel.aspx[/dim]")
        save_state(state)
        return

    # ── Step 3: Display ────────────────────────────────────────────────────
    table = Table(title=f"{len(issues)} Bulletins Officiels trouvés")
    table.add_column("N°",     style="cyan",  width=8)
    table.add_column("Date",   style="dim",   width=12)
    table.add_column("Statut", style="green", width=12)
    table.add_column("URL",    style="dim",   width=50)

    for issue in issues:
        num    = str(issue.get("number", "?"))
        status = "[dim]déjà téléchargé[/dim]" if (num in state["downloaded"] and not FORCE) else "[green]nouveau[/green]"
        urls   = issue.get("urls") or ([issue.get("url", "")])
        table.add_row(num, issue.get("date") or "—", status, (urls[0] if urls else "")[:50])

    console.print(table)

    if DRY_RUN:
        console.print("\n[yellow]Mode dry-run — aucun téléchargement.[/yellow]")
        save_state(state)
        return

    # ── Step 4: Download new issues ────────────────────────────────────────
    total_downloaded = []
    for issue in issues:
        files = download_bo(issue, state)
        total_downloaded.extend(files)

    save_state(state)

    # ── Step 5: Auto-launch extract.py if new PDFs downloaded ──────────────
    if total_downloaded:
        console.print(f"\n[bold green]✅ {len(total_downloaded)} PDFs téléchargés[/bold green]")
        console.print("[cyan]→ Lancement automatique de extract.py...[/cyan]")
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "extract.py")],
            cwd=str(Path(__file__).parent),
        )
        if result.returncode == 0:
            console.print("[bold green]✅ Pipeline terminé — textes insérés dans Supabase[/bold green]")
        else:
            console.print("[yellow]⚠ extract.py a rencontré des erreurs[/yellow]")
    else:
        console.print("\n[yellow]Aucun nouveau BO à traiter.[/yellow]")

    console.print(f"\n[dim]Prochain check recommandé: lundi prochain[/dim]")
    console.print(f"[dim]Pour installer le check automatique: python bo_monitor.py --install[/dim]")


if __name__ == "__main__":
    main()
