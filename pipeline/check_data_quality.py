# -*- coding: utf-8 -*-
"""
check_data_quality.py — Détecte les records avec métadonnées corrompues
=======================================================================
Cas détectés :
  1. Numéro stocké dans title_fr au lieu du champ number
     ex: number="Dahir n°1-23-95" au lieu de "1-23-95"
  2. Numéro contenant le type (Dahir/Loi/Décret) → devrait être juste les chiffres
  3. Date anormale : date stockée > 2000 mais le numéro contient "XX" (année ancienne)
     ex: number="1-72-255" → devrait être ~1972-1973 pas 2023
  4. Doublon de numéro normalisé ET de type → deux records distincts visibles
  5. Numéro qui inclut l'année en dernière partie et date incohérente
     ex: number="2-08-69" → date devrait être ~2008, pas 2023

Usage :
  python -X utf8 pipeline/check_data_quality.py              # rapport console
  python -X utf8 pipeline/check_data_quality.py --fix        # corriger ce qui est auto-corrigeable
  python -X utf8 pipeline/check_data_quality.py --export     # exporter CSV
"""

import os, re, sys, csv, argparse, requests
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

TYPE_PREFIXES = [
    'dahir', 'loi organique', 'loi', 'décret royal', 'decret royal',
    'décret', 'decret', 'arrêté conjoint', 'arrete conjoint',
    'arrêté', 'arrete', 'circulaire', 'code', 'ordonnance',
    'note circulaire', 'règlement',
]

def fetch_all():
    rows, offset = [], 0
    while True:
        r = requests.get(f'{SUPABASE_URL}/rest/v1/laws', headers=SB, params={
            'select': 'id,number,type,title_fr,date,status,source_name,canonical_slug,is_publicly_indexable',
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


def normalize_number(n: str) -> str:
    """Enlève le type + n° en tête, normalise séparateurs → tirets."""
    if not n: return ''
    n = n.strip().lower()
    for prefix in TYPE_PREFIXES:
        n = re.sub(rf'^{re.escape(prefix)}\s*', '', n, flags=re.IGNORECASE)
    n = re.sub(r'^n[°o]?\s*', '', n)
    n = re.sub(r'[\s\.\-/]+', '-', n).strip('-')
    return n


def extract_year_from_number(norm: str) -> int | None:
    """
    Tente d'extraire l'année depuis le numéro.
    Convention marocaine : X-YY-ZZZ où YY = derniers 2 chiffres de l'année.
    Ex: 1-72-255 → 1972, 2-08-69 → 2008, 1-23-95 → 2023 ou 1923?
    On retourne l'année complète : si YY <= 30 → 20YY, sinon → 19YY.
    """
    m = re.match(r'^\d+[-.](\d{2})[-.]', norm)
    if m:
        yy = int(m.group(1))
        return 2000 + yy if yy <= 30 else 1900 + yy
    return None


def check_number_has_type(number: str) -> bool:
    """True si le champ number contient un préfixe de type (ex: 'Dahir n°...')."""
    if not number: return False
    n = number.strip().lower()
    for prefix in TYPE_PREFIXES:
        if n.startswith(prefix):
            return True
    return False


def clean_number_from_type(number: str) -> str:
    """Extrait uniquement la partie numérique depuis un number contenant le type."""
    return normalize_number(number) if normalize_number(number) else number


def check_year_coherence(law: dict) -> dict | None:
    """
    Vérifie que l'année dans le numéro correspond à la date stockée.
    Retourne un dict avec détails si incohérent, None sinon.
    """
    norm = normalize_number(law.get('number') or '')
    expected_year = extract_year_from_number(norm)
    if not expected_year:
        return None

    date_str = law.get('date') or ''
    if not date_str or len(date_str) < 4:
        return None

    stored_year = int(date_str[:4])
    # Tolérance de ±2 ans (numéros publiés fin/début d'année)
    if abs(stored_year - expected_year) > 2:
        return {
            'id':            law['id'],
            'number':        law.get('number', ''),
            'norm_number':   norm,
            'title_fr':      (law.get('title_fr') or '')[:80],
            'stored_date':   date_str,
            'stored_year':   stored_year,
            'expected_year': expected_year,
            'problem':       f'date {stored_year} ≠ année dans numéro ({expected_year})',
            'auto_fixable':  False,  # nécessite vérification manuelle
        }
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fix',    action='store_true', help='Corriger les cas auto-corrigeables')
    parser.add_argument('--export', action='store_true', help='Exporter rapport CSV')
    args = parser.parse_args()

    print('Chargement des lois...', flush=True)
    laws = fetch_all()
    print(f'{len(laws):,} lois chargées\n', flush=True)

    issues = []

    # ── Problème 1 : numéro contient le type ──────────────────────────────────
    type_in_number = [l for l in laws if check_number_has_type(l.get('number') or '')]
    print(f'📋 Numéro contenant le type (ex: "Dahir n°..."): {len(type_in_number)}')
    for l in type_in_number[:5]:
        print(f'   id={l["id"]:>6}  number={l["number"]!r:40}  → corrigé: {clean_number_from_type(l["number"])!r}')
    if len(type_in_number) > 5:
        print(f'   ... et {len(type_in_number)-5} autres')

    for l in type_in_number:
        cleaned = clean_number_from_type(l['number'])
        issues.append({
            'id':          l['id'],
            'number':      l.get('number', ''),
            'norm_number': cleaned,
            'title_fr':    (l.get('title_fr') or '')[:80],
            'stored_date': l.get('date', ''),
            'problem':     f'number contient le type → devrait être {cleaned!r}',
            'auto_fixable': True,
            'fix_field':   'number',
            'fix_value':   cleaned,
        })

    # ── Problème 2 : date incohérente avec l'année du numéro ─────────────────
    print(f'\n📅 Vérification cohérence date/numéro...', flush=True)
    year_issues = []
    for l in laws:
        issue = check_year_coherence(l)
        if issue:
            # Exclure les records déjà listés dans problème 1
            if not check_number_has_type(l.get('number') or ''):
                year_issues.append(issue)

    print(f'   Date incohérente avec l\'année dans le numéro: {len(year_issues)}')
    for issue in year_issues[:10]:
        print(f'   id={issue["id"]:>6}  {issue["number"]:20}  date={issue["stored_date"]}  attendu≈{issue["expected_year"]}  — {issue["title_fr"][:50]}')
    if len(year_issues) > 10:
        print(f'   ... et {len(year_issues)-10} autres')

    issues.extend(year_issues)

    # ── Problème 3 : doublons de numéro normalisé (même type + même numéro) ──
    print(f'\n🔁 Vérification doublons (même type + même numéro normalisé)...', flush=True)
    by_key = defaultdict(list)
    for l in laws:
        if not l.get('is_publicly_indexable', True):
            continue  # ignorer les déjà masqués
        t = (l.get('type') or '').lower()
        norm = normalize_number(l.get('number') or '')
        if norm and len(norm) > 2:
            key = f'{t}::{norm}'
            by_key[key].append(l)

    visible_dupes = {k: v for k, v in by_key.items() if len(v) > 1}
    print(f'   Doublons visibles (is_publicly_indexable=true): {len(visible_dupes)} groupes')
    for key, group in sorted(visible_dupes.items(), key=lambda x: -len(x[1]))[:10]:
        print(f'   [{len(group)}x] {key}')
        for l in group:
            print(f'     id={l["id"]:>6}  {(l.get("title_fr") or "")[:60]}')

    # ── Résumé ─────────────────────────────────────────────────────────────────
    auto_fixable = [i for i in issues if i.get('auto_fixable')]
    manual_review = [i for i in issues if not i.get('auto_fixable')]

    print(f'\n{"═"*60}')
    print(f'  Total problèmes détectés : {len(issues)}')
    print(f'  Auto-corrigeables        : {len(auto_fixable)}  (--fix pour appliquer)')
    print(f'  Revue manuelle requise   : {len(manual_review)}')
    print(f'  Doublons visibles        : {len(visible_dupes)} groupes')
    print(f'{"═"*60}')

    # ── Auto-fix ───────────────────────────────────────────────────────────────
    if args.fix and auto_fixable:
        print(f'\nApplication de {len(auto_fixable)} corrections auto...', flush=True)
        fixed = errors = 0
        for issue in auto_fixable:
            try:
                r = requests.patch(
                    f'{SUPABASE_URL}/rest/v1/laws', headers=SB,
                    params={'id': f'eq.{issue["id"]}'},
                    json={issue['fix_field']: issue['fix_value']},
                    timeout=10,
                )
                r.raise_for_status()
                fixed += 1
                print(f'  ✅ id={issue["id"]}  {issue["fix_field"]}={issue["fix_value"]!r}')
            except Exception as e:
                errors += 1
                print(f'  ❌ id={issue["id"]} : {e}')
        print(f'\n  Corrigés: {fixed}  |  Erreurs: {errors}')

    # ── Export CSV ─────────────────────────────────────────────────────────────
    if args.export and issues:
        out = 'pipeline/data_quality_report.csv'
        with open(out, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'number', 'norm_number', 'title_fr', 'stored_date',
                'stored_year', 'expected_year', 'problem', 'auto_fixable'
            ], extrasaction='ignore')
            writer.writeheader()
            writer.writerows(issues)
        print(f'\nRapport exporté → {out}')

    # Rapport doublons visibles dans CSV séparé
    if args.export and visible_dupes:
        out2 = 'pipeline/data_quality_duplicates.csv'
        with open(out2, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['group_key', 'id', 'title_fr', 'number', 'date', 'source_name'])
            for key, group in visible_dupes.items():
                for l in group:
                    writer.writerow([key, l['id'], (l.get('title_fr') or '')[:80],
                                     l.get('number',''), l.get('date',''), l.get('source_name','')])
        print(f'Doublons exportés → {out2}')


if __name__ == '__main__':
    main()
