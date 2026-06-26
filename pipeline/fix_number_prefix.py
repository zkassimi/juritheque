"""
fix_number_prefix.py — Corrige les numbers avec préfixe n° + les 2 records cassés
"""
import os, re, sys, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))
from slug_utils import make_slug_from_law
from title_lookup import get_best_title

URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
H  = {"apikey": KEY, "Authorization": f"Bearer {KEY}",
      "Content-Type": "application/json", "Prefer": "return=minimal"}

DRY_RUN = "--dry-run" in sys.argv

try:
    from rich.console import Console
    console = Console()
    def log(m): console.print(m)
except ImportError:
    def log(m): print(m)


def patch(law_id, payload: dict) -> bool:
    if DRY_RUN:
        return True
    r = requests.patch(f"{URL}/rest/v1/laws", headers=H,
                       params={"id": f"eq.{law_id}"}, json=payload, timeout=10)
    return r.status_code in (200, 204)


def clean_number(n: str) -> str:
    return re.sub(r"^n[°º\s.]+\s*", "", (n or "").strip(), flags=re.IGNORECASE).strip()


# ── CAS 1 : 17 records avec number comme 'n° XXXX' ──────────────────────────
log("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
log(f"[bold gold1]  fix_number_prefix {'[DRY-RUN]' if DRY_RUN else ''}[/]")
log("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,number,type,title_fr,canonical_slug,date",
            "number": "like.n%", "limit": "50"})

rows = r.json()
log(f"[dim]→ {len(rows)} records avec number préfixe 'n'[/]")

ok_count = 0
for x in rows:
    law_id   = x["id"]
    old_num  = x["number"] or ""
    new_num  = clean_number(old_num)
    old_slug = x["canonical_slug"] or ""
    typ      = x["type"] or ""
    title    = x["title_fr"] or ""
    date     = str(x["date"] or "")

    # Cas spéciaux à ignorer
    if new_num == old_num or new_num == "null":
        log(f"  [yellow]↷ ID {law_id} ignoré (number={old_num!r})[/]")
        continue

    # ID 6191 : title_fr aussi faux → lookup AI
    if law_id == 6191:
        log(f"  [cyan]ID 6191 — lookup AI pour title_fr...[/]")
        ai_title = get_best_title(law_type=typ, number=new_num, date=date)
        if ai_title:
            title = ai_title
            log(f"  [green]  → AI title: {ai_title[:70]}[/]")
        else:
            log(f"  [yellow]  → AI: NULL — on garde le title_fr existant[/]")

    new_slug = make_slug_from_law(law_type=typ, number=new_num,
                                   title_fr=title, date=date)

    log(f"  [dim]ID {law_id}[/] {old_num!r:20} → {new_num!r}")
    log(f"         slug: [dim]/{old_slug[:55]}[/]")
    log(f"               [green]/{new_slug[:55]}[/]")

    payload = {"number": new_num, "canonical_slug": new_slug}
    if law_id == 6191 and title != (x["title_fr"] or ""):
        payload["title_fr"] = title

    if patch(law_id, payload):
        ok_count += 1
    else:
        log(f"  [red]✗ PATCH échoué pour id={law_id}[/]")

log(f"\n[bold]CAS 1 :[/] {ok_count} records corrigés\n")


# ── CAS 3 : 2 records cassés ─────────────────────────────────────────────────
log("[bold gold1]CAS 3 — 2 records cassés[/]")

cas3 = [
    {
        "id":       7770,
        "title_fr": "Loi n° 2001-1 relative aux télécommunications",
        "number":   "2001-1",
        "type":     "Loi",
        "date":     "",
        "slug":     True,   # régénérer le slug
    },
    {
        "id":       4041,
        "title_fr": None,   # vider
        "number":   "decret cncp Ar",
        "type":     "Décret",
        "date":     "",
        "slug":     False,  # garder slug actuel
    },
]

for x in cas3:
    law_id    = x["id"]
    new_title = x["title_fr"]
    payload   = {"title_fr": new_title}

    if x["slug"] and new_title:
        new_slug = make_slug_from_law(x["type"], x["number"], new_title, x["date"])
        payload["canonical_slug"] = new_slug
        log(f"  ID {law_id}: title → {new_title!r}")
        log(f"             slug  → /{new_slug}")
    else:
        log(f"  ID {law_id}: title → NULL (vider)")

    if patch(law_id, payload):
        log(f"  [green]✓ OK[/]")
    else:
        log(f"  [red]✗ PATCH échoué[/]")

log(f"\n[bold green]{'✅ DRY-RUN terminé' if DRY_RUN else '✅ Toutes les corrections appliquées'}[/]")
