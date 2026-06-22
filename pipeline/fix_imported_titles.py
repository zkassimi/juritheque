"""
fix_imported_titles.py — Corrige les textes importés par la veille qui ont
des titres avec .pdf et des numéros URL-encodés dans la table laws.

Usage :
  python pipeline/fix_imported_titles.py --dry-run   # aperçu
  python pipeline/fix_imported_titles.py             # correction réelle
"""

import os, re, sys, unicodedata
from pathlib import Path
from urllib.parse import unquote
from dotenv import load_dotenv

try:
    import requests
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print("pip install requests rich")
    sys.exit(1)

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", ""))
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

console = Console()

def clean_number(n: str) -> str:
    """Décoder URL-encoding et nettoyer."""
    cleaned = unquote(n)
    cleaned = re.sub(r'\.(pdf|PDF)$', '', cleaned).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned[:60]

def clean_title(t: str) -> str:
    """Supprimer l'extension .pdf et décoder URL encoding."""
    cleaned = unquote(t)
    cleaned = re.sub(r'\.(pdf|PDF)$', '', cleaned).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned[:400]

def looks_broken_number(n: str) -> bool:
    """Vrai si le numéro contient du URL-encoding (%20, %C3, etc.)"""
    return '%' in (n or '')

def looks_broken_title(t: str) -> bool:
    """Vrai si le titre se termine par .pdf ou contient du URL-encoding"""
    return (t or '').endswith('.pdf') or (t or '').endswith('.PDF') or '%' in (t or '')

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        console.print("[yellow]Mode DRY-RUN — aucune écriture[/]\n")

    # Chercher les textes avec source_name contenant des sources de la veille
    # et dont le number ou title_fr est cassé
    console.print("Chargement des textes importés par la veille…")
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={
            "extraction_status": "eq.pending",
            "select": "id,number,title_fr,source_name",
            "limit": "500",
        },
        timeout=20,
    )

    if resp.status_code != 200:
        console.print(f"[red]Erreur: {resp.status_code} {resp.text[:100]}[/]")
        sys.exit(1)

    rows = resp.json()
    console.print(f"  {len(rows)} textes avec extraction_status=pending\n")

    to_fix = []
    for row in rows:
        num   = row.get("number", "") or ""
        title = row.get("title_fr", "") or ""
        patch = {}
        if looks_broken_number(num):
            patch["number"] = clean_number(num)
        if looks_broken_title(title):
            patch["title_fr"] = clean_title(title)
        if patch:
            to_fix.append((row["id"], num, title, patch))

    console.print(f"  [bold]{len(to_fix)}[/] textes à corriger\n")

    if not to_fix:
        console.print("  ✅ Rien à corriger.")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID",         width=10)
    table.add_column("Avant",      width=45)
    table.add_column("Après",      width=45)
    table.add_column("Résultat",   width=10)

    fixed = 0
    for (law_id, old_num, old_title, patch) in to_fix:
        before = (patch.get("number") and f"n°{old_num[:40]}") or f"«{old_title[:40]}»"
        after  = (patch.get("number") and f"n°{patch['number'][:40]}") or f"«{patch.get('title_fr','')[:40]}»"

        if not args.dry_run:
            r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/laws",
                headers=HEADERS,
                params={"id": f"eq.{law_id}"},
                json=patch,
                timeout=10,
            )
            ok = r.status_code in (200, 204)
            status = "✅" if ok else f"❌{r.status_code}"
            if ok:
                fixed += 1
        else:
            status = "🔍"

        table.add_row(law_id[:8] + "…", before, after, status)

    console.print(table)
    if not args.dry_run:
        console.print(f"\n  ✅ {fixed}/{len(to_fix)} textes corrigés.")
    else:
        console.print(f"\n  [yellow][DRY-RUN] {len(to_fix)} textes seraient corrigés.[/]")

if __name__ == "__main__":
    main()
