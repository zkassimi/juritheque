# -*- coding: utf-8 -*-
"""
migrate_pdfs_to_r2.py — Migre les PDFs stockés dans Supabase Storage vers
Cloudflare R2 (egress gratuit). N'affecte QUE les lois dont pdf_url pointe vers
Supabase ; les lois servies en direct depuis source_url (gov.ma) sont ignorées.

Source des octets pour chaque PDF (dans l'ordre) :
  1. Mirror local (pipeline/pdfs/mirror/) si le PDF y est déjà — 0 egress Supabase
  2. Téléchargement depuis pdf_url (Supabase) — dernier recours

Idempotent : un objet déjà présent sur R2 est sauté (sauf --force).
NE MODIFIE PAS la base — l'update de pdf_url se fait avec update_pdf_urls_r2.py.

Prérequis :
  pip install boto3
  Variables dans pipeline/.env :
    R2_ACCOUNT_ID=xxxxxxxx
    R2_ACCESS_KEY_ID=xxxxxxxx
    R2_SECRET_ACCESS_KEY=xxxxxxxx
    R2_BUCKET=juritheque-pdfs
    R2_PUBLIC_DOMAIN=pdfs.juritheque.com

Usage :
  python -X utf8 pipeline/migrate_pdfs_to_r2.py --dry-run
  python -X utf8 pipeline/migrate_pdfs_to_r2.py --limit 20
  python -X utf8 pipeline/migrate_pdfs_to_r2.py            # tout
  python -X utf8 pipeline/migrate_pdfs_to_r2.py --force    # ré-upload même si présent
"""

from __future__ import annotations

import os, sys, json, argparse
from pathlib import Path
from urllib.parse import unquote

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_KEY']
SB = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}

R2_ACCOUNT_ID     = os.getenv('R2_ACCOUNT_ID', '')
R2_ACCESS_KEY_ID  = os.getenv('R2_ACCESS_KEY_ID', '')
R2_SECRET_KEY     = os.getenv('R2_SECRET_ACCESS_KEY', '')
R2_BUCKET         = os.getenv('R2_BUCKET', 'juritheque-pdfs')
R2_PUBLIC_DOMAIN  = os.getenv('R2_PUBLIC_DOMAIN', 'pdfs.juritheque.com')

MIRROR_DIR   = Path(__file__).parent / 'pdfs' / 'mirror'
MIRROR_INDEX = MIRROR_DIR / 'index.json'
MANIFEST     = Path(__file__).parent / 'r2_migration_manifest.json'


def _r2_client():
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        print('❌ boto3 manquant. Installe-le :  pip install boto3', flush=True)
        sys.exit(1)
    if not (R2_ACCOUNT_ID and R2_ACCESS_KEY_ID and R2_SECRET_KEY):
        print('❌ Variables R2 manquantes dans pipeline/.env '
              '(R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY)', flush=True)
        sys.exit(1)
    return boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_KEY,
        config=Config(signature_version='s3v4', region_name='auto'),
    )


def _load_mirror_index() -> dict:
    try:
        if MIRROR_INDEX.exists():
            return json.loads(MIRROR_INDEX.read_text(encoding='utf-8'))
    except Exception:
        pass
    return {}


def fetch_supabase_pdfs() -> list[dict]:
    """Toutes les lois dont pdf_url pointe vers Supabase Storage (paginé)."""
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
    """Clé R2 = nom de fichier (dernier segment de l'URL Supabase)."""
    return unquote(pdf_url.rstrip('/').split('/')[-1])


def _pdf_bytes(law: dict, mirror_index: dict) -> tuple[bytes | None, str]:
    """Récupère les octets du PDF : mirror local d'abord, puis Supabase."""
    # 1. Mirror local (0 egress)
    p = mirror_index.get(str(law['id']))
    if p and Path(p).exists():
        data = Path(p).read_bytes()
        if data[:4] == b'%PDF':
            return data, 'mirror_local'
    # 2. Téléchargement depuis Supabase
    try:
        r = requests.get(law['pdf_url'], headers=SB, timeout=30)
        if r.ok and r.content[:4] == b'%PDF':
            return r.content, 'supabase_download'
        return None, f'bad_response_{r.status_code}'
    except Exception as e:
        return None, f'error_{type(e).__name__}'


def main():
    ap = argparse.ArgumentParser(description='Migration PDFs Supabase → Cloudflare R2')
    ap.add_argument('--dry-run', action='store_true', help='Aperçu sans upload')
    ap.add_argument('--limit', type=int, help='Limiter à N PDFs')
    ap.add_argument('--force', action='store_true', help='Ré-uploader même si déjà sur R2')
    args = ap.parse_args()

    print('Chargement des lois avec pdf_url Supabase…', flush=True)
    laws = fetch_supabase_pdfs()
    if args.limit:
        laws = laws[:args.limit]
    print(f'{len(laws)} PDFs à migrer\n', flush=True)

    mirror_index = _load_mirror_index()
    s3 = None if args.dry_run else _r2_client()

    manifest = {}
    uploaded = skipped = failed = 0
    src_counts = {'mirror_local': 0, 'supabase_download': 0}

    for i, law in enumerate(laws):
        lid = law['id']
        key = _key_from_url(law['pdf_url'])
        new_url = f'https://{R2_PUBLIC_DOMAIN}/{key}'
        manifest[str(lid)] = {'key': key, 'old_url': law['pdf_url'], 'new_url': new_url}

        if args.dry_run:
            src = 'mirror_local' if str(lid) in mirror_index else 'supabase_download'
            print(f'[{i+1:>4}/{len(laws)}] id={lid:>6}  {key[:55]}  (source: {src})', flush=True)
            continue

        # Idempotence : déjà sur R2 ?
        if not args.force:
            try:
                s3.head_object(Bucket=R2_BUCKET, Key=key)
                skipped += 1
                if (i + 1) % 50 == 0:
                    print(f'[{i+1:>4}/{len(laws)}] …{skipped} déjà présents', flush=True)
                continue
            except Exception:
                pass  # absent → on upload

        data, src = _pdf_bytes(law, mirror_index)
        if not data:
            failed += 1
            print(f'[{i+1:>4}/{len(laws)}] id={lid:>6}  ❌ {src}', flush=True)
            continue

        try:
            s3.put_object(Bucket=R2_BUCKET, Key=key, Body=data,
                          ContentType='application/pdf')
            uploaded += 1
            src_counts[src] = src_counts.get(src, 0) + 1
            print(f'[{i+1:>4}/{len(laws)}] id={lid:>6}  ✓ {key[:50]}  ({src}, {len(data)//1024} Ko)', flush=True)
        except Exception as e:
            failed += 1
            print(f'[{i+1:>4}/{len(laws)}] id={lid:>6}  ❌ upload: {e}', flush=True)

    # Manifest (mapping id → clé/URL) pour l'étape update_pdf_urls_r2.py
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'\n{"═"*60}')
    if args.dry_run:
        print(f'  DRY-RUN — {len(laws)} PDFs seraient migrés')
        print(f'  Manifest écrit → {MANIFEST}')
    else:
        print(f'  Uploadés : {uploaded}  (mirror={src_counts.get("mirror_local",0)}, '
              f'supabase={src_counts.get("supabase_download",0)})')
        print(f'  Déjà présents (sautés) : {skipped}')
        print(f'  Échecs : {failed}')
        print(f'  Manifest → {MANIFEST}')
        print(f'\n  Étape suivante : python -X utf8 pipeline/update_pdf_urls_r2.py --dry-run')
    print(f'{"═"*60}')


if __name__ == '__main__':
    main()
