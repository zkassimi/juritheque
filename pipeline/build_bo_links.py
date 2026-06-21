"""
build_bo_links.py
─────────────────
Récupère les métadonnées des Bulletins Officiels marocains
via l'API publique de huquqai.ma, et écrit un fichier JSON statique.

Source   : https://www.huquqai.ma/api/sgg  (API publique, 12 642 BOs)
PDF URLs : redirigent vers sgg.gov.ma (source officielle)

NE TÉLÉCHARGE PAS les PDF.
NE STOCKE PAS dans Supabase.
NE MODIFIE PAS la table laws.

Usage :
  python pipeline/build_bo_links.py                          # tout récupérer
  python pipeline/build_bo_links.py --dry-run                # sans écriture
  python pipeline/build_bo_links.py --limit 200              # 200 BOs max
  python pipeline/build_bo_links.py --year 2025              # filtre année
  python pipeline/build_bo_links.py --lang fr                # seulement FR
  python pipeline/build_bo_links.py --lang ar                # seulement AR
  python pipeline/build_bo_links.py --output public/data/bulletins-officiels.json
"""

import re, sys, json, argparse, time
from datetime import datetime
from pathlib import Path

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

API_URL  = "https://www.huquqai.ma/api/sgg"
API_PAGE_SIZE = 100   # max par requête

# ── Mapping édition depuis l'URL PDF ─────────────────────────────────────────
EDITION_MAP = {
    "AR/3111": "edition_generale",
    "FR/2873": "traduction_officielle",
    "FR/3111": "traduction_officielle",
}

def detect_edition(pdf_url: str) -> str:
    for key, val in EDITION_MAP.items():
        if key in pdf_url:
            return val
    return "unknown"

def detect_lang(pdf_url: str) -> str:
    if "/BO/FR/" in pdf_url.upper():
        return "fr"
    if "/BO/AR/" in pdf_url.upper():
        return "ar"
    return "ar"  # défaut

def derive_fr_url(ar_url: str) -> str | None:
    """
    Dérive l'URL française depuis l'URL arabe.
    Ex: .../BO/AR/3111/2025/BO_7413_Ar.pdf
      → .../BO/FR/2873/2025/BO_7413_Fr.pdf
    """
    if "/BO/AR/3111/" not in ar_url:
        return None
    fr_url = ar_url.replace("/BO/AR/3111/", "/BO/FR/2873/")
    # Remplacer le suffixe _Ar par _Fr (tous les cas)
    fr_url = re.sub(r'_Ar\.pdf$', '_Fr.pdf', fr_url, flags=re.IGNORECASE)
    return fr_url

def make_title(number: str, lang: str, edition: str) -> str:
    edition_labels = {
        "traduction_officielle": {"fr": "Traduction officielle", "ar": "ترجمة رسمية"},
        "edition_generale":      {"fr": "Édition générale (arabe)", "ar": "الطبعة العامة"},
        "unknown":               {"fr": "Édition officielle", "ar": "الطبعة الرسمية"},
    }
    lbl = edition_labels.get(edition, edition_labels["unknown"])[lang]
    if lang == "ar":
        return f"الجريدة الرسمية عدد {number} — {lbl}"
    return f"Bulletin Officiel n° {number} — {lbl}"

def api_to_row(item: dict, include_fr: bool = True) -> list[dict]:
    """
    Convertit un item API en 1 ou 2 rows (AR + FR optionnel).
    """
    rows = []
    number    = str(item.get("bulletin_number") or item.get("document_number") or "")
    if not number:
        return []

    raw_date  = item.get("published_date") or ""
    date      = raw_date[:10] if raw_date else None   # "2025-06-19"
    year      = int(date[:4]) if date and len(date) >= 4 else None
    pdf_ar    = item.get("pdf_url") or ""
    tags      = item.get("tags") or []

    # ── Version arabe ──
    if pdf_ar:
        rows.append({
            "number":      number,
            "date":        date,
            "year":        year,
            "language":    "ar",
            "edition":     detect_edition(pdf_ar),
            "title":       item.get("title") or make_title(number, "ar", detect_edition(pdf_ar)),
            "officialUrl": pdf_ar,
            "source":      "SGG",
            "isExternal":  True,
            "tags":        [t.get("label") for t in tags if t.get("label")],
        })

    # ── Version française dérivée ──
    if include_fr and pdf_ar:
        fr_url = derive_fr_url(pdf_ar)
        if fr_url:
            rows.append({
                "number":      number,
                "date":        date,
                "year":        year,
                "language":    "fr",
                "edition":     "traduction_officielle",
                "title":       make_title(number, "fr", "traduction_officielle"),
                "officialUrl": fr_url,
                "source":      "SGG",
                "isExternal":  True,
                "tags":        [t.get("label") for t in tags if t.get("label")],
            })

    return rows


def fetch_all(limit: int | None, year_filter: int | None,
              lang_filter: str | None) -> list[dict]:
    """
    Pagine l'API huquqai.ma/api/sgg et retourne tous les BOs.
    """
    all_rows   = []
    seen_keys  = set()
    page       = 1
    total_api  = None
    fetched    = 0

    include_fr = lang_filter in (None, "fr")
    include_ar = lang_filter in (None, "ar")

    with httpx.Client(timeout=30) as client:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Récupération API…", total=None)

            while True:
                url = f"{API_URL}?page={page}&limit={API_PAGE_SIZE}"
                try:
                    resp = client.get(url, headers={"User-Agent": "JuriTheque-Bot/1.0"}, timeout=20)
                except Exception as e:
                    console.print(f"[red]❌ Erreur réseau p.{page}: {e}[/]")
                    break

                if resp.status_code != 200:
                    console.print(f"[red]❌ API {resp.status_code} p.{page}[/]")
                    break

                payload    = resp.json()
                items      = payload.get("data") or []
                total_api  = payload.get("totalCount") or total_api
                fetched   += len(items)

                if total_api and progress.tasks[task].total is None:
                    progress.update(task, total=total_api)
                progress.update(task, completed=fetched,
                                description=f"Page {page} — {fetched}/{total_api or '?'} BOs")

                if not items:
                    break

                for item in items:
                    rows = api_to_row(item, include_fr=include_fr)
                    for row in rows:
                        # Filtre langue
                        if lang_filter and row["language"] != lang_filter:
                            continue
                        # Filtre année
                        if year_filter and row.get("year") and row["year"] != year_filter:
                            continue
                        key = f"{row['number']}-{row['language']}"
                        if key in seen_keys:
                            continue
                        seen_keys.add(key)
                        all_rows.append(row)

                        if limit and len(all_rows) >= limit:
                            return all_rows

                if not limit and fetched >= (total_api or 0):
                    break

                page += 1
                time.sleep(0.1)   # politesse

    return all_rows


def main():
    parser = argparse.ArgumentParser(description="Build bulletins-officiels.json depuis huquqai.ma API")
    parser.add_argument("--dry-run",  action="store_true", help="Sans écriture fichier")
    parser.add_argument("--limit",    type=int,  default=None, help="Nombre max de BOs (ex: 200)")
    parser.add_argument("--year",     type=int,  default=None, help="Filtre sur l'année (ex: 2025)")
    parser.add_argument("--lang",     choices=["fr", "ar"], default=None)
    parser.add_argument(
        "--output",
        default="public/data/bulletins-officiels.json",
        help="Chemin du fichier JSON (relatif à la racine du projet)",
    )
    args = parser.parse_args()

    console.print(f"\n[bold blue]📰 Build Bulletins Officiels via huquqai.ma API"
                  f"{'  [DRY-RUN]' if args.dry_run else ''}[/]")
    if args.limit:
        console.print(f"[dim]Limite : {args.limit} BOs[/]")
    if args.year:
        console.print(f"[dim]Filtre année : {args.year}[/]")
    if args.lang:
        console.print(f"[dim]Filtre langue : {args.lang}[/]")
    console.print()

    bos = fetch_all(args.limit, args.year, args.lang)

    # Trier par numéro décroissant
    def sort_key(x):
        n = x["number"].split("-")[0]
        return int(n) if n.isdigit() else 0

    bos.sort(key=sort_key, reverse=True)

    console.print(f"\n[bold green]{len(bos)} Bulletins Officiels récupérés[/]")

    # Aperçu
    if bos:
        console.print("\nAperçu (5 premiers) :")
        for b in bos[:5]:
            console.print(
                f"  n°[cyan]{b['number']:>8}[/]  [{b['language'].upper()}]  "
                f"{b.get('date') or '?':>12}  {b['officialUrl'][:60]}"
            )

    if args.dry_run:
        console.print("\n[dim][DRY-RUN] Aucun fichier écrit.[/]\n")
        return

    # Écrire le JSON
    script_dir   = Path(__file__).parent
    project_root = script_dir.parent
    output_path  = project_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(bos, f, ensure_ascii=False, indent=2)

    console.print(f"\n[bold green]✅ {len(bos)} BOs écrits → {output_path}[/]")

    # Rapport
    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "run_at":  ts,
        "source":  API_URL,
        "count":   len(bos),
        "filters": {"lang": args.lang, "year": args.year, "limit": args.limit},
        "sample":  bos[:3],
    }
    report_path = report_dir / f"bo_links_report_{ts}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    console.print(f"[dim]Rapport : {report_path}[/]\n")


if __name__ == "__main__":
    main()
