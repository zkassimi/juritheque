# -*- coding: utf-8 -*-
"""
fix_duplicate_slugs.py — Corrige les canonical_slug en doublon
==============================================================
Pour chaque slug qui apparaît plusieurs fois :
  - Garde le premier enregistrement tel quel (ou tente un meilleur slug)
  - Renomme les autres en {type}-{number_clean} suffixé si nécessaire

Usage :
  python -X utf8 pipeline/fix_duplicate_slugs.py --dry-run   # aperçu
  python -X utf8 pipeline/fix_duplicate_slugs.py             # applique
"""

import os, re, sys, time, unicodedata, argparse, requests
from collections import Counter, defaultdict
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_KEY']
SB = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}',
      'Content-Type': 'application/json', 'Prefer': 'return=minimal'}

STOPWORDS = {'le','la','les','du','de','des','au','aux','et','ou','n','un','une',
             'relatif','relative','portant','fixant','instituant','modifiant',
             'dahir','decret','loi','arrete','circulaire','texte','code',
             'revue','justice','droit','numero'}

def slugify(text: str) -> str:
    norm = unicodedata.normalize('NFD', (text or '').lower())
    norm = ''.join(c for c in norm if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', norm).strip('-')

def make_slug_from_law(law: dict, suffix: str = '') -> str:
    """Génère un slug unique depuis type + number + mots-clés titre."""
    type_s = slugify(law.get('type') or 'texte')

    # Nettoyer le number : enlever le nom du type s'il est déjà dedans
    # ex: "Dahir n°1-03-194" → garder juste "1-03-194"
    raw_num = (law.get('number') or '').strip()
    type_lc = (law.get('type') or '').lower()
    # Supprimer le préfixe type + "n°" / "n " du numéro
    clean_num = re.sub(
        r'^(' + re.escape(type_lc) + r')\s*n[o°]?\s*',
        '', raw_num, flags=re.IGNORECASE
    ).strip()
    if not clean_num:
        clean_num = raw_num
    number_s = slugify(clean_num)

    title = law.get('title_fr') or ''
    words = re.sub(r'[^a-zA-Z0-9\s]', ' ', title).lower().split()
    kw = [w for w in words if w not in STOPWORDS and len(w) > 2][:5]
    kw_s = '-'.join(kw)

    parts = [p for p in [type_s, number_s, kw_s] if p]
    slug = '-'.join(parts)[:100]
    slug = re.sub(r'-+', '-', slug).strip('-')
    if suffix:
        slug = f'{slug}-{suffix}'[:100]
    return slug or f'texte-{law["id"]}'

def fetch_all():
    rows, offset = [], 0
    while True:
        r = requests.get(f'{SUPABASE_URL}/rest/v1/laws', headers=SB, params={
            'select': 'id,canonical_slug,number,type,title_fr',
            'canonical_slug': 'not.is.null',
            'order': 'id.asc',
            'limit': '1000',
            'offset': str(offset),
        })
        batch = r.json()
        if not batch: break
        rows.extend(batch)
        if len(batch) < 1000: break
        offset += 1000
    return rows

def patch_slug(law_id, new_slug: str):
    r = requests.patch(f'{SUPABASE_URL}/rest/v1/laws', headers=SB,
                       params={'id': f'eq.{law_id}'},
                       json={'canonical_slug': new_slug}, timeout=10)
    r.raise_for_status()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    print('Chargement des lois...', flush=True)
    laws = fetch_all()
    print(f'{len(laws):,} lois chargées', flush=True)

    # Grouper par slug
    by_slug = defaultdict(list)
    for law in laws:
        by_slug[law['canonical_slug']].append(law)

    duplicates = {slug: group for slug, group in by_slug.items() if len(group) > 1}
    print(f'{len(duplicates)} slugs en doublon, {sum(len(g) for g in duplicates.values())} enregistrements\n', flush=True)

    # Construire l'ensemble de tous les slugs existants pour éviter les collisions
    existing_slugs = {law['canonical_slug'] for law in laws}

    fixed = 0
    errors = 0

    for slug, group in sorted(duplicates.items()):
        print(f'[{len(group)}x] {slug[:70]}', flush=True)
        # On garde le 1er tel quel (ou on améliore aussi si le slug est générique)
        is_generic = slug in ('synthese', 'arabe', 'version-en-arabe', 'texte-inconnu',
                              'loi-revue-justice-droit-numero') or len(slug) < 10

        for i, law in enumerate(group):
            if i == 0 and not is_generic:
                print(f'  ✓ KEEP  id={law["id"]} slug={slug}', flush=True)
                continue

            # Générer un nouveau slug unique
            new_slug = make_slug_from_law(law)
            # Éviter collision
            attempt = 0
            base = new_slug
            while new_slug in existing_slugs and new_slug != law['canonical_slug']:
                attempt += 1
                new_slug = f'{base}-{attempt}'

            print(f'  → FIX   id={law["id"]} → {new_slug[:80]}', flush=True)

            if not args.dry_run:
                try:
                    patch_slug(law['id'], new_slug)
                    existing_slugs.add(new_slug)
                    existing_slugs.discard(law['canonical_slug'])
                    fixed += 1
                    time.sleep(0.05)
                except Exception as e:
                    print(f'    ✗ Erreur: {e}', flush=True)
                    errors += 1
            else:
                existing_slugs.add(new_slug)
                fixed += 1

    print(f'\n{"═"*50}', flush=True)
    if args.dry_run:
        print(f'DRY-RUN — {fixed} slugs seraient corrigés', flush=True)
    else:
        print(f'✅ Corrigés : {fixed}  |  ✗ Erreurs : {errors}', flush=True)

if __name__ == '__main__':
    main()
