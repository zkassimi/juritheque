"""
import_from_queue.py — Importe les textes détectés par la veille dans la table laws
====================================================================================
Lit les entrées 'pending' de import_queue, télécharge les PDFs, extrait le texte,
et insère dans laws. Rien n'est automatique : tu lances ce script manuellement
après avoir vérifié la queue dans Supabase.

Usage :
  python pipeline/import_from_queue.py              # importe tout (pending)
  python pipeline/import_from_queue.py --dry-run    # aperçu sans écriture
  python pipeline/import_from_queue.py --limit 5    # importe max 5 textes
  python pipeline/import_from_queue.py --id UUID    # importe un seul item
  python pipeline/import_from_queue.py --skip-pdf   # sans extraction texte PDF
"""

import os, sys, re, json, argparse, tempfile, time, unicodedata
from pathlib import Path
from datetime import date, datetime
from urllib.parse import urlparse, unquote

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.progress import track

try:
    import requests
    import fitz          # PyMuPDF
except ImportError:
    print("❌ Installe : pip install requests pymupdf")
    sys.exit(1)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", ""))

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/pdf,*/*",
}

console = Console()

# ── Détection langue ─────────────────────────────────────────────────────────

_AR_PATTERN = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')

def detect_language(text_fr: str, text_ar: str = "") -> str:
    has_ar = bool(_AR_PATTERN.search(text_ar)) or bool(_AR_PATTERN.search(text_fr[:500]))
    has_fr = bool(re.search(r'[a-zA-ZéàèùâêîôûçÉÀÈÙÂÊÎÔÛÇ]{4,}', text_fr[:500]))
    if has_ar and has_fr:
        return "Bilingue"
    if has_ar:
        return "Arabe"
    return "Français"

def split_ar_fr(text: str) -> tuple[str, str]:
    """Sépare le texte arabe et français d'un PDF bilingue."""
    lines = text.split('\n')
    fr_lines, ar_lines = [], []
    for line in lines:
        if _AR_PATTERN.search(line):
            ar_lines.append(line)
        else:
            fr_lines.append(line)
    return '\n'.join(fr_lines).strip(), '\n'.join(ar_lines).strip()

# ── Slug ─────────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:100]

def make_slug(law_type: str, number: str, title_fr: str) -> str:
    if number:
        base = f"{law_type}-{number}".replace(' ', '-').replace('/', '-')
        return slugify(base)
    # fallback : premiers mots du titre
    words = title_fr.split()[:5]
    return slugify('-'.join(words))

# ── Types & domaines ─────────────────────────────────────────────────────────

TYPE_MAP = {
    "loi": "Loi", "dahir": "Dahir", "décret": "Décret", "decret": "Décret",
    "arrêté": "Arrêté", "arrete": "Arrêté", "circulaire": "Circulaire",
    "code": "Code", "ordonnance": "Ordonnance", "règlement": "Règlement",
    "recueil": "Recueil", "avis": "Avis", "bulletin": "Bulletin Officiel",
    "قانون": "Loi", "مرسوم": "Décret", "قرار": "Arrêté",
}

def normalize_type(raw: str) -> str:
    if not raw:
        return "Texte juridique"
    low = raw.lower().strip()
    for key, val in TYPE_MAP.items():
        if key in low:
            return val
    return raw.title() or "Texte juridique"

DOMAIN_MAP = {
    "numerique": "numerique", "numérique": "numerique",
    "bancaire": "bancaire", "fiscal": "fiscal", "fiscalité": "fiscal",
    "travail": "travail", "emploi": "travail",
    "civil": "civil", "pénal": "penal", "penal": "penal",
    "commercial": "commercial", "commerce": "commercial",
    "administratif": "administratif",
    "collectivites": "collectivites", "collectivités": "collectivites",
    "finances_publiques": "finances_publiques",
    "environnement": "environnement",
    "urbanisme": "urbanisme",
    "sante": "sante", "santé": "sante",
    "constitutionnel": "constitutionnel",
    "international": "international",
}

def normalize_domain(raw: str) -> str:
    if not raw:
        return "administratif"
    low = raw.lower().strip()
    return DOMAIN_MAP.get(low, low) or "administratif"

# ── Extraction PDF ────────────────────────────────────────────────────────────

def download_pdf(url: str, timeout: int = 30) -> bytes | None:
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=timeout, verify=False, stream=True)
        if resp.status_code == 200 and 'pdf' in resp.headers.get('Content-Type', '').lower():
            return resp.content
        elif resp.status_code == 200:
            # Certains serveurs ne mettent pas le bon Content-Type
            content = resp.content
            if content[:4] == b'%PDF':
                return content
        console.print(f"    [yellow]HTTP {resp.status_code} — {url[:60]}[/]")
        return None
    except Exception as e:
        console.print(f"    [red]⚠️  Download error: {str(e)[:60]}[/]")
        return None

def extract_text_from_pdf(pdf_bytes: bytes) -> tuple[str, str]:
    """Retourne (text_fr, text_ar) depuis le contenu binaire du PDF."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"
        doc.close()
        # Limiter à 50 000 chars pour éviter de surcharger la DB
        full_text = full_text[:50_000]
        text_fr, text_ar = split_ar_fr(full_text)
        return text_fr, text_ar
    except Exception as e:
        console.print(f"    [yellow]PDF parse error: {str(e)[:60]}[/]")
        return "", ""

def extract_title_from_text(text: str) -> str:
    """Extrait le titre depuis les premières lignes du texte."""
    lines = [l.strip() for l in text.split('\n') if l.strip()][:10]
    # Cherche la ligne qui ressemble à un titre juridique
    for line in lines:
        if len(line) > 20 and any(kw in line.lower() for kw in ['loi', 'dahir', 'décret', 'arrêté', 'مرسوم', 'قانون', 'قرار']):
            return line[:300]
    # fallback : première ligne non vide suffisamment longue
    for line in lines:
        if len(line) > 15:
            return line[:300]
    return ""

# ── Supabase ─────────────────────────────────────────────────────────────────

def get_queue(limit: int = 100, item_id: str = None) -> list[dict]:
    params = {"status": "eq.pending", "select": "*", "order": "detected_at.asc"}
    if item_id:
        params = {"id": f"eq.{item_id}", "select": "*"}
    else:
        params["limit"] = str(limit)
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/import_queue", headers=HEADERS, params=params, timeout=15)
    if resp.status_code == 200:
        return resp.json() if isinstance(resp.json(), list) else []
    console.print(f"[red]❌ Erreur queue: {resp.status_code} — {resp.text[:100]}[/]")
    return []

def set_queue_status(item_id: str, status: str, notes: str = ""):
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/import_queue",
        headers=HEADERS,
        params={"id": f"eq.{item_id}"},
        json={"status": status, "notes": notes},
        timeout=10,
    )

def law_exists(number: str) -> bool:
    if not number:
        return False
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={"number": f"ilike.*{number}*", "select": "id", "limit": "1"},
        timeout=10,
    )
    rows = resp.json() if resp.status_code == 200 and isinstance(resp.json(), list) else []
    return len(rows) > 0

def insert_law(data: dict) -> tuple[bool, str]:
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        json=data,
        timeout=20,
    )
    if resp.status_code in (200, 201):
        rows = resp.json()
        inserted_id = rows[0].get("id", "?") if rows else "?"
        return True, str(inserted_id)
    return False, resp.text[:150]

# ── Import d'un item ─────────────────────────────────────────────────────────

def import_item(item: dict, dry_run: bool, skip_pdf: bool) -> dict:
    """Traite un item de la queue. Retourne un dict résultat."""
    iid       = item["id"]
    pdf_url   = item.get("pdf_url") or item.get("bo_url") or ""
    title_fr  = item.get("title_fr") or ""
    law_num   = item.get("law_number") or ""
    law_type  = normalize_type(item.get("law_type") or "")
    domain    = normalize_domain(item.get("domain_guess") or "administratif")
    action    = item.get("action", "new")
    source    = item.get("source", "")

    # ── Nettoyer le titre dès le départ ────────────────────────────────────────
    # Strip extension .pdf et décoder URL encoding (%20, %C3%A9, etc.)
    if title_fr:
        title_fr = unquote(title_fr)                       # decode URL encoding
        title_fr = re.sub(r'\.(pdf|PDF)$', '', title_fr).strip()

    result = {
        "id": iid[:8] + "…",
        "title": title_fr[:55] or pdf_url.split('/')[-1][:55],
        "action": action,
        "status": "?",
        "notes": "",
    }

    # Vérifier doublon
    if law_num and law_exists(law_num):
        result["status"] = "⏭️ DOUBLON"
        result["notes"]  = f"Loi {law_num} déjà dans la base"
        if not dry_run:
            set_queue_status(iid, "done", f"Doublon — {law_num} déjà présent")
        return result

    # Télécharger et extraire le PDF
    text_fr, text_ar = "", ""
    if not skip_pdf and pdf_url:
        if not dry_run:
            set_queue_status(iid, "importing")
        pdf_bytes = download_pdf(pdf_url)
        if pdf_bytes:
            text_fr, text_ar = extract_text_from_pdf(pdf_bytes)
            # Améliorer le titre si on a extrait du texte
            if text_fr and (not title_fr or len(title_fr) < 20):
                extracted = extract_title_from_text(text_fr)
                if extracted:
                    title_fr = extracted
            if text_ar and (not title_fr or len(title_fr) < 5):
                extracted_ar = extract_title_from_text(text_ar)
        time.sleep(0.5)  # politesse

    # Générer le slug
    slug = make_slug(law_type, law_num, title_fr or Path(urlparse(pdf_url).path).stem)

    # ── Générer un numéro fallback si absent ────────────────────────────────
    # La colonne `number` est NOT NULL dans laws — toujours fournir une valeur
    if not law_num:
        # Décoder le nom du fichier PDF (URL-encoding → texte lisible)
        raw_stem = Path(urlparse(pdf_url).path).stem if pdf_url else ""
        filename = unquote(raw_stem)   # ex: D%C3%A9cret_%20... → Décret_ ...
        filename = re.sub(r'\s+', ' ', filename).strip()
        if filename and len(filename) > 3:
            law_num = filename[:60]
        else:
            ts = date.today().strftime("%Y%m%d")
            law_num = f"VEILLE-{source.upper()[:10]}-{ts}-{iid.split('-')[0]}"

    # ── Construire l'entrée laws ─────────────────────────────────────────────
    lang = detect_language(text_fr, text_ar)
    law_data = {
        "number":            law_num,
        "title_fr":          (title_fr[:400] or law_num)[:400],
        "type":              law_type,
        "status":            "En vigueur" if action != "repeal" else "Abrogé",
        "domain_id":         domain,
        "language":          lang,
        "extraction_status": "pending",
        "source_name":       source,
    }
    # Champs optionnels (uniquement si non vides)
    if item.get("title_ar"):
        law_data["title_ar"] = item["title_ar"][:400]
    if text_fr:
        law_data["content_fr"] = text_fr
    if text_ar:
        law_data["content_ar"] = text_ar
    if pdf_url:
        law_data["pdf_url"] = pdf_url
        law_data["source_url"] = item.get("bo_url") or pdf_url
    if slug:
        law_data["canonical_slug"] = slug
    if item.get("bo_number"):
        law_data["bo_number"] = item["bo_number"]
    if item.get("bo_date"):
        law_data["bo_date"]   = item["bo_date"]
        law_data["date"]      = item["bo_date"]   # aussi le champ date principal

    if dry_run:
        result["status"] = "🔍 DRY-RUN"
        result["notes"]  = f"slug={slug} | lang={law_data.get('language')} | text={len(text_fr)} chars"
        return result

    ok, info = insert_law(law_data)
    if ok:
        set_queue_status(iid, "done", f"Importé — id={info}")
        result["status"] = "✅ IMPORTÉ"
        result["notes"]  = f"laws.id={info}"
    else:
        set_queue_status(iid, "rejected", f"Erreur insert: {info}")
        result["status"] = "❌ ERREUR"
        result["notes"]  = info[:80]

    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",  action="store_true", help="Aperçu sans écriture")
    parser.add_argument("--limit",    type=int, default=50, help="Max items à traiter (défaut: 50)")
    parser.add_argument("--id",       help="Importer un seul item (UUID)")
    parser.add_argument("--skip-pdf", action="store_true", help="Ne pas télécharger/extraire les PDFs")
    args = parser.parse_args()

    console.print("\n[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    console.print("[bold]  📥 Import depuis la file d'attente (import_queue)[/]")
    console.print("[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

    if args.dry_run:
        console.print("[yellow]Mode DRY-RUN — aucune écriture en base[/]\n")

    if not SUPABASE_URL or not SUPABASE_KEY:
        console.print("[red]❌ Variables SUPABASE_URL / SUPABASE_KEY manquantes[/]")
        sys.exit(1)

    # Charger la queue
    items = get_queue(limit=args.limit, item_id=args.id)
    if not items:
        console.print("  Aucune entrée 'pending' dans import_queue. Rien à faire.")
        return

    console.print(f"  [bold]{len(items)} entrée(s)[/] à traiter")
    if args.skip_pdf:
        console.print("  [yellow]--skip-pdf : extraction PDF désactivée[/]")
    console.print()

    results  = []
    imported = rejected = skipped = 0

    for item in track(items, description="  Import…"):
        r = import_item(item, dry_run=args.dry_run, skip_pdf=args.skip_pdf)
        results.append(r)
        if "IMPORTÉ" in r["status"] or "DRY-RUN" in r["status"]:
            imported += 1
        elif "ERREUR" in r["status"]:
            rejected += 1
        else:
            skipped += 1

    # ── Rapport ────────────────────────────────────────────────────────────────
    console.print("\n[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    console.print("[bold]  Rapport d'import[/]")
    console.print("[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID",      width=10)
    table.add_column("Titre",   width=50)
    table.add_column("Action",  width=10)
    table.add_column("Résultat", width=18)
    table.add_column("Notes",   width=35)

    for r in results:
        color = "green" if "IMPORTÉ" in r["status"] else ("red" if "ERREUR" in r["status"] else "dim")
        table.add_row(
            r["id"], r["title"], r["action"],
            f"[{color}]{r['status']}[/{color}]",
            r["notes"],
        )
    console.print(table)

    console.print(f"\n  ✅ Importés   : [green]{imported}[/]")
    console.print(f"  ⏭️  Ignorés    : [dim]{skipped}[/]")
    console.print(f"  ❌ Erreurs    : [red]{rejected}[/]")
    if args.dry_run:
        console.print("\n  [yellow][DRY-RUN] Rien n'a été écrit en base.[/]")
    console.print()


if __name__ == "__main__":
    main()
