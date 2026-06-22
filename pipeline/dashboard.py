# -*- coding: utf-8 -*-
"""
dashboard.py — JuriThèque Admin Dashboard Local
════════════════════════════════════════════════
Interface web locale pour lancer les scripts pipeline avec des boutons,
voir les logs en temps réel et suivre l'avancement.

Usage :
  python pipeline/dashboard.py
  → ouvre automatiquement http://localhost:8000

Sécurité :
  - Écoute uniquement sur 127.0.0.1 (jamais exposé au réseau)
  - Token requis pour toutes les actions (affiché au démarrage)
  - Seuls les scripts de la whitelist peuvent être exécutés
"""

import os, sys, uuid, subprocess, threading, secrets, webbrowser, time
from pathlib import Path
from datetime import date
from typing import Dict, Any
import requests as req_lib

# ── FastAPI ────────────────────────────────────────────────────────────────────
try:
    from fastapi import FastAPI, HTTPException, Request, Response
    from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
    import uvicorn
except ImportError:
    print("⚠  FastAPI/uvicorn manquant. Installez avec : pip install fastapi uvicorn")
    sys.exit(1)

# ── Configuration ──────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://bmargdbbcnhkrjeidmvh.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')
ROOT_DIR     = str(Path(__file__).parent.parent)  # dossier lexbase/

# Token de sécurité (depuis .env ou généré aléatoirement)
TOKEN = os.environ.get('DASHBOARD_TOKEN', '') or secrets.token_urlsafe(12)

# ── Whitelist des scripts ──────────────────────────────────────────────────────
SCRIPTS: Dict[str, Any] = {

  # ── Import & Crawl ──────────────────────────────────────────────────────────
  "crawl_adala": {
    "label":    "Crawler Adala (justice.gov.ma)",
    "desc":     "Crawle les ~7 867 textes du portail adala.justice.gov.ma",
    "category": "📥 Import & Crawl",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/crawl_adala.py"],
    "danger":   False,
    "risk":     "long",
  },
  "crawl_sgg": {
    "label":    "Crawler SGG",
    "desc":     "Crawle les ~140 PDFs de sgg.gov.ma (textes consolidés + importants)",
    "category": "📥 Import & Crawl",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/crawl_sgg.py"],
    "danger":   False,
    "risk":     "long",
  },
  "scraper_all": {
    "label":    "Scraper toutes sources",
    "desc":     "Lance le scraper sur les 11 sources officielles (ANRT, BKAM, MEM...)",
    "category": "📥 Import & Crawl",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/scraper.py", "--source", "all"],
    "danger":   True,
    "risk":     "sensitive",
  },
  "import_adala": {
    "label":    "Importer lois JSON",
    "desc":     "Importe public/data/lois-adala.json dans la base (500 lois par batch)",
    "category": "📥 Import & Crawl",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/import_lois_adala.py", "--limit", "500"],
    "danger":   True,
    "risk":     "sensitive",
  },
  "build_adala_meta": {
    "label":    "Fetch métadonnées lois",
    "desc":     "Récupère les métadonnées de ~6 808 lois depuis huquqai.ma → lois-adala.json",
    "category": "📥 Import & Crawl",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/build_lois_adala.py", "--limit", "500"],
    "danger":   False,
    "risk":     "long",
  },
  "extract_pdf": {
    "label":    "Extraire PDFs → DB",
    "desc":     "Extrait le texte de tous les PDFs dans pipeline/pdfs/ et insère dans Supabase (Gemini 2.5 Flash, ~$0.0005/PDF)",
    "category": "📥 Import & Crawl",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/extract.py"],
    "danger":   False,
    "risk":     "ai",
    "ai_cost_note": "~250 PDFs × $0.0005 ≈ $0.13 (Gemini 2.5 Flash)",
  },
  "extract_pdf_dry": {
    "label":    "Extraire PDFs (dry-run)",
    "desc":     "Teste l'extraction sans écrire en base — vérifie le nombre de PDFs et l'appel IA",
    "category": "📥 Import & Crawl",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/extract.py", "--dry-run"],
    "danger":   False,
    "risk":     "safe",
  },
  "extract_source_url": {
    "label":    "Extraire URLs sources",
    "desc":     "Détecte et complète les source_url manquantes dans la base",
    "category": "📥 Import & Crawl",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/extract_source_url.py"],
    "danger":   False,
    "risk":     "safe",
  },

  # ── Enrichissement IA ────────────────────────────────────────────────────────
  "enrich": {
    "label":    "Enrichir lois (résumés + TOC)",
    "desc":     "Génère résumés FR, TOC, mots-clés via OpenRouter (200 lois)",
    "category": "🧠 Enrichissement IA",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/enrich.py", "--only-missing", "--limit", "200"],
    "danger":   False,
    "risk":     "ai",
    "ai_cost_note": "~200 lois × $0.002 ≈ $0.40 (OpenRouter)",
  },
  "summaries_adala_new": {
    "label":    "Générer résumés manquants",
    "desc":     "Génère des résumés IA via Gemini pour les lois sans résumé (title_ar → résumé FR)",
    "category": "🧠 Enrichissement IA",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/generate_adala_summaries.py", "--mode", "null", "--limit", "500"],
    "danger":   False,
    "risk":     "ai",
    "ai_cost_note": "~500 lois × $0.00008 ≈ $0.04 (Gemini 2.5 Flash Lite)",
  },
  "summaries_adala_fix": {
    "label":    "Améliorer résumés génériques",
    "desc":     "Remplace les résumés placeholder par de vrais résumés IA — lancer avant Traduction AR",
    "category": "🧠 Enrichissement IA",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/generate_adala_summaries.py", "--mode", "placeholders", "--limit", "500"],
    "danger":   False,
    "risk":     "ai",
    "ai_cost_note": "~500 résumés × $0.00008 ≈ $0.04 (Gemini 2.5 Flash Lite)",
  },
  "translate_ar": {
    "label":    "Traduction AR (résumés)",
    "desc":     "Traduit simple_summary_fr → simple_summary_ar en arabe juridique (500 lois) — Gemini 2.5 Flash Lite",
    "category": "🧠 Enrichissement IA",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/translate_summaries_ar.py", "--limit", "500"],
    "danger":   False,
    "risk":     "ai",
    "ai_cost_note": "~500 résumés × $0.00006 ≈ $0.03 (Gemini 2.5 Flash Lite)",
  },
  "translate_titles": {
    "label":    "Traduction titres FR",
    "desc":     "Traduit les titres arabes → français pour les lois sans titre FR (200 titres)",
    "category": "🧠 Enrichissement IA",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/translate_titles_batch.py", "--limit", "200"],
    "danger":   False,
    "risk":     "ai",
    "ai_cost_note": "~200 titres × $0.00006 ≈ $0.01 (Gemini 2.5 Flash Lite)",
  },
  "translate_titles_adala": {
    "label":    "Traduction titres AR→FR",
    "desc":     "Traduit les titres arabes des lois vers le français (200 titres)",
    "category": "🧠 Enrichissement IA",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/translate_titles_adala.py", "--limit", "200"],
    "danger":   False,
    "risk":     "ai",
    "ai_cost_note": "~200 titres × $0.00006 ≈ $0.01 (Gemini 2.5 Flash Lite)",
  },
  "fix_adala": {
    "label":    "Nettoyer titres mal formatés",
    "desc":     "Supprime '— portail Adala' et autres artefacts des titres",
    "category": "🧠 Enrichissement IA",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/fix_adala_batch.py", "--titles"],
    "danger":   True,
    "risk":     "sensitive",
  },
  "assign_domains": {
    "label":    "Auto-assigner domaines",
    "desc":     "Détecte et assigne automatiquement le domaine juridique (500 lois)",
    "category": "🧠 Enrichissement IA",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/assign_domains.py", "--limit", "500"],
    "danger":   False,
    "risk":     "safe",
  },
  "enrich_sources": {
    "label":    "Enrichir sources",
    "desc":     "Complète source_name, source_url, bo_number, bo_date (500 lois)",
    "category": "🧠 Enrichissement IA",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/enrich_sources.py", "--limit", "500"],
    "danger":   False,
    "risk":     "safe",
  },
  "enrich_from_source_dry": {
    "label":    "Enrichir guides (dry-run)",
    "desc":     "Aperçu de enrich_from_source.py — voir les PDFs sources disponibles dans pipeline/sources/",
    "category": "🧠 Enrichissement IA",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/enrich_from_source.py", "--dry-run"],
    "danger":   False,
    "risk":     "safe",
  },
  "add_metadata": {
    "label":    "Ajouter métadonnées",
    "desc":     "Complète les champs metadata manquants (bo_number, bo_date, source_name...)",
    "category": "🧠 Enrichissement IA",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/add_metadata_laws.py"],
    "danger":   False,
    "risk":     "safe",
  },

  # ── SEO & Index ──────────────────────────────────────────────────────────────
  "sitemap": {
    "label":    "Générer sitemap.xml",
    "desc":     "Régénère public/sitemap.xml avec toutes les URLs indexables",
    "category": "🔍 SEO & Index",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/generate_sitemap.py"],
    "danger":   False,
    "risk":     "safe",
  },
  "search_index": {
    "label":    "Rebuilder index recherche",
    "desc":     "Reconstruit la table site_search_index (lois + guides + domaines)",
    "category": "🔍 SEO & Index",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/build_site_search_index.py"],
    "danger":   False,
    "risk":     "safe",
  },
  "submit_indexing": {
    "label":    "Soumettre URLs Google",
    "desc":     "Soumet toutes les URLs à Google Indexing API : lois + guides FR/AR + domaines + pages statiques (200/jour, reprend automatiquement)",
    "category": "🔍 SEO & Index",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/submit_indexing.py"],
    "danger":   False,
    "risk":     "safe",
  },
  "submit_indexing_dry": {
    "label":    "Preview indexation Google",
    "desc":     "Affiche les URLs à soumettre à Google sans rien envoyer (dry-run)",
    "category": "🔍 SEO & Index",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/submit_indexing.py", "--dry-run"],
    "danger":   False,
    "risk":     "safe",
  },
  "check_laws_list": {
    "label":    "Vérifier lois prioritaires",
    "desc":     "Compare la liste des ~70 lois essentielles du droit marocain avec la base Supabase — indique lesquelles sont présentes ou manquantes",
    "category": "🔍 SEO & Index",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/check_laws_list.py", "--missing-only"],
    "danger":   False,
    "risk":     "safe",
  },
  "check_laws_list_full": {
    "label":    "Vérifier lois prioritaires (complet)",
    "desc":     "Même vérification mais affiche TOUTES les lois (trouvées + manquantes) avec export CSV",
    "category": "🔍 SEO & Index",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/check_laws_list.py", "--export", "pipeline/laws_report.csv"],
    "danger":   False,
    "risk":     "safe",
  },
  "check_laws_v2": {
    "label":    "✅ Vérifier liste élargie v2 (~250 lois)",
    "desc":     "Vérifie les ~250 textes prioritaires (Constitution, Codes, Finances, Justice, Urbanisme, Travail, Santé, Environnement...) — affiche seulement les manquants groupés par domaine",
    "category": "🔍 SEO & Index",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/check_laws_list.py", "--csv", "pipeline/laws_priority_list_v2.csv", "--missing-only"],
    "danger":   False,
    "risk":     "safe",
  },
  "check_laws_v2_export": {
    "label":    "📊 Vérifier liste v2 + export CSV",
    "desc":     "Même vérification v2 mais exporte le rapport complet dans laws_report_v2.csv (Excel-compatible)",
    "category": "🔍 SEO & Index",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/check_laws_list.py", "--csv", "pipeline/laws_priority_list_v2.csv", "--export", "pipeline/laws_report_v2.csv"],
    "danger":   False,
    "risk":     "safe",
  },
  "hide_sensitive": {
    "label":    "Masquer textes sensibles (dry-run)",
    "desc":     "Détecte les textes à masquer (données perso, < 30 mots) — dry-run par défaut",
    "category": "🔍 SEO & Index",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/hide_sensitive_texts.py", "--dry-run"],
    "danger":   True,
    "risk":     "sensitive",
  },

  # ── Bulletins Officiels ──────────────────────────────────────────────────────
  "bo_monitor": {
    "label":    "Surveiller nouveaux BO",
    "desc":     "Vérifie les nouvelles parutions du Bulletin Officiel (dry-run)",
    "category": "📰 Bulletins Officiels",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/bo_monitor.py", "--dry-run"],
    "danger":   False,
    "risk":     "safe",
  },
  "scrape_bo": {
    "label":    "Scraper Bulletins Officiels",
    "desc":     "Met à jour la table bulletins_officiels depuis les lois détectées",
    "category": "📰 Bulletins Officiels",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/scrape_bulletins.py"],
    "danger":   False,
    "risk":     "long",
  },
  "build_bo_links": {
    "label":    "Rebuilder index BO",
    "desc":     "Récupère les métadonnées des 12 642 BO depuis huquqai.ma (100 par batch)",
    "category": "📰 Bulletins Officiels",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/build_bo_links.py", "--limit", "100"],
    "danger":   False,
    "risk":     "long",
  },

  # ── Build & Deploy ───────────────────────────────────────────────────────────
  "build": {
    "label":    "npm run build:full",
    "desc":     "Build Vite + prerendering 82 pages (37 guides FR + 37 AR + 8 statiques) → dist/ prêt à uploader",
    "category": "🔨 Build & Deploy",
    "cmd":      ["npm.cmd", "run", "build:full"],
    "danger":   False,
    "risk":     "safe",
  },
  "assign_domains_full": {
    "label":    "1. Assigner domaines (post-PDF)",
    "desc":     "Étape 1 après extract.py — remplit domain_ids[] sur les nouvelles lois insérées",
    "category": "🔨 Build & Deploy",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/assign_domains.py"],
    "danger":   False,
    "risk":     "safe",
  },
  "enrich_missing": {
    "label":    "2. Enrichir lois manquantes",
    "desc":     "Étape 2 après extract.py — génère canonical_slug, simple_summary_fr pour les nouvelles lois",
    "category": "🔨 Build & Deploy",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/enrich.py", "--only-missing"],
    "danger":   False,
    "risk":     "ai",
    "ai_cost_note": "~nouvelles lois × $0.002 (OpenRouter Gemini 2.5 Flash)",
  },
  "rebuild_search": {
    "label":    "3. Rebuilder index recherche",
    "desc":     "Étape 3 après extract.py — reconstruit site_search_index avec les nouvelles lois",
    "category": "🔨 Build & Deploy",
    "cmd":      [sys.executable, "-X", "utf8", "pipeline/build_site_search_index.py", "--source", "laws"],
    "danger":   False,
    "risk":     "safe",
  },
  "favicon": {
    "label":    "Générer favicon",
    "desc":     "Génère favicon.ico et apple-touch-icon.png depuis public/favicon.svg",
    "category": "🔨 Build & Deploy",
    "cmd":      [sys.executable, "pipeline/generate_favicon.py"],
    "danger":   False,
    "risk":     "safe",
  },
  "git_push": {
    "label":    "🚀 Git Push → Vercel",
    "desc":     "git add . + commit + push → Vercel rebuilde et déploie www.juritheque.com automatiquement",
    "category": "🔨 Build & Deploy",
    "cmd":      ["powershell", "-Command",
                 f"Set-Location '{ROOT_DIR}'; git add .; "
                 "$msg = 'deploy: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm'); "
                 "git commit -m $msg --allow-empty; "
                 "git push origin main"],
    "danger":   False,
    "risk":     "sensitive",
  },
  "build_and_push": {
    "label":    "🏗️ Build + Push → Vercel",
    "desc":     "npm run build:full → git push → Vercel déploie (tout en une commande)",
    "category": "🔨 Build & Deploy",
    "cmd":      ["powershell", "-Command",
                 f"Set-Location '{ROOT_DIR}'; npm.cmd run build:full; "
                 "if ($LASTEXITCODE -eq 0) { "
                 "git add .; "
                 "$msg = 'build: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm'); "
                 "git commit -m $msg --allow-empty; "
                 "git push origin main; "
                 "Write-Output 'Deploy envoyé à Vercel OK' "
                 "} else { Write-Output 'Build échoué — push annulé' }"],
    "danger":   False,
    "risk":     "sensitive",
  },
}

# ── Catégories ordonnées ───────────────────────────────────────────────────────
CATEGORIES = [
  "📥 Import & Crawl",
  "🧠 Enrichissement IA",
  "🔍 SEO & Index",
  "📰 Bulletins Officiels",
  "🔨 Build & Deploy",
]

# ── État des jobs en mémoire ───────────────────────────────────────────────────
jobs: Dict[str, Any] = {}
# { job_id: { process, script_id, label, status, logs: [], start_time } }

# ── App FastAPI ────────────────────────────────────────────────────────────────
app = FastAPI(title="JuriThèque Dashboard", docs_url=None, redoc_url=None)

# ── Auth helper ────────────────────────────────────────────────────────────────
def check_token(request: Request):
    token = (
        request.headers.get("X-Dashboard-Token")
        or request.cookies.get("dashboard_token")
        or request.query_params.get("token")
    )
    if token != TOKEN:
        raise HTTPException(status_code=401, detail="Token invalide")

# ── Stats Supabase + local ─────────────────────────────────────────────────────
def _count(headers, url, params):
    try:
        r = req_lib.get(url, headers=headers, params={**params, "limit": "1"}, timeout=5)
        return int(r.headers.get("content-range", "0/0").split("/")[-1])
    except Exception:
        return "?"

def get_stats():
    h   = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Prefer": "count=exact"}
    base = f"{SUPABASE_URL}/rest/v1/laws"
    _p  = Path(__file__).parent

    try:
        # ── Base de données ─────────────────────────────────────────────
        total         = _count(h, base, {"select": "id"})
        with_content  = _count(h, base, {"select": "id", "content_fr": "not.is.null"})
        with_content_ar = _count(h, base, {"select": "id", "content_ar": "not.is.null"})
        no_domain     = _count(h, base, {"select": "id", "domain_id": "is.null"})
        no_slug       = _count(h, base, {"select": "id", "canonical_slug": "is.null"})
        public_idx    = _count(h, base, {"select": "id", "is_publicly_indexable": "eq.true"})

        # ── Enrichissement ──────────────────────────────────────────────
        has_sum_fr    = _count(h, base, {"select": "id", "simple_summary_fr": "not.is.null"})
        no_sum_fr     = total - has_sum_fr if isinstance(total, int) and isinstance(has_sum_fr, int) else "?"
        has_sum_ar    = _count(h, base, {"select": "id", "simple_summary_ar": "not.is.null"})
        to_translate  = _count(h, base, {"select": "id", "simple_summary_fr": "not.is.null", "simple_summary_ar": "is.null"})

        # ── Pipeline local ──────────────────────────────────────────────
        pdfs_dir   = _p / "pdfs"
        done_dir   = _p / "pdfs" / "done"
        errors_dir = _p / "pdfs" / "errors"
        pdf_pending = len(list(pdfs_dir.glob("*.pdf")))     if pdfs_dir.exists()   else 0
        pdf_done    = len(list(done_dir.glob("*.pdf")))     if done_dir.exists()    else 0
        pdf_errors  = len(list(errors_dir.glob("*.pdf")))   if errors_dir.exists()  else 0

        # ── Google Indexing ─────────────────────────────────────────────
        today = date.today().isoformat().replace("-", "")
        log_today = _p.parent / f"pipeline/indexing_log_{date.today()}.json"
        indexed_today = 0
        if log_today.exists():
            try:
                import json as _json
                log = _json.loads(log_today.read_text(encoding="utf-8"))
                indexed_today = len(log.get("submitted", []))
            except Exception:
                pass

        # ── Guides SEO ──────────────────────────────────────────────────
        guides_file = _p.parent / "src" / "data" / "seoIntentPages.js"
        guide_count = 0
        if guides_file.exists():
            import re as _re
            txt = guides_file.read_text(encoding="utf-8")
            guide_count = len(_re.findall(r"slug\s*:", txt))

        return {
            "ok": True,
            # DB
            "total": total, "public_idx": public_idx,
            "with_content_fr": with_content, "with_content_ar": with_content_ar,
            "no_domain": no_domain, "no_slug": no_slug,
            # Enrichissement
            "has_sum_fr": has_sum_fr, "no_sum_fr": no_sum_fr,
            "has_sum_ar": has_sum_ar, "to_translate": to_translate,
            # Pipeline local
            "pdf_pending": pdf_pending, "pdf_done": pdf_done, "pdf_errors": pdf_errors,
            # SEO
            "guide_count": guide_count, "indexed_today": indexed_today,
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "total": "?", "ar": "?", "to_translate": "?", "review": "?"}

# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return HTMLResponse(HTML_PAGE, headers={"Cache-Control": "no-store, no-cache, must-revalidate"})

@app.post("/run/{script_id}")
async def run_script(script_id: str, request: Request):
    check_token(request)
    if script_id not in SCRIPTS:
        raise HTTPException(status_code=404, detail=f"Script '{script_id}' inconnu")

    script = SCRIPTS[script_id]

    # Verrou global — empêcher 2 jobs simultanés
    running = [j for j in jobs.values() if j["status"] == "running"]
    if running:
        raise HTTPException(status_code=409, detail=f"Job '{running[0]['label']}' déjà en cours. Arrêtez-le d'abord.")

    job_id = str(uuid.uuid4())[:8]

    try:
        proc = subprocess.Popen(
            script["cmd"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT_DIR,
            bufsize=1,
            shell=False,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossible de lancer le script : {e}")

    jobs[job_id] = {
        "process":    proc,
        "script_id":  script_id,
        "label":      script["label"],
        "status":     "running",
        "logs":       [],
        "start_time": time.time(),
    }
    return {"job_id": job_id, "script_id": script_id, "label": script["label"]}

@app.get("/stream/{job_id}")
async def stream_logs(job_id: str, request: Request):
    check_token(request)
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job introuvable")

    def event_generator():
        proc = jobs[job_id]["process"]
        try:
            for line in iter(proc.stdout.readline, ''):
                if not line:
                    break
                clean = line.rstrip('\n')
                jobs[job_id]["logs"].append(clean)
                yield f"data: {clean}\n\n"
        except Exception:
            pass
        finally:
            proc.wait()
            rc = proc.returncode
            jobs[job_id]["status"] = "done" if rc == 0 else "error"
            elapsed = int(time.time() - jobs[job_id]["start_time"])
            m, s = divmod(elapsed, 60)
            status_msg = "✅ Terminé" if rc == 0 else f"❌ Erreur (code {rc})"
            yield f"data: [DONE:{rc}] {status_msg} en {m}m{s:02d}s\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream",
                              headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.get("/status")
async def get_status(request: Request):
    check_token(request)
    result = {}
    for job_id, job in jobs.items():
        proc = job["process"]
        if job["status"] == "running" and proc.poll() is not None:
            job["status"] = "done" if proc.returncode == 0 else "error"
        elapsed = int(time.time() - job["start_time"])
        result[job_id] = {
            "script_id": job["script_id"],
            "label":     job["label"],
            "status":    job["status"],
            "elapsed":   elapsed,
            "log_lines": len(job["logs"]),
        }
    return result

@app.post("/stop/{job_id}")
async def stop_job(job_id: str, request: Request):
    check_token(request)
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job introuvable")
    proc = jobs[job_id]["process"]
    if proc.poll() is None:
        proc.terminate()
        jobs[job_id]["status"] = "stopped"
        return {"ok": True, "message": "Processus arrêté"}
    return {"ok": False, "message": "Processus déjà terminé"}

@app.get("/stats")
async def stats_endpoint(request: Request):
    check_token(request)
    return get_stats()

@app.get("/scripts")
async def list_scripts(request: Request):
    check_token(request)
    return {sid: {"label": s["label"], "desc": s["desc"], "category": s["category"], "danger": s["danger"]}
            for sid, s in SCRIPTS.items()}

# ── HTML Dashboard ─────────────────────────────────────────────────────────────
# (généré dynamiquement avec les scripts de la whitelist)

def build_html():
    by_cat = {c: [] for c in CATEGORIES}
    for sid, s in SCRIPTS.items():
        by_cat[s["category"]].append((sid, s))

    # Map chaque catégorie à un id de page court
    cat_pids = {cat: f"cat{i}" for i, cat in enumerate(CATEGORIES)}

    # Sidenav
    nav_html = '<button class="nav-link nav-active" data-page="stats" onclick="showPage(\'stats\')">📊 Statistiques</button>\n'
    for cat in CATEGORIES:
        if not by_cat[cat]:
            continue
        pid = cat_pids[cat]
        nav_html += f'    <button class="nav-link" data-page="{pid}" onclick="showPage(\'{pid}\')">{cat}</button>\n'

    # Pages scripts
    script_pages = ""
    for cat in CATEGORIES:
        if not by_cat[cat]:
            continue
        pid = cat_pids[cat]
        btns = ""
        for sid, s in by_cat[cat]:
            risk  = s.get("risk", "safe")
            da    = 'data-danger="true"' if s.get("danger") else ""
            ac    = s.get("ai_cost_note", "")
            aca   = f'data-ai-cost="{ac}"' if ac else ""
            rl    = {"safe": "SAFE", "long": "⏱ LONG", "sensitive": "⚠ SENSIBLE", "ai": "🤖 IA"}
            badge = f'<span class="risk-badge badge-{risk}">{rl.get(risk, risk)}</span>'
            desc  = f'<span class="btn-desc">{s["desc"]}</span>' if s.get("desc") else ""
            btns += f'''
              <button class="script-btn btn-{risk}" onclick="handleBtnClick(this)"
                      data-id="{sid}" data-risk="{risk}"
                      data-label="{s['label']}" {da} {aca}>
                <span class="btn-main"><span class="btn-label">{s['label']}</span>{badge}</span>{desc}
              </button>'''
        script_pages += f'''
        <div class="page" id="page-{pid}">
          <h2 class="page-title">{cat}</h2>
          <div class="btn-grid">{btns}
          </div>
        </div>'''

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>JuriThèque Admin Dashboard</title>
<style>
  :root{{--navy:#1a2e4a;--navy2:#243d5c;--navy3:#0f1c2e;--gold:#c9a84c;--green:#22c55e;--red:#ef4444;--amber:#f59e0b;--bg:#f0f4f8;--white:#fff;--muted:#64748b;--radius:10px;--shadow:0 2px 8px rgba(0,0,0,.12);--nav-w:200px;--hdr:52px;--log-h:42vh}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  html,body{{height:100%;overflow:hidden}}
  body{{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--navy);font-size:14px;display:flex;flex-direction:column}}
  /* ── Header ── */
  #topbar{{height:var(--hdr);flex-shrink:0;background:var(--navy);color:#fff;padding:0 18px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 12px rgba(0,0,0,.3);z-index:100}}
  .tb-left{{display:flex;align-items:center;gap:10px}}
  #topbar h1{{font-size:16px;font-weight:700}}
  .tb-sub{{color:var(--gold);font-size:11px}}
  #token-hint{{font-size:11px;color:rgba(255,255,255,.35);font-family:monospace}}
  .tb-btn{{font-size:11px;padding:4px 10px;border-radius:6px;border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.08);color:rgba(255,255,255,.7);cursor:pointer}}
  .tb-btn:hover{{background:rgba(255,255,255,.15);color:#fff}}
  /* ── Body area ── */
  #body-area{{flex:1;display:flex;overflow:hidden}}
  body.fullscreen #body-area{{display:none}}
  /* ── Sidenav ── */
  #sidenav{{width:var(--nav-w);flex-shrink:0;background:var(--navy2);display:flex;flex-direction:column;overflow-y:auto;padding:10px 8px;gap:2px}}
  .nav-link{{display:flex;align-items:center;gap:6px;padding:9px 12px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:500;color:rgba(255,255,255,.55);transition:all .15s;white-space:nowrap;border:none;background:transparent;width:100%;text-align:left}}
  .nav-link:hover{{background:rgba(255,255,255,.08);color:#fff}}
  .nav-link.nav-active{{background:var(--gold);color:var(--navy);font-weight:700}}
  /* ── Content ── */
  #content{{flex:1;overflow-y:auto;padding:16px}}
  .page{{display:none}}
  .page.active{{display:block}}
  /* ── Stats page ── */
  .stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(195px,1fr));gap:12px;margin-bottom:14px}}
  .stat-group{{background:var(--white);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow);border-top:3px solid var(--gold)}}
  .stat-group.blue{{border-top-color:#3b82f6}}.stat-group.purple{{border-top-color:#8b5cf6}}.stat-group.amber{{border-top-color:var(--amber)}}
  .sg-title{{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:10px;font-weight:700}}
  .stat-row{{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #f1f5f9}}
  .stat-row:last-child{{border-bottom:none}}
  .stat-label{{color:var(--muted);font-size:12px}}
  .stat-value{{font-weight:700;color:var(--navy);font-size:15px}}
  .stat-value.gold{{color:var(--gold)}}.stat-value.green{{color:var(--green)}}.stat-value.amber{{color:var(--amber)}}.stat-value.red{{color:var(--red)}}
  .stats-refresh{{width:100%;margin-top:10px;padding:6px;border-radius:6px;border:1px solid #e2e8f0;background:#fff;cursor:pointer;font-size:11px;color:var(--muted)}}
  .stats-refresh:hover{{background:#f8fafc}}
  /* ── Jobs section ── */
  .jobs-section{{background:var(--white);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow)}}
  .jobs-section h4{{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:12px;font-weight:700}}
  .jobs-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:8px}}
  .job-item{{background:#f8fafc;border-radius:8px;padding:8px 10px;border-left:3px solid var(--muted);font-size:12px}}
  .job-item.running{{border-color:var(--gold)}}.job-item.done{{border-color:var(--green)}}.job-item.error{{border-color:var(--red)}}.job-item.stopped{{opacity:.6}}
  .job-hd{{display:flex;justify-content:space-between;align-items:center;gap:4px}}
  .job-name{{font-weight:600;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
  .job-badge{{font-size:10px;font-weight:700;padding:1px 6px;border-radius:20px;background:#e2e8f0;color:var(--muted)}}
  .job-badge.running{{background:#fef3c7;color:#92400e}}.job-badge.done{{background:#dcfce7;color:#166534}}.job-badge.error{{background:#fee2e2;color:#991b1b}}
  .job-elapsed{{color:var(--muted);font-size:10px;margin-top:2px}}
  .btn-stop-sm{{font-size:10px;padding:2px 6px;border-radius:4px;border:1px solid #e2e8f0;background:#fff;cursor:pointer;color:var(--red)}}
  .btn-stop-sm:hover{{background:#fee2e2}}
  .no-jobs{{color:var(--muted);font-size:12px;font-style:italic;text-align:center;padding:16px 0;grid-column:1/-1}}
  /* ── Script pages ── */
  .page-title{{font-size:15px;font-weight:700;color:var(--navy);margin-bottom:14px;padding-bottom:10px;border-bottom:2px solid #f1f5f9}}
  .btn-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:10px}}
  .script-btn{{padding:10px 14px;border-radius:8px;font-size:13px;cursor:pointer;border:1.5px solid transparent;transition:all .15s;display:flex;flex-direction:column;align-items:flex-start;gap:4px;text-align:left;width:100%}}
  .btn-main{{display:flex;align-items:center;gap:6px;flex-wrap:wrap}}
  .btn-label{{font-weight:600}}
  .btn-desc{{font-size:11px;opacity:.6;line-height:1.3}}
  .btn-safe{{background:var(--navy);color:#fff;border-color:var(--navy)}}
  .btn-safe:hover{{background:var(--gold);border-color:var(--gold);color:var(--navy)}}
  .btn-long{{background:#fffbeb;color:#92400e;border-color:var(--amber)}}
  .btn-long:hover{{background:#fef3c7}}
  .btn-sensitive{{background:#fff;color:var(--red);border-color:var(--red)}}
  .btn-sensitive:hover{{background:#fee2e2}}
  .btn-ai{{background:#eff6ff;color:#1d4ed8;border-color:#93c5fd}}
  .btn-ai:hover{{background:#dbeafe}}
  .script-btn:disabled{{opacity:.5;cursor:not-allowed!important}}
  .btn-running{{background:#fef3c7!important;color:#92400e!important;border-color:#fde68a!important;animation:pulse 1.5s infinite}}
  @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.7}}}}
  .risk-badge{{font-size:10px;font-weight:700;padding:1px 5px;border-radius:4px;text-transform:uppercase;letter-spacing:.03em}}
  .badge-safe{{background:#d1fae5;color:#065f46}}.badge-long{{background:#fef3c7;color:#92400e}}.badge-sensitive{{background:#fee2e2;color:#991b1b}}.badge-ai{{background:#dbeafe;color:#1e40af}}
  /* ── Log panel ── */
  #log-panel{{height:var(--log-h);min-height:160px;flex-shrink:0;background:var(--navy3);display:flex;flex-direction:column;border-top:2px solid var(--navy2)}}
  body.fullscreen #log-panel{{height:calc(100vh - var(--hdr))}}
  #log-header{{background:var(--navy2);padding:7px 14px;display:flex;align-items:center;gap:8px;flex-shrink:0}}
  .logs-dot{{width:8px;height:8px;border-radius:50%;background:var(--muted);flex-shrink:0}}
  .logs-dot.running{{background:var(--gold);animation:pulse 1s infinite}}.logs-dot.done{{background:var(--green)}}.logs-dot.error{{background:var(--red)}}
  #log-job-label{{color:#fff;font-size:12px;font-weight:600;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
  #log-elapsed{{color:rgba(255,255,255,.4);font-size:11px;font-family:monospace;min-width:48px;text-align:right}}
  .log-ctrl{{font-size:11px;padding:3px 9px;border-radius:4px;border:1px solid rgba(255,255,255,.2);background:transparent;color:rgba(255,255,255,.6);cursor:pointer;white-space:nowrap}}
  .log-ctrl:hover{{background:rgba(255,255,255,.1);color:#fff}}
  #btn-log-stop{{border-color:rgba(239,68,68,.5);color:#fca5a5}}
  #btn-log-stop:hover{{background:rgba(239,68,68,.2)}}
  #logs-area{{flex:1;padding:10px 14px;font-family:'Courier New',monospace;font-size:12px;color:#94a3b8;line-height:1.6;overflow-y:auto;white-space:pre-wrap;word-break:break-all}}
  #logs-area .log-ok{{color:#86efac}}#logs-area .log-err{{color:#fca5a5}}#logs-area .log-warn{{color:#fde68a}}#logs-area .log-info{{color:#7dd3fc}}#logs-area .log-done{{color:#86efac;font-weight:bold}}
  /* ── Toast ── */
  .toast{{position:fixed;bottom:calc(var(--log-h) + 10px);right:20px;padding:10px 16px;border-radius:8px;font-size:13px;font-weight:600;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.2);animation:slideIn .3s ease}}
  .toast-ok{{background:#dcfce7;color:#166534;border:1px solid #86efac}}.toast-err{{background:#fee2e2;color:#991b1b;border:1px solid #fca5a5}}
  @keyframes slideIn{{from{{transform:translateY(20px);opacity:0}}to{{transform:none;opacity:1}}}}
  /* ── Modal ── */
  .modal-overlay{{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:500;display:flex;align-items:center;justify-content:center}}
  .modal{{background:#fff;border-radius:var(--radius);padding:24px;max-width:400px;width:90%;box-shadow:0 10px 40px rgba(0,0,0,.3)}}
  .modal h3{{font-size:16px;margin-bottom:8px;color:var(--red)}}.modal p{{color:var(--muted);font-size:13px;margin-bottom:20px;line-height:1.5}}
  .modal-actions{{display:flex;gap:8px;justify-content:flex-end}}
  .btn-cancel{{padding:8px 16px;border-radius:6px;border:1px solid #e2e8f0;background:#fff;cursor:pointer;font-size:13px}}
  .btn-confirm{{padding:8px 16px;border-radius:6px;border:none;background:var(--red);color:#fff;cursor:pointer;font-size:13px;font-weight:600}}
</style>
</head>
<body>

<div id="topbar">
  <div class="tb-left">
    <span style="font-size:20px">⚖️</span>
    <div>
      <h1>JuriThèque Admin Dashboard</h1>
      <span class="tb-sub">Pipeline & scripts — gestion locale</span>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:10px">
    <button class="tb-btn" onclick="loadStats()">↺ Stats</button>
    <span id="token-hint"></span>
  </div>
</div>

<div id="body-area">
  <nav id="sidenav">
    {nav_html}
  </nav>
  <div id="content">

    <!-- ── Page Statistiques ── -->
    <div class="page" id="page-stats">
      <div class="stats-grid">

        <div class="stat-group amber">
          <div class="sg-title">📥 Pipeline local</div>
          <div class="stat-row"><span class="stat-label">PDFs en attente</span><span class="stat-value amber" id="stat-pdf-pending">…</span></div>
          <div class="stat-row"><span class="stat-label">PDFs traités ✅</span><span class="stat-value green" id="stat-pdf-done">…</span></div>
          <div class="stat-row"><span class="stat-label">PDFs en erreur ⚠</span><span class="stat-value red" id="stat-pdf-errors">…</span></div>
        </div>

        <div class="stat-group">
          <div class="sg-title">📊 Base de données</div>
          <div class="stat-row"><span class="stat-label">Total lois</span><span class="stat-value gold" id="stat-total">…</span></div>
          <div class="stat-row"><span class="stat-label">Indexables publics</span><span class="stat-value green" id="stat-public">…</span></div>
          <div class="stat-row"><span class="stat-label">Avec texte FR</span><span class="stat-value" id="stat-content-fr">…</span></div>
          <div class="stat-row"><span class="stat-label">Avec texte AR</span><span class="stat-value" id="stat-content-ar">…</span></div>
          <div class="stat-row"><span class="stat-label">Sans domaine ⚠</span><span class="stat-value amber" id="stat-no-domain">…</span></div>
          <div class="stat-row"><span class="stat-label">Sans slug ⚠</span><span class="stat-value amber" id="stat-no-slug">…</span></div>
        </div>

        <div class="stat-group blue">
          <div class="sg-title">🧠 Enrichissement</div>
          <div class="stat-row"><span class="stat-label">Résumés FR ✅</span><span class="stat-value green" id="stat-sum-fr">…</span></div>
          <div class="stat-row"><span class="stat-label">Sans résumé FR ⚠</span><span class="stat-value amber" id="stat-no-sum-fr">…</span></div>
          <div class="stat-row"><span class="stat-label">Résumés AR ✅</span><span class="stat-value green" id="stat-sum-ar">…</span></div>
          <div class="stat-row"><span class="stat-label">À traduire → AR</span><span class="stat-value amber" id="stat-totrans">…</span></div>
        </div>

        <div class="stat-group purple">
          <div class="sg-title">🔍 SEO & Guides</div>
          <div class="stat-row"><span class="stat-label">Guides publiés</span><span class="stat-value gold" id="stat-guides">…</span></div>
          <div class="stat-row"><span class="stat-label">Indexées aujourd'hui</span><span class="stat-value green" id="stat-indexed">…</span></div>
          <button class="stats-refresh" onclick="loadStats()">↻ Actualiser les stats</button>
        </div>

      </div>
      <div class="jobs-section">
        <h4>📋 Jobs récents</h4>
        <div class="jobs-grid" id="jobs-list"><div class="no-jobs">Aucun job lancé</div></div>
      </div>
    </div>

    <!-- ── Pages scripts par catégorie ── -->
    {script_pages}

  </div>
</div>

<!-- Log panel — toujours visible en bas -->
<div id="log-panel">
  <div id="log-header">
    <div class="logs-dot" id="logs-dot"></div>
    <span id="log-job-label">Logs — en attente d'un script</span>
    <span id="log-elapsed"></span>
    <button class="log-ctrl" id="btn-log-stop" style="display:none" onclick="stopActiveJob()">⏹ Stop</button>
    <button class="log-ctrl" onclick="copyLogs()">📋 Copier</button>
    <button class="log-ctrl" id="btn-fullscreen" onclick="toggleFullscreen()">⛶ Plein écran</button>
    <button class="log-ctrl" onclick="clearLogs()">✕ Effacer</button>
  </div>
  <div id="logs-area"><span style="color:#475569">Cliquez sur un bouton pour lancer un script et voir les logs ici.</span></div>
</div>

<!-- Modal confirmation -->
<div id="modal" class="modal-overlay" style="display:none">
  <div class="modal">
    <h3 id="modal-title">⚠️ Action sensible</h3>
    <p id="modal-msg">Cette action peut modifier des données importantes. Confirmer ?</p>
    <div id="modal-ai-cost" style="display:none;background:#eff6ff;border:1px solid #93c5fd;border-radius:6px;padding:8px 12px;margin-bottom:12px;font-size:12px;color:#1d4ed8;">
      💰 <strong>Coût estimé :</strong> <span id="modal-ai-cost-text"></span>
    </div>
    <div class="modal-actions">
      <button class="btn-cancel" onclick="closeModal()">Annuler</button>
      <button class="btn-confirm" id="modal-confirm">Confirmer</button>
    </div>
  </div>
</div>

<script>
var TOKEN = '{TOKEN}';
var activeES = null;
var jobRunning = false;
var activeJobId = null;
var elapsedStart = null;
var elapsedTimer = null;

document.cookie = 'dashboard_token=' + TOKEN + '; path=/';
document.getElementById('token-hint').textContent = 'Token: ' + TOKEN;

// ── Navigation SPA ────────────────────────────────────────────────────────────
function showPage(pageId) {{
  var pages = document.querySelectorAll('.page');
  for (var i = 0; i < pages.length; i++) pages[i].classList.remove('active');
  var t = document.getElementById('page-' + pageId);
  if (t) t.classList.add('active');
  var links = document.querySelectorAll('.nav-link');
  for (var i = 0; i < links.length; i++)
    links[i].classList.toggle('nav-active', links[i].dataset.page === pageId);
  try {{ localStorage.setItem('dash_page', pageId); }} catch(e) {{}}
}}

function toggleFullscreen() {{
  document.body.classList.toggle('fullscreen');
  var btn = document.getElementById('btn-fullscreen');
  btn.textContent = document.body.classList.contains('fullscreen') ? '⊡ Réduire' : '⛶ Plein écran';
}}

// ── Elapsed timer ─────────────────────────────────────────────────────────────
function startElapsed() {{
  elapsedStart = Date.now();
  if (elapsedTimer) clearInterval(elapsedTimer);
  elapsedTimer = setInterval(function() {{
    if (!elapsedStart) return;
    var s = Math.floor((Date.now() - elapsedStart) / 1000);
    document.getElementById('log-elapsed').textContent =
      Math.floor(s/60) + 'm' + (s%60 < 10 ? '0' : '') + (s%60) + 's';
  }}, 1000);
}}
function stopElapsed() {{
  if (elapsedTimer) clearInterval(elapsedTimer);
  elapsedTimer = null; elapsedStart = null;
  document.getElementById('log-elapsed').textContent = '';
}}

function stopActiveJob() {{
  if (activeJobId) stopJob(activeJobId);
}}

// ── Bouton script ─────────────────────────────────────────────────────────────
function handleBtnClick(btn) {{
  var scriptId = btn.getAttribute('data-id');
  var risk     = btn.getAttribute('data-risk') || 'safe';
  var isDanger = btn.getAttribute('data-danger') === 'true';
  var aiCost   = btn.getAttribute('data-ai-cost') || '';
  var label    = btn.getAttribute('data-label') || scriptId;

  clearLogs();
  appendLog('>>> CLIC : ' + scriptId + ' [risk=' + risk + ']', 'log-info');

  if (jobRunning) {{
    appendLog('>>> BLOQUÉ : un job tourne déjà', 'log-warn');
    showToast('Un job est déjà en cours. Arrêtez-le avant.', 'err');
    return;
  }}

  if (isDanger || risk === 'ai') {{
    document.getElementById('modal-title').textContent =
      risk === 'ai' ? '🤖 Action IA (coût API)' : '⚠️ Action sensible';
    document.getElementById('modal-msg').textContent =
      label + (isDanger ? ` peut modifier des données importantes.` : ` utilise l'API Gemini.`) + ` Confirmer ?`;
    var costDiv = document.getElementById('modal-ai-cost');
    if (aiCost) {{ document.getElementById('modal-ai-cost-text').textContent = aiCost; costDiv.style.display = 'block'; }}
    else {{ costDiv.style.display = 'none'; }}
    document.getElementById('modal').style.display = 'flex';
    document.getElementById('modal-confirm').onclick = function() {{ closeModal(); launchScript(scriptId, btn); }};
    return;
  }}
  launchScript(scriptId, btn);
}}

function launchScript(scriptId, btn) {{
  if (!btn) btn = document.querySelector('[data-id="' + scriptId + '"]');
  var label = btn.getAttribute('data-label') || scriptId;
  jobRunning = true;
  btn.disabled = true;
  btn.classList.add('btn-running');
  var allBtns = document.querySelectorAll('.script-btn');
  for (var i = 0; i < allBtns.length; i++) allBtns[i].disabled = true;

  clearLogs();
  setLogsTitle(label, 'running');
  startElapsed();
  appendLog('>>> Lancement : ' + scriptId, 'log-info');
  appendLog('>>> Envoi requête POST /run/' + scriptId + ' ...', 'log-info');

  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/run/' + scriptId, true);
  xhr.setRequestHeader('X-Dashboard-Token', TOKEN);
  xhr.onload = function() {{
    if (xhr.status === 200) {{
      try {{
        var data = JSON.parse(xhr.responseText);
        activeJobId = data.job_id;
        document.getElementById('btn-log-stop').style.display = 'inline-block';
        appendLog('>>> Job ID : ' + data.job_id, 'log-ok');
        appendLog('>>> Connexion SSE ...', 'log-info');
        streamLogs(data.job_id, btn, label);
      }} catch(ex) {{ appendLog('ERREUR parse JSON : ' + xhr.responseText, 'log-err'); resetBtns(btn); }}
    }} else {{
      appendLog('ERREUR HTTP ' + xhr.status + ' : ' + xhr.responseText, 'log-err');
      resetBtns(btn);
    }}
  }};
  xhr.onerror = function() {{ appendLog('ERREUR RÉSEAU — le dashboard est-il arrêté ?', 'log-err'); resetBtns(btn); }};
  xhr.send();
}}

function resetBtns(btn) {{
  jobRunning = false; activeJobId = null;
  stopElapsed();
  document.getElementById('btn-log-stop').style.display = 'none';
  if (btn) {{ btn.disabled = false; btn.classList.remove('btn-running'); }}
  var allBtns = document.querySelectorAll('.script-btn');
  for (var i = 0; i < allBtns.length; i++) allBtns[i].disabled = false;
}}

// ── SSE Stream ────────────────────────────────────────────────────────────────
function streamLogs(jobId, btn, label) {{
  if (activeES) activeES.close();
  document.getElementById('logs-area').innerHTML = '';
  var es = new EventSource('/stream/' + jobId + '?token=' + TOKEN);
  activeES = es;
  es.onmessage = function(e) {{
    var line = e.data;
    if (line.indexOf('[DONE:') === 0) {{
      var m = line.match(/[0-9]+/);
      var code = m ? parseInt(m[0]) : -1;
      resetBtns(btn);
      setLogsTitle(label, code === 0 ? 'done' : 'error');
      appendLog(line, code === 0 ? 'log-done' : 'log-err');
      es.close(); loadStatus(); return;
    }}
    var cls = '';
    if (/OK|done|termin|✅/.test(line)) cls = 'log-ok';
    else if (/error|erreur|failed|traceback/i.test(line)) cls = 'log-err';
    else if (/warning|attention/.test(line)) cls = 'log-warn';
    else if (/═|─|info/.test(line)) cls = 'log-info';
    appendLog(line, cls);
  }};
  es.onerror = function() {{ resetBtns(btn); setLogsTitle(label, 'error'); es.close(); loadStatus(); }};
}}

function appendLog(text, cls) {{
  var a = document.getElementById('logs-area');
  var d = document.createElement('div');
  if (cls) d.className = cls;
  d.textContent = text;
  a.appendChild(d);
  a.scrollTop = a.scrollHeight;
}}

function clearLogs() {{ document.getElementById('logs-area').innerHTML = ''; }}

function copyLogs() {{
  var kids = document.getElementById('logs-area').children;
  var lines = [];
  for (var i = 0; i < kids.length; i++) lines.push(kids[i].textContent);
  var text = lines.join('\\n');
  if (!text.trim()) {{ showToast('Aucun log à copier', 'err'); return; }}
  if (navigator.clipboard) navigator.clipboard.writeText(text).then(function() {{ showToast('Logs copiés !', 'ok'); }});
}}

// ── Status polling ─────────────────────────────────────────────────────────────
function loadStatus() {{
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/status', true);
  xhr.setRequestHeader('X-Dashboard-Token', TOKEN);
  xhr.onload = function() {{
    if (xhr.status !== 200) return;
    try {{
      var jobs = JSON.parse(xhr.responseText);
      var list = document.getElementById('jobs-list');
      var entries = Object.entries(jobs).sort(function(a,b) {{ return b[1].elapsed - a[1].elapsed; }}).slice(0, 6);
      if (entries.length === 0) {{ list.innerHTML = '<div class="no-jobs">Aucun job lancé</div>'; return; }}
      var html = '';
      for (var i = 0; i < entries.length; i++) {{
        var jid = entries[i][0]; var job = entries[i][1];
        var m = Math.floor(job.elapsed/60); var s = job.elapsed % 60;
        var sBtn = job.status === 'running'
          ? `<button class="btn-stop-sm" onclick="stopJob('${{jid}}')">Stop</button>` : ``;
        html += '<div class="job-item ' + job.status + '"><div class="job-hd">'
          + '<span class="job-name">' + job.label + '</span>'
          + '<span class="job-badge ' + job.status + '">' + job.status + '</span>'
          + sBtn + '</div><div class="job-elapsed">'
          + m + 'm' + (s < 10 ? '0' : '') + s + 's</div></div>';
      }}
      list.innerHTML = html;
    }} catch(ex) {{}}
  }};
  xhr.send();
}}

function stopJob(jobId) {{
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/stop/' + jobId, true);
  xhr.setRequestHeader('X-Dashboard-Token', TOKEN);
  xhr.onload = function() {{ showToast('Job arrêté', 'ok'); loadStatus(); }};
  xhr.send();
}}

function loadStats() {{
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/stats', true);
  xhr.setRequestHeader('X-Dashboard-Token', TOKEN);
  xhr.onload = function() {{
    if (xhr.status !== 200) return;
    try {{
      var s = JSON.parse(xhr.responseText);
      var set = function(id, val, warn) {{
        var el = document.getElementById(id);
        if (!el) return;
        el.textContent = (val === undefined || val === null) ? '?' : val;
        if (warn && parseInt(val) > 0) el.style.color = 'var(--amber)';
        if (warn && parseInt(val) === 0) el.style.color = 'var(--green)';
      }};
      set('stat-pdf-pending', s.pdf_pending);
      set('stat-pdf-done',    s.pdf_done);
      set('stat-pdf-errors',  s.pdf_errors, true);
      set('stat-total',      s.total);
      set('stat-public',     s.public_idx);
      set('stat-content-fr', s.with_content_fr);
      set('stat-content-ar', s.with_content_ar);
      set('stat-no-domain',  s.no_domain, true);
      set('stat-no-slug',    s.no_slug,   true);
      set('stat-sum-fr',    s.has_sum_fr);
      set('stat-no-sum-fr', s.no_sum_fr, true);
      set('stat-sum-ar',    s.has_sum_ar);
      set('stat-totrans',   s.to_translate, true);
      set('stat-guides',  s.guide_count);
      set('stat-indexed', s.indexed_today);
    }} catch(ex) {{ console.error('stats error', ex); }}
  }};
  xhr.send();
}}

function setLogsTitle(label, status) {{
  document.getElementById('log-job-label').textContent = 'Logs — ' + label;
  document.getElementById('logs-dot').className = 'logs-dot ' + status;
}}

function closeModal() {{ document.getElementById('modal').style.display = 'none'; }}

function showToast(msg, type) {{
  var t = document.createElement('div');
  t.className = 'toast toast-' + type;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(function() {{ t.parentNode && t.parentNode.removeChild(t); }}, 3000);
}}

// ── Init ──────────────────────────────────────────────────────────────────────
var savedPage = 'stats';
try {{ savedPage = localStorage.getItem('dash_page') || 'stats'; }} catch(e) {{}}
showPage(savedPage);
loadStats();
loadStatus();
setInterval(loadStatus, 4000);
setInterval(loadStats,  60000);
</script>
</body>
</html>"""

HTML_PAGE = build_html()

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    PORT = int(os.environ.get("DASHBOARD_PORT", 8000))

    print("═" * 56)
    print("  ⚖️  JuriThèque Admin Dashboard")
    print(f"  URL    : http://127.0.0.1:{PORT}")
    print(f"  Token  : {TOKEN}")
    print("  Arrêt  : Ctrl+C")
    print("═" * 56)

    # Ouvrir le navigateur après 1.5s
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://127.0.0.1:{PORT}")

    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
