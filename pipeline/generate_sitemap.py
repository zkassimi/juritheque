"""
JuriThèque — Générateur de sitemap.xml
════════════════════════════════════════════════════════════════════
Récupère tous les IDs de lois et domaines depuis Supabase,
puis génère public/sitemap.xml (copié dans dist/ par Vite au build).

Usage :
  python pipeline/generate_sitemap.py          # génère sitemap dans public/
  python pipeline/generate_sitemap.py --stdout # affiche sur stdout uniquement

Prérequis :
  pip install httpx python-dotenv rich
  Variables dans .env : SUPABASE_URL, SUPABASE_SERVICE_KEY
"""

import os, re, sys
from datetime import date, datetime
from pathlib import Path
from dotenv import load_dotenv
import httpx
try:
    from rich.console import Console
    console = Console()
    def log(msg): console.print(msg)
except ImportError:
    def log(msg): print(msg)

# ── Config ─────────────────────────────────────────────────────────────────────
load_dotenv()

# Supporte les deux formats : avec ou sans préfixe VITE_
# Pour la lecture des données publiques, la clé anon suffit (RLS public read actif)
SUPABASE_URL = (
    os.getenv("SUPABASE_URL")
    or os.getenv("VITE_SUPABASE_URL", "")
).rstrip("/")

SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("VITE_SUPABASE_ANON_KEY", "")
)
BASE_SITE    = "https://juritheque.com"
TODAY        = date.today().isoformat()          # YYYY-MM-DD
STDOUT_ONLY  = "--stdout" in sys.argv

# Sortie : public/sitemap.xml (relatif à la racine du projet)
SCRIPT_DIR   = Path(__file__).parent             # pipeline/
PROJECT_ROOT = SCRIPT_DIR.parent                 # lexbase/
OUT_PATH     = PROJECT_ROOT / "public" / "sitemap.xml"

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

# ── Slugs des guides — lus dynamiquement depuis seoIntentPages.js ────────────
def _read_guide_slugs() -> list[str]:
    """Extrait les slugs depuis src/data/seoIntentPages.js via regex."""
    js_path = PROJECT_ROOT / "src" / "data" / "seoIntentPages.js"
    if not js_path.exists():
        log("[yellow]⚠  seoIntentPages.js introuvable — liste de guides vide[/]")
        return []
    src = js_path.read_text(encoding="utf-8")
    slugs = re.findall(r"slug:\s*'([a-z0-9][a-z0-9-]+)'", src)
    # Déduplication en préservant l'ordre
    seen, result = set(), []
    for s in slugs:
        if s not in seen:
            seen.add(s)
            result.append(s)
    log(f"[dim]→ {len(result)} slugs de guides lus depuis seoIntentPages.js[/]")
    return result

_GUIDE_SLUGS = _read_guide_slugs()

STATIC_PAGES = [
    # ── Pages principales ────────────────────────────────────────────────
    {"loc": "/",                          "priority": "1.0", "changefreq": "weekly"},
    {"loc": "/base",                      "priority": "0.9", "changefreq": "daily"},
    {"loc": "/domaines",                  "priority": "0.8", "changefreq": "weekly"},
    {"loc": "/glossaire",                 "priority": "0.7", "changefreq": "monthly"},
    {"loc": "/videos",                    "priority": "0.6", "changefreq": "weekly"},
    {"loc": "/assistant",                 "priority": "0.7", "changefreq": "monthly"},
    {"loc": "/a-propos",                  "priority": "0.5", "changefreq": "yearly"},
    {"loc": "/methodologie",              "priority": "0.5", "changefreq": "yearly"},
    {"loc": "/contact",                   "priority": "0.4", "changefreq": "yearly"},
    {"loc": "/mentions-legales",          "priority": "0.3", "changefreq": "yearly"},
    {"loc": "/politique-confidentialite", "priority": "0.3", "changefreq": "yearly"},
    # ── Veille et Bulletins ──────────────────────────────────────────────
    {"loc": "/fr/veille-juridique",       "priority": "0.85", "changefreq": "daily"},
    {"loc": "/fr/bulletins-officiels",    "priority": "0.80", "changefreq": "weekly"},
    # ── Index des guides ─────────────────────────────────────────────────
    {"loc": "/fr/guides",                 "priority": "0.85", "changefreq": "weekly"},
    # ── Guides FR (30 guides) ────────────────────────────────────────────
    *[{"loc": f"/fr/guides/{s}", "priority": "0.85", "changefreq": "monthly"}
      for s in _GUIDE_SLUGS],
    # ── Guides AR (30 guides — version arabe) ───────────────────────────
    *[{"loc": f"/ar/guides/{s}", "priority": "0.80", "changefreq": "monthly"}
      for s in _GUIDE_SLUGS],
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def sb_get(endpoint: str, params: dict) -> list:
    """Appel GET à l'API REST Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        log("[yellow]⚠  SUPABASE_URL ou SUPABASE_SERVICE_KEY manquant dans .env[/]")
        return []
    try:
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/{endpoint}",
            headers=HEADERS,
            params=params,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log(f"[red]✗ Supabase GET /{endpoint}: {e}[/]")
        return []


def url_entry(loc: str, lastmod: str = TODAY,
              changefreq: str = "monthly", priority: str = "0.5") -> str:
    return (
        f"  <url>\n"
        f"    <loc>{BASE_SITE}{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        f"  </url>"
    )


# ── Récupération des données ──────────────────────────────────────────────────
def fetch_laws() -> list[dict]:
    """Récupère les lois indexables avec canonical_slug (par batch de 1000).

    Filtres appliqués :
    - canonical_slug IS NOT NULL  → exclut les lois sans URL SEO propre
    - is_publicly_indexable != false → exclut les lois marquées non-indexables
    """
    all_rows = []
    offset   = 0
    batch    = 1000
    while True:
        rows = sb_get("laws", {
            "select":               "id,canonical_slug,updated_at,date,simple_summary_fr,simple_summary_ar",
            "canonical_slug":       "not.is.null",
            "is_publicly_indexable":"not.is.false",
            "order":                "id.asc",
            "limit":                str(batch),
            "offset":               str(offset),
        })
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < batch:
            break
        offset += batch
    return all_rows


def fetch_domains() -> list[dict]:
    """Récupère tous les IDs de domaines."""
    return sb_get("domains", {"select": "id"})


# ── Génération ────────────────────────────────────────────────────────────────
def generate() -> str:
    log("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log("[bold gold1]  JuriThèque — Génération du sitemap.xml    [/]")
    log("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

    entries = []

    # 1. Pages statiques
    log(f"[dim]→ Ajout des {len(STATIC_PAGES)} pages statiques...[/]")
    for p in STATIC_PAGES:
        entries.append(url_entry(
            loc=p["loc"],
            lastmod=TODAY,
            changefreq=p["changefreq"],
            priority=p["priority"],
        ))

    # 2. Domaines
    domains = fetch_domains()
    log(f"[dim]→ {len(domains)} domaines récupérés depuis Supabase[/]")
    for d in domains:
        entries.append(url_entry(
            loc=f"/domaine/{d['id']}",
            lastmod=TODAY,
            changefreq="weekly",
            priority="0.8",
        ))

    # 3. Lois — uniquement celles avec canonical_slug (filtrées en DB)
    laws = fetch_laws()
    log(f"[dim]→ {len(laws)} textes juridiques récupérés depuis Supabase (avec canonical_slug)[/]")
    skipped = 0
    for law in laws:
        slug = law.get("canonical_slug")
        if not slug or re.fullmatch(r'\d+', slug):
            # Sécurité double : ne jamais inclure un ID numérique (pur chiffres) dans le sitemap
            skipped += 1
            continue

        # Utiliser updated_at si disponible, sinon date de publication, sinon aujourd'hui
        raw_date = law.get("updated_at") or law.get("date") or TODAY
        lastmod  = raw_date[:10]   # tronquer à YYYY-MM-DD

        # Priorité selon la qualité du contenu enrichi
        has_summary = bool(law.get("simple_summary_fr") or law.get("simple_summary_ar"))
        priority = "0.9" if has_summary else "0.7"

        entries.append(url_entry(
            loc=f"/loi/{slug}",
            lastmod=lastmod,
            changefreq="monthly",
            priority=priority,
        ))
    if skipped:
        log(f"[yellow]⚠  {skipped} loi(s) ignorée(s) (pas de canonical_slug malgré le filtre DB)[/]")

    # ── Assembler le XML ──────────────────────────────────────────────────────
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n'
        '        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n\n'
    )
    xml += "\n".join(entries)
    xml += "\n\n</urlset>\n"

    n_guides   = sum(1 for p in STATIC_PAGES if '/guides' in p['loc'])
    n_static   = len(STATIC_PAGES) - n_guides
    n_laws_ok  = len(laws) - skipped
    n_enriched = sum(1 for l in laws if l.get("simple_summary_fr") or l.get("simple_summary_ar"))
    total = len(entries)
    log(f"\n[bold green]✅ {total} URLs générées[/]  "
        f"({n_static} statiques · {n_guides} guides · {len(domains)} domaines · {n_laws_ok} lois)")
    log(f"[dim]   ↳ Lois avec résumé enrichi (priorité 0.9) : {n_enriched}[/]")
    log(f"[dim]   ↳ Lois sans résumé (priorité 0.7)         : {n_laws_ok - n_enriched}[/]")

    return xml


# ── Point d'entrée ────────────────────────────────────────────────────────────
def main():
    content = generate()

    if STDOUT_ONLY:
        print(content)
        return

    # Créer public/ si nécessaire
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(content, encoding="utf-8")
    log(f"\n[bold]📄 Sitemap écrit dans :[/] {OUT_PATH}")
    log(f"[dim]→ Lancez ensuite : npm run build:full[/]")
    log(f"[dim]→ Le fichier sera copié dans dist/sitemap.xml + pages pré-rendues générées[/]\n")


if __name__ == "__main__":
    main()
