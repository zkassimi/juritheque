"""
JuriThèque — Constructeur de l'index de recherche interne
══════════════════════════════════════════════════════════════════════════════
Reconstruit la table `site_search_index` dans Supabase à partir :
  - des lois (is_publicly_indexable = true)
  - des guides SEO (définis statiquement)
  - des domaines juridiques
  - des pages statiques importantes

Usage :
  python pipeline/build_site_search_index.py              # reconstruction complète
  python pipeline/build_site_search_index.py --dry-run    # simulation sans écriture
  python pipeline/build_site_search_index.py --clear      # vide l'index avant reconstruction
  python pipeline/build_site_search_index.py --limit 50   # limite aux 50 premières lois
  python pipeline/build_site_search_index.py --source laws     # lois uniquement
  python pipeline/build_site_search_index.py --source guides   # guides uniquement
  python pipeline/build_site_search_index.py --source domains  # domaines uniquement

Prérequis :
  pip install httpx python-dotenv rich
  Variables dans .env : SUPABASE_URL, SUPABASE_SERVICE_KEY
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

try:
    import httpx
except ImportError:
    print("Erreur : pip install httpx"); sys.exit(1)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
    console = Console()
    def log(msg, style=None): console.print(msg, style=style)
except ImportError:
    def log(msg, style=None): print(msg)
    def track(iterable, description="", total=None): return iterable

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv()

SUPABASE_URL = (
    os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")
).rstrip("/")

SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("VITE_SUPABASE_ANON_KEY", "")
)

BASE_SITE = "https://juritheque.com"

HEADERS = {
    "apikey":           SUPABASE_KEY,
    "Authorization":    f"Bearer {SUPABASE_KEY}",
    "Content-Type":     "application/json",
    "Prefer":           "return=minimal",
}

# ── Guides SEO (miroir du fichier src/data/seoIntentPages.js) ─────────────────
SEO_GUIDES = [
    {
        "slug": "code-du-travail-maroc",
        "title": "Code du Travail au Maroc : textes et lois applicables",
        "description": "Consultez les textes juridiques du Code du Travail marocain : contrat de travail, congés, licenciement, syndicats, inspection du travail.",
        "summary": "Le droit du travail marocain encadre les relations entre employeurs et salariés du secteur privé. Cette page regroupe les principaux textes disponibles dans JuriThèque sur le droit du travail.",
        "legal_domain": "travail",
        "keywords": ["code du travail", "contrat de travail", "licenciement", "congés payés", "SMIG", "syndicats"],
        "priority": 0.85,
    },
    {
        "slug": "licenciement-maroc",
        "title": "Licenciement au Maroc : droits, procédures et textes",
        "description": "Textes juridiques sur le licenciement au Maroc : licenciement abusif, indemnités, préavis, procédure disciplinaire.",
        "summary": "Le licenciement est strictement encadré par le Code du Travail marocain. Cette page regroupe les textes disponibles sur les procédures et droits liés au licenciement.",
        "legal_domain": "travail",
        "keywords": ["licenciement", "licenciement abusif", "indemnité", "préavis", "faute grave"],
        "priority": 0.85,
    },
    {
        "slug": "code-de-commerce-maroc",
        "title": "Code de Commerce du Maroc : textes juridiques",
        "description": "Les textes du Code de Commerce marocain : obligations commerciales, sociétés, registre de commerce, fonds de commerce.",
        "summary": "Le droit commercial marocain régit les relations entre commerçants et les activités commerciales.",
        "legal_domain": "commercial",
        "keywords": ["code de commerce", "commerçant", "registre de commerce", "fonds de commerce", "baux commerciaux"],
        "priority": 0.85,
    },
    {
        "slug": "sarl-maroc",
        "title": "SARL au Maroc : création, fonctionnement et textes juridiques",
        "description": "Guide complet sur la Société à Responsabilité Limitée au Maroc : capital, gérance, associés, dissolution.",
        "summary": "La SARL est la forme sociétaire la plus répandue au Maroc, régie par la Loi 5-96.",
        "legal_domain": "commercial",
        "keywords": ["SARL", "société responsabilité limitée", "gérant", "associés", "capital social", "Loi 5-96"],
        "priority": 0.85,
    },
    {
        "slug": "bail-commercial-maroc",
        "title": "Bail commercial au Maroc : droits et obligations",
        "description": "Textes sur le bail commercial marocain : durée, renouvellement, résiliation, droit au bail.",
        "summary": "Le bail commercial est encadré par le Code de Commerce marocain et protège les fonds de commerce.",
        "legal_domain": "commercial",
        "keywords": ["bail commercial", "loyer commercial", "renouvellement bail", "résiliation", "droit au bail"],
        "priority": 0.85,
    },
    {
        "slug": "recouvrement-maroc",
        "title": "Recouvrement de créances au Maroc",
        "description": "Procédures de recouvrement au Maroc : injonction de payer, saisie, voies d'exécution.",
        "summary": "Le recouvrement de créances au Maroc passe par des procédures judiciaires spécifiques.",
        "legal_domain": "commercial",
        "keywords": ["recouvrement", "injonction de payer", "saisie", "créance", "voies d'exécution"],
        "priority": 0.85,
    },
    {
        "slug": "cheque-sans-provision-maroc",
        "title": "Chèque sans provision au Maroc : sanctions et recours",
        "description": "Textes sur le chèque sans provision au Maroc : sanctions pénales, civiles, interdiction bancaire.",
        "summary": "Le chèque sans provision est une infraction pénale au Maroc passible de sanctions.",
        "legal_domain": "commercial",
        "keywords": ["chèque sans provision", "chèque impayé", "interdiction bancaire", "Code Pénal", "sanctions"],
        "priority": 0.85,
    },
    {
        "slug": "creation-societe-maroc",
        "title": "Création de société au Maroc : étapes et textes",
        "description": "Guide pour créer une société au Maroc : SA, SARL, SNC — formalités, RC, statuts.",
        "summary": "La création d'une société au Maroc implique plusieurs étapes : rédaction des statuts, dépôt au RC, publication.",
        "legal_domain": "commercial",
        "keywords": ["création société", "RC", "statuts", "SA", "SARL", "SNC", "formalités constitutives"],
        "priority": 0.85,
    },
    {
        "slug": "code-de-la-famille-maroc",
        "title": "Code de la Famille (Moudawwana) au Maroc",
        "description": "Textes du Code de la Famille marocain : mariage, divorce, garde des enfants, héritage.",
        "summary": "La Moudawwana régit le droit de la famille au Maroc : mariage, divorce, filiation, succession.",
        "legal_domain": "civil",
        "keywords": ["moudawwana", "code de la famille", "mariage", "divorce", "garde enfants", "héritage", "succession"],
        "priority": 0.85,
    },
    {
        "slug": "divorce-maroc",
        "title": "Divorce au Maroc : procédures et droits",
        "description": "Textes sur le divorce au Maroc : chiqaq, talaq, divorce judiciaire, pension alimentaire.",
        "summary": "Le divorce au Maroc est régi par la Moudawwana et peut prendre plusieurs formes.",
        "legal_domain": "civil",
        "keywords": ["divorce", "chiqaq", "talaq", "khol", "pension alimentaire", "Moudawwana", "garde"],
        "priority": 0.85,
    },
    {
        "slug": "delai-de-prescription-maroc",
        "title": "Délais de prescription au Maroc",
        "description": "Délais de prescription en droit marocain : civil, commercial, pénal, administratif.",
        "summary": "Les délais de prescription varient selon la nature de l'action et le domaine juridique au Maroc.",
        "legal_domain": "civil",
        "keywords": ["prescription", "délai de prescription", "forclusion", "DOC", "Code Pénal", "commerce"],
        "priority": 0.85,
    },
    {
        "slug": "procedure-civile-maroc",
        "title": "Procédure civile au Maroc",
        "description": "Textes sur la procédure civile marocaine : tribunaux, appel, cassation, exécution des jugements.",
        "summary": "La procédure civile marocaine est régie par le Code de Procédure Civile.",
        "legal_domain": "civil",
        "keywords": ["procédure civile", "tribunal", "appel", "cassation", "jugement", "exécution", "CPC"],
        "priority": 0.85,
    },
]

# ── Pages statiques ───────────────────────────────────────────────────────────
STATIC_PAGES = [
    {
        "url": "/base",
        "title": "Base de données juridique marocaine — JuriThèque",
        "description": "Recherchez dans plus de 600 textes juridiques marocains : lois, décrets, dahirs, codes, arrêtés.",
        "document_type": "Base de données",
        "priority": 0.9,
        "keywords": ["lois marocaines", "textes juridiques", "base de données", "décrets", "dahirs"],
    },
    {
        "url": "/domaines",
        "title": "Domaines juridiques — JuriThèque",
        "description": "Explorez les 11 domaines juridiques marocains : civil, commercial, travail, pénal, fiscal, famille…",
        "document_type": "Navigation",
        "priority": 0.8,
        "keywords": ["domaines juridiques", "droit civil", "droit commercial", "droit du travail", "droit pénal"],
    },
    {
        "url": "/fr/guides",
        "title": "Guides juridiques thématiques — JuriThèque",
        "description": "12 guides thématiques sur le droit marocain basés sur les textes officiels.",
        "document_type": "Index guides",
        "priority": 0.85,
        "keywords": ["guides juridiques", "droit marocain", "thématique"],
    },
    {
        "url": "/fr/veille-juridique",
        "title": "Veille juridique marocaine — Nouveaux textes et modifications",
        "description": "Suivez les nouveaux textes juridiques marocains et les modifications récentes de la législation.",
        "document_type": "Veille juridique",
        "priority": 0.85,
        "keywords": ["veille juridique", "nouveaux textes", "modifications", "législation récente"],
    },
    {
        "url": "/assistant",
        "title": "Assistant IA juridique — Droit marocain",
        "description": "Posez vos questions sur le droit marocain à notre assistant IA spécialisé.",
        "document_type": "Assistant IA",
        "priority": 0.7,
        "keywords": ["assistant juridique", "IA juridique", "questions droit"],
    },
]

# ── Helpers Supabase ──────────────────────────────────────────────────────────
def sb_get(endpoint: str, params: dict) -> list:
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
        log(f"[red]✗ GET /{endpoint}: {e}[/]")
        return []


def sb_delete_all(dry_run: bool) -> bool:
    """Vide la table site_search_index."""
    if dry_run:
        log("[dim]  [dry-run] Suppression de l'index ignorée.[/]")
        return True
    try:
        r = httpx.delete(
            f"{SUPABASE_URL}/rest/v1/site_search_index",
            headers={**HEADERS, "Prefer": "return=minimal"},
            params={"id": "gte.0"},  # supprime tout
            timeout=30,
        )
        r.raise_for_status()
        log("[green]✓ Index vidé.[/]")
        return True
    except Exception as e:
        log(f"[red]✗ Suppression index: {e}[/]")
        return False


def sb_upsert(rows: list[dict], dry_run: bool) -> int:
    """Insère/met à jour des lignes dans site_search_index. Retourne le nombre de lignes."""
    if dry_run:
        return len(rows)
    if not rows:
        return 0

    BATCH = 200
    total = 0
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        try:
            r = httpx.post(
                f"{SUPABASE_URL}/rest/v1/site_search_index",
                headers={**HEADERS, "Prefer": "resolution=merge-duplicates,return=minimal"},
                json=batch,
                timeout=60,
            )
            r.raise_for_status()
            total += len(batch)
        except Exception as e:
            log(f"[red]✗ Upsert batch {i//BATCH + 1}: {e}[/]")
    return total


# ── Récupération des données ──────────────────────────────────────────────────
def fetch_laws(limit: int | None = None) -> list[dict]:
    """Récupère les champs utiles des lois publiques (sans content_fr/content_ar)."""
    fields = ",".join([
        "id", "number", "title_fr", "title_ar", "type", "status",
        "date", "domain_id", "excerpt_fr", "simple_summary_fr",
        "legal_keywords", "extraction_confidence_score",
        "needs_human_review", "updated_at",
    ])
    all_rows = []
    offset   = 0
    batch    = 1000
    while True:
        params = {
            "select":                    fields,
            "is_publicly_indexable":     "eq.true",
            "order":                     "id.asc",
            "limit":                     str(min(batch, limit - len(all_rows)) if limit else batch),
            "offset":                    str(offset),
        }
        rows = sb_get("laws", params)
        if not rows:
            break
        all_rows.extend(rows)
        if limit and len(all_rows) >= limit:
            break
        if len(rows) < batch:
            break
        offset += batch
    return all_rows[:limit] if limit else all_rows


def fetch_domains() -> list[dict]:
    return sb_get("domains", {"select": "id,name_fr,name_ar,sub_domains,law_count"})


# ── Construction des lignes d'index ──────────────────────────────────────────
def law_to_index_row(law: dict) -> dict:
    """Convertit un enregistrement law en ligne site_search_index."""
    score  = law.get("extraction_confidence_score") or 0
    review = law.get("needs_human_review") or False

    # Priorité : 0.3 si à vérifier, sinon proportionnelle au score (min 0.3)
    if review:
        priority = 0.3
    else:
        priority = round(max(0.3, min(1.0, (score or 50) / 100)), 2)

    # Résumé : simple_summary_fr → excerpt_fr (jamais content_fr)
    summary = (
        (law.get("simple_summary_fr") or "")[:400].strip()
        or (law.get("excerpt_fr") or "")[:300].strip()
    )

    # Mots-clés
    raw_kw = law.get("legal_keywords") or []
    keywords = raw_kw if isinstance(raw_kw, list) else []

    title = law.get("title_fr") or law.get("title_ar") or f"Texte {law['id']}"
    desc  = (law.get("excerpt_fr") or "")[:200].strip()

    return {
        "source_type":   "law",
        "source_id":     str(law["id"]),
        "url":           f"/loi/{law['id']}",
        "title":         title,
        "description":   desc or None,
        "summary":       summary or None,
        "keywords":      keywords,
        "legal_domain":  law.get("domain_id") or None,
        "document_type": law.get("type") or None,
        "language":      "fr",
        "priority":      priority,
        "is_public":     True,
        "updated_at":    law.get("updated_at") or datetime.now(timezone.utc).isoformat(),
    }


def guide_to_index_row(guide: dict) -> dict:
    return {
        "source_type":   "guide",
        "source_id":     guide["slug"],
        "url":           f"/fr/guides/{guide['slug']}",
        "title":         guide["title"],
        "description":   guide.get("description") or None,
        "summary":       guide.get("summary") or None,
        "keywords":      guide.get("keywords") or [],
        "legal_domain":  guide.get("legal_domain") or None,
        "document_type": "Guide thématique",
        "language":      "fr",
        "priority":      guide.get("priority", 0.85),
        "is_public":     True,
        "updated_at":    datetime.now(timezone.utc).isoformat(),
    }


def domain_to_index_row(domain: dict) -> dict:
    sub = domain.get("sub_domains") or []
    sub_str = ", ".join(sub[:5]) if isinstance(sub, list) else ""
    return {
        "source_type":   "domain",
        "source_id":     domain["id"],
        "url":           f"/domaine/{domain['id']}",
        "title":         domain.get("name_fr") or domain["id"],
        "description":   f"Textes juridiques marocains en matière de {domain.get('name_fr','').lower()}. {sub_str}".strip(". ") or None,
        "summary":       None,
        "keywords":      [domain.get("name_fr") or "", domain.get("name_ar") or ""],
        "legal_domain":  domain["id"],
        "document_type": "Domaine juridique",
        "language":      "fr",
        "priority":      0.8,
        "is_public":     True,
        "updated_at":    datetime.now(timezone.utc).isoformat(),
    }


def static_to_index_row(page: dict) -> dict:
    return {
        "source_type":   "static_page",
        "source_id":     page["url"],
        "url":           page["url"],
        "title":         page["title"],
        "description":   page.get("description") or None,
        "summary":       None,
        "keywords":      page.get("keywords") or [],
        "legal_domain":  None,
        "document_type": page.get("document_type") or None,
        "language":      "fr",
        "priority":      page.get("priority", 0.5),
        "is_public":     True,
        "updated_at":    datetime.now(timezone.utc).isoformat(),
    }


# ── Point d'entrée ────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Reconstruit le site_search_index dans Supabase")
    parser.add_argument("--dry-run",  action="store_true", help="Simulation sans écriture")
    parser.add_argument("--clear",    action="store_true", help="Vide l'index avant reconstruction")
    parser.add_argument("--limit",    type=int,            help="Limite le nombre de lois indexées")
    parser.add_argument("--source",   choices=["laws", "guides", "domains", "static"],
                                                           help="Indexer uniquement cette source")
    args = parser.parse_args()

    do_laws    = args.source in (None, "laws")
    do_guides  = args.source in (None, "guides")
    do_domains = args.source in (None, "domains")
    do_static  = args.source in (None, "static")

    log("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log("[bold gold1]  JuriThèque — Reconstruction du site_search_index         [/]")
    log("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")
    if args.dry_run:
        log("[yellow]⚠  Mode DRY-RUN activé — aucune écriture en base.[/]\n")

    # ── Vidage optionnel ─────────────────────────────────────────────────────
    if args.clear and not args.source:
        log("[dim]→ Vidage de l'index...[/]")
        sb_delete_all(args.dry_run)

    rows = []
    report = {}

    # ── Lois ─────────────────────────────────────────────────────────────────
    if do_laws:
        log(f"[dim]→ Récupération des lois (limit={args.limit or 'toutes'})...[/]")
        laws = fetch_laws(args.limit)
        law_rows = [law_to_index_row(l) for l in laws]
        report["laws"] = len(law_rows)
        rows.extend(law_rows)
        log(f"  [green]✓[/] {len(law_rows)} lois préparées")

    # ── Guides ───────────────────────────────────────────────────────────────
    if do_guides:
        guide_rows = [guide_to_index_row(g) for g in SEO_GUIDES]
        report["guides"] = len(guide_rows)
        rows.extend(guide_rows)
        log(f"  [green]✓[/] {len(guide_rows)} guides préparés")

    # ── Domaines ─────────────────────────────────────────────────────────────
    if do_domains:
        log("[dim]→ Récupération des domaines...[/]")
        domains = fetch_domains()
        domain_rows = [domain_to_index_row(d) for d in domains]
        report["domains"] = len(domain_rows)
        rows.extend(domain_rows)
        log(f"  [green]✓[/] {len(domain_rows)} domaines préparés")

    # ── Pages statiques ──────────────────────────────────────────────────────
    if do_static:
        static_rows = [static_to_index_row(p) for p in STATIC_PAGES]
        report["static_pages"] = len(static_rows)
        rows.extend(static_rows)
        log(f"  [green]✓[/] {len(static_rows)} pages statiques préparées")

    # ── Insertion ────────────────────────────────────────────────────────────
    total_rows = len(rows)
    log(f"\n[bold]Total à indexer : {total_rows} lignes[/]")

    if total_rows == 0:
        log("[yellow]⚠  Aucune ligne à indexer.[/]")
        return

    if not args.dry_run:
        log("[dim]→ Écriture dans Supabase...[/]")

    inserted = sb_upsert(rows, args.dry_run)

    # ── Rapport final ────────────────────────────────────────────────────────
    log("\n[bold green]✅ Indexation terminée[/]")
    if args.dry_run:
        log("[yellow]   (dry-run — aucune ligne écrite)[/]")
    else:
        log(f"   [green]{inserted}/{total_rows} lignes écrites avec succès[/]")

    log("\n[bold]Détail par source :[/]")
    for source, count in report.items():
        log(f"  {source:15s} → {count} lignes")

    # Rapport JSON
    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "total": total_rows,
        "inserted": inserted if not args.dry_run else 0,
        "by_source": report,
    }
    report_path = Path(__file__).parent / "last_index_report.json"
    report_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"\n[dim]→ Rapport JSON : {report_path}[/]")


if __name__ == "__main__":
    main()
