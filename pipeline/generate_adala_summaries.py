"""
JuriThèque — Génération de résumés IA pour toutes les sources
══════════════════════════════════════════════════════════════
Génère simple_summary_fr via Gemini 2.5 Flash Lite à partir du titre arabe
(title_ar) et des métadonnées. Couvre toutes les sources (SGG, ANRT, BKAM,
CDR, Adala, etc.) — pas seulement Adala.

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
SYSTEM_PROMPT = """Tu es un expert en droit marocain spécialisé en rédaction juridique SEO. Tu génères un résumé juridique ET une liste de mots-clés pour les moteurs de recherche.

Tu retournes UNIQUEMENT un JSON valide avec exactement deux champs :
{
  "summary": "...",
  "keywords": ["...", "...", ...]
}

RÈGLES POUR LE RÉSUMÉ (champ "summary") :
- 4 à 5 phrases, 600 à 900 caractères (environ 100-150 mots), texte brut sans Markdown
- Structure en 3 points :
  1. OBJET : verbes précis (institue, fixe, crée, abroge, modifie, réglemente, soumet à autorisation...)
  2. CHAMP D'APPLICATION : qui est concerné + secteur concerné
  3. PORTÉE : obligations CONCRÈTES (permis requis, délais, seuils chiffrés, organes créés, sanctions pénales/administratives)
- Mentionne explicitement : domaine juridique + acteurs institutionnels (Bank Al-Maghrib, ANRT, Ministère de...)
- INTERDIT : "impose des obligations strictes", "prévoit des dispositions", "établit un cadre" sans préciser lesquels
- INTERDIT : "Adala", "PDF", "JuriThèque", "base de données", "portail", "téléchargeable"
- Ne commence pas par "Ce texte" ou "Ce document"

RÈGLES POUR LES MOTS-CLÉS (champ "keywords") :
- 12 à 18 mots-clés en français
- Couvrir tous les types de recherche :
  * Exact : "{type} n° {numéro}", "{type} {numéro} maroc"
  * Long-tail descriptif : "{objet} maroc", "{domaine} marocain {année}"
  * Long-tail pratique : "comment {faire X} maroc", "procédure {X} maroc", "conditions {X} maroc"
  * Variantes populaires : nom court du texte, acronyme, titre court connu
  * Questions utilisateurs : "qui peut {faire X}", "quel délai pour {X}", "sanction {infraction}"
- Mélanger : termes officiels + termes de recherche citoyens/praticiens
- Pas de doublons, pas de stop words seuls ("le", "de")"""

def generate_summary_llm(law: dict, model: str = DEFAULT_MODEL) -> tuple[str | None, list[str]]:
    """Génère résumé + keywords via LLM. Retourne (summary, keywords)."""
    import json as _json, re as _re

    type_fr    = law.get('type') or 'Texte juridique'
    number     = law.get('number') or ''
    title_ar   = law.get('title_ar') or ''
    title_fr   = law.get('title_fr') or ''
    domain_id  = law.get('domain_id') or ''
    date_str   = law.get('date') or ''
    domain_label = DOMAIN_LABELS.get(domain_id, domain_id)

    clean_title_fr = title_fr.replace("— portail Adala", "").replace("portail Adala", "").strip(" —–-")
    if clean_title_fr.lower().startswith("texte juridique"):
        clean_title_fr = ''

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
            {'role': 'user',   'content': f'Génère le résumé et les mots-clés SEO pour ce texte juridique marocain :\n\n{context}'},
        ],
        'max_tokens': 1500,
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
            raw = r.json()['choices'][0]['message']['content'].strip()
            # Nettoyer fences markdown
            raw = _re.sub(r'^```(?:json)?\s*', '', raw)
            raw = _re.sub(r'\s*```$', '', raw).strip()
            # Parser JSON
            try:
                data = _json.loads(raw)
            except _json.JSONDecodeError:
                m = _re.search(r'\{.*\}', raw, _re.DOTALL)
                data = _json.loads(m.group()) if m else {}

            summary  = (data.get('summary') or '').strip()
            keywords = [k.strip() for k in (data.get('keywords') or []) if k.strip()]
            if summary.startswith('"') and summary.endswith('"'):
                summary = summary[1:-1].strip()
            return summary, keywords

        except requests.exceptions.HTTPError as e:
            if r.status_code == 429:
                wait = (attempt + 1) * 5
                print(f'  ⏳ Rate limit — attente {wait}s...', flush=True)
                time.sleep(wait)
            else:
                print(f'  ✗ HTTP {r.status_code}: {r.text[:200]}', flush=True)
                return None, []
        except Exception as e:
            print(f'  ✗ Erreur: {e}', flush=True)
            if attempt < MAX_RETRIES - 1:
                time.sleep(3)
            else:
                return None, []
    return None, []

# ── Fetch depuis Supabase ──────────────────────────────────────────────────────
def fetch_batch_null(batch_size: int, offset: int) -> list:
    """Lois sans résumé (toutes sources confondues, avec title_ar)."""
    r = session.get(
        f'{SUPABASE_URL}/rest/v1/laws',
        headers=SB_HEADERS,
        params={
            'simple_summary_fr':  'is.null',
            'title_ar':           'not.is.null',
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
    """Lois avec résumés génériques (toutes sources, contenant 'téléchargeable')."""
    r = session.get(
        f'{SUPABASE_URL}/rest/v1/laws',
        headers=SB_HEADERS,
        params={
            'simple_summary_fr':  'ilike.*téléchargeable*',
            'title_ar':           'not.is.null',
            'select':             'id,number,type,title_fr,title_ar,domain_id,date',
            'order':              'id.asc',
            'limit':              str(batch_size),
            'offset':             str(offset),
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()

def fetch_batch_force(batch_size: int, offset: int) -> list:
    """TOUTES les lois avec title_ar — écrase les résumés existants."""
    r = session.get(
        f'{SUPABASE_URL}/rest/v1/laws',
        headers=SB_HEADERS,
        params={
            'title_ar': 'not.is.null',
            'select':   'id,number,type,title_fr,title_ar,domain_id,date',
            'order':    'id.asc',
            'limit':    str(batch_size),
            'offset':   str(offset),
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()

def count_laws(mode: str) -> int:
    params_null = {
        'simple_summary_fr': 'is.null',
        'title_ar': 'not.is.null',
        'select': 'id', 'limit': '1',
    }
    params_ph = {
        'simple_summary_fr': 'ilike.*téléchargeable*',
        'title_ar': 'not.is.null',
        'select': 'id', 'limit': '1',
    }
    params_force = {
        'title_ar': 'not.is.null',
        'select': 'id', 'limit': '1',
    }
    total = 0
    if mode == 'force':
        r = session.get(f'{SUPABASE_URL}/rest/v1/laws',
                        headers={**SB_HEADERS, 'Prefer': 'count=exact'},
                        params=params_force, timeout=10)
        return int(r.headers.get('content-range', '0/0').split('/')[-1])
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

def update_summary(law_id: str, summary: str, keywords: list[str] | None = None):
    patch = {
        'simple_summary_fr':  summary[:1000],
        'simple_summary_ar':  None,   # reset AR pour retraduction
        'needs_human_review': False,
    }
    if keywords:
        patch['legal_keywords'] = keywords[:20]  # max 20 mots-clés
    r = session.patch(
        f'{SUPABASE_URL}/rest/v1/laws',
        headers=SB_HEADERS,
        params={'id': f'eq.{law_id}'},
        json=patch,
        timeout=10,
    )
    r.raise_for_status()

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Génération résumés IA — Lois Adala')
    parser.add_argument('--mode',    default='null',
                        choices=['null', 'placeholders', 'all', 'force'],
                        help='null=sans résumé | placeholders=remplacer génériques | all=les deux | force=tout régénérer')
    parser.add_argument('--limit',   type=int, default=0,   help='Max lois à traiter (0=tout)')
    parser.add_argument('--dry-run', action='store_true',   help='Simuler sans écrire')
    parser.add_argument('--model',   default=DEFAULT_MODEL, help='Modèle OpenRouter')
    args = parser.parse_args()

    total = count_laws(args.mode)
    to_process = min(args.limit, total) if args.limit > 0 else total

    print(f'{"═"*55}', flush=True)
    print(f'  JuriThèque — Résumés IA toutes sources (mode: {args.mode})', flush=True)
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
    if args.mode == 'force':
        fetchers.append(('force', fetch_batch_force))
    else:
        if args.mode in ('null', 'all'):
            fetchers.append(('null', fetch_batch_null))
        if args.mode in ('placeholders', 'all'):
            fetchers.append(('placeholders', fetch_batch_placeholders))

    for fetch_label, fetch_fn in fetchers:
        offset = 0
        # En mode force : l'offset avance car on écrase sans filtre IS NULL
        # En autres modes : l'offset reste 0 (les textes traités disparaissent du filtre)
        use_offset = (fetch_label == 'force')
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

                summary, keywords = generate_summary_llm(law, model=args.model)
                if not summary:
                    errors += 1
                    print(f'  ✗ Échec: {typ} {number}', flush=True)
                    continue

                try:
                    update_summary(law_id, summary, keywords)
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
                    f' | {len(summary)} chars | {len(keywords)} kw'
                    f' | ETA: {int(eta_sec//60)}m{int(eta_sec%60):02d}s',
                    flush=True
                )

                # Aperçu toutes les 20 lois
                if done % 20 == 0:
                    print(f'\n  ── Aperçu ──', flush=True)
                    print(f'  FR: {summary[:150]}...', flush=True)
                    print(f'  KW: {", ".join(keywords[:5])}...', flush=True)
                    print(flush=True)

                time.sleep(DELAY_SEC)

            if use_offset:
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
