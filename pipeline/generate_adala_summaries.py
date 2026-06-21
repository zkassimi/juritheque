"""
JuriThèque — Génération de résumés IA pour les lois Adala
══════════════════════════════════════════════════════════
Génère simple_summary_fr via Gemini 2.5 Flash Lite à partir du titre arabe
(title_ar) et des métadonnées. Produit de vrais résumés juridiques, pas du
texte générique.

Modes :
  --mode null          : lois sans résumé (défaut)
  --mode placeholders  : lois avec résumés génériques à remplacer
  --mode all           : les deux (null + placeholders)

Usage :
  python -X utf8 pipeline/generate_adala_summaries.py                      # lois sans résumé
  python -X utf8 pipeline/generate_adala_summaries.py --mode placeholders  # améliore les mauvais
  python -X utf8 pipeline/generate_adala_summaries.py --mode all           # tout
  python -X utf8 pipeline/generate_adala_summaries.py --limit 50 --dry-run # test
"""

import argparse
import os
import sys
import time
from datetime import date

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── Configuration ──────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SUPABASE_URL   = os.environ.get('SUPABASE_URL', 'https://bmargdbbcnhkrjeidmvh.supabase.co')
SUPABASE_KEY   = os.environ.get('SUPABASE_SERVICE_KEY', '')
OPENROUTER_KEY = os.environ.get('OPENROUTER_API_KEY', '')

DEFAULT_MODEL = 'google/gemini-2.5-flash-lite'
BATCH_SIZE    = 50
DELAY_SEC     = 0.8
MAX_RETRIES   = 3

# Phrases qui identifient un résumé placeholder (sans valeur SEO)
PLACEHOLDER_PHRASES = [
    "consultable et téléchargeable en format pdf",
    "retrouvez l'intégralité de ce texte",
    "portail officiel du ministère de la justice marocain (adala)",
    "texte est consultable et téléchargeable",
    "texte fait partie de la base de données juridique marocaine jurithèque",
]

# ── Domaines → labels ──────────────────────────────────────────────────────────
DOMAIN_LABELS = {
    "civil":                    "droit civil",
    "penal":                    "droit pénal",
    "commercial":               "droit commercial",
    "administratif":            "droit administratif",
    "travail":                  "droit du travail",
    "fiscal":                   "droit fiscal",
    "constitutionnel":          "droit constitutionnel",
    "numerique":                "droit numérique",
    "bancaire":                 "droit bancaire",
    "international":            "droit international",
    "finances_publiques":       "finances publiques",
    "collectivites":            "collectivités territoriales",
    "transport":                "droit des transports",
    "environnement":            "droit de l'environnement",
    "sante":                    "droit de la santé",
    "education":                "droit de l'éducation",
    "agriculture":              "droit agricole",
    "energie":                  "droit de l'énergie",
    "immobilier":               "droit immobilier",
    "propriete_intellectuelle": "propriété intellectuelle",
}

# ── Session HTTP ───────────────────────────────────────────────────────────────
def make_session():
    s = requests.Session()
    retry = Retry(total=5, backoff_factor=1.5, status_forcelist=[429, 500, 502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retry))
    return s

session = make_session()

SB_HEADERS = {
    'apikey':        SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal',
}

OR_HEADERS = {
    'Authorization': f'Bearer {OPENROUTER_KEY}',
    'Content-Type':  'application/json',
    'HTTP-Referer':  'https://juritheque.com',
    'X-Title':       'JuriThèque Summary Generation',
}

# ── Prompt LLM ─────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es un expert en droit marocain. Tu rédiges des résumés juridiques courts et précis en français.

Règles impératives :
- 3 phrases maximum, 350-450 caractères au total
- Explique l'OBJET du texte : ce qu'il régit, qui il concerne, ce qu'il impose ou autorise
- Style juridique professionnel et formel
- Ne mentionne JAMAIS : "Adala", "PDF", "JuriThèque", "base de données", "portail", "téléchargeable"
- Ne commence pas par "Ce texte", "Ce document" — commence par une phrase informative
- Retourne UNIQUEMENT le résumé, sans explication ni commentaire"""

def generate_summary_llm(law: dict, model: str = DEFAULT_MODEL) -> str | None:
    """Génère un résumé via LLM à partir du titre arabe + métadonnées."""
    type_fr    = law.get('type') or 'Texte juridique'
    number     = law.get('number') or ''
    title_ar   = law.get('title_ar') or ''
    title_fr   = law.get('title_fr') or ''
    domain_id  = law.get('domain_id') or ''
    date_str   = law.get('date') or ''
    domain_label = DOMAIN_LABELS.get(domain_id, domain_id)

    # Nettoyer le titre FR si présent
    clean_title_fr = title_fr.replace("— portail Adala", "").replace("portail Adala", "").strip(" —–-")
    if clean_title_fr.lower().startswith("texte juridique"):
        clean_title_fr = ''

    # Construire le contexte
    context_parts = [f"Type : {type_fr}"]
    if number:
        context_parts.append(f"Numéro : {number}")
    if title_ar:
        context_parts.append(f"Titre officiel (arabe) : {title_ar}")
    if clean_title_fr:
        context_parts.append(f"Titre (français) : {clean_title_fr}")
    if domain_label:
        context_parts.append(f"Domaine : {domain_label}")
    if date_str:
        context_parts.append(f"Date : {date_str}")

    context = "\n".join(context_parts)

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user',   'content': f'Rédige un résumé juridique en français pour ce texte marocain :\n\n{context}'},
        ],
        'max_tokens': 600,
        'temperature': 0.2,
    }

    for attempt in range(MAX_RETRIES):
        try:
            r = session.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=OR_HEADERS,
                json=payload,
                timeout=30,
            )
            r.raise_for_status()
            text = r.json()['choices'][0]['message']['content'].strip()
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1].strip()
            return text
        except requests.exceptions.HTTPError as e:
            if r.status_code == 429:
                wait = (attempt + 1) * 5
                print(f'  ⏳ Rate limit — attente {wait}s...', flush=True)
                time.sleep(wait)
            else:
                print(f'  ✗ HTTP {r.status_code}: {r.text[:200]}', flush=True)
                return None
        except Exception as e:
            print(f'  ✗ Erreur: {e}', flush=True)
            if attempt < MAX_RETRIES - 1:
                time.sleep(3)
            else:
                return None
    return None

# ── Fetch depuis Supabase ──────────────────────────────────────────────────────
def fetch_batch_null(batch_size: int, offset: int) -> list:
    """Lois Adala sans résumé."""
    r = session.get(
        f'{SUPABASE_URL}/rest/v1/laws',
        headers=SB_HEADERS,
        params={
            'source_name':        'eq.Adala',
            'simple_summary_fr':  'is.null',
            'select':             'id,number,type,title_fr,title_ar,domain_id,date',
            'order':              'id.asc',
            'limit':              str(batch_size),
            'offset':             str(offset),
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()

def fetch_batch_placeholders(batch_size: int, offset: int) -> list:
    """Lois Adala avec résumés génériques (contenant 'téléchargeable')."""
    r = session.get(
        f'{SUPABASE_URL}/rest/v1/laws',
        headers=SB_HEADERS,
        params={
            'source_name':        'eq.Adala',
            'simple_summary_fr':  'ilike.*téléchargeable*',
            'select':             'id,number,type,title_fr,title_ar,domain_id,date',
            'order':              'id.asc',
            'limit':              str(batch_size),
            'offset':             str(offset),
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()

def count_laws(mode: str) -> int:
    params_null = {
        'source_name': 'eq.Adala',
        'simple_summary_fr': 'is.null',
        'select': 'id', 'limit': '1',
    }
    params_ph = {
        'source_name': 'eq.Adala',
        'simple_summary_fr': 'ilike.*téléchargeable*',
        'select': 'id', 'limit': '1',
    }
    total = 0
    if mode in ('null', 'all'):
        r = session.get(f'{SUPABASE_URL}/rest/v1/laws',
                        headers={**SB_HEADERS, 'Prefer': 'count=exact'},
                        params=params_null, timeout=10)
        total += int(r.headers.get('content-range', '0/0').split('/')[-1])
    if mode in ('placeholders', 'all'):
        r = session.get(f'{SUPABASE_URL}/rest/v1/laws',
                        headers={**SB_HEADERS, 'Prefer': 'count=exact'},
                        params=params_ph, timeout=10)
        total += int(r.headers.get('content-range', '0/0').split('/')[-1])
    return total

def update_summary(law_id: str, summary: str):
    r = session.patch(
        f'{SUPABASE_URL}/rest/v1/laws',
        headers=SB_HEADERS,
        params={'id': f'eq.{law_id}'},
        json={
            'simple_summary_fr':    summary[:600],
            'simple_summary_ar':    None,    # Reset AR pour retraduction
            'needs_human_review':   False,   # ✓ Résumé généré — plus besoin de révision
        },
        timeout=10,
    )
    r.raise_for_status()

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Génération résumés IA — Lois Adala')
    parser.add_argument('--mode',    default='null',
                        choices=['null', 'placeholders', 'all'],
                        help='null=sans résumé | placeholders=remplacer génériques | all=les deux')
    parser.add_argument('--limit',   type=int, default=0,   help='Max lois à traiter (0=tout)')
    parser.add_argument('--dry-run', action='store_true',   help='Simuler sans écrire')
    parser.add_argument('--model',   default=DEFAULT_MODEL, help='Modèle OpenRouter')
    args = parser.parse_args()

    total = count_laws(args.mode)
    to_process = min(args.limit, total) if args.limit > 0 else total

    print(f'{"═"*55}', flush=True)
    print(f'  JuriThèque — Résumés IA Adala (mode: {args.mode})', flush=True)
    print(f'  Modèle    : {args.model}', flush=True)
    print(f'  À traiter : {total:,} lois', flush=True)
    if args.limit:
        print(f'  Limite    : {args.limit}', flush=True)
    if args.dry_run:
        print(f'  MODE DRY-RUN — aucune écriture', flush=True)
    print(f'{"═"*55}', flush=True)

    done = 0; errors = 0
    start = time.time()

    # Construire la liste des fetchers selon le mode
    fetchers = []
    if args.mode in ('null', 'all'):
        fetchers.append(('null', fetch_batch_null))
    if args.mode in ('placeholders', 'all'):
        fetchers.append(('placeholders', fetch_batch_placeholders))

    for fetch_label, fetch_fn in fetchers:
        offset = 0
        print(f'\n  ── Batch [{fetch_label}] ──', flush=True)

        while done < to_process:
            batch_size = min(BATCH_SIZE, to_process - done)
            try:
                laws = fetch_fn(batch_size, offset)
            except Exception as e:
                print(f'\n✗ Erreur fetch: {e}', flush=True)
                time.sleep(5)
                continue

            if not laws:
                break

            for law in laws:
                if done >= to_process:
                    break

                law_id = law['id']
                number = law.get('number') or law_id
                typ    = law.get('type', '')

                if args.dry_run:
                    print(f'  DRY ✓ {typ} {number} | title_ar: {str(law.get("title_ar",""))[:60]}', flush=True)
                    done += 1
                    continue

                summary = generate_summary_llm(law, model=args.model)
                if not summary:
                    errors += 1
                    print(f'  ✗ Échec: {typ} {number}', flush=True)
                    continue

                try:
                    update_summary(law_id, summary)
                except Exception as e:
                    errors += 1
                    print(f'  ✗ Update {number}: {e}', flush=True)
                    continue

                done += 1
                elapsed = time.time() - start
                rate = done / elapsed if elapsed > 0 else 0
                eta_sec = (to_process - done) / rate if rate > 0 else 0

                print(
                    f'  ✓ [{done:>5}/{to_process}] {typ[:8]:<8} {str(number)[:25]:<25}'
                    f' | {len(summary)} chars'
                    f' | ETA: {int(eta_sec//60)}m{int(eta_sec%60):02d}s',
                    flush=True
                )

                # Aperçu toutes les 20 lois
                if done % 20 == 0:
                    print(f'\n  ── Aperçu ──', flush=True)
                    print(f'  AR: {str(law.get("title_ar",""))[:80]}', flush=True)
                    print(f'  FR: {summary[:150]}...', flush=True)
                    print(flush=True)

                time.sleep(DELAY_SEC)

            offset += batch_size
            if len(laws) < batch_size:
                break

    elapsed = time.time() - start
    print(f'\n{"═"*55}', flush=True)
    print(f'  ✅ Générés  : {done:,}', flush=True)
    print(f'  ⚠  Erreurs  : {errors}', flush=True)
    print(f'  ⏱  Durée    : {int(elapsed//60)}m{int(elapsed%60):02d}s', flush=True)
    print(f'{"═"*55}', flush=True)

if __name__ == '__main__':
    main()
