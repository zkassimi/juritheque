# -*- coding: utf-8 -*-
"""
update_pdf_urls_r2.py — Remplace les pdf_url Supabase par les URLs Cloudflare R2
une fois les PDFs migrés (migrate_pdfs_to_r2.py).

Sécurité :
  - Vérifie que chaque objet existe bien sur R2 (head_object) AVANT de patcher —
    on ne casse jamais un lien vers un PDF absent.
  - Écrit une sauvegarde CSV (id, ancienne_url, nouvelle_url) avant modification,
    pour rollback éventuel.
  - N'affecte QUE les lois dont pdf_url pointe encore vers Supabase.

Usage :
  python -X utf8 pipeline/update_pdf_urls_r2.py --dry-run
  python -X utf8 pipeline/update_pdf_urls_r2.py --limit 20
  python -X utf8 pipeline/update_pdf_urls_r2.py            # tout
  python -X utf8 pipeline/update_pdf_urls_r2.py --no-verify  # sauter la vérif R2 (rapide)
"""

from __future__ import annotations

import os, sys, csv, argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_KEY']
SB = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}',
      'Content-Type': 'application/json'}

R2_ACCOUNT_ID    = os.getenv('R2_ACCOUNT_ID', '')
R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID', '')
R2_SECRET_KEY    = os.getenv('R2_SECRET_ACCESS_KEY', '')
R2_BUCKET        = os.getenv('R2_BUCKET', 'juritheque-pdfs')
R2_PUBLIC_DOMAIN = os.getenv('R2_PUBLIC_DOMAIN', 'pdfs.juritheque.com')

BACKUP_DIR = Path(__file__).parent / 'audit_results'


def _r2_client():
    import boto3
    from botocore.config import Config
    return boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_KEY,
        config=Config(signature_version='s3v4', region_name='auto'),
    )


def fetch_supabase_pdfs() -> list[dict]:
    out, offset, page = [], 0, 1000
    while True:
        r = requests.get(
            f'{SUPABASE_URL}/rest/v1/laws',
            headers={**SB, 'Range-Unit': 'items', 'Range': f'{offset}-{offset + page - 1}'},
            params={'select': 'id,pdf_url', 'pdf_url': 'like.*supabase*', 'order': 'id.asc'},
            timeout=30,
        )
        r.raise_for_status()
        batch = r.json()
        out.extend(batch)
        if len(batch) < page:
            break
        offset += page
    return out


def _key_from_url(pdf_url: str) -> str:
    return unquote(pdf_url.rstrip('/').split('/')[-1])


def main():
    ap = argparse.ArgumentParser(description='Mise à jour pdf_url Supabase → R2')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--limit', type=int)
    ap.add_argument('--no-verify', action='store_true',
                    help='Ne pas vérifier la présence sur R2 avant de patcher')
    args = ap.parse_args()

    print('Chargement des lois avec pdf_url Supabase…', flush=True)
    laws = fetch_supabase_pdfs()
    if args.limit:
        laws = laws[:args.limit]
    print(f'{len(laws)} lois à mettre à jour\n', flush=True)

    s3 = None
    if not args.no_verify and not args.dry_run:
        if not (R2_ACCOUNT_ID and R2_ACCESS_KEY_ID and R2_SECRET_KEY):
            print('❌ Variables R2 manquantes (ou utilise --no-verify).', flush=True)
            sys.exit(1)
        s3 = _r2_client()

    # Sauvegarde avant modification
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup = BACKUP_DIR / f'pdf_url_backup_{datetime.now():%Y%m%d_%H%M%S}.csv'

    updated = skipped_missing = failed = 0
    with open(backup, 'w', newline='', encoding='utf-8-sig') as bf:
        w = csv.writer(bf)
        w.writerow(['id', 'old_pdf_url', 'new_pdf_url'])

        for i, law in enumerate(laws):
            lid = law['id']
            key = _key_from_url(law['pdf_url'])
            new_url = f'https://{R2_PUBLIC_DOMAIN}/{key}'

            # Vérifier présence R2
            if s3 is not None:
                try:
                    s3.head_object(Bucket=R2_BUCKET, Key=key)
                except Exception:
                    skipped_missing += 1
                    print(f'[{i+1:>4}/{len(laws)}] id={lid:>6}  ⏭ absent sur R2 — non patché', flush=True)
                    continue

            w.writerow([lid, law['pdf_url'], new_url])

            if args.dry_run:
                print(f'[{i+1:>4}/{len(laws)}] id={lid:>6}  {law["pdf_url"][-45:]} → {new_url}', flush=True)
                continue

            try:
                r = requests.patch(
                    f'{SUPABASE_URL}/rest/v1/laws',
                    headers={**SB, 'Prefer': 'return=minimal'},
                    params={'id': f'eq.{lid}'},
                    json={'pdf_url': new_url},
                    timeout=15,
                )
                if r.status_code in (200, 204):
                    updated += 1
                else:
                    failed += 1
                    print(f'[{i+1:>4}] id={lid} ❌ {r.status_code}: {r.text[:100]}', flush=True)
            except Exception as e:
                failed += 1
                print(f'[{i+1:>4}] id={lid} ❌ {e}', flush=True)

    print(f'\n{"═"*60}')
    if args.dry_run:
        print(f'  DRY-RUN — {len(laws)} lois seraient mises à jour')
    else:
        print(f'  Mises à jour : {updated}')
        print(f'  Sautées (absent R2) : {skipped_missing}')
        print(f'  Échecs : {failed}')
    print(f'  Sauvegarde → {backup}')
    print(f'{"═"*60}')


if __name__ == '__main__':
    main()
