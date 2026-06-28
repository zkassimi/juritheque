"""
recalc_scores.py — Recalcule les scores de confiance sur les lois existantes
=============================================================================
Calcule global_confidence_score (et les 7 sous-scores) sur les lois qui
n'ont pas encore de score — typiquement les lois importées avant la migration
021 ou enrichies avant l'intégration de score_utils dans enrich.py.

Aucun appel IA — coût = $0. Vitesse : ~500 lois/minute.

Usage :
  python pipeline/recalc_scores.py --dry-run         # aperçu sans écriture
  python pipeline/recalc_scores.py --limit 500        # 500 lois sans score
  python pipeline/recalc_scores.py --all              # toutes les lois
  python pipeline/recalc_scores.py --needs-review     # lois flaggées needs_human_review
  python pipeline/recalc_scores.py --low              # lois avec score < 70

Prérequis :
  Variables .env : SUPABASE_URL, SUPABASE_SERVICE_KEY
  score_utils.py doit être dans pipeline/ (migration 021 appliquée)
"""

import os, sys, time, argparse
from pathlib import Path
from dotenv import load_dotenv
import httpx

try:
    from rich.console import Console
    from rich.progress import track
    console = Console()
    def log(msg): console.print(msg)
    def log_err(msg): console.print(f"[red]{msg}[/]")
except ImportError:
    def log(msg): print(msg)
    def log_err(msg): print(f"ERROR: {msg}", file=sys.stderr)
    def track(it, description=""): return it

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY", ""))

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}


def fetch_laws(mode: str, limit: int) -> list[dict]:
    """Récupère les lois selon le filtre demandé."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        log_err("SUPABASE_URL / SUPABASE_SERVICE_KEY manquants dans .env")
        return []

    SELECT = (
        "id,number,title_fr,title_ar,type,status,date,domain_id,"
        "source_url,source_name,pdf_url,content_fr,content_ar,"
        "canonical_slug,simple_summary_fr,seo_title_fr,seo_description_fr,"
        "legal_keywords,extraction_confidence_score,global_confidence_score,"
        "needs_human_review,is_publicly_indexable"
    )

    params = {"select": SELECT, "order": "id.desc", "limit": str(limit)}

    if mode == "missing":
        params["global_confidence_score"] = "is.null"
    elif mode == "needs_review":
        params["needs_human_review"] = "eq.true"
    elif mode == "low":
        params["global_confidence_score"] = "lt.70"
        params["global_confidence_score2"] = "not.is.null"  # Note: PostgREST ne supporte pas deux filtres sur même champ facilement
    # mode == "all" : pas de filtre supplémentaire

    try:
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers={**HEADERS, "Prefer": "count=exact"},
            params=params,
            timeout=30,
        )
        if r.status_code != 200:
            log_err(f"Erreur Supabase {r.status_code}: {r.text[:200]}")
            return []
        return r.json()
    except Exception as e:
        log_err(f"Erreur fetch: {e}")
        return []


def patch_law(law_id: int, fields: dict) -> bool:
    """PATCH un texte en Supabase."""
    try:
        r = httpx.patch(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers=HEADERS,
            params={"id": f"eq.{law_id}"},
            json=fields,
            timeout=10,
        )
        return r.status_code in (200, 204)
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Recalcule global_confidence_score sur les lois existantes (0 coût IA)"
    )
    parser.add_argument("--dry-run",      action="store_true", help="Aperçu sans écrire en base")
    parser.add_argument("--limit",        type=int, default=500, help="Nb max lois à traiter (défaut: 500)")
    parser.add_argument("--all",          action="store_true", help="Traiter TOUTES les lois (ignore --limit)")
    parser.add_argument("--needs-review", action="store_true", help="Traiter uniquement les lois needs_human_review=true")
    parser.add_argument("--low",          action="store_true", help="Traiter les lois avec score < 70")
    args = parser.parse_args()

    # Vérification score_utils disponible
    try:
        from score_utils import compute_scores, apply_automation_rules, scores_to_db_fields
    except ImportError:
        log_err("[bold red]❌ score_utils.py non trouvé.[/] Assurez-vous que la migration 021 est appliquée.")
        log_err("   Chemin attendu : pipeline/score_utils.py")
        sys.exit(1)

    # Déterminer le mode de filtrage
    if args.needs_review:
        mode = "needs_review"
    elif args.low:
        mode = "low"
    elif args.all:
        mode = "all"
    else:
        mode = "missing"

    limit = 99999 if args.all else args.limit

    log(f"\n[bold]🎯 Recalcul des scores de confiance[/]")
    log(f"   Mode     : {mode}")
    log(f"   Limite   : {'toutes' if args.all else limit}")
    log(f"   Dry-run  : {'[yellow]OUI — aucune écriture[/]' if args.dry_run else '[green]NON — écriture réelle[/]'}\n")

    laws = fetch_laws(mode, limit)
    if not laws:
        log("[yellow]Aucune loi trouvée pour ce filtre.[/]")
        return 0

    log(f"[dim]→ {len(laws)} loi(s) à traiter[/]\n")

    stats = {
        "total": len(laws),
        "updated": 0,
        "failed": 0,
        "score_auto": 0,   # score ≥ 85
        "score_review": 0, # 70 ≤ score < 85
        "score_low": 0,    # score < 70
        "avg_score": 0,
    }
    scores_sum = 0

    for law in track(laws, description="Calcul scores…"):
        law_id = law["id"]
        try:
            # Calculer les 7 scores
            scores = compute_scores(law)
            g = scores.get("global_confidence_score", 0)

            # Décision automation en mode semi (ne publie pas automatiquement)
            decision = apply_automation_rules(scores, mode="semi")

            # Champs à écrire
            db_fields = scores_to_db_fields(scores)
            db_fields["needs_human_review"] = decision["needs_human_review"]
            db_fields["pipeline_notes"]     = decision["pipeline_notes"]
            # Ne pas toucher à is_publicly_indexable (déjà géré par import/admin)

            scores_sum += g
            if g >= 85:
                stats["score_auto"] += 1
            elif g >= 70:
                stats["score_review"] += 1
            else:
                stats["score_low"] += 1

            if args.dry_run:
                badge = "[green]≥85[/]" if g >= 85 else ("[yellow]70-84[/]" if g >= 70 else "[red]<70[/]")
                log(f"  #{law_id:>6}  score={g:3d}  {badge}  "
                    f"[dim]{(law.get('title_fr') or '')[:50]}[/]")
                stats["updated"] += 1
            else:
                ok = patch_law(law_id, db_fields)
                if ok:
                    stats["updated"] += 1
                else:
                    stats["failed"] += 1
                    log_err(f"  #{law_id}: PATCH échoué")

        except Exception as e:
            log_err(f"  #{law_id}: Erreur — {e}")
            stats["failed"] += 1

    # ── Rapport final ─────────────────────────────────────────────────────
    stats["avg_score"] = round(scores_sum / stats["total"]) if stats["total"] > 0 else 0

    log("\n[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log(f"[bold green]✅ Traités    :[/] {stats['total']}")
    log(f"[bold blue]📝 Mis à jour :[/] {stats['updated']}" + (" (DRY-RUN)" if args.dry_run else ""))
    log(f"[bold red]✗  Échecs     :[/] {stats['failed']}")
    log(f"\n[bold]Distribution des scores :[/]")
    log(f"  [green]🚀 Score ≥ 85  (publiables) :[/] {stats['score_auto']}")
    log(f"  [yellow]👁 Score 70-84 (à valider)  :[/] {stats['score_review']}")
    log(f"  [red]⚠  Score < 70  (à améliorer):[/] {stats['score_low']}")
    log(f"  [dim]Moyenne globale            :[/] {stats['avg_score']}/100")

    if args.dry_run:
        log("\n[yellow]ℹ  Mode DRY-RUN — aucune donnée écrite.[/]")

    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
