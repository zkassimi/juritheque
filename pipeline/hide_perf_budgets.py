# -*- coding: utf-8 -*-
"""
hide_perf_budgets.py — Masque les "projets de performance" dans la base
=======================================================================
Ces records ont un titre tout en MAJUSCULES (nom de ministère), sans date
ni contenu — ce sont des projets de performance budgétaire mal catégorisés
comme textes juridiques. Ils ne doivent pas être indexables publiquement.

Usage :
  python -X utf8 pipeline/hide_perf_budgets.py           # aperçu
  python -X utf8 pipeline/hide_perf_budgets.py --apply   # masquer en base
"""

import os, re, sys, argparse, requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_KEY']
SB = {
    'apikey':        SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal',
}
SB_REP = {**SB, 'Prefer': 'return=representation'}


def fetch_all():
    rows, offset = [], 0
    while True:
        r = requests.get(f'{SUPABASE_URL}/rest/v1/laws', headers=SB, params={
            'select': 'id,number,type,title_fr,date,content_fr,is_publicly_indexable,source_name',
            'order':  'id.asc',
            'limit':  '1000',
            'offset': str(offset),
        })
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000
    return rows


def is_perf_budget(law: dict) -> bool:
    """
    Détecte un "projet de performance" :
    - titre tout en MAJUSCULES (lettres + espaces/tirets/parenthèses)
    - sans date stockée
    - sans contenu textuel
    """
    title = (law.get('title_fr') or '').strip()
    if not title or len(title) < 10:
        return False

    # Titre tout en majuscules (lettres accentuées comprises)
    cleaned = re.sub(r'[^A-Za-zÀ-ÿ]', '', title)
    if not cleaned:
        return False
    all_caps = cleaned == cleaned.upper() and len(cleaned) > 5

    # Sans date
    no_date = not law.get('date')

    # Sans contenu
    no_content = not (law.get('content_fr') or '').strip()

    return all_caps and no_date and no_content


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true',
                        help='Appliquer is_publicly_indexable=false en base')
    args = parser.parse_args()

    print('Chargement des lois...', flush=True)
    laws = fetch_all()
    print(f'{len(laws):,} lois chargées\n', flush=True)

    targets = [l for l in laws if is_perf_budget(l) and l.get('is_publicly_indexable', True)]

    print(f'Projets de performance détectés (publics) : {len(targets)}')
    print()
    for l in targets:
        print(f'  id={l["id"]:>6}  [{l.get("type",""):25}]  {l.get("title_fr","")[:70]}')

    if not targets:
        print('Rien à faire.')
        return

    if not args.apply:
        print(f'\n→ Dry-run. Ajouter --apply pour masquer ces {len(targets)} records.')
        return

    print(f'\nMasquage de {len(targets)} records...', flush=True)
    fixed = errors = 0
    for l in targets:
        try:
            r = requests.patch(
                f'{SUPABASE_URL}/rest/v1/laws',
                headers=SB,
                params={'id': f'eq.{l["id"]}'},
                json={
                    'is_publicly_indexable': False,
                    'pipeline_notes': (
                        (l.get('pipeline_notes') or '') +
                        ' [auto: projet-de-performance masqué 2026-06-30]'
                    ).strip(),
                },
                timeout=10,
            )
            r.raise_for_status()
            fixed += 1
            print(f'  ✅ id={l["id"]}  {l.get("title_fr","")[:60]}')
        except Exception as e:
            errors += 1
            print(f'  ❌ id={l["id"]} : {e}')

    print(f'\n  Masqués: {fixed}  |  Erreurs: {errors}')


if __name__ == '__main__':
    main()
