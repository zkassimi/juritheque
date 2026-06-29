"""
enrich_pipeline.py — Orchestrateur d'enrichissement complet (7 étapes)
=======================================================================
Lance toutes les étapes d'enrichissement dans l'ordre logique. Couvre
TOUTES les sources (SGG, ANRT, BKAM, Adala, CDR, etc.).

Étapes :
  1. Nettoyage titres        fix_adala_batch.py --titles
  2. Traduction titres AR→FR translate_titles_adala.py --limit 300
  3. Assignation domaines    assign_domains.py --limit 500
  4. Résumés (title_ar)      generate_adala_summaries.py --mode all --limit 300
  5. Résumés (content_fr)    enrich.py --only-missing --limit 50
  6. Traduction FR→AR        translate_summaries_ar.py --limit 300
  7. Recalcul scores         recalc_scores.py --limit 1000

Usage :
  python -X utf8 pipeline/enrich_pipeline.py --dry-run          # aperçu sans écriture
  python -X utf8 pipeline/enrich_pipeline.py --limit 100         # 100 textes max par étape
  python -X utf8 pipeline/enrich_pipeline.py --steps 4,5,7       # étapes sélectives
  python -X utf8 pipeline/enrich_pipeline.py                     # tout (limites par défaut)
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    def log(msg):         console.print(msg)
    def log_ok(msg):      console.print(f"[bold green]{msg}[/]")
    def log_warn(msg):    console.print(f"[yellow]{msg}[/]")
    def log_err(msg):     console.print(f"[bold red]{msg}[/]")
    def log_title(msg):   console.print(Panel(msg, style="bold blue"))
except ImportError:
    def log(msg):         print(msg, flush=True)
    def log_ok(msg):      print(f"✅ {msg}", flush=True)
    def log_warn(msg):    print(f"⚠  {msg}", flush=True)
    def log_err(msg):     print(f"❌ {msg}", flush=True)
    def log_title(msg):   print(f"\n{'═'*55}\n  {msg}\n{'═'*55}", flush=True)

# Répertoire racine du projet (parent de pipeline/)
ROOT = Path(__file__).resolve().parent.parent

STEPS = [
    {
        "num":              1,
        "name":             "Nettoyage titres",
        "desc":             "Nettoie les titres mal formatés (fix_adala_batch.py)",
        "cmd":              ["pipeline/fix_adala_batch.py", "--titles"],
        "cost":             "~$0 (aucun appel IA)",
        "supports_dry_run": False,  # fix_adala_batch.py ne supporte pas --dry-run
    },
    {
        "num":   2,
        "name":  "Traduction titres AR→FR",
        "desc":  "Traduit les titres arabes sans titre français",
        "cmd":   ["pipeline/translate_titles_adala.py", "--limit", "{limit}"],
        "cost":  "~$0.01/100 titres",
    },
    {
        "num":   3,
        "name":  "Assignation domaines",
        "desc":  "Assigne les domaines juridiques aux lois sans domaine",
        "cmd":   ["pipeline/assign_domains.py", "--limit", "{limit}"],
        "cost":  "~$0 (règles lexicales)",
    },
    {
        "num":   4,
        "name":  "Résumés depuis title_ar",
        "desc":  "Génère des résumés FR via Gemini pour toutes les lois avec title_ar (toutes sources)",
        "cmd":   ["pipeline/generate_adala_summaries.py", "--mode", "all", "--limit", "{limit}"],
        "cost":  "~$0.04/500 résumés (Gemini Flash Lite)",
    },
    {
        "num":   5,
        "name":  "Résumés depuis content_fr",
        "desc":  "Enrichit les lois avec content_fr extrait (résumé + TOC + SEO)",
        "cmd":   ["pipeline/enrich.py", "--only-missing", "--limit", "50"],
        "cost":  "~$0.40/200 lois (OpenRouter)",
    },
    {
        "num":   6,
        "name":  "Traduction résumés FR→AR",
        "desc":  "Traduit simple_summary_fr → simple_summary_ar",
        "cmd":   ["pipeline/translate_summaries_ar.py", "--limit", "{limit}"],
        "cost":  "~$0.03/500 résumés",
    },
    {
        "num":   7,
        "name":  "Recalcul scores de confiance",
        "desc":  "Recalcule global_confidence_score sur toutes les lois (sans coût IA)",
        "cmd":   ["pipeline/recalc_scores.py", "--limit", "1000"],
        "cost":  "~$0 (calcul local)",
    },
]


def build_cmd(step: dict, limit: int, dry_run: bool) -> list[str]:
    """Construit la commande finale en substituant {limit}."""
    limit_str = str(limit)
    cmd = [sys.executable, "-X", "utf8"]
    for part in step["cmd"]:
        cmd.append(part.replace("{limit}", limit_str))
    # N'ajouter --dry-run que si le script le supporte
    if dry_run and step.get("supports_dry_run", True):
        cmd.append("--dry-run")
    return cmd


def run_step(step: dict, limit: int, dry_run: bool) -> dict:
    """Exécute une étape et retourne {ok, returncode, duration, output}."""
    log(f"\n[dim]{'─'*55}[/]")
    log(f"[bold]Étape {step['num']}/7 — {step['name']}[/]")
    log(f"[dim]{step['desc']}[/]")
    log(f"[dim]Coût estimé : {step['cost']}[/]")

    # Si dry-run et script ne supporte pas --dry-run : ignorer l'étape proprement
    if dry_run and not step.get("supports_dry_run", True):
        log(f"[yellow]  ⏭ Ignoré en aperçu — script sans support dry-run[/]")
        return {"ok": True, "returncode": 0, "duration": 0}

    if dry_run:
        log(f"[yellow]  Mode DRY-RUN — aucune écriture[/]")
    cmd = build_cmd(step, limit, dry_run)
    log(f"[dim]  $ {' '.join(cmd[2:])}[/]\n")  # Affiche la commande réelle (avec limit substitué)

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=False,   # Streaming live vers le terminal
            timeout=1800,           # 30 min max par étape (traduction 300 résumés ≈ 10-15 min)
        )
        duration = time.time() - start
        ok = result.returncode == 0
        if ok:
            log_ok(f"  ✓ Étape {step['num']} terminée en {int(duration)}s")
        else:
            log_warn(f"  ⚠ Étape {step['num']} terminée avec code {result.returncode} ({int(duration)}s)")
        return {"ok": ok, "returncode": result.returncode, "duration": duration}
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        log_err(f"  ✗ Étape {step['num']} — TIMEOUT ({int(duration)}s > 600s)")
        return {"ok": False, "returncode": -1, "duration": duration}
    except FileNotFoundError as e:
        log_err(f"  ✗ Script introuvable : {e}")
        return {"ok": False, "returncode": -2, "duration": 0}
    except Exception as e:
        log_err(f"  ✗ Erreur inattendue : {e}")
        return {"ok": False, "returncode": -3, "duration": 0}


def main():
    parser = argparse.ArgumentParser(
        description="Enrichissement complet — 7 étapes ordonnées, toutes sources"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Aperçu sans écriture en base")
    parser.add_argument("--limit", type=int, default=300,
                        help="Nb max textes par étape (défaut: 300)")
    parser.add_argument("--steps", type=str, default="",
                        help="Étapes à exécuter, ex: '1,3,4,7' (défaut: toutes)")
    args = parser.parse_args()

    # Parsing des étapes sélectives
    if args.steps:
        try:
            selected = set(int(s.strip()) for s in args.steps.split(","))
        except ValueError:
            log_err("--steps doit être une liste de numéros séparés par des virgules, ex: '1,3,5'")
            sys.exit(1)
    else:
        selected = set(s["num"] for s in STEPS)

    steps_to_run = [s for s in STEPS if s["num"] in selected]

    log_title("🚀 JuriThèque — Enrichissement complet (toutes sources)")
    log(f"  Étapes    : {', '.join(str(s['num']) for s in steps_to_run)}")
    log(f"  Limite    : {args.limit} textes/étape")
    log(f"  Dry-run   : {'[yellow]OUI — aucune écriture[/]' if args.dry_run else '[green]NON — écriture réelle[/]'}")
    log(f"  Racine    : {ROOT}")

    results = {}
    total_start = time.time()

    for step in steps_to_run:
        result = run_step(step, args.limit, args.dry_run)
        results[step["num"]] = {"step": step, **result}
        # Une étape qui échoue n'arrête pas les suivantes
        if not result["ok"] and result["returncode"] not in (0, 1):
            log_warn(f"  → Script introuvable ou erreur critique — étape ignorée, on continue")

    total_duration = time.time() - total_start

    # ── Rapport final ─────────────────────────────────────────────────────────
    log(f"\n[bold]{'═'*55}[/]")
    log(f"[bold]📊 Rapport final[/]")
    log(f"[bold]{'═'*55}[/]")

    ok_count = sum(1 for r in results.values() if r["ok"])
    warn_count = sum(1 for r in results.values() if not r["ok"] and r["returncode"] in (1, 2))
    err_count = sum(1 for r in results.values() if not r["ok"] and r["returncode"] not in (0, 1, 2))

    for num, r in results.items():
        step = r["step"]
        status = "[green]✓[/]" if r["ok"] else "[yellow]⚠[/]" if r["returncode"] in (1, 2) else "[red]✗[/]"
        log(f"  {status} Étape {num} — {step['name']:<35} {int(r['duration'])}s")

    log(f"\n[bold green]✅ Réussies  : {ok_count}/{len(steps_to_run)}[/]")
    if warn_count:
        log(f"[yellow]⚠  Warnings  : {warn_count}[/]")
    if err_count:
        log(f"[red]✗  Erreurs   : {err_count}[/]")
    log(f"[dim]⏱  Durée totale : {int(total_duration//60)}m{int(total_duration%60):02d}s[/]")

    if args.dry_run:
        log(f"\n[yellow]ℹ  Mode DRY-RUN — aucune donnée écrite.[/]")
    else:
        log(f"\n[green]✅ Enrichissement terminé. Vérifier Admin → Qualité pour les nouvelles statistiques.[/]")

    return 0 if err_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
