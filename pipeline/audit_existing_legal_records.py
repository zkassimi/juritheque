# -*- coding: utf-8 -*-
"""
audit_existing_legal_records.py — Audit canonique des textes juridiques
========================================================================
Lit les records de la base, télécharge leur PDF (ou utilise le cache local),
extrait la première page, compare avec les métadonnées stockées, et produit
un rapport d'audit sans jamais écrire en base.

Basé sur le prototype de juritheque-legal-canonicalization-proposal/

Usage :
  python -X utf8 pipeline/audit_existing_legal_records.py
  python -X utf8 pipeline/audit_existing_legal_records.py --limit 50
  python -X utf8 pipeline/audit_existing_legal_records.py --id 1234
  python -X utf8 pipeline/audit_existing_legal_records.py --source Adala
  python -X utf8 pipeline/audit_existing_legal_records.py --low-score
  python -X utf8 pipeline/audit_existing_legal_records.py --export
"""

from __future__ import annotations

import os, re, sys, json, csv, time, argparse, tempfile, shutil
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Any

import requests
from dotenv import load_dotenv

# ── Setup ────────────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_KEY']
SB = {
    'apikey':        SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal',
}
DOWNLOAD_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; JuriTheque-Audit/1.0)',
    'Accept': 'application/pdf,*/*',
}

MIRROR_DIR   = Path(__file__).parent / 'pdfs' / 'mirror'
MIRROR_INDEX = MIRROR_DIR / 'index.json'
AUDIT_DIR    = Path(__file__).parent / 'audit_results'

# ── PDF libraries ─────────────────────────────────────────────────────────────
try:
    import fitz  # PyMuPDF
    FITZ_OK = True
except ImportError:
    FITZ_OK = False

try:
    import pdfplumber
    PDFPLUMBER_OK = True
except ImportError:
    PDFPLUMBER_OK = False

# ── OCR Vision (Gemini multimodal via OpenRouter) ──────────────────────────────
# Pour les PDFs scannés ou à police non embarquée : on rend la page en image
# et on demande à un modèle vision de transcrire le texte (lit l'arabe nativement,
# aucun install local type Tesseract requis).
OPENROUTER_KEY  = os.getenv('OPENROUTER_API_KEY') or os.getenv('VITE_OPENROUTER_KEY', '')
OCR_VISION_MODEL = os.getenv('OCR_VISION_MODEL', 'google/gemini-2.5-flash')
USE_VISION_OCR  = bool(OPENROUTER_KEY)   # désactivable via --no-ocr dans main()

OCR_PROMPT = (
    "Tu reçois l'image de la première page d'un document juridique marocain "
    "(Bulletin Officiel, dahir, loi, décret, arrêté — en arabe et/ou en français). "
    "Transcris FIDÈLEMENT tout le texte visible de l'en-tête et du début du document. "
    "Conserve EXACTEMENT les numéros (ex: 1-15-83, 103-12, 2-22-431), les dates "
    "(grégoriennes et hégiriennes) et les intitulés (Dahir, Loi, Décret, Arrêté, "
    "ظهير، قانون، مرسوم، قرار). Ne traduis pas, ne résume pas, n'ajoute aucun commentaire. "
    "Réponds uniquement par le texte transcrit tel qu'il apparaît."
)

# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class AuditFlag:
    code: str
    severity: str       # info | warning | critical | blocking
    field: str | None
    detail: str

@dataclass
class CanonicalRecord:
    law_id: int
    formal_instrument_type: str | None = None
    subject_text_type: str | None = None
    dahir_number: str | None = None
    law_number: str | None = None
    decree_number: str | None = None
    arrete_number: str | None = None
    official_number: str | None = None
    signature_date: str | None = None
    official_title_fr: str | None = None
    number_ambiguous: bool = False
    date_ambiguous: bool = False
    source_priority: str = 'db_only'
    canonical_confidence_score: int = 50
    canonical_validation_status: str = 'unknown'
    flags: list[AuditFlag] = field(default_factory=list)
    first_page_text: str = ''
    pdf_resolved: bool = False

@dataclass
class DiffItem:
    field: str
    current_value: str | None
    proposed_value: str | None
    severity: str
    action: str

@dataclass
class AuditResult:
    law_id: int
    score: int
    decision: str          # auto_update | review | review_high_priority | block
    flags: list[AuditFlag]
    diffs: list[DiffItem]
    safe_to_auto_update: bool
    canonical: CanonicalRecord
    error: str | None = None


# ── Moroccan legal number / date patterns ─────────────────────────────────────

MONTHS_FR = {
    'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12,
}
MONTHS_AR = {
    'يناير': 1, 'فبراير': 2, 'مارس': 3, 'أبريل': 4, 'ابريل': 4,
    'ماي': 5, 'يونيو': 6, 'يوليوز': 7, 'يوليو': 7, 'غشت': 8,
    'شتنبر': 9, 'أكتوبر': 10, 'اكتوبر': 10, 'نونبر': 11, 'دجنبر': 12,
}

# Conversion chiffres arabes orientaux → chiffres occidentaux
_AR_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

# Marqueurs introduisant l'historique des modifications / consolidation :
# tout ce qui suit cite des numéros d'AUTRES textes — l'en-tête seul fait foi.
MODIF_HISTORY_MARKERS = [
    r"comme il a été modifié",
    r"tel qu'?il a été modifié",
    r"telle qu'?elle a été modifiée",
    r"tel que modifié",
    r"modifié et complété par",
    r"modifiée et complétée par",
    r"version consolidée",
    r"vu le dahir",          # préambule citant d'autres textes
    r"كما تم تغييره",          # "tel que modifié" en arabe
    r"كما وقع تغييره",
    r"بناء على الظهير",        # "vu le dahir" en arabe
]

# Connecteurs introduisant un texte SECONDAIRE (modifié, abrogé, appliqué).
# Tout ce qui suit cite le numéro/date d'un AUTRE instrument que l'acte présent.
# NB : "portant promulgation de la loi" est EXCLU — pour un dahir de promulgation,
# le n° de la loi promulguée est souvent celui stocké en base.
CONNECTOR_RE = re.compile(
    r'\b(?:modifiant et complétant|complétant et modifiant'
    r'|modifiant|complétant|completant|abrogeant|remplaçant|remplacant'
    r'|en application|pris pour (?:l[\'’])?application|portant application)\b',
    re.IGNORECASE)

# Détection de texte arabe et d'encodage CID corrompu
_ARABIC_RE = re.compile(r'[؀-ۿݐ-ݿࢠ-ࣿ]')
_CID_RE    = re.compile(r'\(cid:\d+\)')


def _is_primarily_arabic(text: str) -> bool:
    """True si le texte est principalement en caractères arabes (>40% des chars non-espace)."""
    alpha = re.sub(r'\s', '', text or '')
    if not alpha:
        return False
    return len(_ARABIC_RE.findall(alpha)) / len(alpha) > 0.4


def _header_region(text: str) -> str:
    """
    Retourne uniquement l'en-tête du texte — la portion AVANT toute mention
    d'historique de modifications. C'est là que figure l'identité officielle
    (Règle 6 : la première page / l'en-tête fait foi). Évite de capter les
    numéros/dates d'autres textes cités dans la liste des modifications.
    """
    cut = len(text)
    low = text.lower()
    for marker in MODIF_HISTORY_MARKERS:
        m = re.search(marker, low)
        if m and m.start() < cut:
            cut = m.start()
    head = text[:cut].strip()
    # Garde-fou : si la coupure est trop agressive (en-tête trop court),
    # garder au moins les 600 premiers caractères.
    if len(head) < 80:
        head = text[:600]
    return head


def _extract_from_page1(text: str) -> dict[str, Any]:
    """Extrait type, numéros et date depuis l'EN-TÊTE du document (pas le corps)."""
    result: dict[str, Any] = {
        'dahir_number': None,
        'law_number': None,
        'decree_number': None,
        'arrete_number': None,
        'formal_type': None,
        'signature_date': None,
        'title_lines': [],
        'has_connector': False,
        'number_ambiguous': False,
        'date_ambiguous': False,
    }

    # Normaliser les chiffres arabes orientaux (٠١٢...) → occidentaux (012...)
    text = text.translate(_AR_DIGITS)

    # Restreindre l'extraction à l'en-tête (avant l'historique des modifications)
    header = _header_region(text)

    # Segment PRIMAIRE = en-tête tronqué au 1er connecteur introduisant un texte
    # secondaire (modifiant/en application/…). Les numéros et dates de l'acte
    # présent figurent AVANT ce connecteur ; ce qui suit cite d'autres instruments.
    cm = CONNECTOR_RE.search(header)
    has_connector = bool(cm)
    primary = header[:cm.start()] if cm else header
    result['has_connector'] = has_connector

    # Ambiguïté : combien de numéros / dates distincts dans TOUT l'en-tête ?
    # (sert de garde-fou : un texte modificatif cite plusieurs numéros/dates)
    _all_nums = re.findall(r'\b\d+[.\-]\d+(?:[.\-]\d+)?\b', header)
    _num_count = len({re.sub(r'[.\s]+', '-', n).strip('-') for n in _all_nums})
    _all_dates_fr = re.findall(
        r'\d{1,2}\s+(?:' + '|'.join(MONTHS_FR.keys()) + r')\s+\d{4}', header, re.IGNORECASE)
    _all_dates_ar = re.findall(
        r'\d{1,2}\s+(?:' + '|'.join(MONTHS_AR.keys()) + r')\s+\d{4}', header)
    _date_count = len(_all_dates_fr) + len(_all_dates_ar)
    result['number_ambiguous'] = has_connector and _num_count >= 2
    result['date_ambiguous']   = has_connector and _date_count >= 2

    # Type formel (ordre de priorité) — sur l'en-tête
    type_patterns = [
        (r'\bDahir\b',      'Dahir'),
        (r'\bظهير\b',       'Dahir'),
        (r'\bLoi organique\b', 'Loi organique'),
        (r'\bقانون تنظيمي\b', 'Loi organique'),
        (r'\bLoi\b',        'Loi'),
        (r'\bقانون\b',      'Loi'),
        (r'\bDécret royal\b', 'Décret royal'),
        (r'\bمرسوم ملكي\b', 'Décret royal'),
        (r'\bDécret\b',     'Décret'),
        (r'\bمرسوم\b',      'Décret'),
        (r'\bArrêté\b',     'Arrêté'),
        (r'\bقرار\b',       'Arrêté'),
        (r'\bCirculaire\b', 'Circulaire'),
        (r'\bمنشور\b',      'Circulaire'),
    ]
    # Type = instrument AGISSANT = 1er mot-clé de type dans le SEGMENT PRIMAIRE
    # (avant tout connecteur). On prend la position la plus précoce ; à position
    # égale, le libellé le plus long (« Loi organique » > « Loi »). Évite d'attraper
    # le type d'un instrument cité ("...en application de la loi n° X" pour un décret,
    # "...promulguée par le dahir..." pour une loi).
    best = None  # ((start, -len), type)
    for pat, typ in type_patterns:
        m = re.search(pat, primary, re.IGNORECASE)
        if m:
            key = (m.start(), -(m.end() - m.start()))
            if best is None or key < best[0]:
                best = (key, typ)
    if best:
        result['formal_type'] = best[1]

    # Numéros extraits du SEGMENT PRIMAIRE (avant tout connecteur) → ignore les
    # numéros des textes modifiés/référencés.
    # Numéro dahir : 1-XX-YYY — casse INSENSIBLE, supporte رقم (arabe) et n° (français)
    dm = re.search(
        r'(?:Dahir|ظهير|الظهير)\s+(?:[shn°]*\s*)?(?:[nN][°o]?\s*|رقم\s*)?([\d]+[\.\-][\d]+[\.\-][\d]+)',
        primary, re.IGNORECASE)
    if dm:
        result['dahir_number'] = re.sub(r'[\.\s]+', '-', dm.group(1)).strip('-')

    # Numéro loi : XX-YYY (supporte قانون رقم)
    lm = re.search(
        r'(?:Loi|قانون|القانون)\s+(?:[nr°]*\s*)?(?:[nN][°o]?\s*|رقم\s*)?([\d]+[\.\-][\d]+)',
        primary, re.IGNORECASE)
    if lm:
        result['law_number'] = re.sub(r'[\.\s]+', '-', lm.group(1)).strip('-')

    # Numéro décret : 2-XX-YYY (supporte مرسوم رقم)
    decm = re.search(
        r'(?:Décret|Decret|مرسوم|المرسوم)\s+(?:[nr°]*\s*)?(?:[nN][°o]?\s*|رقم\s*)?([\d]+[\.\-][\d]+[\.\-][\d]+)',
        primary, re.IGNORECASE)
    if decm:
        result['decree_number'] = re.sub(r'[\.\s]+', '-', decm.group(1)).strip('-')

    # Numéro arrêté : format variable (ex: 2085-25, 1234.20)
    am = re.search(
        r'(?:Arrêté|Arrete|قرار)\s+(?:[a-z°]*\s*)?(?:[nN][°o]?\s*|رقم\s*)?([\d]+[\.\-][\d]+)',
        primary, re.IGNORECASE)
    if am:
        result['arrete_number'] = re.sub(r'[\.\s]+', '-', am.group(1)).strip('-')

    # Date signature FR : "12 mars 2023" — première date du SEGMENT PRIMAIRE
    dm_fr = re.search(
        r'(\d{1,2})\s+(' + '|'.join(MONTHS_FR.keys()) + r')\s+(\d{4})',
        primary, re.IGNORECASE
    )
    if dm_fr:
        d, m, y = dm_fr.group(1), dm_fr.group(2).lower(), dm_fr.group(3)
        month_num = MONTHS_FR.get(m)
        if month_num:
            result['signature_date'] = f'{y}-{month_num:02d}-{int(d):02d}'

    # Date signature AR : "5 ماي 2026"
    if not result['signature_date']:
        dm_ar = re.search(
            r'(\d{1,2})\s+(' + '|'.join(MONTHS_AR.keys()) + r')\s+(\d{4})',
            primary
        )
        if dm_ar:
            d, m, y = dm_ar.group(1), dm_ar.group(2), dm_ar.group(3)
            month_num = MONTHS_AR.get(m)
            if month_num:
                result['signature_date'] = f'{y}-{month_num:02d}-{int(d):02d}'

    # Lignes de titre — en écartant l'en-tête institutionnel (papier à en-tête),
    # les en-têtes de Bulletin Officiel ("N° 6440 – ...") et le corps du texte
    # (formules de promulgation, visas, structure) qui ne sont JAMAIS un titre.
    junk_line = re.compile(
        r'^(?:'
        r'royaume du maroc|المملكة المغربية|minist[èe]re|وزارة|direction|'
        r'secr[ée]tariat|bulletin officiel|الجريدة الرسمية|grand sceau|'
        r'louange à dieu|الحمد لله|\(grand sceau|'
        r'n[°o]\s*\d|'                                   # en-tête BO : "N° 6440 – ..."
        r'textes? g[ée]n[ée]r|نصوص عامة|'                # rubrique "TEXTES GENERAUX"
        r'titre\s+(?:pr[ée]liminaire|premier|[ivx]+)|'   # "TITRE PRÉLIMINAIRE/I/..."
        r'chapitre\s|الباب|الفصل|article\s+(?:premier|\d)|'
        r'que l[\'’]on sache|que l on sache|'            # formule de promulgation
        r'est promulgu|sera publi|'                      # "Est promulguée et sera publiée..."
        r'vu\s+(?:la|le|l[\'’]|les)\s|بناء على|'         # visas
        r'\d{1,4}$'                                       # numéro de page seul
        r')',
        re.IGNORECASE
    )
    # Indicateurs de bruit pouvant apparaître N'IMPORTE OÙ dans la ligne
    # (en-tête de page paginé : "260 BULLETIN OFFICIEL N° 6440 – ...")
    junk_anywhere = re.compile(
        r'bulletin officiel|الجريدة الرسمية|n[°o]\s*\d{3,}',
        re.IGNORECASE
    )

    def _is_junk(l: str) -> bool:
        return bool(junk_line.match(l) or junk_anywhere.search(l))

    lines = [l.strip() for l in header.split('\n')
             if l.strip() and len(l.strip()) > 5 and not _is_junk(l.strip())]
    result['title_lines'] = lines[:6]

    return result


# ── PDF resolution ────────────────────────────────────────────────────────────

def _load_mirror_index() -> dict:
    if MIRROR_INDEX.exists():
        return json.loads(MIRROR_INDEX.read_text(encoding='utf-8'))
    return {}


def _save_mirror_index(index: dict):
    MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    MIRROR_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')


def _safe_filename(law_id: int, slug: str) -> str:
    slug_clean = re.sub(r'[^a-z0-9\-]', '', (slug or '').lower())[:40]
    return f"{law_id}_{slug_clean}.pdf"


PDF_MAGIC = b'%PDF'

FALLBACK_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
]


def _download_to_tmp(url: str) -> tuple[Path | None, str]:
    """
    Télécharge un PDF en fichier temporaire avec validation robuste.
    Retourne (path, raison_echec). path=None si échec.

    Stratégie :
      1. Tentative avec User-Agent standard
      2. Si retour HTML ou trop petit → essai avec 2 UA alternatifs
      3. Vérification magic bytes %PDF (évite les pages de login déguisées)
    """
    last_reason = 'unknown'
    agents = [DOWNLOAD_HEADERS['User-Agent']] + FALLBACK_USER_AGENTS

    for ua in agents:
        try:
            headers = {**DOWNLOAD_HEADERS, 'User-Agent': ua}
            r = requests.get(url, headers=headers, timeout=30, stream=True,
                             allow_redirects=True)

            if r.status_code != 200:
                last_reason = f'HTTP {r.status_code}'
                continue

            # Lire les premiers octets pour validation
            first_chunk = b''
            tmp = Path(tempfile.mktemp(suffix='.pdf'))
            with open(tmp, 'wb') as f:
                for i, chunk in enumerate(r.iter_content(8192)):
                    if i == 0:
                        first_chunk = chunk[:8]
                    f.write(chunk)

            size = tmp.stat().st_size

            # Fichier trop petit = probablement une page d'erreur
            if size < 1000:
                tmp.unlink()
                last_reason = f'trop_petit ({size}B)'
                continue

            # Vérification magic bytes %PDF — écarte les pages HTML retournées en 200
            if not first_chunk.startswith(PDF_MAGIC):
                tmp.unlink()
                ct = r.headers.get('Content-Type', '')
                last_reason = f'pas_un_pdf (Content-Type={ct[:40]!r}, magic={first_chunk[:8]!r})'
                continue

            return tmp, 'ok'

        except requests.exceptions.Timeout:
            last_reason = 'timeout'
        except requests.exceptions.ConnectionError as e:
            last_reason = f'connexion: {str(e)[:60]}'
        except Exception as e:
            last_reason = str(e)[:80]

    return None, last_reason


def resolve_pdf(law: dict, mirror_index: dict) -> tuple[Path | None, str]:
    """
    Résout le PDF source — TOUJOURS prioritaire sur le contenu DB.

    Ordre :
      1. Cache local (mirror_index) — déjà téléchargé
      2. pdf_url (Supabase Storage) → téléchargé ET sauvegardé localement
      3. source_url (externe, fallback User-Agents) → téléchargé ET sauvegardé localement

    Les PDFs téléchargés sont PERSISTÉS dans pipeline/pdfs/mirror/ (backup local
    + cache pour les runs suivants). Aucun upload vers Supabase.

    Retourne (path, source_label).
    """
    id_str = str(law['id'])
    slug   = law.get('canonical_slug') or ''

    # 1. Cache local
    if id_str in mirror_index:
        p = Path(mirror_index[id_str])
        if p.exists():
            return p, 'local_mirror'

    # 2+3. Télécharger depuis pdf_url puis source_url, persister localement
    last_reason = 'no_url'
    for url, label in [(law.get('pdf_url'), 'supabase_storage'),
                       (law.get('source_url'), 'external_source')]:
        if not url:
            continue
        tmp, reason = _download_to_tmp(url)
        if not tmp:
            last_reason = reason
            continue
        # Persister dans le mirror local (backup + cache)
        try:
            MIRROR_DIR.mkdir(parents=True, exist_ok=True)
            dest = MIRROR_DIR / _safe_filename(law['id'], slug)
            shutil.move(str(tmp), str(dest))
            mirror_index[id_str] = str(dest)
            _save_mirror_index(mirror_index)
            return dest, label
        except Exception:
            # Si la persistance échoue, utiliser le tmp tel quel
            return tmp, label

    return None, f'no_pdf:{last_reason}'


# ── Text extraction ──────────────────────────────────────────────────────────

def _legal_pattern_found(text: str) -> bool:
    """Retourne True si le texte contient au moins un pattern juridique exploitable.
    Couvre : FR (Dahir/Loi/Décret/Arrêté), AR avec et sans article défini (ظهير/الظهير...),
    majuscules BO (DAHIR/LOI), et chiffres arabes orientaux normalisés."""
    normalized = text.translate(_AR_DIGITS)
    return bool(re.search(
        r'(?:'
        r'Dahir|DAHIR'
        r'|ظهير|الظهير'
        r'|Loi(?:\s+organique)?|LOI'
        r'|قانون|القانون|قانون\s+تنظيمي'
        r'|Décret|DÉCRET|Decret'
        r'|مرسوم|المرسوم'
        r'|Arrêté|ARRÊTÉ|Arrete'
        r'|قرار|القرار'
        r'|Circulaire|منشور'
        r'|ن°\s*\d|رقم\s+\d'        # "n° X" arabe ou "رقم X"
        r')',
        normalized, re.IGNORECASE | re.UNICODE
    ))


def extract_first_pages(pdf_path: Path, max_pages: int = 5) -> str:
    """
    Extrait le texte des premières pages d'un PDF.

    Stratégie adaptative :
      - Essai pages 1-3 avec pdfplumber
      - Si patterns absents → étend à pages 1-5
      - Fallback PyMuPDF si pdfplumber vide
    """
    def _read_plumber(n: int) -> str:
        if not PDFPLUMBER_OK:
            return ''
        try:
            with pdfplumber.open(pdf_path) as pdf:
                parts = []
                for p in pdf.pages[:n]:
                    # layout=True préserve l'ordre spatial (crucial pour l'arabe RTL
                    # et les mises en page en colonnes des BO). x_tolerance bas =
                    # meilleure séparation des mots collés.
                    try:
                        t = p.extract_text(layout=True, x_tolerance=1.5, y_tolerance=3) or ''
                    except Exception:
                        t = p.extract_text() or ''
                    parts.append(t)
                return '\n\n'.join(parts).strip()
        except Exception:
            return ''

    def _read_fitz(n: int) -> str:
        if not FITZ_OK:
            return ''
        try:
            doc = fitz.open(str(pdf_path))
            # sort=True réordonne les blocs en ordre de lecture naturel
            # (haut→bas, gauche→droite) au lieu de l'ordre interne du PDF,
            # souvent aléatoire pour les documents arabes / scannés vectorisés.
            parts = [doc[i].get_text('text', sort=True) for i in range(min(n, len(doc)))]
            doc.close()
            return '\n\n'.join(parts).strip()
        except Exception:
            return ''

    # 1. pdfplumber 3 pages
    text = _read_plumber(3)

    # 2. Si pdfplumber insuffisant → PyMuPDF 3 pages
    if len(text) < 100:
        text = _read_fitz(3)

    # 3. Si patterns juridiques absents après 3 pages → élargir à 5
    if text and not _legal_pattern_found(text):
        extended = _read_plumber(max_pages) or _read_fitz(max_pages)
        if _legal_pattern_found(extended):
            text = extended

    return text


# Compteurs OCR pour le rapport final
_OCR_STATS = {'attempts': 0, 'success': 0, 'failures': 0, 'cache_hits': 0}

# Cache disque des transcriptions OCR (clé = nom du PDF dans le mirror).
# Évite de refaire les appels API à chaque run : un run interrompu accumule
# le cache, le run suivant relit tout instantanément et peut terminer l'export.
OCR_CACHE_FILE = MIRROR_DIR / 'ocr_cache.json'


def _load_ocr_cache() -> dict:
    try:
        if OCR_CACHE_FILE.exists():
            return json.loads(OCR_CACHE_FILE.read_text(encoding='utf-8'))
    except Exception:
        pass
    return {}


def _save_ocr_cache(cache: dict) -> None:
    try:
        MIRROR_DIR.mkdir(parents=True, exist_ok=True)
        OCR_CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')
    except Exception:
        pass


_OCR_CACHE = _load_ocr_cache()


def gemini_vision_ocr(pdf_path: Path, max_pages: int = 2) -> str:
    """
    OCR via modèle vision (Gemini multimodal sur OpenRouter) — pour PDFs scannés
    ou à police non embarquée où l'extraction texte échoue.

    Rend les premières pages en images PNG (200 dpi) et demande au modèle de
    transcrire fidèlement le texte. Lit l'arabe nativement, aucun binaire local.
    Résultats mis en cache disque (clé = nom du PDF) → relances instantanées.

    Retourne le texte transcrit, ou '' en cas d'échec / si désactivé.
    """
    if not (USE_VISION_OCR and FITZ_OK and OPENROUTER_KEY):
        return ''

    # Cache hit : transcription déjà obtenue lors d'un run précédent
    cache_key = pdf_path.name
    if cache_key in _OCR_CACHE:
        _OCR_STATS['cache_hits'] += 1
        return _OCR_CACHE[cache_key]

    import base64
    _OCR_STATS['attempts'] += 1
    try:
        doc = fitz.open(str(pdf_path))
        content: list[dict] = [{'type': 'text', 'text': OCR_PROMPT}]
        n = min(max_pages, len(doc))
        for i in range(n):
            pix = doc[i].get_pixmap(dpi=200)
            b64 = base64.b64encode(pix.tobytes('png')).decode()
            content.append({
                'type': 'image_url',
                'image_url': {'url': f'data:image/png;base64,{b64}'},
            })
        doc.close()

        r = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENROUTER_KEY}',
                'Content-Type':  'application/json',
            },
            json={
                'model':       OCR_VISION_MODEL,
                'messages':    [{'role': 'user', 'content': content}],
                'max_tokens':  2500,
                'temperature': 0,
            },
            timeout=120,
        )
        if not r.ok:
            _OCR_STATS['failures'] += 1
            print(f'         ✗ OCR Vision HTTP {r.status_code}: {r.text[:120]}', flush=True)
            return ''
        out = (r.json()['choices'][0]['message']['content'] or '').strip()
        if out:
            _OCR_STATS['success'] += 1
            _OCR_CACHE[cache_key] = out
            _save_ocr_cache(_OCR_CACHE)   # persister immédiatement (résilient aux interruptions)
        return out
    except Exception as e:
        _OCR_STATS['failures'] += 1
        print(f'         ✗ OCR Vision erreur: {e}', flush=True)
        return ''


def resolve_text_source(law: dict, pdf_path: Path | None) -> tuple[str, str]:
    """
    Choisit la source de texte pour l'audit. Le PDF source FAIT FOI
    (Règle 5/6 du pipeline) — il est toujours prioritaire sur le contenu DB,
    car content_fr a été produit par la même IA qui a pu introduire l'erreur
    qu'on cherche à détecter (et peut provenir d'un PDF croisé/erroné).

    Ordre :
      1. Extraction fraîche depuis le PDF source (référence indépendante)
      2. content_fr en base — UNIQUEMENT en dernier recours, signalé comme
         non fiable (l'audit n'a pas pu valider contre le document officiel)

    Retourne (texte, source_label).
    """
    # Priorité 1 : le PDF source fait foi
    if pdf_path:
        text = extract_first_pages(pdf_path, max_pages=6)
        if _legal_pattern_found(text):
            return text, 'pdf_extracted'

        # Extraction texte faible/illisible (scanné, police non embarquée, CID) :
        # tenter l'OCR Vision avant de dégrader vers content_fr.
        ocr_text = gemini_vision_ocr(pdf_path, max_pages=2)
        if ocr_text and _legal_pattern_found(ocr_text):
            return ocr_text, 'pdf_ocr_vision'
        # Garder le meilleur des deux pour un éventuel fallback "weak"
        if ocr_text and len(ocr_text) > len(text):
            text = ocr_text

        if len(text) > 200:
            # PDF lu mais patterns juridiques faibles (OCR n'a pas aidé non plus)
            return text, 'pdf_extracted_weak'

    # Priorité 2 (dernier recours) : content_fr — NON validé contre le PDF
    content_fr = (law.get('content_fr') or '').strip()
    if content_fr:
        return content_fr[:5000], 'db_content_fallback'

    return '', 'no_text'


# ── Canonical record builder ──────────────────────────────────────────────────

def build_canonical_record(law: dict, page1_text: str, pdf_source: str) -> CanonicalRecord:
    parsed = _extract_from_page1(page1_text)
    cr = CanonicalRecord(law_id=law['id'])
    cr.first_page_text = page1_text[:500]
    # pdf_resolved = True UNIQUEMENT si le texte vient réellement du PDF source
    cr.pdf_resolved = pdf_source in ('pdf_extracted', 'pdf_extracted_weak', 'pdf_ocr_vision')
    cr.source_priority = pdf_source
    cr.formal_instrument_type = parsed['formal_type'] or law.get('type')
    cr.dahir_number  = parsed['dahir_number']
    cr.law_number    = parsed['law_number']
    cr.decree_number = parsed['decree_number']
    cr.arrete_number = parsed['arrete_number']
    cr.signature_date = parsed['signature_date']
    cr.number_ambiguous = parsed['number_ambiguous']
    cr.date_ambiguous   = parsed['date_ambiguous']

    # Numéro officiel : préférer le numéro de l'instrument correspondant au TYPE
    # en base. La cascade type-agnostique précédente prenait le numéro de la loi
    # référencée (ex: "en application de la loi n° 98-15") pour un Décret.
    db_type = (law.get('type') or '').lower()
    if 'dahir' in db_type and parsed['dahir_number']:
        cr.official_number = parsed['dahir_number']
    elif ('décret' in db_type or 'decret' in db_type) and parsed['decree_number']:
        cr.official_number = parsed['decree_number']
    elif ('arrêté' in db_type or 'arrete' in db_type) and (parsed['arrete_number'] or parsed['law_number']):
        cr.official_number = parsed['arrete_number'] or parsed['law_number']
    elif 'loi' in db_type and parsed['law_number']:
        cr.official_number = parsed['law_number']
    else:
        # Type inconnu / non trouvé : premier numéro disponible (dahir→décret→loi→arrêté)
        cr.official_number = (parsed['dahir_number'] or parsed['decree_number']
                              or parsed['law_number'] or parsed['arrete_number'])

    # Titre officiel : préférer la ligne qui porte le type juridique (Dahir/Loi/...)
    type_kw = re.compile(
        r'\b(dahir|ظهير|loi|قانون|décret|مرسوم|arrêté|قرار|circulaire|منشور)\b',
        re.IGNORECASE
    )
    title_lines = parsed['title_lines']
    chosen = None
    # On n'accepte comme titre QU'UNE ligne portant un mot-clé d'instrument
    # juridique (Dahir/Loi/Décret/Arrêté…). Sans ce signal fort, on ne propose
    # PAS de correction de titre : une ligne quelconque (en-tête BO, corps de
    # texte, visa) produirait une fausse correction qui écraserait un titre
    # correct. Mieux vaut une correction manquée qu'une correction nuisible.
    for line in title_lines:
        if len(line) > 20 and type_kw.search(line):
            chosen = line
            break
    # Cas titre composite sur 2 lignes : "Dahir n° ... portant" + "promulgation
    # de la loi n° ... relative à ..." → concaténer la ligne suivante si la
    # première se termine par un mot de liaison.
    if chosen and re.search(r'\b(portant|fixant|relatif|relative|modifiant|'
                            r'compl[ée]tant|instituant|approuvant)\s*$',
                            chosen, re.IGNORECASE):
        idx = title_lines.index(chosen)
        if idx + 1 < len(title_lines):
            chosen = (chosen + ' ' + title_lines[idx + 1]).strip()
    if chosen:
        cr.official_title_fr = chosen[:200]

    # Supprimer les titres inutilisables : arabe (PDF en arabe ≠ title_fr français)
    # ou encodage CID corrompu (police non embarquée → texte illisible)
    if cr.official_title_fr and _is_primarily_arabic(cr.official_title_fr):
        cr.official_title_fr = None
    if cr.official_title_fr and _CID_RE.search(cr.official_title_fr):
        cr.official_title_fr = None

    return cr


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_and_flag(law: dict, cr: CanonicalRecord) -> tuple[int, list[AuditFlag]]:
    score = 100
    flags: list[AuditFlag] = []

    def add(code, sev, fld, detail, penalty):
        nonlocal score
        flags.append(AuditFlag(code=code, severity=sev, field=fld, detail=detail))
        score -= penalty

    # Source texte
    has_text = len(cr.first_page_text) >= 100
    text_from_db = cr.source_priority == 'db_content_fallback'

    # PDF source totalement absent
    if cr.source_priority.startswith('no'):
        add('source_pdf_missing', 'warning', 'pdf_url', 'Aucun PDF source exploitable', 20)

    # Audité sans le PDF officiel → non fiable (jamais auto_update)
    if text_from_db:
        add('audited_without_source_pdf', 'warning', 'pdf_url',
            'PDF source indisponible — audité contre content_fr (non validé)', 20)

    # PDF lu mais OCR/patterns faibles
    if cr.source_priority == 'pdf_extracted_weak':
        add('pdf_extraction_weak', 'warning', 'content_fr',
            'PDF lu mais patterns juridiques faibles (scanné/OCR partiel?)', 10)

    # Texte obtenu par OCR Vision (PDF scanné) — fiable mais signalé pour relecture
    # car l'OCR peut mal lire un chiffre. Léger malus pour rester en "review".
    if cr.source_priority == 'pdf_ocr_vision':
        add('pdf_text_from_ocr', 'info', 'content_fr',
            'Texte extrait par OCR Vision (PDF scanné) — vérifier les numéros/dates', 5)

    # Texte extrait insuffisant
    if not has_text:
        add('low_extraction_text', 'warning', 'content_fr', f'Texte source < 100 chars ({len(cr.first_page_text)})', 15)

    if has_text:
        db_type   = (law.get('type') or '').lower()
        db_number = (law.get('number') or '').strip()
        db_date   = law.get('date') or ''
        db_title  = (law.get('title_fr') or '').strip()

        # Mismatch type
        pdf_type = (cr.formal_instrument_type or '').lower()
        if pdf_type and db_type and pdf_type not in db_type and db_type not in pdf_type:
            add('type_mismatch_pdf_vs_record', 'critical', 'type',
                f'PDF={cr.formal_instrument_type!r} vs DB={law.get("type")!r}', 25)

        # Confusion dahir/loi
        if cr.dahir_number and cr.law_number:
            norm_db = re.sub(r'[^0-9]', '-', db_number).strip('-')
            norm_dahir = re.sub(r'[^0-9]', '-', cr.dahir_number).strip('-')
            if norm_db == norm_dahir and 'loi' in db_type and 'dahir' not in db_type:
                add('law_number_dahir_number_confused', 'critical', 'number',
                    f'DB stocke le numéro dahir {cr.dahir_number!r} comme numéro de loi', 25)

        # Mismatch numéro
        if cr.official_number and db_number:
            norm_off = re.sub(r'[^0-9]', '-', cr.official_number).strip('-')
            norm_db2 = re.sub(r'[^0-9]', '-', db_number).strip('-')
            # Tolérance : l'un contient l'autre (numéros partiels)
            if norm_off and norm_db2 and norm_off not in norm_db2 and norm_db2 not in norm_off:
                if cr.number_ambiguous:
                    # Texte modificatif citant plusieurs numéros : signaler sans
                    # proposer (build_diffs supprime le diff). Pas de malus lourd.
                    add('number_needs_manual_check', 'info', 'number',
                        f'Plusieurs numéros dans l\'en-tête — à vérifier manuellement '
                        f'(candidat PDF={cr.official_number!r} vs DB={db_number!r})', 5)
                else:
                    add('number_mismatch_pdf_vs_record', 'critical', 'number',
                        f'PDF={cr.official_number!r} vs DB={db_number!r}', 30)

        # Mismatch date (tolérance ±1 an)
        if cr.signature_date and db_date and len(db_date) >= 4:
            pdf_year = int(cr.signature_date[:4])
            db_year  = int(db_date[:4])
            if abs(pdf_year - db_year) > 1:
                if cr.date_ambiguous:
                    add('date_needs_manual_check', 'info', 'date',
                        f'Plusieurs dates dans l\'en-tête — à vérifier manuellement '
                        f'(candidat PDF={cr.signature_date!r} vs DB={db_date!r})', 3)
                else:
                    add('date_mismatch_pdf_vs_record', 'warning', 'date',
                        f'PDF={cr.signature_date!r} vs DB={db_date!r}', 15)

        # Mismatch titre (heuristique : moins de 50% de mots communs)
        if cr.official_title_fr and db_title and len(db_title) > 10:
            def _words(t):
                t = re.sub(r'[^a-zA-ZÀ-ÿ\s]', ' ', t.lower())
                return set(w for w in t.split() if len(w) > 4)
            w_pdf = _words(cr.official_title_fr)
            w_db  = _words(db_title)
            if w_pdf and w_db:
                overlap = len(w_pdf & w_db) / max(len(w_pdf | w_db), 1)
                if overlap < 0.25:
                    add('title_mismatch_pdf_vs_record', 'critical', 'title_fr',
                        f'Peu de mots communs ({overlap:.0%}) entre PDF et DB', 25)

    # Metadata_only public
    if law.get('extraction_status') == 'metadata_only' and law.get('is_publicly_indexable'):
        add('metadata_only_public', 'warning', 'extraction_status',
            'Texte public avec extraction_status=metadata_only', 10)

    # Indexable avec score bas
    gcs = law.get('global_confidence_score')
    if gcs is not None and gcs < 40 and law.get('is_publicly_indexable'):
        add('public_indexing_too_risky', 'blocking', 'is_publicly_indexable',
            f'global_confidence_score={gcs} mais is_publicly_indexable=true', 20)

    # Bonus : source officielle
    src = (law.get('source_name') or '').lower()
    if any(s in src for s in ('sgg', 'bo', 'bulletin')):
        score = min(100, score + 10)

    return max(0, score), flags


def make_decision(score: int, flags: list[AuditFlag]) -> tuple[str, bool]:
    has_critical = any(f.severity in ('critical', 'blocking') for f in flags)
    has_blocking = any(f.severity == 'blocking' for f in flags)
    # Garde-fou : un record non validé contre le PDF source ne peut JAMAIS
    # être auto_update — on n'a pas confronté la métadonnée au document officiel.
    not_pdf_validated = any(
        f.code in ('audited_without_source_pdf', 'source_pdf_missing',
                   'pdf_extraction_weak', 'pdf_text_from_ocr')
        for f in flags
    )

    if has_blocking or score < 50:
        return 'block', False
    if has_critical or score < 75:
        return 'review_high_priority', False
    if score < 90 or not_pdf_validated:
        return 'review', False
    return 'auto_update', True


# ── Diff builder ──────────────────────────────────────────────────────────────

def _same_title_ignoring_case(a: str, b: str) -> bool:
    """True si deux titres sont identiques à la casse/espaces/ponctuation près."""
    def _norm(t):
        t = re.sub(r'[^a-zA-ZÀ-ÿ0-9]', ' ', (t or '').lower())
        return re.sub(r'\s+', ' ', t).strip()
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return False
    # Identiques, ou l'un contenu dans l'autre (titre DB plus complet)
    return na == nb or na in nb or nb in na


def build_diffs(law: dict, cr: CanonicalRecord) -> list[DiffItem]:
    diffs = []
    comparisons = [
        ('type',     cr.formal_instrument_type, 'critical'),
        ('number',   cr.official_number,        'critical'),
        ('date',     cr.signature_date,         'warning'),
        ('title_fr', cr.official_title_fr,      'warning'),
    ]
    for field, proposed, sev in comparisons:
        current = (law.get(field) or '').strip()
        if not proposed or proposed == current:
            continue
        # Garde-fou anti-fausse-correction : sur un texte modificatif/d'application
        # citant plusieurs numéros/dates, ne PAS proposer de valeur concrète (elle
        # pourrait venir d'un instrument tiers). L'ambiguïté est signalée par un
        # flag info dans score_and_flag ; aucune correction erronée à approuver.
        if field == 'number' and cr.number_ambiguous:
            continue
        if field == 'date' and cr.date_ambiguous:
            continue
        # Titre : ne pas proposer si c'est le même titre (casse/ponctuation près).
        # Le titre en base, souvent en casse propre, vaut mieux que la version PDF MAJUSCULES.
        if field == 'title_fr' and _same_title_ignoring_case(proposed, current):
            continue
        diffs.append(DiffItem(
            field=field,
            current_value=current or None,
            proposed_value=proposed,
            severity=sev,
            action='review' if sev == 'critical' else 'check',
        ))
    return diffs


# ── Supabase fetch ────────────────────────────────────────────────────────────

FIELDS = ','.join([
    'id', 'number', 'type', 'date', 'title_fr', 'title_ar',
    'pdf_url', 'source_url', 'source_name', 'canonical_slug',
    'extraction_status', 'extraction_confidence_score',
    'global_confidence_score', 'needs_human_review',
    'is_publicly_indexable', 'verification_status',
    'simple_summary_fr', 'content_fr',
])


def fetch_records(args) -> list[dict]:
    if args.id:
        r = requests.get(f'{SUPABASE_URL}/rest/v1/laws', headers=SB, params={
            'select': FIELDS, 'id': f'eq.{args.id}',
        })
        r.raise_for_status()
        return r.json()

    params: dict = {
        'select': FIELDS,
        'is_publicly_indexable': 'eq.true',
        'order': 'id.asc',
        'limit': str(min(args.limit, 200)),
    }
    if args.source:
        params['source_name'] = f'eq.{args.source}'
    if args.low_score:
        params['global_confidence_score'] = 'lt.70'

    r = requests.get(f'{SUPABASE_URL}/rest/v1/laws', headers=SB, params=params)
    r.raise_for_status()
    return r.json()


# ── Mode RECORD : audit PDF↔métadonnées, record par record ────────────────────

def mode_record(args):
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    mirror_index = _load_mirror_index()

    print('Chargement des records...', flush=True)
    laws = fetch_records(args)
    print(f'{len(laws)} records chargés\n', flush=True)

    results: list[AuditResult] = []

    for i, law in enumerate(laws):
        id_ = law['id']
        title = (law.get('title_fr') or '')[:60]
        print(f'[{i+1:>3}/{len(laws)}] id={id_:>6}  {title}', flush=True)

        # 1. Résoudre le PDF source EN PRIORITÉ (le PDF fait foi)
        pdf_path, pdf_src = resolve_pdf(law, mirror_index)
        # Les PDFs persistés dans le mirror ne sont PAS supprimés (backup local)

        # 2. Choisir la source de texte (PDF d'abord, content_fr en dernier recours)
        page1_text, text_src = resolve_text_source(law, pdf_path)

        if text_src == 'pdf_extracted':
            print(f'         ✓ PDF={pdf_src}  texte extrait={len(page1_text):,} chars', flush=True)
        elif text_src == 'pdf_ocr_vision':
            print(f'         ✓ PDF={pdf_src}  OCR Vision réussi={len(page1_text):,} chars (scanné)', flush=True)
        elif text_src == 'pdf_extracted_weak':
            print(f'         ~ PDF={pdf_src} lu mais patterns faibles ({len(page1_text):,} chars) — OCR insuffisant', flush=True)
        elif text_src == 'db_content_fallback':
            reason = pdf_src.replace('no_pdf:', '') if pdf_src.startswith('no_pdf') else pdf_src
            print(f'         ⚠ PDF indisponible ({reason}) → content_fr en fallback (NON validé)', flush=True)
        else:
            reason = pdf_src.replace('no_pdf:', '') if pdf_src.startswith('no_pdf') else 'no_text'
            print(f'         ⚠ Aucun texte disponible ({reason})', flush=True)

        # 3. Construire canonical record
        cr = build_canonical_record(law, page1_text, text_src)

        # 4. Scorer + flags
        score, flags = score_and_flag(law, cr)
        cr.canonical_confidence_score = score
        cr.flags = flags

        # 5. Décision
        decision, safe = make_decision(score, flags)
        cr.canonical_validation_status = decision

        # 6. Diffs
        diffs = build_diffs(law, cr)

        result = AuditResult(
            law_id=id_,
            score=score,
            decision=decision,
            flags=flags,
            diffs=diffs,
            safe_to_auto_update=safe,
            canonical=cr,
        )
        results.append(result)

        # Affichage résumé
        flag_codes = [f.code for f in flags]
        print(f'         score={score}  decision={decision}  flags={flag_codes}')
        for d in diffs:
            print(f'           diff [{d.severity}] {d.field}: {str(d.current_value)[:40]!r} → {str(d.proposed_value)[:40]!r}')

        time.sleep(0.1)

    # Les PDFs téléchargés sont conservés dans pipeline/pdfs/mirror/ (backup local)

    # ── Rapport console ───────────────────────────────────────────────────────
    by_decision = {}
    for r in results:
        by_decision.setdefault(r.decision, []).append(r)

    print(f'\n{"═"*70}')
    print(f'  Records audités       : {len(results)}')
    for dec, lst in sorted(by_decision.items()):
        print(f'  {dec:30} : {len(lst)}')
    n_pdf_audited = sum(1 for r in results if r.canonical.pdf_resolved)
    n_no_pdf      = sum(1 for r in results if any(f.code == 'source_pdf_missing' for f in r.flags))
    n_db_fallback = sum(1 for r in results if any(f.code == 'audited_without_source_pdf' for f in r.flags))
    n_critical    = sum(1 for r in results if any(f.severity == 'critical' for f in r.flags))
    n_ocr = sum(1 for r in results if any(f.code == 'pdf_text_from_ocr' for f in r.flags))
    print(f'  ── Source de l\'audit ──')
    print(f'  Validés via PDF source : {n_pdf_audited}')
    print(f'  dont OCR Vision        : {n_ocr}  (PDFs scannés récupérés)')
    print(f'  Fallback content_fr    : {n_db_fallback}  (non validés contre PDF)')
    print(f'  Aucun PDF ni contenu   : {n_no_pdf}')
    print(f'  Flags critiques        : {n_critical}')
    if _OCR_STATS['attempts'] or _OCR_STATS['cache_hits']:
        print(f'  ── OCR Vision ──')
        print(f'  Appels API={_OCR_STATS["attempts"]}  réussites={_OCR_STATS["success"]}  '
              f'échecs={_OCR_STATS["failures"]}  cache={_OCR_STATS["cache_hits"]}')
    print(f'{"═"*70}')

    # ── Export vers Supabase ──────────────────────────────────────────────────
    if getattr(args, 'export_to_db', False):
        laws_by_id = {law['id']: law for law in laws}
        export_to_db(results, laws_by_id)

    if not args.export:
        return

    # ── Export local CSV/JSON ─────────────────────────────────────────────────
    # Résumé JSON
    summary = {
        'total': len(results),
        'by_decision': {k: len(v) for k, v in by_decision.items()},
        'validated_via_pdf': n_pdf_audited,
        'fallback_content_fr': n_db_fallback,
        'no_pdf': n_no_pdf,
        'critical_flags': n_critical,
    }
    (AUDIT_DIR / 'audit_summary.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8'
    )

    # Records à revoir (CSV)
    review_rows = [r for r in results if r.decision in ('review_high_priority', 'block')]
    if review_rows:
        with open(AUDIT_DIR / 'records_to_review.csv', 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(['id', 'score', 'decision', 'flags', 'diffs'])
            for r in review_rows:
                w.writerow([
                    r.law_id, r.score, r.decision,
                    ';'.join(f.code for f in r.flags),
                    ';'.join(f'{d.field}:{d.current_value}→{d.proposed_value}' for d in r.diffs),
                ])

    # Issues bloquantes (CSV)
    blocking = [r for r in results if r.decision == 'block']
    if blocking:
        with open(AUDIT_DIR / 'blocking_issues.csv', 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(['id', 'score', 'flags'])
            for r in blocking:
                w.writerow([r.law_id, r.score, ';'.join(f.code for f in r.flags)])

    # Patches sûrs (JSON) — score >= 95 sans flag critique
    safe_patches = []
    for r in results:
        if r.safe_to_auto_update and r.score >= 95 and r.diffs:
            patch = {'id': r.law_id}
            for d in r.diffs:
                if d.severity != 'critical':
                    patch[d.field] = d.proposed_value
            if len(patch) > 1:
                safe_patches.append(patch)

    (AUDIT_DIR / 'safe_patches_preview.json').write_text(
        json.dumps(safe_patches, ensure_ascii=False, indent=2), encoding='utf-8'
    )

    print(f'\nRapports exportés → {AUDIT_DIR}/')
    print(f'  audit_summary.json        : {len(results)} records')
    print(f'  records_to_review.csv     : {len(review_rows)} records')
    print(f'  blocking_issues.csv       : {len(blocking)} records')
    print(f'  safe_patches_preview.json : {len(safe_patches)} patches')


# ── Export vers Supabase audit_queue ─────────────────────────────────────────

def export_to_db(results: list[AuditResult], laws_by_id: dict) -> None:
    """Écrit les diffs dans la table audit_queue Supabase pour validation via Admin."""
    law_ids_with_diffs = [r.law_id for r in results if r.diffs]
    if not law_ids_with_diffs:
        print('  → Aucun diff à exporter.')
        return

    # Supprimer les entrées "pending" existantes pour ces law_ids (évite doublons si re-run)
    ids_str = ','.join(str(i) for i in law_ids_with_diffs)
    try:
        requests.delete(
            f'{SUPABASE_URL}/rest/v1/audit_queue',
            headers={**SB, 'Prefer': ''},
            params={'law_id': f'in.({ids_str})', 'status': 'eq.pending'},
            timeout=15,
        )
    except Exception as e:
        print(f'  ⚠ Nettoyage audit_queue : {e}')

    rows = []
    for r in results:
        if not r.diffs:
            continue
        law = laws_by_id.get(r.law_id, {})
        for diff in r.diffs:
            rows.append({
                'law_id':    r.law_id,
                'law_title': (law.get('title_fr') or '')[:120],
                'law_number': law.get('number'),
                'field':      diff.field,
                'current_val': str(diff.current_value or '')[:300],
                'proposed':    str(diff.proposed_value or '')[:300],
                'severity':   diff.severity,
                'decision':   r.decision,
                'score':      r.score,
                'flags':      [f.code for f in r.flags],
                'pdf_source': r.canonical.source_priority,
            })

    if not rows:
        print('  → Aucun diff à exporter.')
        return

    resp = requests.post(
        f'{SUPABASE_URL}/rest/v1/audit_queue',
        headers={**SB, 'Content-Type': 'application/json', 'Prefer': 'return=minimal'},
        json=rows,
        timeout=30,
    )
    if resp.status_code in (200, 201):
        print(f'  ✅ {len(rows)} corrections exportées → Supabase audit_queue')
        print(f'     Admin → onglet "Corrections" pour valider')
    else:
        print(f'  ❌ Export échoué ({resp.status_code}): {resp.text[:200]}')


# ── Mode MIRROR : backup local des PDFs (absorbe mirror_external_pdfs.py) ──────

def mode_mirror(args):
    """Télécharge et persiste localement les PDFs (pdf_url puis source_url)."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    mirror_index = _load_mirror_index()

    print('Chargement des records à mirorer...', flush=True)
    # Cibler en priorité les records avec une source PDF mais pas encore en cache
    laws = fetch_records(args)
    print(f'{len(laws)} records chargés\n', flush=True)

    already = downloaded = failed = no_url = 0
    for i, law in enumerate(laws):
        id_ = law['id']
        id_str = str(id_)
        title = (law.get('title_fr') or '')[:55]

        if id_str in mirror_index and Path(mirror_index[id_str]).exists():
            already += 1
            continue
        if not (law.get('pdf_url') or law.get('source_url')):
            no_url += 1
            continue

        print(f'[{i+1:>4}/{len(laws)}] id={id_:>6}  {title}', flush=True)
        # resolve_pdf télécharge ET persiste dans le mirror + met à jour l'index
        pdf_path, pdf_src = resolve_pdf(law, mirror_index)
        if pdf_path:
            downloaded += 1
            print(f'         ✅ {pdf_src} → {pdf_path.name}', flush=True)
        else:
            failed += 1
            reason = pdf_src.replace('no_pdf:', '')
            print(f'         ❌ {reason}', flush=True)
        time.sleep(0.3)  # politesse serveur

    print(f'\n{"═"*60}')
    print(f'  Déjà en cache     : {already}')
    print(f'  Téléchargés       : {downloaded}')
    print(f'  Échecs            : {failed}')
    print(f'  Sans URL          : {no_url}')
    print(f'  Index local       : {MIRROR_INDEX}')
    print(f'{"═"*60}')


# ── Mode DUPLICATES : détection croisée par pdf_url ───────────────────────────

def _norm_pdf_url(url: str | None) -> str | None:
    """Normalise une URL de PDF pour comparer (retire query string, casse)."""
    if not url:
        return None
    u = url.strip().lower()
    u = u.split('?')[0].split('#')[0]
    return u or None


GENERIC_NUMBERS = {'dahir', 'loi', 'décret', 'decret', 'arrêté', 'arrete',
                   'texte', 'circulaire', 'n/a', 'na', ''}


def _number_is_clean(num: str | None) -> bool:
    """True si le numéro ressemble à un vrai numéro marocain (X-YY-ZZZ ou XX-YY)."""
    n = (num or '').strip()
    if not n or n.lower() in GENERIC_NUMBERS:
        return False
    if re.search(r'[؀-ۿ]', n):       # contient de l'arabe = champ pollué
        return False
    return bool(re.match(r'^\d+[.\-]\d+([.\-]\d+)?$', n))


def _metadata_broken(law: dict) -> bool:
    """True si les métadonnées du record sont visiblement cassées (à corriger via PDF)."""
    num = (law.get('number') or '')
    title = (law.get('title_fr') or '').strip().lower()
    if re.search(r'[؀-ۿ]', num):                 # arabe dans le numéro
        return True
    if num.strip().lower() in GENERIC_NUMBERS:             # numéro générique
        return True
    if not law.get('date'):                                # date manquante
        return True
    if title.startswith('texte n'):                        # titre placeholder
        return True
    return False


def _record_quality(law: dict) -> float:
    """Score de qualité d'un record pour choisir le survivant d'un doublon."""
    score = 0.0
    ct = len((law.get('content_fr') or '').strip())
    score += min(ct, 30000) / 1000.0          # contenu : jusqu'à 30 pts (signal fort)
    if _number_is_clean(law.get('number')):
        score += 10                            # vrai numéro propre
    elif law.get('number') and not re.search(r'[؀-ۿ]', law.get('number')):
        score += 2                             # numéro présent mais imparfait
    if law.get('date'):
        score += 5
    score += min(len(law.get('simple_summary_fr') or ''), 2000) / 1000.0
    if law.get('is_publicly_indexable'):
        score += 1                             # léger biais : ne pas casser l'existant
    return score


def _choose_survivor(rows: list[dict]) -> tuple[dict, list[dict]]:
    """Choisit le record à garder dans un groupe de doublons + la liste à masquer."""
    ranked = sorted(rows, key=lambda l: (_record_quality(l), -l['id']), reverse=True)
    keep = ranked[0]
    drop = [r for r in rows if r['id'] != keep['id']]
    return keep, drop


def mode_duplicates(args):
    """
    2e couche : groupe les records par pdf_url normalisé et décide, pour chaque
    groupe, lequel GARDER (et rendre public) et lesquels MASQUER.

    Le PDF est l'unité de record : 1 PDF distinct = 1 record légitime.
    Sélection du survivant : contenu > numéro propre > date > résumé > déjà public.
    Le survivant est toujours rendu public ; les autres masqués.
    Si les métadonnées du survivant sont cassées → flag 'corriger-méta' (lire le PDF
    via --mode record).

    Dry-run par défaut. --apply applique UNIQUEMENT les changements de visibilité
    (réversibles) ; ne touche jamais aux métadonnées.
    """
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    print('Chargement de TOUS les records...', flush=True)

    laws, offset = [], 0
    fields = 'id,number,type,date,title_fr,pdf_url,source_url,content_fr,simple_summary_fr,is_publicly_indexable,canonical_slug,source_name'
    while True:
        params = {'select': fields, 'order': 'id.asc', 'limit': '1000', 'offset': str(offset)}
        if args.source:
            params['source_name'] = f'eq.{args.source}'
        r = requests.get(f'{SUPABASE_URL}/rest/v1/laws', headers=SB, params=params)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        laws.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000
    print(f'{len(laws)} records chargés\n', flush=True)

    # Grouper par pdf_url normalisé
    by_pdf: dict[str, list[dict]] = {}
    shells: list[dict] = []
    for law in laws:
        norm = _norm_pdf_url(law.get('pdf_url'))
        ct = len((law.get('content_fr') or '').strip())
        if not norm:
            if ct < 100 and not law.get('source_url'):
                shells.append(law)
            continue
        by_pdf.setdefault(norm, []).append(law)

    dup_groups = {url: rows for url, rows in by_pdf.items() if len(rows) > 1}

    # Construire le plan d'action par groupe
    plan = []
    for url, rows in dup_groups.items():
        keep, drop = _choose_survivor(rows)
        plan.append({
            'pdf_url': url,
            'keep_id': keep['id'],
            'keep_needs_publish': not keep.get('is_publicly_indexable'),
            'keep_meta_broken': _metadata_broken(keep),
            'mask_ids': [r['id'] for r in drop if r.get('is_publicly_indexable')],
            'already_hidden_ids': [r['id'] for r in drop if not r.get('is_publicly_indexable')],
            'rows': rows, 'keep': keep, 'drop': drop,
        })

    # ── Rapport ───────────────────────────────────────────────────────────────
    n_publish = sum(1 for p in plan if p['keep_needs_publish'])
    n_mask    = sum(len(p['mask_ids']) for p in plan)
    n_fix     = sum(1 for p in plan if p['keep_meta_broken'])
    print(f'{"═"*72}')
    print(f'  Records totaux                  : {len(laws)}')
    print(f'  PDFs distincts                  : {len(by_pdf)}')
    print(f'  Groupes de doublons (même PDF)  : {len(dup_groups)}')
    print(f'  → survivants à publier          : {n_publish}')
    print(f'  → doublons à masquer            : {n_mask}')
    print(f'  → survivants à méta corriger    : {n_fix}  (lire PDF via --mode record)')
    print(f'  Coquilles (sans PDF ni contenu) : {len(shells)}')
    print(f'{"═"*72}\n')

    print('── PLAN PAR GROUPE (garder 1 public, masquer les autres) ──')
    for p in plan[:60]:
        print(f'\n  PDF: ...{p["pdf_url"][-58:]}')
        for r in sorted(p['rows'], key=_record_quality, reverse=True):
            ct = len(r.get('content_fr') or '')
            pub = 'public' if r.get('is_publicly_indexable') else 'caché '
            if r['id'] == p['keep_id']:
                act = 'GARDER+PUBLIER' if p['keep_needs_publish'] else 'GARDER'
                if p['keep_meta_broken']:
                    act += ' +corriger-méta'
            else:
                act = 'masquer' if r.get('is_publicly_indexable') else '(déjà caché)'
            print(f'    id={r["id"]:>6} [{r.get("type",""):10}] {pub} ct={ct:>6} num={str(r.get("number"))[:14]:14} → {act}')

    if shells:
        print(f'\n── COQUILLES (sans PDF ni contenu — à corriger ou retirer) ──')
        for r in shells[:40]:
            print(f'    id={r["id"]:>6} [{r.get("type",""):10}] num={str(r.get("number")):12} {r.get("title_fr","")[:50]}')

    if args.export:
        out = {
            'total': len(laws), 'distinct_pdfs': len(by_pdf),
            'duplicate_groups': len(dup_groups),
            'to_publish': n_publish, 'to_mask': n_mask, 'to_fix_meta': n_fix,
            'plan': [{'pdf_url': p['pdf_url'], 'keep_id': p['keep_id'],
                      'keep_needs_publish': p['keep_needs_publish'],
                      'keep_meta_broken': p['keep_meta_broken'],
                      'mask_ids': p['mask_ids']} for p in plan],
            'shell_ids': [r['id'] for r in shells],
        }
        (AUDIT_DIR / 'duplicates_report.json').write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'\nRapport exporté → {AUDIT_DIR / "duplicates_report.json"}')

    # ── Application (visibilité seulement) ────────────────────────────────────
    if not args.apply:
        print(f'\n⚠ DRY-RUN : aucune écriture. Ajoute --apply pour publier les survivants '
              f'et masquer {n_mask} doublons (réversible).')
        return

    print(f'\nApplication des changements de visibilité...', flush=True)
    published = masked = errors = 0
    for p in plan:
        # Publier le survivant si caché
        if p['keep_needs_publish']:
            try:
                rr = requests.patch(f'{SUPABASE_URL}/rest/v1/laws', headers=SB,
                                    params={'id': f'eq.{p["keep_id"]}'},
                                    json={'is_publicly_indexable': True}, timeout=10)
                rr.raise_for_status(); published += 1
            except Exception as e:
                errors += 1; print(f'  ❌ publier id={p["keep_id"]}: {e}')
        # Masquer les doublons publics
        for mid in p['mask_ids']:
            try:
                rr = requests.patch(f'{SUPABASE_URL}/rest/v1/laws', headers=SB,
                                    params={'id': f'eq.{mid}'},
                                    json={'is_publicly_indexable': False,
                                          'pipeline_notes': '[auto: doublon même PDF masqué]'}, timeout=10)
                rr.raise_for_status(); masked += 1
            except Exception as e:
                errors += 1; print(f'  ❌ masquer id={mid}: {e}')
    print(f'\n  Survivants publiés : {published}')
    print(f'  Doublons masqués   : {masked}')
    print(f'  Erreurs            : {errors}')


# ── Main : dispatcher de modes ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Moteur de canonicalisation juridique (dry-run)')
    parser.add_argument('--mode', choices=['record', 'duplicates', 'mirror', 'all'],
                        default='record',
                        help='record=audit PDF↔méta | duplicates=détection croisée | '
                             'mirror=backup PDFs local | all=record+duplicates')
    parser.add_argument('--limit',     type=int, default=20,  help='Nb de records (défaut: 20)')
    parser.add_argument('--id',        type=int,               help='Cibler 1 record par ID')
    parser.add_argument('--source',    type=str,               help='Filtrer par source_name')
    parser.add_argument('--low-score', action='store_true',    help='Seulement score < 70')
    parser.add_argument('--export',        action='store_true', help='Exporter CSV/JSON local')
    parser.add_argument('--export-to-db',  action='store_true', help='Exporter corrections vers Supabase audit_queue (Admin → Corrections)')
    parser.add_argument('--apply',         action='store_true', help='[mode duplicates] Appliquer visibilité (publier survivant + masquer doublons)')
    parser.add_argument('--no-ocr',        action='store_true', help='Désactiver l\'OCR Vision (PDFs scannés non récupérés)')
    args = parser.parse_args()

    global USE_VISION_OCR
    if args.no_ocr:
        USE_VISION_OCR = False
    elif not OPENROUTER_KEY:
        print('⚠ OPENROUTER_API_KEY absente — OCR Vision désactivé (PDFs scannés non récupérés)')

    if not FITZ_OK and not PDFPLUMBER_OK:
        print('⚠ Ni PyMuPDF ni pdfplumber disponibles — extraction PDF désactivée')

    if args.mode == 'record':
        mode_record(args)
    elif args.mode == 'mirror':
        mode_mirror(args)
    elif args.mode == 'duplicates':
        mode_duplicates(args)
    elif args.mode == 'all':
        print('### MODE RECORD ###\n')
        mode_record(args)
        print('\n\n### MODE DUPLICATES ###\n')
        mode_duplicates(args)


if __name__ == '__main__':
    main()
