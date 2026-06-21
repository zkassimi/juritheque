# -*- coding: utf-8 -*-
"""
translate_summaries_ar.py — Traduction juridique FR→AR des résumés
═══════════════════════════════════════════════════════════════════
Traduit les simple_summary_fr en arabe professionnel et juridique
et insère le résultat dans simple_summary_ar.

Usage :
  python -X utf8 pipeline/translate_summaries_ar.py              # traduction complète
  python -X utf8 pipeline/translate_summaries_ar.py --limit 200  # test sur 200
  python -X utf8 pipeline/translate_summaries_ar.py --dry-run    # vérif sans écrire

Modèle par défaut : google/gemini-2.5-flash-lite (10x moins cher que Claude Haiku, terminologie juridique marocaine)
"""

import sys, time, argparse, os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── Configuration ──────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SUPABASE_URL  = os.environ.get('SUPABASE_URL', 'https://bmargdbbcnhkrjeidmvh.supabase.co')
SUPABASE_KEY  = os.environ.get('SUPABASE_SERVICE_KEY', '')   # service_role — droits WRITE
OPENROUTER_KEY= os.environ.get('OPENROUTER_API_KEY', '')

DEFAULT_MODEL = 'google/gemini-2.5-flash-lite'  # 10x moins cher que Claude Haiku, meilleure terminologie juridique marocaine
BATCH_SIZE    = 50    # lois par cycle de fetch
DELAY_SEC     = 0.8   # pause entre chaque appel LLM (respecter rate limits)
MAX_RETRIES   = 3     # retries si erreur API

# ── Détection résumés placeholder (générés sans LLM, sans valeur SEO) ──────────
PLACEHOLDER_PHRASES = [
    "consultable et téléchargeable en format pdf",
    "retrouvez l'intégralité de ce texte",
    "portail officiel du ministère de la justice marocain (adala)",
    "texte est consultable et téléchargeable",
    "texte fait partie de la base de données juridique marocaine jurithèque",
]

def is_placeholder_summary(text: str) -> bool:
    """Retourne True si le résumé est du texte générique sans valeur — ne pas traduire."""
    if not text or len(text.strip()) < 200:
        return True
    return any(phrase in text.lower() for phrase in PLACEHOLDER_PHRASES)

# ── Session HTTP robuste ────────────────────────────────────────────────────────
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
    'X-Title':       'JuriThèque Legal Translation',
}

# ── Prompt de traduction juridique ─────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es un traducteur juridique expert en droit marocain.
Tu traduis des résumés juridiques du français vers l'arabe standard moderne (الفصحى).

Règles impératives :
- Utilise le vocabulaire juridique officiel marocain (ex: ظهير، مرسوم، قانون، قرار، مقرر...)
- Conserve les numéros, dates et références tels quels
- Même longueur et structure que l'original (3 phrases environ)
- Ne traduis PAS le nom propre "JuriThèque"
- Style professionnel et formel, pas de langage courant
- Retourne UNIQUEMENT la traduction arabe, sans explication ni commentaire"""

def translate_fr_to_ar(text_fr, model=DEFAULT_MODEL, law_number=''):
    """Traduit un résumé juridique FR → AR via OpenRouter."""
    if not text_fr or not text_fr.strip():
        return None

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user',   'content': f'Traduis ce résumé juridique en arabe :\n\n{text_fr.strip()}'},
        ],
        'max_tokens': 900,
        'temperature': 0.1,   # très déterministe pour la traduction
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
            data = r.json()
            ar = data['choices'][0]['message']['content'].strip()
            # Nettoyage : retirer les guillemets englobants si présents
            if ar.startswith('"') and ar.endswith('"'):
                ar = ar[1:-1].strip()
            return ar
        except requests.exceptions.HTTPError as e:
            if r.status_code == 429:
                wait = (attempt + 1) * 5
                print(f'  ⏳ Rate limit — attente {wait}s...', flush=True)
                time.sleep(wait)
            else:
                print(f'  ✗ HTTP {r.status_code} pour {law_number}: {e}', flush=True)
                try:
                    print(f'  ✗ Réponse OpenRouter: {r.text[:300]}', flush=True)
                except:
                    pass
                return None
        except Exception as e:
            print(f'  ✗ Erreur réseau pour {law_number}: {e}', flush=True)
            if attempt < MAX_RETRIES - 1:
                time.sleep(3)
            else:
                return None
    return None

# ── Fetch batch depuis Supabase ─────────────────────────────────────────────────
def fetch_batch(batch_size=BATCH_SIZE):
    """Récupère les lois avec FR mais sans AR (offset=0 toujours — les MAJ retirent du filtre)."""
    params = {
        'select':             'id,number,type,simple_summary_fr',
        'simple_summary_fr':  'not.is.null',
        'simple_summary_ar':  'is.null',
        'order':              'id.asc',
        'limit':              str(batch_size),
        'offset':             '0',
    }
    r = session.get(f'{SUPABASE_URL}/rest/v1/laws', headers=SB_HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

# ── Update Supabase ─────────────────────────────────────────────────────────────
def update_ar_summary(law_id, ar_text):
    r = session.patch(
        f'{SUPABASE_URL}/rest/v1/laws',
        headers=SB_HEADERS,
        params={'id': f'eq.{law_id}'},
        json={'simple_summary_ar': ar_text},
        timeout=10,
    )
    r.raise_for_status()
    return True

# ── Comptage restant ────────────────────────────────────────────────────────────
def count_remaining():
    params = {
        'select':            'id',
        'simple_summary_fr': 'not.is.null',
        'simple_summary_ar': 'is.null',
        'limit':             '1',
    }
    r = session.get(
        f'{SUPABASE_URL}/rest/v1/laws',
        headers={**SB_HEADERS, 'Prefer': 'count=exact'},
        params=params,
        timeout=10,
    )
    cr = r.headers.get('content-range', '0/0')
    return int(cr.split('/')[-1]) if '/' in cr else 0

# ── Main ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Traduction juridique FR→AR des résumés')
    parser.add_argument('--limit',   type=int, default=0,        help='Nombre max de lois à traiter (0 = tout)')
    parser.add_argument('--dry-run', action='store_true',         help='Afficher sans écrire')
    parser.add_argument('--model',   default=DEFAULT_MODEL,       help='Modèle OpenRouter à utiliser')
    parser.add_argument('--batch',   type=int, default=BATCH_SIZE,help='Taille du batch Supabase')
    args = parser.parse_args()

    remaining = count_remaining()
    to_process = min(args.limit, remaining) if args.limit > 0 else remaining

    print(f'═══════════════════════════════════════════════════', flush=True)
    print(f'  JuriThèque — Traduction juridique FR→AR', flush=True)
    print(f'  Modèle    : {args.model}', flush=True)
    print(f'  À traduire: {remaining:,} résumés', flush=True)
    if args.limit:
        print(f'  Limite    : {args.limit}', flush=True)
    if args.dry_run:
        print(f'  MODE DRY-RUN — aucune écriture', flush=True)
    print(f'═══════════════════════════════════════════════════', flush=True)

    done = 0; errors = 0; skipped = 0
    start_time = time.time()

    while done < to_process:
        # Fetch un batch
        batch_size = min(args.batch, to_process - done)
        try:
            laws = fetch_batch(batch_size)
        except Exception as e:
            print(f'\n✗ Erreur fetch batch: {e}', flush=True)
            time.sleep(5)
            continue

        if not laws:
            print('\n✓ Plus de lois à traduire.', flush=True)
            break

        for law in laws:
            law_id  = law['id']
            number  = law.get('number') or law_id
            typ     = law.get('type', '')
            fr_text = law.get('simple_summary_fr', '')

            if not fr_text or not fr_text.strip():
                skipped += 1
                continue

            # Ignorer les résumés génériques/placeholder (pas de valeur SEO)
            if is_placeholder_summary(fr_text):
                skipped += 1
                continue

            # Traduction
            ar_text = translate_fr_to_ar(fr_text, model=args.model, law_number=number)

            if not ar_text:
                errors += 1
                print(f'  ✗ Échec: {typ} {number}', flush=True)
                continue

            # Écriture
            if not args.dry_run:
                try:
                    update_ar_summary(law_id, ar_text)
                except Exception as e:
                    errors += 1
                    print(f'  ✗ Erreur update {number}: {e}', flush=True)
                    continue

            done += 1
            elapsed = time.time() - start_time
            rate = done / elapsed if elapsed > 0 else 0
            eta_sec = (to_process - done) / rate if rate > 0 else 0
            eta_min = int(eta_sec // 60)
            eta_s   = int(eta_sec % 60)

            print(
                f'  ✓ [{done:>5}/{to_process}] {typ[:8]:<8} {str(number)[:25]:<25}'
                f' | {len(ar_text)} chars'
                f' | ETA: {eta_min}m{eta_s:02d}s',
                flush=True
            )

            # Aperçu de la traduction (toutes les 50 lois)
            if done % 50 == 0:
                print(f'\n  ── Aperçu ──', flush=True)
                print(f'  FR: {fr_text[:120]}...', flush=True)
                print(f'  AR: {ar_text[:120]}...', flush=True)
                print(flush=True)

            time.sleep(DELAY_SEC)

        # Fin du batch
        if len(laws) < batch_size:
            break

    # ── Rapport final ────────────────────────────────────────────────────────────
    elapsed = time.time() - start_time
    print(f'\n{"═"*50}', flush=True)
    print(f'  ✅ Traductions : {done:,}', flush=True)
    print(f'  ⚠  Erreurs    : {errors}', flush=True)
    print(f'  ⏭  Ignorés    : {skipped}', flush=True)
    print(f'  ⏱  Durée      : {int(elapsed//60)}m{int(elapsed%60):02d}s', flush=True)
    print(f'  🔢 Restants   : {count_remaining():,}', flush=True)
    print(f'{"═"*50}', flush=True)

if __name__ == '__main__':
    main()
