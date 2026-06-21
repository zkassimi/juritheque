"""
enrich_sources.py
─────────────────
Enrichit les lois existantes avec :
  - source_name  : nom lisible de la source (SGG, Adala, ANRT, BKAM, ...)
  - source_url   : URL officielle (= pdf_url si disponible)
  - bo_number    : numéro du Bulletin Officiel extrait du contenu (ex: "7432")
  - bo_date      : date de parution au BO

Usage :
  python pipeline/enrich_sources.py              # enrichit tout
  python pipeline/enrich_sources.py --dry-run    # sans écriture
  python pipeline/enrich_sources.py --force      # écrase les valeurs existantes
  python pipeline/enrich_sources.py --limit 50   # test sur 50 lois
"""

import os, re, sys, json, argparse
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track

load_dotenv()
console = Console()

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    console.print("[red]❌ Variables SUPABASE_URL / SUPABASE_SERVICE_KEY manquantes dans .env[/]")
    sys.exit(1)

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}

# ── Mapping domaine → source par défaut ──────────────────────────────────────
DOMAIN_SOURCE_MAP = {
    "numerique":         ("ANRT",    "https://www.anrt.ma"),
    "bancaire":          ("BKAM",    "https://www.bkam.ma"),
    "finances_publiques":("MEF",     "https://www.finances.gov.ma"),
    "fiscal":            ("MEF",     "https://www.finances.gov.ma"),
    "travail":           ("MMSP",    "https://www.mmsp.gov.ma"),
    "constitutionnel":   ("SGG",     "https://www.sgg.gov.ma"),
    "international":     ("WIPO",    "https://www.wipo.int"),
}

# ── Mapping hostname → (source_name, label) ──────────────────────────────────
HOSTNAME_SOURCE_MAP = {
    "sgg.gov.ma":                      "SGG",
    "adala.justice.gov.ma":            "Adala",
    "adala2.justice.gov.ma":           "Adala",
    "anrt.ma":                         "ANRT",
    "bkam.ma":                         "BKAM",
    "finances.gov.ma":                 "MEF",
    "lof.finances.gov.ma":             "MEF",
    "dgi.gov.ma":                      "DGI",
    "mmsp.gov.ma":                     "MMSP",
    "mem.gov.ma":                      "MEM",
    "environnement.gov.ma":            "MECDD",
    "chambredesrepresentants.ma":      "Parlement",
    "wipo.int":                        "WIPO",
    "unodc.org":                       "UNODC",
    "maroclear.ma":                    "Maroclear",
    "ism.ma":                          "ISM",
}

# ── Regex extraction numéro de BO ─────────────────────────────────────────────
BO_PATTERNS = [
    # "Bulletin Officiel n° 7432" ou "B.O. n° 7432"
    re.compile(r'[Bb]ulletin\s+[Oo]fficiel\s+n[°o\.\s]*\s*(\d{4,5})', re.IGNORECASE),
    re.compile(r'\bB\.?\s*O\.?\s*n[°o\.\s]*\s*(\d{4,5})', re.IGNORECASE),
    # "BO 7432"
    re.compile(r'\bBO\s+(\d{4,5})\b'),
    # Dans un titre de type "... – BO n° 7432 du ..."
    re.compile(r'B\.O\.\s*[Nn]°?\s*(\d{4,5})'),
]

# Regex date BO : "du 21 août 2025" après le numéro
BO_DATE_PATTERN = re.compile(
    r'(?:du|le)\s+(\d{1,2})\s+'
    r'(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)'
    r'\s+(\d{4})',
    re.IGNORECASE
)

MONTH_MAP = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
}


def detect_source(law: dict) -> tuple[str | None, str | None]:
    """Retourne (source_name, source_url) depuis pdf_url ou domain_id."""
    pdf_url = law.get("pdf_url") or ""
    domain  = law.get("domain_id") or ""

    # 1. Depuis le hostname de pdf_url
    if pdf_url:
        try:
            host = urlparse(pdf_url).netloc.lower().replace("www.", "")
            for pattern, name in HOSTNAME_SOURCE_MAP.items():
                if pattern in host:
                    return name, pdf_url
        except Exception:
            pass

    # 2. Depuis le domaine juridique
    if domain in DOMAIN_SOURCE_MAP:
        name, base_url = DOMAIN_SOURCE_MAP[domain]
        return name, pdf_url or base_url

    # 3. Fallback SGG si pdf_url présent mais non reconnu
    if pdf_url:
        return "Source officielle", pdf_url

    return None, None


def extract_bo_number(text: str) -> str | None:
    """Extrait le numéro de BO depuis le texte."""
    if not text:
        return None
    for pat in BO_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1).strip()
    return None


def extract_bo_date(text: str) -> str | None:
    """Extrait la date de parution au BO (ISO format YYYY-MM-DD)."""
    if not text:
        return None
    m = BO_DATE_PATTERN.search(text)
    if m:
        day   = int(m.group(1))
        month = MONTH_MAP.get(m.group(2).lower(), 0)
        year  = int(m.group(3))
        if month and 1900 < year < 2100:
            try:
                return f"{year:04d}-{month:02d}-{day:02d}"
            except Exception:
                pass
    return None


def fetch_laws(limit: int | None = None) -> list[dict]:
    """Récupère toutes les lois (champs nécessaires seulement)."""
    fields = "id,pdf_url,domain_id,content_fr,source_name,source_url,bo_number,bo_date"
    url    = f"{SUPABASE_URL}/rest/v1/laws?select={fields}&order=id.asc"
    if limit:
        url += f"&limit={limit}"

    all_rows = []
    page_size = 500
    offset    = 0

    while True:
        paged = url + f"&offset={offset}&limit={page_size}"
        resp  = httpx.get(paged, headers={**HEADERS, "Range-Unit": "items"}, timeout=30)
        if resp.status_code not in (200, 206):
            console.print(f"[red]Erreur fetch laws: {resp.status_code} {resp.text[:200]}[/]")
            break
        rows = resp.json()
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < page_size:
            break
        offset += page_size

    return all_rows


def patch_law(law_id: int, updates: dict, client: httpx.Client, dry_run: bool) -> bool:
    """PATCH partiel d'une loi — client persistant + retry."""
    if dry_run or not updates:
        return True
    import time
    url = f"{SUPABASE_URL}/rest/v1/laws?id=eq.{law_id}"
    for attempt in range(3):
        try:
            resp = client.patch(url, headers=HEADERS, json=updates, timeout=20)
            return resp.status_code in (200, 204)
        except (httpx.ReadError, httpx.ConnectError, httpx.TimeoutException):
            if attempt < 2:
                time.sleep(2 ** attempt)   # 1s, 2s
    return False


def main():
    parser = argparse.ArgumentParser(description="Enrichit source_name, source_url, bo_number, bo_date")
    parser.add_argument("--dry-run", action="store_true", help="Simule sans écrire")
    parser.add_argument("--force",   action="store_true", help="Écrase les valeurs existantes")
    parser.add_argument("--limit",   type=int, default=None, help="Limite le nombre de lois traitées")
    args = parser.parse_args()

    console.print(f"\n[bold blue]🔍 Enrichissement sources & BO{'  [DRY-RUN]' if args.dry_run else ''}[/]\n")

    laws = fetch_laws(args.limit)
    console.print(f"[dim]{len(laws)} lois chargées[/]\n")

    stats = {"updated": 0, "skipped": 0, "no_source": 0, "bo_found": 0, "errors": 0}

    # Client persistant — une seule connexion TCP réutilisée pour tous les PATCH
    with httpx.Client(timeout=20, limits=httpx.Limits(max_keepalive_connections=5)) as client:
        for law in track(laws, description="Enrichissement…"):
            law_id  = law["id"]
            updates = {}

            # ── Source ──
            already_has_source = law.get("source_name") and law.get("source_url")
            if not already_has_source or args.force:
                src_name, src_url = detect_source(law)
                if src_name:
                    updates["source_name"] = src_name
                if src_url:
                    updates["source_url"] = src_url
                if not src_name:
                    stats["no_source"] += 1

            # ── BO number ──
            already_has_bo = law.get("bo_number")
            if not already_has_bo or args.force:
                content = (law.get("content_fr") or "")[:3000]
                bo_num  = extract_bo_number(content)
                if bo_num:
                    updates["bo_number"] = bo_num
                    stats["bo_found"] += 1
                    if not law.get("bo_date") or args.force:
                        bo_dt = extract_bo_date(content)
                        if bo_dt:
                            updates["bo_date"] = bo_dt

            if not updates:
                stats["skipped"] += 1
                continue

            ok = patch_law(law_id, updates, client, args.dry_run)
            if ok:
                stats["updated"] += 1
            else:
                stats["errors"] += 1

    # ── Rapport ──
    console.print(f"""
[bold green]✅ Terminé[/]

  Mises à jour  : [cyan]{stats['updated']}[/]
  Déjà enrichis : [dim]{stats['skipped']}[/]
  Sans source   : [yellow]{stats['no_source']}[/]
  BO détectés   : [green]{stats['bo_found']}[/]
  Erreurs       : [red]{stats['errors']}[/]
""")

    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"sources_report_{ts}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"stats": stats, "run_at": ts, "dry_run": args.dry_run}, f, ensure_ascii=False, indent=2)
    console.print(f"[dim]Rapport : {report_path}[/]")


if __name__ == "__main__":
    main()
