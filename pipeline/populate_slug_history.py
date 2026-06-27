"""
populate_slug_history.py
Backfille slug_history pour les lois dont le slug a changé.

L'ancien format était : {type_slug}-{number_slug}  (sans mots-clés)
Le nouveau format est  : {type_slug}-{number_slug}-{keywords}

Usage :
  python pipeline/populate_slug_history.py --dry-run   # aperçu
  python pipeline/populate_slug_history.py             # applique
"""

import os, re, unicodedata, time, argparse
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ['VITE_SUPABASE_URL']
SUPABASE_KEY = os.environ['VITE_SUPABASE_ANON_KEY']
PAGE_SIZE    = 500

HEADERS = {
    'apikey':        SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal',
}

TYPE_SLUG = {
    'Loi': 'loi', 'Dahir': 'dahir', 'Décret': 'decret',
    'Arrêté': 'arrete', 'Circulaire': 'circulaire', 'Code': 'code',
    'Ordonnance': 'ordonnance', 'Règlement': 'reglement',
}

def slugify(text):
    if not text: return ''
    norm = unicodedata.normalize('NFD', text.lower())
    norm = ''.join(c for c in norm if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', norm).strip('-')

def old_slug(law):
    t = law.get('type') or ''
    n = law.get('number') or ''
    if not n: return None
    type_part   = TYPE_SLUG.get(t, slugify(t)) or 'texte-juridique'
    number_part = slugify(n)
    if not number_part: return None
    return f'{type_part}-{number_part}'

def fetch_all():
    laws, offset = [], 0
    while True:
        url = (f"{SUPABASE_URL}/rest/v1/laws"
               f"?select=id,type,number,canonical_slug,slug_history"
               f"&order=id&offset={offset}&limit={PAGE_SIZE}")
        r = httpx.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        page = r.json()
        if not page: break
        laws.extend(page)
        print(f'  Chargé {len(laws)} lois...', end='\r', flush=True)
        if len(page) < PAGE_SIZE: break
        offset += PAGE_SIZE
    print()
    return laws

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    print('Chargement des lois depuis Supabase...')
    laws = fetch_all()
    print(f'{len(laws)} lois chargées\n')

    to_patch = []
    for law in laws:
        canonical = law.get('canonical_slug') or ''
        history   = law.get('slug_history') or []
        computed  = old_slug(law)
        if not computed or computed == canonical or computed in history:
            continue
        to_patch.append({'id': law['id'], 'old': computed,
                         'new_history': list(set(history + [computed]))})

    print(f'{len(to_patch)} lois avec un ancien slug a backfiller')
    if args.dry_run:
        for p in to_patch[:20]:
            print(f"  {p['old']}")
        if len(to_patch) > 20:
            print(f'  ... et {len(to_patch) - 20} autres')
        print('\n[dry-run] Aucune modification appliquee.')
        return

    ok = fail = 0
    for i, p in enumerate(to_patch, 1):
        url = f"{SUPABASE_URL}/rest/v1/laws?id=eq.{p['id']}"
        r = httpx.patch(url, headers=HEADERS, json={'slug_history': p['new_history']}, timeout=10)
        if r.status_code in (200, 204): ok += 1
        else: fail += 1
        if i % 100 == 0: print(f'  {i}/{len(to_patch)} traites...')
        time.sleep(0.05)

    print(f'OK: {ok} | Echecs: {fail}')

if __name__ == '__main__':
    main()
