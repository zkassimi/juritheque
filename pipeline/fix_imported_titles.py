"""
fix_imported_titles.py — Corrige les textes importés par la veille :
  - Titres avec extension .pdf → nettoyés
  - Numéros URL-encodés (%20, %C3%A9…) → décodés
  - PDF externe → re-téléchargé et uploadé vers Supabase Storage

Usage :
  python pipeline/fix_imported_titles.py --dry-run        # aperçu
  python pipeline/fix_imported_titles.py                   # correction titres/numéros
  python pipeline/fix_imported_titles.py --reupload-pdfs  # + re-upload PDFs vers Storage
"""

import os, re, sys, time
from pathlib import Path
from urllib.parse import urlparse, unquote
from dotenv import load_dotenv

try:
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
except ImportError:
    print("pip install requests rich")
    sys.exit(1)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

SUPABASE_URL    = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY    = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", ""))
STORAGE_BUCKET  = "legal-documents"

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/pdf,*/*",
}

console = Console()


def clean_number(n: str) -> str:
    cleaned = unquote(n)
    cleaned = re.sub(r'\.(pdf|PDF)$', '', cleaned).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned[:60]

def clean_title(t: str) -> str:
    cleaned = unquote(t)
    cleaned = re.sub(r'\.(pdf|PDF)$', '', cleaned).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned[:400]

def looks_broken_number(n: str) -> bool:
    return '%' in (n or '')

def looks_broken_title(t: str) -> bool:
    t = t or ''
    return t.lower().endswith('.pdf') or '%' in t

def is_external_pdf(url: str) -> bool:
    """True si l'URL n'est pas hébergée chez nous (pas dans Supabase Storage)."""
    return bool(url) and 'supabase' not in url

def download_pdf(url: str) -> bytes | None:
    try:
        r = requests.get(url, headers=HTTP_HEADERS, timeout=30, verify=False, stream=True)
        if r.status_code == 200:
            content = r.content
            if content[:4] == b'%PDF' or 'pdf' in r.headers.get('Content-Type', '').lower():
                return content
        return None
    except Exception as e:
        console.print(f"    [red]Download error: {str(e)[:60]}[/]")
        return None

def upload_to_storage(pdf_bytes: bytes, source: str, filename: str) -> str | None:
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)[:100]
    if not safe_name.lower().endswith('.pdf'):
        safe_name += '.pdf'
    storage_path = f"veille/{source}/{safe_name}"
    try:
        r = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{storage_path}",
            headers={
                "apikey":        SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type":  "application/pdf",
                "x-upsert":      "true",
            },
            data=pdf_bytes,
            timeout=60,
        )
        if r.status_code in (200, 201):
            return f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{storage_path}"
        console.print(f"    [yellow]Storage {r.status_code}: {r.text[:60]}[/]")
        return None
    except Exception as e:
        console.print(f"    [yellow]Storage error: {str(e)[:60]}[/]")
        return None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",       action="store_true", help="Aperçu sans écriture")
    parser.add_argument("--reupload-pdfs", action="store_true", help="Re-télécharger et uploader les PDFs externes vers Storage")
    args = parser.parse_args()

    if args.dry_run:
        console.print("[yellow]Mode DRY-RUN — aucune écriture[/]\n")

    # ── Charger les textes veille avec extraction_status=pending ──────────────
    console.print("Chargement des textes importés par la veille…")
    select_fields = "id,number,title_fr,source_name,pdf_url"
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={
            "extraction_status": "eq.pending",
            "select":            select_fields,
            "limit":             "500",
        },
        timeout=20,
    )

    if resp.status_code != 200:
        console.print(f"[red]Erreur: {resp.status_code} {resp.text[:100]}[/]")
        sys.exit(1)

    rows = resp.json()
    console.print(f"  {len(rows)} textes avec extraction_status=pending\n")

    # ── Phase 1 : titres et numéros cassés ───────────────────────────────────
    to_fix = []
    for row in rows:
        num   = row.get("number", "") or ""
        title = row.get("title_fr", "") or ""
        patch = {}
        if looks_broken_number(num):
            patch["number"] = clean_number(num)
        if looks_broken_title(title):
            patch["title_fr"] = clean_title(title)
        if patch:
            to_fix.append((row["id"], num, title, patch))

    console.print(f"  [bold]{len(to_fix)}[/] textes avec titre/numéro à corriger")

    if to_fix:
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID",      width=10)
        table.add_column("Avant",   width=42)
        table.add_column("Après",   width=42)
        table.add_column("Status",  width=8)

        fixed = 0
        for (law_id, old_num, old_title, patch) in to_fix:
            before = f"n°{old_num[:38]}" if patch.get("number") else f"«{old_title[:38]}»"
            after  = f"n°{patch['number'][:38]}" if patch.get("number") else f"«{patch.get('title_fr','')[:38]}»"

            if not args.dry_run:
                r = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/laws",
                    headers=HEADERS,
                    params={"id": f"eq.{law_id}"},
                    json=patch,
                    timeout=10,
                )
                ok = r.status_code in (200, 204)
                status = "✅" if ok else f"❌{r.status_code}"
                if ok:
                    fixed += 1
            else:
                status = "🔍"

            table.add_row(str(law_id)[:8] + "…", before, after, status)

        console.print(table)
        if not args.dry_run:
            console.print(f"  ✅ {fixed}/{len(to_fix)} titres/numéros corrigés.\n")

    # ── Phase 2 : re-upload PDFs externes vers Storage ────────────────────────
    if not args.reupload_pdfs:
        console.print("\n  [dim]Astuce : ajouter --reupload-pdfs pour uploader les PDFs externes vers Supabase Storage[/]")
        return

    console.print("\n[bold]Phase 2 — Re-upload PDFs externes vers Supabase Storage[/]\n")

    to_upload = [r for r in rows if r.get("pdf_url") and is_external_pdf(r["pdf_url"])]
    console.print(f"  [bold]{len(to_upload)}[/] PDFs externes à uploader\n")

    if not to_upload:
        console.print("  ✅ Tous les PDFs sont déjà sur Storage.")
        return

    uploaded = failed = 0
    for row in track(to_upload, description="  Upload…"):
        ext_url    = row["pdf_url"]
        source     = row.get("source_name") or "veille"
        raw_name   = Path(unquote(urlparse(ext_url).path)).name

        if args.dry_run:
            console.print(f"  🔍 {raw_name[:60]} ({source})")
            continue

        pdf_bytes = download_pdf(ext_url)
        if not pdf_bytes:
            failed += 1
            console.print(f"  ❌ Download failed: {ext_url[:60]}")
            continue

        storage_url = upload_to_storage(pdf_bytes, source, raw_name)
        if storage_url:
            # Mettre à jour pdf_url dans laws
            r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/laws",
                headers=HEADERS,
                params={"id": f"eq.{row['id']}"},
                json={"pdf_url": storage_url},
                timeout=10,
            )
            if r.status_code in (200, 204):
                uploaded += 1
                console.print(f"  ✅ {raw_name[:50]} → Storage")
            else:
                failed += 1
                console.print(f"  ❌ DB update failed {r.status_code}")
        else:
            failed += 1

        time.sleep(0.3)

    console.print(f"\n  ✅ Uploadés : [green]{uploaded}[/]")
    console.print(f"  ❌ Échecs   : [red]{failed}[/]")


if __name__ == "__main__":
    main()
