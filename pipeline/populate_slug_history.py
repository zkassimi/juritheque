"""
populate_slug_history.py — Backfill rétroactif de slug_history
═══════════════════════════════════════════════════════════════
Reconstitue les anciens slugs connus pour chaque loi et les écrit
dans la colonne slug_history (TEXT[]).

Anciens patterns reconstitués :
  1. texte-juridique-{number}     (avant fix_imported_titles.py)
  2. {type}-{number}              (avant ajout des keywords)
  3. {number} seul                (très anciens liens)

Usage :
  python pipeline/populate_slug_history.py --dry-run   # aperçu
  python pipeline/populate_slug_history.py             # applique
  python pipeline/populate_slug_history.py --limit 100 # test partiel

Prérequis : .env avec SUPABASE_URL + SUPABASE_SERVICE_KEY
"""

import os, re, sys, unicodedata
from pathlib import Path
from dotenv import load_dotenv

try:
    import requests
    from rich.console import Console
    from rich.table import Table
    console = Console()
    def log(m): console.print(m)
except ImportError:
    def log(m): print(m)

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}

DRY_RUN = "--dry-run" in sys.argv
LIMIT   = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--limit=")), None)


# ── Slugification (même logique que le frontend) ─────────────────────────────

def slugify(text: str) -> str:
    """Convertit en slug : minuscule, sans accents, tirets."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFD", text.lower())
    norm = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    norm = re.sub(r"[^a-z0-9]+", "-", norm)
    return norm.strip("-")


TYPE_SLUG = {
    "Dahir":       "dahir",
    "Décret":      "decret",
    "Loi":         "loi",
    "Arrêté":      "arrete",
    "Circulaire":  "circulaire",
    "Code":        "code",
    "Ordonnance":  "ordonnance",
    "Convention":  "convention",
}


def old_slugs_for(law: dict) -> list[str]:
    """Génère la liste des anciens slugs probables pour une loi."""
    canonical = (law.get("canonical_slug") or "").lower()
    number    = (law.get("number") or "").strip()
    law_type  = (law.get("type") or "").strip()

    candidates = set()

    # Pattern 1 : texte-juridique-{number}
    if number:
        num_slug = slugify(number)
        candidates.add(f"texte-juridique-{num_slug}")

    # Pattern 2 : {type}-{number} sans keywords
    if number and law_type:
        type_s = slugify(TYPE_SLUG.get(law_type, law_type))
        num_s  = slugify(number)
        short  = f"{type_s}-{num_s}"
        if short != canonical and short not in canonical:
            candidates.add(short)

    # Pattern 3 : numéro brut seul (très anciens)
    if number:
        candidates.add(slugify(number))

    # Exclure le slug canonique actuel et les slugs trop courts
    return [s for s in candidates if s and s != canonical and len(s) > 5]


# ── Fetch toutes les lois (paginé) ────────────────────────────────────────────

def _column_exists(col: str) -> bool:
    """Vérifie si une colonne existe dans la table laws."""
    r = requests.get(f"{SUPABASE_URL}/rest/v1/laws",
                     headers=HEADERS,
                     params={"select": col, "limit": "1"},
                     timeout=10)
    return r.status_code == 200


def fetch_all_laws() -> list[dict]:
    log("[dim]→ Récupération des lois depuis Supabase...[/]")

    # Détecter si slug_history existe déjà
    has_col = _column_exists("slug_history")
    if not has_col:
        log("[yellow]⚠  La colonne slug_history n'existe pas encore.[/]")
        log("[yellow]   Appliquer d'abord la migration SQL dans le Dashboard Supabase :[/]")
        log("[yellow]   ALTER TABLE laws ADD COLUMN IF NOT EXISTS slug_history TEXT[] DEFAULT '{}';[/]")
        log("[yellow]   CREATE INDEX IF NOT EXISTS idx_laws_slug_history ON laws USING GIN(slug_history);[/]")
        sys.exit(1)

    all_rows, offset, batch = [], 0, 1000
    while True:
        params = {
            "select":         "id,canonical_slug,number,type,slug_history",
            "canonical_slug": "not.is.null",
            "order":          "id.asc",
            "limit":          str(batch),
            "offset":         str(offset),
        }
        r = requests.get(f"{SUPABASE_URL}/rest/v1/laws", headers=HEADERS,
                         params=params, timeout=30)
        r.raise_for_status()
        rows = r.json()
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < batch:
            break
        offset += batch
    log(f"[dim]→ {len(all_rows)} lois récupérées[/]")
    return all_rows


# ── PATCH slug_history ────────────────────────────────────────────────────────

def patch_slug_history(law_id, new_history: list[str]) -> bool:
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={"id": f"eq.{law_id}"},
        json={"slug_history": new_history},
        timeout=10,
    )
    return r.status_code in (200, 204)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    log("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log(f"[bold gold1]  populate_slug_history{'  [DRY-RUN]' if DRY_RUN else ''}   [/]")
    log("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

    laws = fetch_all_laws()
    if LIMIT:
        laws = laws[:LIMIT]

    updated = 0
    skipped = 0
    total_slugs_added = 0

    for law in laws:
        law_id    = law["id"]
        existing  = set(law.get("slug_history") or [])
        new_olds  = old_slugs_for(law)
        to_add    = [s for s in new_olds if s not in existing]

        if not to_add:
            skipped += 1
            continue

        merged = sorted(existing | set(to_add))

        if DRY_RUN:
            log(f"  [cyan]{law.get('canonical_slug', law_id)[:50]}[/] → ajout : {to_add}")
        else:
            ok = patch_slug_history(law_id, merged)
            if ok:
                updated += 1
                total_slugs_added += len(to_add)
            else:
                log(f"  [red]✗ PATCH échoué pour id={law_id}[/]")

    if DRY_RUN:
        log(f"\n[yellow]⚠  DRY-RUN — aucune modification appliquée[/]")
        log(f"[dim]{len(laws) - skipped} lois auraient été mises à jour[/]")
    else:
        log(f"\n[bold green]✅ {updated} lois mises à jour[/]  "
            f"({total_slugs_added} anciens slugs ajoutés)")
        log(f"[dim]{skipped} lois ignorées (slug_history déjà complet)[/]")


if __name__ == "__main__":
    main()
