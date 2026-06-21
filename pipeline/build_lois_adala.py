"""
build_lois_adala.py
────────────────────
Récupère les métadonnées des lois marocaines depuis l'API publique
de huquqai.ma (/api/laws — Adala, Ministère de la Justice),
déduplique contre les lois déjà présentes dans Supabase,
et écrit un fichier JSON statique.

Source   : https://www.huquqai.ma/api/laws  (API publique, ~6 808 lois)
PDF URLs : hébergés sur Cloudflare R2 (r2.dev/adala_documents/)
Source officielle : Adala — Ministère de la Justice (adala.justice.gov.ma)

NE TÉLÉCHARGE PAS les PDF.
NE STOCKE PAS dans Supabase.
NE MODIFIE PAS la table laws.

Usage :
  python pipeline/build_lois_adala.py                          # tout récupérer
  python pipeline/build_lois_adala.py --dry-run                # sans écriture
  python pipeline/build_lois_adala.py --limit 200              # 200 lois max
  python pipeline/build_lois_adala.py --year 2025              # filtre année
  python pipeline/build_lois_adala.py --no-dedup               # sans déduplication Supabase
  python pipeline/build_lois_adala.py --output public/data/lois-adala.json
"""

import os, sys, re, json, argparse, time
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

load_dotenv()
console = Console()

API_URL        = "https://www.huquqai.ma/api/laws"
API_PAGE_SIZE  = 100

SUPABASE_URL   = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY   = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("VITE_SUPABASE_ANON_KEY", "")
)

# ── Mapping type arabe -> français ────────────────────────────────────────────
TYPE_MAP_AR = {
    "قانون":          "Loi",
    "قانون تنظيمي":  "Loi organique",
    "مرسوم":         "Décret",
    "مرسوم ملكي":   "Décret royal",
    "ظهير":          "Dahir",
    "أمر":           "Arrêté",
    "قرار":          "Arrêté",
    "منشور":         "Circulaire",
    "مذكرة":        "Note circulaire",
    "اتفاقية":      "Convention",
    "نظام":          "Règlement",
    "مدونة":        "Code",
}

# ── Mapping tags (domaine arabe) -> slug domaine ──────────────────────────────
DOMAIN_TAG_MAP = {
    "القانون الإداري":      "administratif",
    "القانون التجاري":      "commercial",
    "القانون الجنائي":      "penal",
    "القانون المدني":       "civil",
    "قانون الشغل":          "travail",
    "القانون الضريبي":      "fiscal",
    "القانون المالي":       "finances_publiques",
    "القانون الدولي":       "international",
    "القانون البنكي":       "bancaire",
    "التقنين الرقمي":      "numerique",
    "القانون الدستوري":    "constitutionnel",
    "القانون العقاري":     "immobilier",
    "قانون الأسرة":        "famille",
}


def translate_type(ar_type: str) -> str:
    return TYPE_MAP_AR.get((ar_type or "").strip(), "Autre")


def extract_domain(tags: list) -> str | None:
    for tag in (tags or []):
        label = tag.get("label", "")
        if label in DOMAIN_TAG_MAP:
            return DOMAIN_TAG_MAP[label]
    return None


def normalize_number(raw: str) -> str:
    """Normalise un numéro de loi pour la déduplication."""
    return re.sub(r'\s+', '', (raw or "").strip().lower())


def api_to_row(item: dict) -> dict | None:
    """
    Convertit un item API /api/laws en row statique.
    Retourne None si données insuffisantes.
    """
    number     = str(item.get("law_number") or item.get("document_number") or "").strip()
    if not number:
        return None

    raw_date   = item.get("published_date") or ""
    date       = raw_date[:10] if raw_date else None
    year       = int(date[:4]) if date and len(date) >= 4 else (
                    int(str(item.get("document_year", "") or "")[:4] or 0) or None
                 )

    pdf_url    = item.get("pdf_url") or ""
    ar_type    = item.get("document_type") or ""
    tags       = item.get("tags") or []
    domain     = extract_domain(tags)
    tag_labels = [t.get("label") for t in tags if t.get("label")]

    title_ar   = item.get("title") or item.get("subject") or f"قانون رقم {number}"

    return {
        "id":           item.get("id") or "",
        "number":       number,
        "number_norm":  normalize_number(number),
        "date":         date,
        "year":         year,
        "type_ar":      ar_type,
        "type_fr":      translate_type(ar_type),
        "title_ar":     title_ar,
        "domain":       domain,
        "tags":         tag_labels,
        "pdfUrl":       pdf_url,
        "source":       "Adala",
        "sourceUrl":    f"https://adala.justice.gov.ma",
        "isExternal":   True,
    }


def fetch_existing_numbers() -> set[str]:
    """
    Récupère tous les laws.number depuis Supabase (pour déduplication).
    Retourne un ensemble de numéros normalisés.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        console.print("[yellow]⚠  Supabase non configuré — déduplication désactivée[/]")
        return set()

    headers = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    existing = set()
    offset, batch = 0, 1000

    console.print("[dim]-> Récupération des numéros existants depuis Supabase...[/]")
    with httpx.Client(timeout=30) as client:
        while True:
            try:
                resp = client.get(
                    f"{SUPABASE_URL}/rest/v1/laws",
                    headers=headers,
                    params={"select": "number", "limit": str(batch), "offset": str(offset)},
                )
                resp.raise_for_status()
                rows = resp.json()
            except Exception as e:
                console.print(f"[red]X Supabase erreur: {e}[/]")
                break
            if not rows:
                break
            for r in rows:
                n = normalize_number(r.get("number", ""))
                if n:
                    existing.add(n)
            if len(rows) < batch:
                break
            offset += batch

    console.print(f"[dim]-> {len(existing)} lois existantes dans Supabase[/]")
    return existing


def fetch_all(limit: int | None, year_filter: int | None,
              skip_dedup: bool) -> tuple[list[dict], int, int]:
    """
    Pagine l'API huquqai.ma/api/laws.
    Retourne (rows, total_api, count_duplicates).
    """
    existing_numbers = set() if skip_dedup else fetch_existing_numbers()

    all_rows    = []
    seen_keys   = set()
    duplicates  = 0
    page        = 1
    total_api   = None
    fetched     = 0

    with httpx.Client(timeout=60) as client:
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Récupération API...", total=None)

            while True:
                url = f"{API_URL}?page={page}&limit={API_PAGE_SIZE}"
                try:
                    resp = client.get(
                        url,
                        headers={"User-Agent": "JuriTheque-Bot/1.0"},
                        timeout=60,
                    )
                except Exception as e:
                    console.print(f"[red]X Erreur réseau p.{page}: {e}[/]")
                    break

                if resp.status_code != 200:
                    console.print(f"[red]X API {resp.status_code} p.{page}[/]")
                    break

                payload   = resp.json()
                items     = payload.get("data") or []
                total_api = payload.get("totalCount") or total_api
                fetched  += len(items)

                if total_api and progress.tasks[task].total is None:
                    progress.update(task, total=total_api)
                progress.update(
                    task,
                    completed=fetched,
                    description=f"Page {page} — {fetched}/{total_api or '?'} lois"
                )

                if not items:
                    break

                for item in items:
                    row = api_to_row(item)
                    if not row:
                        continue

                    # Filtre année
                    if year_filter and row.get("year") and row["year"] != year_filter:
                        continue

                    # Déduplication Supabase
                    if row["number_norm"] in existing_numbers:
                        duplicates += 1
                        continue

                    # Déduplication interne (même numéro plusieurs fois dans l'API)
                    if row["number_norm"] in seen_keys:
                        continue
                    seen_keys.add(row["number_norm"])

                    # Supprimer number_norm (champ interne, pas utile dans le JSON final)
                    row.pop("number_norm", None)

                    all_rows.append(row)

                    if limit and len(all_rows) >= limit:
                        return all_rows, total_api or 0, duplicates

                if not limit and fetched >= (total_api or 0):
                    break

                page += 1
                time.sleep(0.1)  # politesse

    return all_rows, total_api or 0, duplicates


def main():
    parser = argparse.ArgumentParser(
        description="Build lois-adala.json depuis huquqai.ma API (Adala / Ministère de la Justice)"
    )
    parser.add_argument("--dry-run",   action="store_true", help="Sans écriture fichier")
    parser.add_argument("--limit",     type=int,  default=None, help="Nombre max de lois")
    parser.add_argument("--year",      type=int,  default=None, help="Filtre sur l'année (ex: 2025)")
    parser.add_argument("--no-dedup",  action="store_true", help="Désactiver déduplication Supabase")
    parser.add_argument(
        "--output",
        default="public/data/lois-adala.json",
        help="Chemin du fichier JSON (relatif à la racine du projet)",
    )
    args = parser.parse_args()

    console.print(f"\n[bold blue]>> Build Lois Adala via huquqai.ma/api/laws"
                  f"{'  [DRY-RUN]' if args.dry_run else ''}[/]")
    if args.limit:
        console.print(f"[dim]Limite : {args.limit} lois[/]")
    if args.year:
        console.print(f"[dim]Filtre année : {args.year}[/]")
    if args.no_dedup:
        console.print(f"[dim]Déduplication : désactivée[/]")
    console.print()

    lois, total_api, duplicates = fetch_all(args.limit, args.year, args.no_dedup)

    # Trier par date décroissante
    def sort_key(x):
        return x.get("date") or ""
    lois.sort(key=sort_key, reverse=True)

    console.print(f"\n[bold green]{len(lois)} lois récupérées[/]  "
                  f"({duplicates} doublons Supabase ignorés · {total_api} total API)")

    # Aperçu
    if lois:
        # Utiliser print() natif pour eviter les problemes cp1252 avec le texte arabe
        print("\nApercu (5 premiers) :")
        for l in lois[:5]:
            print(f"  n {l['number']:>12}  {l.get('date') or '?':>12}  [{l.get('type_fr') or '?'}]  domain={l.get('domain') or '-'}")

    if args.dry_run:
        console.print("\n[dim][DRY-RUN] Aucun fichier écrit.[/]\n")
        return

    # Écrire le JSON
    script_dir   = Path(__file__).parent
    project_root = script_dir.parent
    output_path  = project_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(lois, f, ensure_ascii=False, indent=2)

    print(f"\nOK {len(lois)} lois ecrites -> {output_path}")

    # Rapport
    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "run_at":     ts,
        "source":     API_URL,
        "total_api":  total_api,
        "count":      len(lois),
        "duplicates": duplicates,
        "filters":    {"year": args.year, "limit": args.limit, "no_dedup": args.no_dedup},
        "sample":     lois[:3],
    }
    report_path = report_dir / f"lois_adala_report_{ts}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Rapport : {report_path}\n")


if __name__ == "__main__":
    main()
