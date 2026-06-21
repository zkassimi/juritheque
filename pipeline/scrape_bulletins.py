"""
scrape_bulletins.py
───────────────────
Construit la table bulletins_officiels depuis deux sources :

  1. Les bo_number déjà détectés dans nos lois (table laws)
  2. Une liste manuelle de BOs récents avec leurs URLs SGG connues

Usage :
  python pipeline/scrape_bulletins.py              # insère tout
  python pipeline/scrape_bulletins.py --dry-run    # sans écriture
  python pipeline/scrape_bulletins.py --from-laws  # seulement depuis laws
"""

import os, re, sys, json, argparse
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track

load_dotenv()
console = Console()

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "resolution=merge-duplicates,return=minimal",
}

# ── URL pattern SGG pour les PDFs BO ─────────────────────────────────────────
# Format confirmé : https://www.sgg.gov.ma/BO/AR/3111/{year}/BO_{number}_Ar.pdf
#                   https://www.sgg.gov.ma/BO/FR/3111/{year}/BO_{number}_Fr.pdf
SGG_BO_FR_PATTERN = "https://www.sgg.gov.ma/BO/FR/3111/{year}/BO_{number}_Fr.pdf"
SGG_BO_AR_PATTERN = "https://www.sgg.gov.ma/BO/AR/3111/{year}/BO_{number}_Ar.pdf"

def build_sgg_url(number: str, year: int | None) -> str:
    """Construit l'URL française du BO sur sgg.gov.ma."""
    y = year or datetime.now().year
    return SGG_BO_FR_PATTERN.format(year=y, number=number)

def build_sgg_url_ar(number: str, year: int | None) -> str:
    """Construit l'URL arabe du BO sur sgg.gov.ma."""
    y = year or datetime.now().year
    return SGG_BO_AR_PATTERN.format(year=y, number=number)


# ── Fetch des bo_number depuis la table laws ──────────────────────────────────
def fetch_bo_from_laws(client: httpx.Client) -> list[dict]:
    """
    Récupère tous les bo_number/bo_date distincts depuis la table laws.
    Retourne une liste de dicts {number, date, law_count, title_sample}.
    """
    fields = "bo_number,bo_date,title_fr,date"
    url    = f"{SUPABASE_URL}/rest/v1/laws?select={fields}&bo_number=not.is.null&order=bo_date.desc"

    resp = client.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        console.print(f"[red]❌ fetch laws: {resp.status_code} {resp.text[:100]}[/]")
        return []

    rows = resp.json()
    # Grouper par bo_number
    groups: dict[str, dict] = {}
    for r in rows:
        num = r.get("bo_number")
        if not num:
            continue
        if num not in groups:
            groups[num] = {
                "number":     num,
                "date":       r.get("bo_date"),
                "law_count":  0,
                "title_sample": r.get("title_fr", "")[:80],
            }
        groups[num]["law_count"] += 1

    console.print(f"[dim]{len(groups)} numéros de BO distincts trouvés dans les lois[/]")
    return list(groups.values())


# ── Construire les rows bulletins_officiels ───────────────────────────────────
def build_bulletin_rows(bo_groups: list[dict]) -> list[dict]:
    rows = []
    for g in bo_groups:
        number = g["number"]
        date   = g.get("date")

        # Extraire l'année depuis la date
        year = None
        if date:
            try:
                year = int(str(date)[:4])
            except Exception:
                pass

        rows.append({
            "number":      number,
            "date":        date,
            "title":       f"Bulletin Officiel n° {number}",
            "url":         build_sgg_url(number, year),       # lien FR
            "url_ar":      build_sgg_url_ar(number, year),    # lien AR
            "description": f"{g['law_count']} texte(s)" if g.get('law_count') else None,
        })

    return rows


# ── Upsert dans Supabase ──────────────────────────────────────────────────────
def upsert_bulletins(rows: list[dict], client: httpx.Client, dry_run: bool) -> int:
    if dry_run:
        console.print(f"[dim][DRY-RUN] {len(rows)} BOs à insérer[/]")
        return len(rows)

    url     = f"{SUPABASE_URL}/rest/v1/bulletins_officiels"
    headers = {**HEADERS, "Prefer": "resolution=merge-duplicates,return=minimal"}

    inserted = 0
    BATCH    = 50
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i+BATCH]
        resp  = client.post(url, headers=headers, json=batch, timeout=30)
        if resp.status_code in (200, 201):
            inserted += len(batch)
        else:
            console.print(f"[red]❌ upsert batch {i}: {resp.status_code} {resp.text[:150]}[/]")

    return inserted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",    action="store_true")
    parser.add_argument("--from-laws",  action="store_true", help="Seulement depuis laws (défaut)")
    args = parser.parse_args()

    console.print(f"\n[bold blue]📰 Construction Bulletins Officiels{'  [DRY-RUN]' if args.dry_run else ''}[/]\n")

    with httpx.Client(timeout=30) as client:

        # ── Source 1 : bo_number dans nos lois ───────────────────────────────
        bo_groups = fetch_bo_from_laws(client)

        if not bo_groups:
            console.print("[yellow]Aucun bo_number trouvé dans la table laws.[/]")
            console.print("[dim]Lance d'abord : python pipeline/enrich_sources.py --force[/]")
            return

        rows = build_bulletin_rows(bo_groups)

        # Aperçu
        console.print(f"\n[green]{len(rows)} Bulletins Officiels à insérer :[/]")
        for r in sorted(rows, key=lambda x: x.get("date") or "", reverse=True)[:8]:
            console.print(f"  BO n°[cyan]{r['number']:>6}[/]  {r.get('date') or '?':>12}  {r['url'][:55]}")
        if len(rows) > 8:
            console.print(f"  [dim]… + {len(rows)-8} autres[/]")

        inserted = upsert_bulletins(rows, client, args.dry_run)

    console.print(f"\n[bold green]✅ {inserted} BOs {'simulés' if args.dry_run else 'insérés/mis à jour'}[/]\n")

    # Rapport
    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(report_dir / f"bulletins_report_{ts}.json", "w", encoding="utf-8") as f:
        json.dump({"count": len(rows), "sample": rows[:10]}, f, ensure_ascii=False, indent=2)
    console.print(f"[dim]Rapport : {report_dir / f'bulletins_report_{ts}.json'}[/]")


if __name__ == "__main__":
    main()
