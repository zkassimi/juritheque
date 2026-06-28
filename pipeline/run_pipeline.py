"""
run_pipeline.py — Orchestrateur du pipeline juridique complet
=============================================================
Enchaîne les 7 étapes du pipeline en une seule commande :
  1. Veille (détection nouveaux textes)
  2. Import depuis la queue
  3. Enrichissement (résumés, mots-clés, SEO + scores)
  3b. Assignation des domaines juridiques
  3c. Traduction résumés FR → AR
  4. Régénération du sitemap
  5. Reconstruction de l'index de recherche

Modes d'exécution :
  --mode auto   : publie automatiquement si global_confidence_score ≥ 85
  --mode semi   : prépare, calcule les scores, ne publie pas sans validation
  --mode manual : prépare uniquement, review humaine systématique sur tout

Usage :
  python pipeline/run_pipeline.py --dry-run
  python pipeline/run_pipeline.py --mode semi --source sgg_home
  python pipeline/run_pipeline.py --mode auto --limit 20
  python pipeline/run_pipeline.py --step veille          # étape unique
  python pipeline/run_pipeline.py --step import
  python pipeline/run_pipeline.py --step enrich

Flags :
  --dry-run      aperçu sans aucune écriture
  --mode         auto | semi | manual  (défaut: semi)
  --source       id de la source (ex: sgg_home, adala) — filtre la veille
  --limit        max items à importer (défaut: 50)
  --step         étape unique à exécuter (veille|import|enrich|domains|translate_ar|sitemap|index)
  --skip-veille  sauter l'étape de veille (import depuis queue existante)
  --skip-enrich  sauter l'enrichissement après import
  --no-sitemap   ne pas régénérer le sitemap
"""

import os, sys, json, time, argparse, subprocess
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY", ""))

console = Console()

PIPELINE_DIR = Path(__file__).parent

# ── Coûts IA estimés par opération (USD approximatifs) ───────────────────────
AI_COST_PER_IMPORT   = 0.003   # ~3 pages PDF → Gemini Flash
AI_COST_PER_ENRICH   = 0.015   # résumé + SEO → Claude Haiku


# ── Outils de base ────────────────────────────────────────────────────────────

def run_step(label: str, cmd: list, dry_run: bool = False, capture: bool = False) -> dict:
    """Lance un sous-script Python et retourne les résultats."""
    if dry_run:
        console.print(f"  [yellow]DRY-RUN[/] → skipped: {' '.join(cmd)}")
        return {"ok": True, "skipped": True, "duration": 0}

    console.print(f"  [cyan]▶ {label}[/]")
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, "-X", "utf8"] + cmd,
        cwd=str(PIPELINE_DIR.parent),
        capture_output=capture,
        text=True,
    )
    duration = round(time.time() - t0, 1)
    ok = result.returncode == 0
    if not ok:
        console.print(f"  [red]❌ Échec ({result.returncode}) — {label}[/]")
        if result.stderr:
            console.print(f"  [dim]{result.stderr[:300]}[/]")
    else:
        console.print(f"  [green]✓ {label}[/] ({duration}s)")
    return {"ok": ok, "duration": duration, "returncode": result.returncode}


def post_run_record(run_id: str | None, report: dict) -> None:
    """Enregistre le rapport de run dans pipeline_runs (si Supabase dispo)."""
    if not SUPABASE_URL or not SUPABASE_KEY or not run_id:
        return
    try:
        import requests
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        }
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/pipeline_runs",
            headers={**headers, "Prefer": "return=minimal"},
            params={"id": f"eq.{run_id}"},
            json={
                "finished_at":       datetime.now(timezone.utc).isoformat(),
                "status":            "done" if report.get("errors", 0) == 0 else "failed",
                "sources_checked":   report.get("sources_checked", 0),
                "items_detected":    report.get("items_detected", 0),
                "items_imported":    report.get("items_imported", 0),
                "items_published":   report.get("items_published", 0),
                "items_draft":       report.get("items_draft", 0),
                "items_review":      report.get("items_review", 0),
                "errors":            report.get("errors", 0),
                "ai_cost_usd":       report.get("ai_cost_usd", 0),
                "duration_seconds":  report.get("duration_seconds", 0),
                "report_json":       report,
            },
            timeout=10,
        )
    except Exception as e:
        console.print(f"  [dim]pipeline_runs non enregistré: {e}[/]")


def create_run_record(mode: str, sources: list, dry_run: bool) -> str | None:
    """Crée un enregistrement dans pipeline_runs et retourne l'id."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        import requests
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/pipeline_runs",
            headers=headers,
            json={
                "mode": mode,
                "sources": sources or [],
                "dry_run": dry_run,
                "status": "running",
            },
            timeout=10,
        )
        if resp.status_code in (200, 201):
            rows = resp.json()
            return rows[0]["id"] if rows else None
    except Exception:
        pass
    return None


# ── Étapes du pipeline ────────────────────────────────────────────────────────

def step_veille(args, report: dict) -> None:
    """Étape 1 : Veille juridique (détection nouveaux textes)."""
    console.print("\n[bold]Étape 1/5 — Veille juridique[/]")
    cmd = ["pipeline/veille_juridique.py"]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.source:
        cmd += ["--source", args.source]
    r = run_step("Veille juridique", cmd, dry_run=False)  # on laisse le script gérer --dry-run
    if not r["ok"]:
        report["errors"] += 1
    report["steps"]["veille"] = r


def step_import(args, report: dict) -> None:
    """Étape 2 : Import depuis la queue."""
    console.print("\n[bold]Étape 2/5 — Import depuis la queue[/]")
    cmd = [
        "pipeline/import_from_queue.py",
        "--mode", args.mode,
        "--limit", str(args.limit),
    ]
    if args.dry_run:
        cmd.append("--dry-run")
    r = run_step("Import queue", cmd, dry_run=False)
    if not r["ok"]:
        report["errors"] += 1
    report["steps"]["import"] = r
    # Coût IA estimé (approximation)
    report["ai_cost_usd"] += args.limit * AI_COST_PER_IMPORT * 0.3  # ~30% ont vraiment du PDF


def step_enrich(args, report: dict) -> None:
    """Étape 3 : Enrichissement (résumés, mots-clés, SEO)."""
    console.print("\n[bold]Étape 3/5 — Enrichissement IA[/]")
    cmd = [
        "pipeline/enrich.py",
        "--only-missing",
        "--limit", str(min(args.limit, 20)),   # max 20 enrichissements par run
    ]
    if args.dry_run:
        cmd.append("--dry-run")
    r = run_step("Enrichissement", cmd, dry_run=False)
    if not r["ok"]:
        report["warnings"] += 1   # Enrich échoue = warning, pas erreur critique
    report["steps"]["enrich"] = r
    report["ai_cost_usd"] += min(args.limit, 20) * AI_COST_PER_ENRICH * 0.5


def step_domains(args, report: dict) -> None:
    """Étape 3b : Auto-assigner domaines juridiques aux nouvelles lois."""
    console.print("\n[bold]Étape 3b — Assign domaines juridiques[/]")
    cmd = [
        "pipeline/assign_domains.py",
        "--limit", str(args.limit),
    ]
    r = run_step("Assign domaines", cmd, dry_run=args.dry_run)
    if not r["ok"]:
        report["warnings"] += 1
    report["steps"]["domains"] = r


def step_translate_ar(args, report: dict) -> None:
    """Étape 3c : Traduire résumés FR → AR pour les nouvelles lois."""
    console.print("\n[bold]Étape 3c — Traduction résumés AR[/]")
    cmd = [
        "pipeline/translate_summaries_ar.py",
        "--limit", str(min(args.limit, 30)),  # max 30 traductions par run
    ]
    r = run_step("Traduction AR", cmd, dry_run=args.dry_run)
    if not r["ok"]:
        report["warnings"] += 1
    report["steps"]["translate_ar"] = r


def step_sitemap(args, report: dict) -> None:
    """Étape 4 : Régénération du sitemap."""
    console.print("\n[bold]Étape 4/5 — Sitemap[/]")
    cmd = ["pipeline/generate_sitemap.py"]
    r = run_step("Sitemap", cmd, dry_run=args.dry_run)
    if not r["ok"]:
        report["warnings"] += 1
    report["steps"]["sitemap"] = r


def step_index(args, report: dict) -> None:
    """Étape 5 : Reconstruction de l'index de recherche."""
    console.print("\n[bold]Étape 5/5 — Index de recherche[/]")
    cmd = ["pipeline/build_site_search_index.py"]
    r = run_step("Index recherche", cmd, dry_run=args.dry_run)
    if not r["ok"]:
        report["warnings"] += 1
    report["steps"]["index"] = r


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Orchestrateur du pipeline juridique JuriThèque"
    )
    parser.add_argument("--mode",        choices=["auto","semi","manual"], default="semi",
                        help="Mode pipeline : auto / semi / manual (défaut: semi)")
    parser.add_argument("--dry-run",     action="store_true",
                        help="Aperçu sans aucune écriture en base")
    parser.add_argument("--source",      default="",
                        help="Filtrer la veille sur une source (ex: sgg_home, adala)")
    parser.add_argument("--limit",       type=int, default=50,
                        help="Max items à importer (défaut: 50)")
    parser.add_argument("--step",        choices=["veille","import","enrich","domains","translate_ar","sitemap","index"],
                        help="Exécuter une seule étape")
    parser.add_argument("--skip-veille", action="store_true",
                        help="Sauter l'étape de veille")
    parser.add_argument("--skip-enrich", action="store_true",
                        help="Sauter l'enrichissement après import")
    parser.add_argument("--no-sitemap",  action="store_true",
                        help="Ne pas régénérer le sitemap")
    args = parser.parse_args()

    t_start = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── En-tête ───────────────────────────────────────────────────────────────
    mode_colors = {"auto": "green", "semi": "yellow", "manual": "red"}
    console.print(Panel(
        f"[bold]⚖️  JuriThèque — Pipeline Juridique[/]\n"
        f"Mode : [{mode_colors.get(args.mode, 'white')}]{args.mode.upper()}[/]  "
        f"{'[yellow]DRY-RUN[/]  ' if args.dry_run else ''}"
        f"Lancé le {now_str}",
        expand=False,
    ))

    # ── Rapport initial ───────────────────────────────────────────────────────
    report = {
        "started_at":     now_str,
        "mode":           args.mode,
        "dry_run":        args.dry_run,
        "source_filter":  args.source or "toutes",
        "sources_checked": 0,
        "items_detected":  0,
        "items_imported":  0,
        "items_published": 0,
        "items_draft":     0,
        "items_review":    0,
        "errors":          0,
        "warnings":        0,
        "ai_cost_usd":     0.0,
        "duration_seconds": 0,
        "steps":           {},
    }

    # Créer le run en base
    sources_list = [args.source] if args.source else []
    run_id = create_run_record(args.mode, sources_list, args.dry_run)
    if run_id:
        console.print(f"  [dim]Run ID: {run_id}[/]")

    # ── Exécution ─────────────────────────────────────────────────────────────

    if args.step:
        # Mode étape unique
        steps = {
            "veille":       step_veille,
            "import":       step_import,
            "enrich":       step_enrich,
            "domains":      step_domains,
            "translate_ar": step_translate_ar,
            "sitemap":      step_sitemap,
            "index":        step_index,
        }
        steps[args.step](args, report)

    else:
        # Pipeline complet
        if not args.skip_veille:
            step_veille(args, report)

        step_import(args, report)

        if not args.skip_enrich:
            step_enrich(args, report)
            step_domains(args, report)
            step_translate_ar(args, report)

        if not args.no_sitemap:
            step_sitemap(args, report)

        step_index(args, report)

    # ── Rapport final ─────────────────────────────────────────────────────────
    duration = round(time.time() - t_start)
    report["duration_seconds"] = duration
    report["ai_cost_usd"]      = round(report["ai_cost_usd"], 4)

    console.print("\n")
    console.print(Panel(
        f"[bold]Rapport de run[/] ({duration}s)\n"
        f"  Erreurs   : {'[red]' if report['errors'] else '[green]'}{report['errors']}[/]\n"
        f"  Warnings  : {report['warnings']}\n"
        f"  Coût IA   : ~${report['ai_cost_usd']:.4f} USD\n"
        f"  Mode      : {args.mode.upper()}\n"
        + (f"  [yellow]DRY-RUN — aucune donnée écrite[/]" if args.dry_run else ""),
        title="✅ Pipeline terminé" if report["errors"] == 0 else "⚠️ Pipeline terminé avec erreurs",
        expand=False,
    ))

    # Sauvegarder le rapport JSON
    report_path = PIPELINE_DIR / "last_run_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"  [dim]Rapport sauvegardé : {report_path}[/]")

    # Enregistrer dans pipeline_runs
    post_run_record(run_id, report)

    return 0 if report["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
