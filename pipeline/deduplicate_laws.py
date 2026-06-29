# -*- coding: utf-8 -*-
"""
deduplicate_laws.py — Masque les doublons (is_publicly_indexable = false)
=========================================================================
Pour chaque groupe de lois avec le même numéro normalisé :
  - Garde le record le plus complet (meilleur score)
  - Met is_publicly_indexable = false sur les autres

Critères de score (le plus haut = gardé) :
  +4  content_fr présent
  +3  title_fr propre (pas placeholder)
  +2  simple_summary_fr présent
  +2  pdf_url présent
  +2  source officielle (SGG, MEF, BKAM, ANRT, CDR...)
  +1  domain_id présent
  +1  date présente
  +1  canonical_slug propre (contient des mots, pas juste type-number)

Usage :
  python -X utf8 pipeline/deduplicate_laws.py --dry-run   # aperçu
  python -X utf8 pipeline/deduplicate_laws.py             # applique
"""

import os, re, sys, time, argparse, requests
from collections import defaultdict
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

OFFICIAL_SOURCES = {
    'sgg', 'sgg_consolid', 'sgg-lois', 'mef', 'bkam', 'anrt', 'cdr',
    'mem', 'environnement', 'wipo', 'ism', 'mmsp', 'finances',
    'source officielle', 'ministère', 'anrt_lois_autres',
}

PLACEHOLDER_PATTERNS = [
    r'^(dahir|loi|décret|arrêté|circulaire|code|ordonnance)\s+n[°o]?[\d\.\-/]+$',
    r'portail adala',
    r'téléchargeable',
    r'^texte\s+n[°o]?\s*\d',
]

def normalize_number(n: str) -> str:
    if not n: return ''
    n = n.strip().lower()
    n = re.sub(r'^(dahir|loi organique|loi|décret royal|décret|arrêté conjoint|arrêté|'
               r'circulaire|code|ordonnance|note circulaire|règlement|texte réglementaire|'
               r'texte juridique|discours royal|lettre royale|décision|délibération)\s*', '', n, flags=re.IGNORECASE)
    n = re.sub(r'^n[°o]?\s*', '', n)
    n = re.sub(r'[\s\.\-/]+', '-', n).strip('-')
    return n

# Mots-clés qui signalent que le texte est LIÉ à un autre (pas un doublon)
MODIFIER_KEYWORDS = [
    'modifiant', 'complétant', 'modifiant et complétant',
    'abrogeant', 'portant abrogation',
    'portant application', "pris pour l'application",
    'portant promulgation',
    'portant exécution',
    'relatif à l\'application',
]

def type_category(law: dict) -> str:
    """Catégorie de type pour le groupage — seuls les textes de même catégorie sont dédoublonnés."""
    t = (law.get('type') or '').lower()
    if 'loi organique' in t:                           return 'loi-organique'
    if 'loi' in t:                                     return 'loi'
    if 'dahir' in t:                                   return 'dahir'
    if 'décret royal' in t or 'decret royal' in t:     return 'decret-royal'
    if 'décret' in t or 'decret' in t:                 return 'decret'
    if 'arrêté conjoint' in t or 'arrete conjoint' in t: return 'arrete-conjoint'
    if 'arrêté' in t or 'arrete' in t:                 return 'arrete'
    if 'circulaire' in t:                              return 'circulaire'
    return 'autre'

def is_modifier_text(law: dict) -> bool:
    """True si le texte modifie/complète/abroge/applique un autre texte → ne pas dédoublonner."""
    title = (law.get('title_fr') or '').lower()
    return any(kw in title for kw in MODIFIER_KEYWORDS)

def dedup_key(law: dict) -> str:
    """Clé de dédoublonnage = catégorie_type::numéro_normalisé.
    Les textes liés (modifiant, décret d'application, etc.) sont exclus."""
    num = normalize_number(law.get('number') or '')
    cat = type_category(law)
    return f'{cat}::{num}'

def is_placeholder(title: str) -> bool:
    if not title or len(title.strip()) < 10: return True
    t = title.strip().lower()
    return any(re.search(p, t) for p in PLACEHOLDER_PATTERNS)

def score_law(law: dict) -> int:
    s = 0
    if law.get('content_fr') and len(law['content_fr']) > 100:      s += 4
    if not is_placeholder(law.get('title_fr') or ''):                s += 3
    if law.get('simple_summary_fr') and len(law['simple_summary_fr']) > 100: s += 2
    if law.get('pdf_url'):                                            s += 2
    src = (law.get('source_name') or '').lower()
    if any(o in src for o in OFFICIAL_SOURCES):                      s += 2
    if law.get('domain_id'):                                          s += 1
    if law.get('date'):                                               s += 1
    slug = law.get('canonical_slug') or ''
    if slug and len(slug.split('-')) > 4:                             s += 1
    return s

def fetch_all():
    rows, offset = [], 0
    while True:
        r = requests.get(f'{SUPABASE_URL}/rest/v1/laws', headers=SB, params={
            'select': ('id,number,type,title_fr,title_ar,source_name,domain_id,'
                      'date,pdf_url,canonical_slug,simple_summary_fr,'
                      'is_publicly_indexable,content_fr'),
            'order':  'id.asc',
            'limit':  '1000',
            'offset': str(offset),
        })
        r.raise_for_status()
        batch = r.json()
        if not batch: break
        rows.extend(batch)
        if len(batch) < 1000: break
        offset += 1000
    return rows

def patch_indexable(law_id, value: bool):
    r = requests.patch(f'{SUPABASE_URL}/rest/v1/laws', headers=SB,
                       params={'id': f'eq.{law_id}'},
                       json={'is_publicly_indexable': value}, timeout=10)
    r.raise_for_status()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    print('Chargement des lois...', flush=True)
    laws = fetch_all()
    print(f'{len(laws):,} lois chargées\n', flush=True)

    # Grouper par clé = type_catégorie::numéro_normalisé
    # Exclure les textes "liés" (modificatifs, décrets d'application, promulgation)
    by_key = defaultdict(list)
    excluded_modifiers = 0
    for law in laws:
        if is_modifier_text(law):
            excluded_modifiers += 1
            continue                          # texte lié → jamais dédoublonné
        key = dedup_key(law)
        num = normalize_number(law.get('number') or '')
        if num and len(num) > 2:
            by_key[key].append(law)

    groups = {k: v for k, v in by_key.items() if len(v) > 1}
    total_records = sum(len(v) for v in groups.values())
    print(f'{excluded_modifiers} textes liés (modificatifs/application) exclus du dédoublonnage', flush=True)
    print(f'{len(groups)} groupes de vrais doublons — {total_records} enregistrements concernés\n', flush=True)

    # Calculer les IDs qui doivent être masqués (les "others" de chaque groupe)
    ids_to_hide = set()
    ids_to_keep = set()   # best de chaque groupe
    for group in groups.values():
        scored = sorted(group, key=lambda l: score_law(l), reverse=True)
        ids_to_keep.add(scored[0]['id'])
        for law in scored[1:]:
            ids_to_hide.add(law['id'])

    # Records actuellement False mais PAS dans ids_to_hide → faux positifs à restaurer
    false_records = [l for l in laws if l.get('is_publicly_indexable') == False]
    to_restore = [l for l in false_records if l['id'] not in ids_to_hide]
    print(f'{len(false_records)} records actuellement masqués', flush=True)
    print(f'{len(to_restore)} faux positifs à restaurer (masqués à tort par ancienne logique)', flush=True)
    print(f'{len(ids_to_hide)} vrais doublons à masquer\n', flush=True)

    hidden = restored = kept = errors = 0

    # 1. Restaurer les faux positifs
    for law in to_restore:
        if not args.dry_run:
            try:
                patch_indexable(law['id'], True)
                restored += 1
                time.sleep(0.02)
            except Exception as e:
                print(f'  ✗ Restauration id={law["id"]}: {e}', flush=True)
                errors += 1
        else:
            restored += 1

    # 2. Appliquer la nouvelle déduplication
    for num, group in sorted(groups.items(), key=lambda x: -len(x[1])):
        scored = sorted(group, key=lambda l: score_law(l), reverse=True)
        best   = scored[0]
        others = scored[1:]

        print(f'[{len(group)}x] {num}', flush=True)
        print(f'  ✓ KEEP  id={best["id"]:>6} score={score_law(best)} '
              f'src={(best.get("source_name") or "?")[:20]:20} title={str(best.get("title_fr") or "")[:50]}', flush=True)

        if not args.dry_run and best.get('is_publicly_indexable') != True:
            try:
                patch_indexable(best['id'], True)
                print(f'    ↑ Restauré à True', flush=True)
            except Exception as e:
                print(f'    ✗ Erreur restauration id={best["id"]}: {e}', flush=True)

        for law in others:
            print(f'  → HIDE  id={law["id"]:>6} score={score_law(law)} '
                  f'src={(law.get("source_name") or "?")[:20]:20} title={str(law.get("title_fr") or "")[:50]}', flush=True)
            if not args.dry_run:
                try:
                    patch_indexable(law['id'], False)
                    hidden += 1
                    time.sleep(0.03)
                except Exception as e:
                    print(f'    ✗ Erreur id={law["id"]}: {e}', flush=True)
                    errors += 1
            else:
                hidden += 1
        kept += 1

    print(f'\n{"═"*55}', flush=True)
    if args.dry_run:
        print(f'DRY-RUN — {restored} faux positifs seraient restaurés, {hidden} vrais doublons masqués', flush=True)
    else:
        print(f'↑ Restaurés : {restored}  |  ❌ Masqués : {hidden}  |  ✗ Erreurs : {errors}', flush=True)
    print(f'{"═"*55}', flush=True)

if __name__ == '__main__':
    main()
