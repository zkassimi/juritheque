"""
JuriThèque — Extraction de texte depuis source_url
══════════════════════════════════════════════════════════════════
Récupère les lois qui ont un source_url (Adala / R2) mais dont
content_fr / content_ar est vide, télécharge chaque PDF,
extrait le texte et met à jour la base Supabase.

Usage :
  python pipeline/extract_source_url.py              # tout traiter
  python pipeline/extract_source_url.py --limit 100  # 100 lois max
  python pipeline/extract_source_url.py --dry-run    # simulation
  python pipeline/extract_source_url.py --offset 500 # reprendre depuis 500

Prérequis :
  pip install httpx python-dotenv rich pymupdf pdfplumber
"""

import os, sys, re, tempfile, time
from pathlib import Path
from dotenv import load_dotenv
import httpx

try:
    import fitz          # PyMuPDF
    FITZ_OK = True
except ImportError:
    FITZ_OK = False

try:
    import pdfplumber
    PLUMBER_OK = True
except ImportError:
    PLUMBER_OK = False

try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, MofNCompleteColumn
    console = Console()
    def log(msg): console.print(msg)
except ImportError:
    def log(msg): print(msg)
    class Progress:
        def __init__(self, *a, **kw): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def add_task(self, *a, **kw): return 0
        def update(self, *a, **kw): pass

# ── Config ─────────────────────────────────────────────────────────────────────
load_dotenv()

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("VITE_SUPABASE_ANON_KEY", "")
)

DRY_RUN  = "--dry-run"  in sys.argv
LIMIT    = int(next((sys.argv[i+1] for i, a in enumerate(sys.argv) if a == "--limit"),  500))
OFFSET   = int(next((sys.argv[i+1] for i, a in enumerate(sys.argv) if a == "--offset"), 0))
BATCH_SB = 200   # lois récupérées depuis Supabase par appel
DELAY    = 0.3   # secondes entre chaque téléchargement (politesse)

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}

# ── Helpers Supabase ───────────────────────────────────────────────────────────
def sb_fetch_pending(offset: int, limit: int) -> list[dict]:
    """Lois avec source_url mais sans content (fr ou ar)."""
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers={**HEADERS, "Prefer": ""},
        params={
            "select":      "id,source_url,language,content_fr,content_ar",
            "source_url":  "not.is.null",
            "or":          "(content_fr.is.null,content_ar.is.null)",
            "order":       "id.asc",
            "limit":       str(limit),
            "offset":      str(offset),
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def sb_update(law_id: int, patch: dict):
    """Met à jour une loi dans Supabase."""
    r = httpx.patch(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={"id": f"eq.{law_id}"},
        json=patch,
        timeout=30,
    )
    r.raise_for_status()


# ── Extraction de texte ────────────────────────────────────────────────────────
def extract_text_from_path(pdf_path: str) -> str:
    """Extrait le texte d'un PDF. Essaie pdfplumber puis PyMuPDF."""
    text = ""

    # 1. pdfplumber (meilleur pour PDFs textuels)
    if PLUMBER_OK:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages[:50]]
                text = "\n\n".join(pages).strip()
        except Exception:
            text = ""

    # 2. PyMuPDF fallback
    if len(text) < 100 and FITZ_OK:
        try:
            doc = fitz.open(pdf_path)
            pages = [page.get_text("text") for page in doc[:50]]
            doc.close()
            text = "\n\n".join(pages).strip()
        except Exception:
            pass

    return text


def fix_arabic_text(text: str) -> str:
    """
    Corrige le texte arabe extrait de PDFs en ordre visuel inversé.
    Identique à la fonction dans extract.py.
    """
    if not text:
        return text

    def is_arabic_token(tok: str) -> bool:
        return bool(re.search(r'[؀-ۿﭐ-﻿]', tok))

    def fix_line(line: str) -> str:
        stripped = line.strip()
        ar_chars = sum(1 for c in stripped if '؀' <= c <= 'ۿ' or 'ﭐ' <= c <= '﻿')
        if ar_chars < 3:
            return line
        tokens = re.findall(r'[؀-ۿﭐ-﻿]+|[0-9]+(?:[.,][0-9]+)*|[^؀-ۿﭐ-﻿0-9\s]+|\s+', stripped)
        step1 = [tok[::-1] if is_arabic_token(tok) else tok for tok in tokens]
        step1.reverse()
        return ''.join(step1).strip()

    return '\n'.join(fix_line(l) for l in text.split('\n'))


def is_mostly_arabic(text: str) -> bool:
    """Détermine si le texte est majoritairement arabe."""
    ar = sum(1 for c in text if '؀' <= c <= 'ۿ' or 'ﭐ' <= c <= '﻿')
    total = sum(1 for c in text if c.strip())
    return total > 0 and (ar / total) > 0.3


# ── Pipeline principal ─────────────────────────────────────────────────────────
def process_law(law: dict) -> tuple[bool, str]:
    """
    Traite une loi : télécharge le PDF, extrait le texte, met à jour Supabase.
    Retourne (succès, message).
    """
    law_id    = law["id"]
    url       = law["source_url"]
    language  = (law.get("language") or "").lower()

    # Téléchargement du PDF dans un fichier temporaire
    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (JuriTheque/1.0; legal-research)"
        })
        resp.raise_for_status()
        if "pdf" not in resp.headers.get("content-type", "").lower():
            return False, "Non-PDF content-type"
    except Exception as e:
        return False, f"Download error: {e}"

    # Sauvegarder temporairement
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(resp.content)
        tmp_path = tmp.name

    try:
        text = extract_text_from_path(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    if len(text) < 50:
        return False, "Text too short (scanned PDF?)"

    # Déterminer la colonne à remplir
    is_ar = is_mostly_arabic(text) or "arab" in language or "ar" == language
    if is_ar:
        text = fix_arabic_text(text)
        patch = {"content_ar": text}
    else:
        patch = {"content_fr": text}

    if DRY_RUN:
        col = "content_ar" if is_ar else "content_fr"
        return True, f"DRY-RUN — {col} {len(text):,} chars"

    try:
        sb_update(law_id, patch)
    except Exception as e:
        return False, f"Supabase update error: {e}"

    col = "content_ar" if is_ar else "content_fr"
    return True, f"{col} → {len(text):,} chars"


def main():
    log("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log("[bold gold1]  JuriThèque — Extraction depuis source_url   [/]")
    log("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

    if DRY_RUN:
        log("[yellow]⚠  MODE DRY-RUN — aucune écriture en base[/]\n")

    if not FITZ_OK and not PLUMBER_OK:
        log("[red]✗ Ni PyMuPDF ni pdfplumber disponibles. Installez-les :[/]")
        log("  pip install pymupdf pdfplumber")
        sys.exit(1)

    # Récupérer toutes les lois à traiter (par batch)
    log(f"[dim]Récupération des lois depuis Supabase (offset={OFFSET}, limit={LIMIT})...[/]")
    all_laws = []
    current_offset = OFFSET
    while len(all_laws) < LIMIT:
        batch_size = min(BATCH_SB, LIMIT - len(all_laws))
        try:
            batch = sb_fetch_pending(current_offset, batch_size)
        except Exception as e:
            log(f"[red]✗ Erreur Supabase : {e}[/]")
            break
        if not batch:
            break
        all_laws.extend(batch)
        if len(batch) < batch_size:
            break
        current_offset += batch_size

    if not all_laws:
        log("[green]✓ Aucune loi à traiter — tout est déjà extrait ![/]")
        return

    log(f"[bold]{len(all_laws)} lois à traiter[/]\n")

    ok = 0
    skip = 0
    errors = []

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("Extraction...", total=len(all_laws))

        for i, law in enumerate(all_laws):
            success, msg = process_law(law)

            if success:
                ok += 1
                progress.console.print(f"  [green]✓[/] #{law['id']} — {msg}")
            else:
                if "too short" in msg or "DRY-RUN" in msg:
                    skip += 1
                    progress.console.print(f"  [yellow]⚠[/] #{law['id']} — {msg}")
                else:
                    errors.append((law['id'], msg))
                    progress.console.print(f"  [red]✗[/] #{law['id']} — {msg}")

            progress.update(task, advance=1)

            # Pause entre requêtes
            if i < len(all_laws) - 1:
                time.sleep(DELAY)

    log(f"\n[bold green]━━━ Résumé ━━━[/]")
    log(f"✅ Extraits  : [bold green]{ok}[/]")
    log(f"⚠  Ignorés   : [yellow]{skip}[/] (PDFs scannés ou trop courts)")
    log(f"✗  Erreurs   : [red]{len(errors)}[/]")
    if errors:
        log("\n[red]Erreurs détaillées :[/]")
        for law_id, msg in errors[:20]:
            log(f"  #{law_id} — {msg}")
    log("")


if __name__ == "__main__":
    main()
