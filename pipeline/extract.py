"""
LexBase PDF Extraction Pipeline
────────────────────────────────
Drop PDFs in ./pdfs → extracted, structured, renamed,
uploaded to Supabase Storage, inserted into the laws table.

Usage:
    python extract.py              # Process all PDFs in ./pdfs
    python extract.py file.pdf     # Process a single file
    python extract.py --dry-run    # Preview only, no DB writes
"""

import os, sys, json, shutil, re, time, mimetypes, unicodedata
from pathlib import Path
from datetime import datetime
import pdfplumber
import fitz  # PyMuPDF — fallback for Arabic/scanned PDFs
import anthropic
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# ── OCR imports (optional — only used for scanned PDFs) ──────────────────────
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    # Tesseract path on Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
    POPPLER_PATH = r"C:\Users\HP\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin"
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ── Setup ─────────────────────────────────────────────────────────────────────
load_dotenv(Path(__file__).parent / ".env", override=True)
console = Console()

ANTHROPIC_KEY    = os.getenv("ANTHROPIC_API_KEY", "")
OPENROUTER_KEY   = os.getenv("OPENROUTER_API_KEY") or os.getenv("VITE_OPENROUTER_KEY", "")
PROVIDER         = os.getenv("PROVIDER", "openrouter").lower()   # anthropic | openrouter
MODEL            = os.getenv("MODEL", "google/gemini-2.5-pro")
SUPABASE_URL     = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY     = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", ""))
_PIPELINE_DIR    = Path(__file__).parent          # .../lexbase/pipeline/
_PDFS_DEFAULT    = str(_PIPELINE_DIR / "pdfs")
INPUT_FOLDER     = Path(os.getenv("PDF_INPUT_FOLDER",  _PDFS_DEFAULT))
DONE_FOLDER      = Path(os.getenv("PDF_DONE_FOLDER",   str(_PIPELINE_DIR / "pdfs" / "done")))
ERROR_FOLDER     = Path(os.getenv("PDF_ERROR_FOLDER",  str(_PIPELINE_DIR / "pdfs" / "errors")))
STORAGE_BUCKET   = os.getenv("STORAGE_BUCKET", "legal-documents")
DRY_RUN          = "--dry-run"    in sys.argv
UPDATE_CONTENT   = "--update"     in sys.argv   # patch content_fr/content_ar only
FIX_ARABIC       = "--fix-arabic" in sys.argv   # re-fix reversed Arabic in all DB rows

for folder in [INPUT_FOLDER, DONE_FOLDER, ERROR_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

# ── AI Client (Anthropic or OpenRouter) ──────────────────────────────────────
if PROVIDER == "anthropic":
    claude = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
else:
    claude = None  # OpenRouter uses httpx directly

# Supabase via direct REST API (works with all key formats)
HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}

def sb_insert(table: str, record: dict) -> dict:
    """Insert a row into a Supabase table. Raises ValueError on 409 (doublon)."""
    r = httpx.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=record,
        timeout=30,
    )
    if r.status_code == 409:
        raise ValueError(f"DOUBLON_409 — déjà présent en base")
    r.raise_for_status()
    return r.json()[0]

def sb_patch(table: str, row_id: int, record: dict) -> None:
    """Patch (PATCH) an existing row by id."""
    r = httpx.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{row_id}",
        headers=HEADERS,
        json=record,
        timeout=30,
    )
    r.raise_for_status()

def sb_find_by_number(number: str) -> dict | None:
    """Find a law row by its official number."""
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={"number": f"eq.{number}", "select": "id,number,title_fr", "limit": "1"},
        timeout=15,
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None

def sb_upload(bucket: str, path: str, data: bytes) -> str:
    """Upload a file to Supabase Storage. Returns public URL."""
    upload_headers = {
        "apikey":          SUPABASE_KEY,
        "Authorization":   f"Bearer {SUPABASE_KEY}",
        "Content-Type":    "application/pdf",
        "x-upsert":        "true",
    }
    r = httpx.post(
        f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}",
        headers=upload_headers,
        content=data,
        timeout=120,
    )
    r.raise_for_status()
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"


# ── Step 1: Extract text from PDF ────────────────────────────────────────────
def extract_text(pdf_path: Path) -> str:
    text = ""

    # Try pdfplumber first (text-based PDFs)
    # layout=True preserves spatial reading order — essential for Arabic RTL
    # and multi-column Bulletin Officiel layouts.
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            for p in pdf.pages[:30]:
                try:
                    pages.append(p.extract_text(layout=True, x_tolerance=1.5, y_tolerance=3) or "")
                except Exception:
                    pages.append(p.extract_text() or "")
            text = "\n\n".join(pages).strip()
    except Exception:
        pass

    # Fallback: PyMuPDF (sort=True → natural top-to-bottom reading order)
    if len(text) < 200:
        try:
            doc = fitz.open(str(pdf_path))
            pages = [page.get_text("text", sort=True) for page in doc[:30]]
            doc.close()
            text = "\n\n".join(pages).strip()
        except Exception:
            pass

    # Fallback: OCR for scanned PDFs
    if len(text) < 200 and OCR_AVAILABLE:
        console.print("  [yellow]→ Scanned PDF detected — running OCR...[/]")
        try:
            images = convert_from_path(
                str(pdf_path),
                dpi=300,
                first_page=1,
                last_page=15,
                poppler_path=POPPLER_PATH,
            )
            ocr_pages = []
            # --oem 3 = moteur LSTM (réseau de neurones, bien meilleur que legacy)
            # --psm 6 = bloc de texte uniforme (adapté aux pages juridiques denses,
            #           plus fiable que --psm 3 auto sur les documents mono-colonne)
            ocr_cfg = "--oem 3 --psm 6"
            for i, img in enumerate(images):
                # Try French + Arabic OCR
                page_text = pytesseract.image_to_string(img, lang="fra+ara", config=ocr_cfg)
                if not page_text.strip():
                    # Fallback: French only
                    page_text = pytesseract.image_to_string(img, lang="fra", config=ocr_cfg)
                ocr_pages.append(page_text)
                console.print(f"    [dim]OCR page {i+1}/{len(images)} — {len(page_text)} chars[/]")
            text = "\n\n".join(ocr_pages).strip()
            console.print(f"  [green]✓[/] OCR extracted {len(text):,} characters")
        except Exception as e:
            console.print(f"  [red]✗ OCR failed: {e}[/]")

    elif len(text) < 200 and not OCR_AVAILABLE:
        console.print("  [red]✗ Scanned PDF — install pytesseract & pdf2image for OCR support[/]")

    return text


# ── Step 2: Claude structured extraction ─────────────────────────────────────
# NOTE: AI extracts ONLY metadata. Full text is stored separately (see below).
PROMPT = """You are a legal document analyst specializing in Moroccan law (French and Arabic).
Analyze the legal text below and return ONLY a valid JSON object with these metadata fields:
{
  "number":     "official reference (e.g. 'Dahir n°1-04-22')",
  "type":       "one of: Loi, Dahir, Décret, Arrêté, Circulaire, Code, Jurisprudence, Convention, Règlement, Ordonnance",
  "domain":     "one of: civil, penal, commercial, administratif, travail, fiscal, international, numerique, constitutionnel, bancaire, finances_publiques, collectivites_territoriales, sport, famille",
  "status":     "one of: En vigueur, Abrogé, Modifié",
  "date":       "YYYY-MM-DD or null",
  "title_fr":   "full official French title",
  "title_ar":   "full official Arabic title or empty string if not present",
  "excerpt_fr": "2-3 sentence French summary of the law's purpose",
  "excerpt_ar": "2-3 sentence Arabic summary or empty string",
  "tags":       ["3-6 relevant keywords in French"]
}
Rules:
- Default type=Loi, domain=administratif, status=En vigueur if unclear (préfère administratif à civil pour les textes de droit public).
- Do NOT include content_fr or content_ar — the full text is stored separately.
- Return ONLY valid JSON, no markdown, no explanation.

Legal text (first 8000 chars for metadata extraction):
"""

def fix_arabic_text(text: str) -> str:
    """
    Fix Arabic text extracted from PDFs in reversed visual order.
    PDFs often store Arabic chars left→right (visually) instead of right→left (logical).
    This causes both character order AND word order to be reversed.

    Fix: for each Arabic line, reverse chars within Arabic tokens,
         then reverse the whole token sequence.

    Example:  "99.15 مقر نوناقلا"  →  "القانون رقم 99.15"  ✓
    """
    if not text:
        return text

    def is_arabic_token(tok: str) -> bool:
        return bool(re.search(r'[؀-ۿﭐ-﻿]', tok))

    def fix_line(line: str) -> str:
        stripped = line.strip()
        # Only touch lines with significant Arabic content
        ar_chars = sum(1 for c in stripped if '؀' <= c <= 'ۿ' or 'ﭐ' <= c <= '﻿')
        if ar_chars < 3:
            return line

        # Tokenize into Arabic words, numbers, punctuation, spaces
        tokens = re.findall(r'[؀-ۿﭐ-﻿]+|[0-9]+(?:[.,][0-9]+)*|[^؀-ۿﭐ-﻿0-9\s]+|\s+', stripped)

        # Step 1 — reverse characters inside each Arabic token
        step1 = [tok[::-1] if is_arabic_token(tok) else tok for tok in tokens]

        # Step 2 — reverse the full token sequence (fixes word order)
        step1.reverse()

        # Rejoin, collapsing multiple spaces
        result = ''.join(step1).strip()
        return result

    lines = text.split('\n')
    fixed = [fix_line(l) for l in lines]
    return '\n'.join(fixed)


def is_reversed_arabic(text: str) -> bool:
    """Detect if Arabic text is stored in reversed visual order."""
    # These are common Arabic legal words written in reverse
    reversed_markers = {'نوناقلا', 'موسرملا', 'ريهظلا', 'ةداملا', 'لصفلا', 'ةرازو', 'برغملا'}
    words = set(text.split())
    return bool(words & reversed_markers)


def split_bilingual(text: str) -> tuple[str, str]:
    """
    Try to split a bilingual (FR + AR) text into two halves.
    Returns (french_part, arabic_part). If no Arabic found, arabic_part is "".
    """
    # Detect if the text contains significant Arabic content
    arabic_chars = sum(1 for c in text if '؀' <= c <= 'ۿ')
    if arabic_chars < 100:
        return text, ""

    # Heuristic: split at the first long Arabic block after French content
    lines = text.split('\n')
    fr_lines, ar_lines = [], []
    in_arabic = False
    for line in lines:
        line_arabic = sum(1 for c in line if '؀' <= c <= 'ۿ')
        line_latin  = sum(1 for c in line if c.isalpha() and c.isascii())
        if not in_arabic and line_arabic > line_latin and line_arabic > 5:
            in_arabic = True
        if in_arabic:
            ar_lines.append(line)
        else:
            fr_lines.append(line)

    return '\n'.join(fr_lines).strip(), '\n'.join(ar_lines).strip()


def extract_structure(text: str, filename: str) -> dict:
    # Fix reversed Arabic BEFORE AI call so the model gets clean text
    if is_reversed_arabic(text):
        text = fix_arabic_text(text)

    # AI call: metadata only — first 3000 chars contain title/number/date
    content = PROMPT + text[:3000]

    MAX_RETRIES = 3
    raw = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if PROVIDER == "anthropic":
                msg = claude.messages.create(
                    model=MODEL,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": content}]
                )
                raw = msg.content[0].text.strip()

            else:
                if not OPENROUTER_KEY:
                    raise Exception("OPENROUTER_API_KEY manquant — ajoutez-le dans .env ou via $env:OPENROUTER_API_KEY")
                r = httpx.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_KEY}",
                        "Content-Type":  "application/json",
                        "HTTP-Referer":  "https://juritheque.com",
                        "X-Title":       "JuriTheque Pipeline",
                    },
                    json={
                        "model": MODEL,
                        "messages": [{"role": "user", "content": content}],
                        "max_tokens": 2048,
                        "response_format": {"type": "json_object"},
                    },
                    timeout=60,
                )
                if not r.is_success:
                    raise Exception(f"HTTP {r.status_code} — {r.text[:300]}")
                resp_data = r.json()
                choices = resp_data.get("choices") or []
                if not choices:
                    raise Exception(f"Réponse API vide (choices=[]) — {str(resp_data)[:150]}")
                raw = choices[0]["message"]["content"].strip()

            break  # success — exit retry loop

        except Exception as e:
            err_str = str(e)
            if attempt < MAX_RETRIES:
                wait = attempt * 5  # 5s, 10s
                console.print(f"  [yellow]⚠ API erreur (tentative {attempt}/{MAX_RETRIES}): {err_str[:80]}[/]")
                console.print(f"  [dim]→ Nouvelle tentative dans {wait}s...[/]")
                time.sleep(wait)
            else:
                console.print(f"  [red]✗ API inaccessible après {MAX_RETRIES} tentatives: {err_str[:80]}[/]")
                console.print(f"  [yellow]→ Métadonnées générées depuis le nom du fichier[/]")
                raw = "{}"  # fallback to defaults
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*",     "", raw)
    raw = re.sub(r"\s*```$",     "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(match.group()) if match else {}

    defaults = {
        "number": Path(filename).stem, "type": "Loi", "domain": "civil",
        "status": "En vigueur", "date": None,
        "title_fr": None, "title_ar": "",
        "excerpt_fr": "", "excerpt_ar": "",
        "tags": [],
    }
    for k, v in defaults.items():
        data.setdefault(k, v)

    # ── Titre : lookup AI par numéro si l'extraction PDF a échoué ────────────
    # (évite le fallback filename-stem qui pollue la base)
    if not data.get("title_fr") or len(data.get("title_fr", "")) < 10:
        try:
            from title_lookup import get_best_title as _get_best_title
            better = _get_best_title(
                law_type=data.get("type", ""),
                number=data.get("number", ""),
                date=str(data.get("date", "")) if data.get("date") else "",
            )
            if better:
                data["title_fr"] = better
                console.print(f"  [green]→ Titre lookup AI: {better[:70]}[/]")
            else:
                # Dernier recours : filename stem (mieux que rien pour la recherche)
                data["title_fr"] = data["title_fr"] or Path(filename).stem
        except Exception:
            data["title_fr"] = data["title_fr"] or Path(filename).stem

    # ── Store FULL extracted text (not AI-truncated) ──────────────────────
    # Split bilingual documents into FR + AR parts
    content_fr, content_ar = split_bilingual(text)

    # Fix reversed Arabic text (common PDF extraction issue)
    if content_ar and is_reversed_arabic(content_ar):
        console.print("  [yellow]→ Reversed Arabic detected — applying BiDi fix...[/]")
        content_ar = fix_arabic_text(content_ar)

    data["content_fr"] = content_fr
    data["content_ar"] = content_ar

    data["language"] = "Bilingue" if (data.get("title_ar") or content_ar) else "FR"
    return data


# ── Step 3: Upload PDF to Supabase Storage ────────────────────────────────────
def ascii_safe(text: str) -> str:
    """Strip accents and non-ASCII chars to make a safe storage filename."""
    nfkd = unicodedata.normalize('NFD', text)
    ascii_only = nfkd.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^\w]', '_', ascii_only)

def upload_pdf(pdf_path: Path, law_data: dict) -> str:
    safe_title  = ascii_safe(law_data.get("title_fr", "")[:50])
    safe_number = ascii_safe(law_data.get("number",   "")[:30])
    safe_type   = ascii_safe(law_data.get("type",     "Loi"))
    name = re.sub(r'_+', '_', f"{safe_type}_{safe_number}_{safe_title}").strip('_') + ".pdf"
    with open(pdf_path, "rb") as f:
        data = f.read()
    return sb_upload(STORAGE_BUCKET, name, data)


# ── Step 4: Insert into laws table ────────────────────────────────────────────
def insert_law(law_data: dict, pdf_url: str) -> int:
    record = {
        "number":     law_data["number"],
        "type":       law_data["type"],
        "domain_id":  law_data["domain"],
        "status":     law_data["status"],
        "date":       law_data["date"],
        "title_fr":   law_data["title_fr"],
        "title_ar":   law_data.get("title_ar") or None,
        "excerpt_fr": law_data.get("excerpt_fr") or None,
        "excerpt_ar": law_data.get("excerpt_ar") or None,
        "content_fr": law_data.get("content_fr") or None,
        "content_ar": law_data.get("content_ar") or None,
        "language":   law_data.get("language", "FR"),
        "tags":       law_data.get("tags", []),
        "pdf_url":    pdf_url,
    }
    row = sb_insert("laws", record)
    return row["id"]


# ── Step 5: Rename file ────────────────────────────────────────────────────────
def rename_pdf(pdf_path: Path, law_data: dict) -> Path:
    safe  = re.sub(r'[^\w]', '_', law_data.get("title_fr","doc")[:60])
    safe  = re.sub(r'_+', '_', safe).strip('_')
    year  = (law_data.get("date") or "0000")[:4]
    name  = f"{year}_{law_data.get('type','LOI')}_{safe}.pdf"
    dest  = pdf_path.parent / name
    pdf_path.rename(dest)
    return dest


# ── Main processor ────────────────────────────────────────────────────────────
def process_pdf(pdf_path: Path) -> dict:
    result = {"file": pdf_path.name, "status": "error", "law_id": None, "title": None}
    try:
        console.print(f"\n[bold cyan]📄 Processing:[/] {pdf_path.name}")

        console.print("  [dim]→ Extracting text...[/]")
        text = extract_text(pdf_path)
        if len(text) < 50:
            raise ValueError("Too little text — may be a scanned image PDF")
        console.print(f"  [green]✓[/] {len(text):,} characters extracted")

        console.print("  [dim]→ Analysing with Claude...[/]")
        law_data = extract_structure(text, pdf_path.name)
        console.print(f"  [green]✓[/] [{law_data['type']}] {law_data['title_fr'][:60]}")

        if DRY_RUN:
            console.print("  [yellow]⚠ DRY RUN — no upload or DB write[/]")
            console.print(f"\n[dim]{json.dumps(law_data, ensure_ascii=False, indent=2)[:600]}[/]")
            result.update({"status": "dry-run", "title": law_data["title_fr"], "data": law_data})
            return result

        # ── UPDATE mode: patch content only, no re-insert ─────────────────
        if UPDATE_CONTENT:
            existing = sb_find_by_number(law_data["number"])
            if existing:
                sb_patch("laws", existing["id"], {
                    "content_fr": law_data.get("content_fr") or None,
                    "content_ar": law_data.get("content_ar") or None,
                })
                console.print(f"  [green]✓[/] Patched Law #{existing['id']} — {existing['title_fr'][:50]}")
                result.update({"status": "success", "law_id": existing["id"], "title": existing["title_fr"]})
                return result
            else:
                console.print(f"  [yellow]⚠ No existing row found for '{law_data['number']}' — inserting as new[/]")

        # ── Anti-doublon : vérifier si la loi existe déjà ────────────────────
        existing = sb_find_by_number(law_data["number"])
        if existing:
            console.print(f"  [yellow]⚠ Doublon détecté — '{law_data['number']}' existe déjà (ID #{existing['id']})[/]")
            console.print(f"  [dim]  Titre existant : {existing['title_fr'][:60]}[/]")
            # Move PDF to done/ anyway to avoid reprocessing
            try:
                renamed = rename_pdf(pdf_path, law_data)
                shutil.move(str(renamed), DONE_FOLDER / renamed.name)
            except Exception:
                shutil.move(str(pdf_path), DONE_FOLDER / pdf_path.name)
            console.print(f"  [dim]  PDF déplacé dans done/ — pas d'insertion[/]")
            result.update({"status": "skipped", "law_id": existing["id"], "title": existing["title_fr"]})
            return result

        console.print("  [dim]→ Uploading to Supabase Storage...[/]")
        pdf_url = upload_pdf(pdf_path, law_data)
        console.print(f"  [green]✓[/] Uploaded")

        console.print("  [dim]→ Inserting into database...[/]")
        try:
            law_id = insert_law(law_data, pdf_url)
        except ValueError as ve:
            if "DOUBLON_409" in str(ve):
                console.print(f"  [yellow]⚠ Doublon DB (409) — déjà en base, déplacé dans done/[/]")
                try:
                    shutil.move(str(pdf_path), DONE_FOLDER / pdf_path.name)
                except Exception:
                    pass
                result.update({"status": "skipped", "law_id": None, "title": law_data["title_fr"]})
                return result
            raise
        console.print(f"  [green]✓[/] Law #{law_id} created")

        if not UPDATE_CONTENT:
            renamed = rename_pdf(pdf_path, law_data)
            shutil.move(str(renamed), DONE_FOLDER / renamed.name)
            console.print(f"  [green]✓[/] Moved to done/")

        result.update({"status": "success", "law_id": law_id, "title": law_data["title_fr"]})

    except Exception as e:
        console.print(f"  [red]✗ {e}[/]")
        try: shutil.move(str(pdf_path), ERROR_FOLDER / pdf_path.name)
        except Exception: pass
        result["error"] = str(e)
    return result


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    console.print("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    console.print("[bold gold1]  JuriThèque PDF Extraction Pipeline       [/]")
    console.print("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")
    if DRY_RUN:
        console.print("[yellow]⚠  DRY RUN — nothing will be written[/]\n")
    if UPDATE_CONTENT:
        console.print("[cyan]🔄 UPDATE MODE — will patch content_fr/content_ar for existing laws[/]\n")

    # ── Special mode: fix reversed Arabic in all existing DB rows ────────────
    if FIX_ARABIC:
        console.print("[cyan]🔤 FIX-ARABIC MODE — fixing reversed Arabic in Supabase...[/]\n")
        # Fetch all laws with Arabic content
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers=HEADERS,
            params={"select": "id,title_fr,content_ar", "content_ar": "not.is.null", "limit": "500"},
            timeout=30,
        )
        rows = r.json()
        fixed_count = 0
        for row in rows:
            content_ar = row.get("content_ar") or ""
            if content_ar and is_reversed_arabic(content_ar):
                fixed = fix_arabic_text(content_ar)
                sb_patch("laws", row["id"], {"content_ar": fixed})
                console.print(f"  [green]✓[/] Fixed #{row['id']} — {row.get('title_fr','')[:50]}")
                fixed_count += 1
        console.print(f"\n[bold green]✅ Fixed {fixed_count}/{len(rows)} laws[/]")
        return

    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        # Single file specified
        target = Path(sys.argv[1])
        pdf_files = [target] if target.exists() else []
    elif UPDATE_CONTENT:
        # Update mode: scan done/ folder for already-processed PDFs
        pdf_files = sorted([f for f in DONE_FOLDER.glob("*.pdf") if f.is_file()])
        if not pdf_files:
            console.print(f"[yellow]No PDFs found in {DONE_FOLDER}/[/]")
            console.print("Move PDFs back to pipeline/pdfs/done/ or specify a file path.")
            return
    else:
        pdf_files = sorted([f for f in INPUT_FOLDER.glob("*.pdf") if f.is_file()])

    if not pdf_files:
        console.print(f"[yellow]No PDFs found in {INPUT_FOLDER}/[/]")
        console.print("Drop PDFs into [bold]pipeline/pdfs/[/] then run again.")
        return

    console.print(f"[bold]Found {len(pdf_files)} PDF(s)[/]\n")

    results = []
    start = time.time()
    for pdf in pdf_files:
        results.append(process_pdf(pdf))
        time.sleep(0.5)

    elapsed = time.time() - start
    success = [r for r in results if r["status"] == "success"]
    skipped = [r for r in results if r["status"] == "skipped"]
    errors  = [r for r in results if r["status"] == "error"]

    console.print("\n[bold gold1]━━━━ Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("File",   max_width=35)
    table.add_column("Status")
    table.add_column("ID")
    table.add_column("Title", max_width=40)
    for r in results:
        s = {"success":"[green]✓ OK[/]","skipped":"[yellow]⚠ Doublon[/]","error":"[red]✗ Error[/]","dry-run":"[yellow]○ Dry[/]"}.get(r["status"],r["status"])
        table.add_row(r["file"][:35], s, str(r.get("law_id") or "—"), (r.get("title") or r.get("error",""))[:40])
    console.print(table)
    console.print(f"\n✅ {len(success)} insérées  ⚠ {len(skipped)} doublons ignorés  ❌ {len(errors)} erreurs  ⏱ {elapsed:.1f}s\n")

    report = Path(f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    console.print(f"[dim]Report: {report}[/]")

if __name__ == "__main__":
    main()
