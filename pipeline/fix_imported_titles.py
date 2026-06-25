"""
fix_imported_titles.py — Correcteur intelligent de titres juridiques

Détecte et corrige AUTOMATIQUEMENT tous les problèmes de titres dans la base :
  • Titres URL-encodés (%20, %C3%A9…)
  • Extensions .pdf dans les titres
  • Titres type nom-de-fichier (underscores, kebab numérique)
  • Titres type filename espacé (ex: "loi telecom fr 96 24 162 97 1 1997")
  • title_ar corrompus (Arabic Presentation Forms)
  • Titres purement numériques / codes sans sens

Usage :
  python pipeline/fix_imported_titles.py              # corrige tout
  python pipeline/fix_imported_titles.py --dry-run    # aperçu sans écriture
  python pipeline/fix_imported_titles.py --limit 200  # limite à 200 lois
  python pipeline/fix_imported_titles.py --all        # inclut toutes les lois (pas seulement pending)
"""

import os, re, sys, time, json
from pathlib import Path
from urllib.parse import unquote
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

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", ""))
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
AI_MODEL        = "google/gemini-2.5-flash"
AI_MODEL_LOOKUP = "google/gemini-2.5-pro"   # Plus précis pour identifier les lois marocaines

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}

import sys as _sys
console = Console(force_terminal=False, no_color=True) if not _sys.stdout.isatty() else Console()

# ── Détection ──────────────────────────────────────────────────────────────────

def is_url_encoded(s: str) -> bool:
    return bool(s and '%' in s)

def has_pdf_extension(s: str) -> bool:
    return bool(s and re.search(r'\.(pdf|PDF)$', s.strip()))

def is_garbled_arabic(t: str) -> bool:
    """Arabic Presentation Forms (U+FB50–FEFF) = encodage visuel legacy corrompu."""
    if not t or len(t) < 3:
        return False
    pf = sum(1 for c in t if 'ﭐ' <= c <= '﻿')
    total = len(t.replace(' ', ''))
    return total > 0 and pf / total > 0.20

def is_filename_title(t: str) -> bool:
    """Détecte un titre qui ressemble à un nom de fichier."""
    t = (t or '').strip()
    if not t or len(t) > 350:
        return False
    # Sans espace : underscores ou codes (ex: cdr_loi_27.14, 103_12)
    if ' ' not in t:
        if '_' in t:
            return True
        if re.match(r'^[\dA-Za-z]+$', t) and len(t) > 6 and re.search(r'\d', t):
            return True
        if re.search(r'\d{4}[-_]\d', t):
            return True
    # Avec espaces : ratio élevé de tokens numériques (ex: "loi telecom fr 96 24 162 97 1 1997")
    words = t.split()
    if len(words) >= 4:
        digit_tokens = sum(1 for w in words if re.match(r'^\d+$', w))
        if digit_tokens / len(words) >= 0.35:
            return True
    return False

def is_purely_numeric(t: str) -> bool:
    """Titre uniquement numérique ou quasi-numérique (ex: '6399', '13_100')."""
    t = (t or '').strip().replace('_', '').replace('-', '').replace('.', '')
    return bool(t) and t.isdigit() and len(t) <= 10

# Titres génériques à remplacer
GENERIC_TITLES = {
    '(version en arabe)', 'version en arabe', 'version arabe',
    '(version française)', 'version française', 'version fr',
    'texte juridique', 'texte réglementaire', 'document', 'loi', 'décret',
    'arrêté', 'dahir', 'circulaire', 'ordonnance', 'n/a', 'sans titre',
}

def is_generic_title(t: str) -> bool:
    """Titre trop générique / inutile."""
    return (t or '').strip().lower() in GENERIC_TITLES

def is_adala_placeholder(t: str) -> bool:
    """Placeholder auto-généré : 'Texte N° adala-XXXXXXXX' — pas de vraie info."""
    return bool(re.match(r'^Texte\s+N[°o]?\s+adala-[0-9a-f]+\s*$', (t or '').strip(), re.IGNORECASE))

def _normalize_number(n: str) -> str:
    """Normalise les numéros avec underscores/points : 1_09_236 → 1-09-236."""
    return re.sub(r'[_\.\s]+', '-', (n or '').strip()).strip('-')

def is_number_as_title(title_fr: str, number: str) -> bool:
    """Détecte quand le titre est vide ou n'est que le numéro reformaté (inutile)."""
    t = (title_fr or '').strip()
    if not t:
        return True  # Pas de titre du tout
    num_clean = _normalize_number(number or '').replace('-', ' ')
    t_norm = t.replace('_', ' ').replace('-', ' ').strip().lower()
    num_norm = num_clean.lower()
    # Titre = numéro reformaté (ex: "1 09 236" pour number "1_09_236")
    if t_norm == num_norm:
        return True
    # Titre = juste des chiffres et séparateurs
    if re.match(r'^[\d\s\-_\.]+$', t):
        return True
    # Titre = "Texte juridique n°X" ou "Texte N° X" — fallback générique sans sens
    if re.match(r'^(?:texte\s+(?:juridique|réglementaire|reglementaire)?\s*n[°o]?\s*[\d]|texte\s+n[°o°]\s*[\d])', t, re.IGNORECASE):
        return True
    # Titre = "Arrêté n°X", "Décret n°X", "Loi n°X", "Dahir n°X" sans description
    # (le titre ne contient QUE le type + numéro, pas de mots descriptifs)
    m = re.match(
        r'^(?:arrêté|arrete|décret|decret|dahir|loi|circulaire|décision|decision|ordonnance)'
        r'\s+(?:n[°o°]?\s*)?[\d\.]+[\d\.\-/]*\s*$',
        t, re.IGNORECASE
    )
    if m:
        return True
    return False

def is_gibberish(t: str) -> bool:
    """Détecte un titre composé majoritairement de bruit (OCR raté, chars spéciaux aléatoires)."""
    t = (t or '').strip()
    if len(t) < 5:
        return False
    # Ratio de caractères non-imprimables / symboles bizarres
    noise = sum(1 for c in t if not (c.isalnum() or c in ' .,;:()[]/-\'\"àâäéèêëîïôùûüçœæ°–—«»؀-ۿA-z'))
    if noise / len(t) > 0.30:
        return True
    # Aussi : trop de chiffres isolés entremêlés (OCR de tableau de BO)
    tokens = t.split()
    if len(tokens) >= 5:
        digit_tokens = sum(1 for w in tokens if re.match(r'^\d+[\.\-]?\d*$', w))
        non_alpha = sum(1 for w in tokens if not any(c.isalpha() for c in w))
        if non_alpha / len(tokens) > 0.5:
            return True
    return False

def needs_fix(row: dict, fix_adala: bool = False) -> list[str]:
    """Retourne la liste des problèmes détectés pour une ligne."""
    problems = []
    num   = row.get("number", "") or ""
    title = row.get("title_fr", "") or ""
    ar    = row.get("title_ar", "") or ""

    if is_url_encoded(num) or has_pdf_extension(num):
        problems.append("number_encoded")
    if is_url_encoded(title) or has_pdf_extension(title):
        problems.append("title_encoded")
    if is_garbled_arabic(ar):
        problems.append("arabic_garbled")
    # title_fr peut aussi contenir de l'arabe corrompu (mauvais encodage à l'import)
    if is_garbled_arabic(title) and "title_encoded" not in problems:
        problems.append("title_fr_garbled")
    if is_filename_title(title) and "title_encoded" not in problems and "title_fr_garbled" not in problems:
        problems.append("title_filename")
    if is_purely_numeric(title):
        problems.append("title_numeric")
    if is_generic_title(title):
        problems.append("title_generic")
    if is_gibberish(title) and "title_fr_garbled" not in problems and "title_encoded" not in problems:
        problems.append("title_gibberish")
    # Placeholder adala : traduire title_ar → title_fr
    if fix_adala and is_adala_placeholder(title) and ar:
        problems.append("adala_placeholder")
    # Numéro en guise de titre (1_09_236, "1 09 236", etc.)
    if fix_adala and is_number_as_title(title, num) and "adala_placeholder" not in problems:
        problems.append("number_as_title")
    return problems

# ── Corrections simples ────────────────────────────────────────────────────────

def clean_str(s: str, max_len: int = 400) -> str:
    s = unquote(s or '')
    s = re.sub(r'\.(pdf|PDF)$', '', s).strip()
    return re.sub(r'\s+', ' ', s).strip()[:max_len]

def humanize(t: str) -> str:
    t = re.sub(r'\.(pdf|PDF|doc|docx)$', '', t or '')
    t = t.replace('_', ' ').replace('-', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    return t.capitalize()

# ── Détection du type depuis le titre arabe ───────────────────────────────────

def detect_type_from_ar(title_ar: str) -> str:
    """Détecte le vrai type du texte depuis le titre arabe (règles lexicales, gratuit)."""
    t = title_ar or ""
    # Textes royaux
    if "خطاب صاحب الجلالة" in t or "خطاب الملك" in t or "خطاب ملكي" in t:
        return "Discours Royal"
    if "الرسالة الملكية" in t or "الرسالبة الملكية" in t or "رسالة ملكية سامية" in t:
        return "Lettre Royale"
    if "رسالة ملكية" in t or "رسالة سامية" in t:
        return "Message Royal"
    # Institutions
    if "رأي المجلس الاقتصادي" in t or "رأي مجلس" in t:
        return "Avis"
    if "تقرير المجلس الأعلى" in t or "تقرير المجلس الاقتصادي" in t or t.startswith("تقرير"):
        return "Rapport"
    if "قرار" in t[:30]:
        return "Décision"
    if "منشور" in t[:30] or "دورية" in t[:30]:
        return "Circulaire"
    # Textes législatifs
    if "ظهير" in t[:20]:
        return "Dahir"
    if "مرسوم" in t[:20]:
        return "Décret"
    if "قانون" in t[:20]:
        return "Loi"
    return ""  # inconnu → garder le type existant


# ── Correction IA (pour les titres complexes) ─────────────────────────────────

def ai_fix_title(number: str, source: str, bad_title: str, content_snippet: str) -> str | None:
    """Demande à Gemini de générer un titre propre depuis les métadonnées disponibles."""
    if not OPENROUTER_KEY:
        return None

    prompt = (
        "Tu es un expert en droit marocain. "
        "Génère un titre français propre et concis (max 120 caractères) pour ce texte juridique. "
        "Réponds UNIQUEMENT avec le titre, sans guillemets, sans explication.\n\n"
        f"Numéro : {number or 'inconnu'}\n"
        f"Source : {source or 'inconnue'}\n"
        f"Titre brut (à remplacer) : {bad_title[:100]}\n"
        f"Extrait du contenu : {content_snippet[:600] if content_snippet else 'Non disponible'}"
    )

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type":  "application/json",
                "HTTP-Referer":  "https://juritheque.com",
            },
            json={
                "model":       AI_MODEL,
                "max_tokens":  80,
                "temperature": 0.1,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )
        if r.status_code == 200:
            title = r.json()["choices"][0]["message"]["content"].strip()
            title = re.sub(r'^[«"\'`]+|[»"\'`]+$', '', title).strip()
            if 5 < len(title) < 200:
                return title
    except Exception as e:
        print(f"    IA error: {e}", flush=True)
    return None

def ai_translate_from_ar(title_ar: str, law_type: str = "", number: str = "") -> tuple[str | None, str | None]:
    """Traduit un titre arabe → (titre_fr, type_détecté). type peut être None si déjà connu."""
    if not OPENROUTER_KEY or not title_ar:
        return None, None

    need_type = not law_type or law_type.lower() in ('texte juridique', 'texte réglementaire', 'texte', '')
    if need_type:
        prompt = (
            "Tu es un expert en droit marocain. "
            "Réponds en JSON strict sur une seule ligne, sans explication :\n"
            '{"type": "...", "titre": "..."}\n\n'
            "Pour 'type', choisis parmi : Discours Royal, Lettre Royale, Message Royal, "
            "Rapport, Avis, Décision, Circulaire, Dahir, Décret, Loi, Arrêté, Note, Autre.\n"
            "Pour 'titre', donne un titre français concis (max 120 caractères).\n\n"
            f"Numéro : {number or 'N/A'}\n"
            f"Titre arabe : {title_ar[:300]}"
        )
    else:
        prompt = (
            "Tu es un expert en droit marocain. "
            "Traduis ce titre juridique arabe en français clair et concis (max 120 caractères). "
            "Réponds UNIQUEMENT avec le titre traduit, sans guillemets, sans explication.\n\n"
            f"Type : {law_type}\n"
            f"Numéro : {number or 'N/A'}\n"
            f"Titre arabe : {title_ar[:300]}"
        )
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type":  "application/json",
                "HTTP-Referer":  "https://juritheque.com",
            },
            json={
                "model": AI_MODEL, "max_tokens": 120, "temperature": 0.1,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )
        if r.status_code == 200:
            raw = r.json()["choices"][0]["message"]["content"].strip()
            if need_type:
                import json as _json
                try:
                    raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw).strip()
                    data = _json.loads(raw)
                    titre = re.sub(r'^[«"\']+|[»"\']+$', '', (data.get("titre") or "")).strip()
                    detected = (data.get("type") or "").strip()
                    return (titre if 5 < len(titre) < 200 else None), (detected or None)
                except Exception:
                    pass
            else:
                titre = re.sub(r'^[«"\'`]+|[»"\'`]+$', '', raw).strip()
                if 5 < len(titre) < 200:
                    return titre, None
    except Exception as e:
        print(f"    IA translate error: {e}", flush=True)
    return None, None


def is_quality_ok(title_fr: str, law_type: str, slug: str) -> bool:
    """Vérifie qu'un titre/slug généré est suffisamment bon pour être publié."""
    t = (title_fr or "").strip()
    s = (slug or "").strip()

    if len(t) < 10:
        return False  # Titre trop court

    # Titre = juste le type seul
    _GENERIC_TITLES = {'convention', 'loi', 'décision', 'decision', 'texte', 'document',
                       'arrêté', 'arrete', 'décret', 'decret', 'dahir', 'circulaire',
                       'rapport', 'avis', 'note', 'autre'}
    if t.lower() in _GENERIC_TITLES:
        return False

    # Titre encore un nom de fichier (pas d'espaces, underscores/tirets seulement)
    if ' ' not in t and ('_' in t or (t.endswith('.pdf'))):
        return False

    # Titre contient des placeholders IA ("[sujet probable]", "[...]", etc.)
    if re.search(r'\[.*?\]|sujet probable|sujet inconnu|titre inconnu|non identifi|à préciser', t, re.IGNORECASE):
        return False

    # Slug trop court — moins de 3 segments utiles
    if len(s.split('-')) < 3:
        return False

    # Titre = juste un numéro de revue/publication (ex: "Revue Justice et Droit - Numéro 123")
    if re.match(r'^(revue|bulletin|recueil|rapport annuel).{0,40}num[eé]ro\s*\d+', t, re.IGNORECASE):
        return False

    return True


_ADALA_INDEX: dict | None = None  # cache en mémoire

def _load_adala_index() -> dict:
    """Charge l'index Adala local (number → title_ar). Construit via _build_adala_index.py."""
    global _ADALA_INDEX
    if _ADALA_INDEX is not None:
        return _ADALA_INDEX
    idx_path = os.path.join(os.path.dirname(__file__), "adala_index.json")
    if os.path.exists(idx_path):
        import json as _j
        with open(idx_path, encoding="utf-8") as f:
            _ADALA_INDEX = _j.load(f)
        print(f"  [Adala index] {len(_ADALA_INDEX)} entrées chargées", flush=True)
    else:
        _ADALA_INDEX = {}
    return _ADALA_INDEX

def _normalize_num(n: str) -> str:
    """2.72.274 / 2-72-274 → 2-72-274 (clé index)"""
    return re.sub(r'[\.\s]+', '-', (n or "").strip()).strip('-').lower()

def adala_scrape_by_number(number: str, law_type: str = "") -> tuple[str | None, str | None]:
    """Cherche dans l'index Adala local par numéro → titre_fr via titre_ar.
    Prérequis : lancer pipeline/_build_adala_index.py une fois pour créer adala_index.json."""
    if not number:
        return None, None
    index = _load_adala_index()
    if not index:
        return None, None
    key = _normalize_num(number)
    title_ar = index.get(key)
    # Essai avec des variantes si pas trouvé directement
    if not title_ar:
        # Essayer sans le premier chiffre (ex: "2-72-274" → "72-274")
        parts = key.split('-')
        if len(parts) >= 2:
            title_ar = index.get('-'.join(parts[1:]))
    if not title_ar or len(title_ar) < 5:
        return None, None
    # Traduire l'arabe vers le français
    title_fr, detected_type = ai_translate_from_ar(title_ar, law_type, number)
    if not title_fr:
        return None, None
    # Insérer le numéro dans le titre s'il est absent
    num_dot  = number.replace('-', '.')
    num_dash = number.replace('.', '-')
    if num_dot not in title_fr and num_dash not in title_fr and number not in title_fr:
        import unicodedata as _ud
        def _plain(s):
            n = _ud.normalize("NFD", s.lower())
            return "".join(c for c in n if _ud.category(c) != "Mn")
        words = title_fr.split()
        type_word = _plain((law_type or '').split()[0]) if law_type else ''
        if words and type_word and _plain(words[0]) == type_word:
            # "Décret d'application…" → "Décret n° 2.93.751 d'application…"
            title_fr = f"{words[0]} n° {num_dot} {' '.join(words[1:])}"
        else:
            title_fr = f"{title_fr} (n° {num_dot})"
    return title_fr, detected_type


def ai_lookup_by_number(law_type: str, number: str, date: str = "") -> tuple[str | None, str | None]:
    """Identifie un texte juridique marocain par son numéro officiel → (titre_fr, type)."""
    if not OPENROUTER_KEY or not number:
        return None, None
    prompt = (
        "Tu es un expert en droit marocain avec une connaissance encyclopédique des textes officiels. "
        "Identifie ce texte juridique marocain par son numéro et donne son titre officiel français.\n"
        "Réponds en JSON strict sur une seule ligne :\n"
        '{"type": "...", "titre": "...", "known": true/false}\n\n'
        "Règles STRICTES :\n"
        "- 'titre' : titre officiel exact tel que publié au Bulletin Officiel (max 150 caractères).\n"
        "- Si tu connais ce texte avec certitude : 'known': true et donne le titre réel.\n"
        "- Si tu NE connais PAS ce texte : 'known': false et 'titre': null. "
        "N'invente JAMAIS un titre. N'utilise JAMAIS de crochets [] ni de formules comme 'sujet probable'.\n"
        "- 'type' : Dahir, Décret, Loi, Arrêté, Circulaire, Convention, Rapport, Avis, Autre.\n\n"
        f"Type supposé : {law_type or 'inconnu'}\n"
        f"Numéro : {number}\n"
        f"Date : {date or 'inconnue'}"
    )
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type":  "application/json",
                "HTTP-Referer":  "https://juritheque.com",
            },
            json={"model": AI_MODEL_LOOKUP, "max_tokens": 150, "temperature": 0.1,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=20,
        )
        if r.status_code == 200:
            import json as _json
            raw = r.json()["choices"][0]["message"]["content"].strip()
            raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw).strip()
            try:
                data = _json.loads(raw)
            except Exception:
                m = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
                data = _json.loads(m.group()) if m else {}
            titre    = re.sub(r'^[«"\'`]+|[»"\'`]+$', '', (data.get("titre") or "")).strip()
            detected = (data.get("type") or "").strip()
            known    = data.get("known", True)  # Si absent → suppose connu (rétrocompat)

            # Rejeter si l'IA avoue ne pas connaître ou si le titre contient des placeholders
            _PLACEHOLDER = re.compile(
                r'\[.*?\]|sujet probable|sujet inconnu|titre inconnu|non identifi|'
                r'non trouvé|introuvable|à préciser|à compléter|indisponible',
                re.IGNORECASE
            )
            if not known or titre is None or _PLACEHOLDER.search(titre or ''):
                return None, (detected or None)

            return (titre if 5 < len(titre) < 200 else None), (detected or None)
    except Exception as e:
        print(f"    IA lookup error: {e}", flush=True)
    return None, None


from slug_utils import make_slug_from_law  # noqa
from title_lookup import (  # noqa — réexportés pour rétrocompat
    ai_lookup_by_number,
    ai_translate_from_ar,
    adala_lookup_by_number as adala_scrape_by_number,
    get_best_title,
)


# ── Pagination Supabase ────────────────────────────────────────────────────────

def fetch_all(params: dict, page_size: int = 1000) -> list[dict]:
    rows, offset = [], 0
    while True:
        h = {**HEADERS, "Range": f"{offset}-{offset + page_size - 1}"}
        r = requests.get(f"{SUPABASE_URL}/rest/v1/laws", headers=h, params=params, timeout=30)
        if r.status_code not in (200, 206):
            print(f"Erreur fetch: {r.status_code}", flush=True)
            break
        chunk = r.json()
        if not chunk:
            break
        rows.extend(chunk)
        if len(chunk) < page_size:
            break
        offset += page_size
    return rows

def patch(law_id: str, data: dict, retries: int = 3) -> bool:
    for attempt in range(retries):
        try:
            r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/laws",
                headers=HEADERS,
                params={"id": f"eq.{law_id}"},
                json=data,
                timeout=15,
            )
            return r.status_code in (200, 204)
        except requests.exceptions.ConnectionError:
            if attempt < retries - 1:
                import time as _t
                wait = 10 * (attempt + 1)
                print(f"  !! Reseau indisponible, retry {attempt+1}/{retries-1} dans {wait}s...", flush=True)
                _t.sleep(wait)
            else:
                print(f"  XX Echec reseau apres {retries} tentatives -- texte ignore", flush=True)
                return False

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    import argparse
    p = argparse.ArgumentParser(description="Correcteur intelligent de titres juridiques")
    p.add_argument("--dry-run",       action="store_true", help="Aperçu sans écriture")
    p.add_argument("--all",           action="store_true", help="Scanner toutes les lois (pas seulement pending)")
    p.add_argument("--fix-adala",     action="store_true", help="Traduit les titres 'Texte N° adala-...' depuis title_ar via IA")
    p.add_argument("--fix-bad-slugs", action="store_true", help="Corrige les titres des textes avec slug texte-juridique-* (avant fix_bad_slugs.py)")
    p.add_argument("--limit",         type=int, default=0, help="Limiter à N lois (0 = illimité)")
    args = p.parse_args()

    if args.dry_run:
        print("Mode DRY-RUN -- aucune modification en base\n", flush=True)

    fix_adala     = getattr(args, 'fix_adala', False)
    fix_bad_slugs = getattr(args, 'fix_bad_slugs', False)

    # ── 1. Charger les métadonnées légères (sans content_fr) ───────────────────
    print("Chargement des textes...", flush=True)
    params = {"select": "id,number,title_fr,title_ar,source_name,type,canonical_slug,date,simple_summary_ar"}

    if fix_bad_slugs:
        print("  Mode --fix-bad-slugs : enrichissement titres des textes a slug generique", flush=True)
        params["canonical_slug"] = "like.texte-juridique-%"
        fix_adala = True  # Active la détection number_as_title
    elif fix_adala:
        print("  Mode --fix-adala : placeholders adala + titres manquants/numeriques", flush=True)
        # Pas de filtre strict : on charge tout et on filtre par détection
    elif not args.all:
        print("  (ciblage extraction_status=pending -- utilisez --all pour tout scanner)", flush=True)
        params["extraction_status"] = "eq.pending"

    rows = fetch_all(params)
    if args.limit:
        rows = rows[:args.limit]
    print(f"  {len(rows)} textes charges\n", flush=True)

    # ── 2. Détection ────────────────────────────────────────────────────────────
    problems_map: dict[str, list] = {}  # id → [(problem, row)]
    for row in rows:
        probs = needs_fix(row, fix_adala=fix_adala)
        if probs:
            problems_map[row["id"]] = (probs, row)

    total = len(problems_map)
    if total == 0:
        print("OK -- Aucun probleme detecte.", flush=True)
        return

    print(f"{total} textes avec problemes detectes\n", flush=True)

    # ── 3. Afficher aperçu ──────────────────────────────────────────────────────
    counts = {}
    print(f"\n{'='*70}", flush=True)
    print(f"  PROBLEMES DETECTES (30 premiers sur {total})", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"  {'Probleme':<22} {'Avant':<45} Fix", flush=True)
    print(f"  {'-'*22} {'-'*45} {'-'*15}", flush=True)

    for law_id, (probs, row) in list(problems_map.items())[:30]:
        for prob in probs:
            counts[prob] = counts.get(prob, 0) + 1
            val = row.get("title_fr") or row.get("title_ar") or row.get("number") or ""
            fix_label = {
                "number_encoded":   "Decodage URL",
                "title_encoded":    "Decodage URL",
                "title_filename":   "IA" if OPENROUTER_KEY else "Humaniser",
                "title_numeric":    "Formatage",
                "title_generic":    "IA",
                "title_gibberish":  "Effacer",
                "title_fr_garbled": "Effacer",
                "arabic_garbled":   "Effacer title_ar",
                "number_as_title":  "IA lookup",
                "adala_placeholder":"IA traduction",
            }.get(prob, "?")
            print(f"  {prob:<22} {val[:44]:<45} {fix_label}", flush=True)

    if total > 30:
        print(f"  ... et {total - 30} autres\n", flush=True)

    print(f"\nRepartition :", flush=True)
    for k, v in counts.items():
        print(f"  - {k} : {v}", flush=True)
    print(flush=True)

    if args.dry_run:
        print("DRY-RUN termine -- aucune modification appliquee.", flush=True)
        return

    # ── 4. Corriger ─────────────────────────────────────────────────────────────
    fixed = failed = ai_used = skipped_no_fix = 0
    total_to_fix = len(problems_map)

    for idx, (law_id, (probs, row)) in enumerate(problems_map.items(), 1):
        num_display = row.get("number") or law_id
        pct = int(idx * 100 / total_to_fix)
        print(f"[{idx}/{total_to_fix} {pct}%] {probs[0]} — {num_display}", flush=True)
        patch_data = {}

        for prob in probs:
            if prob == "number_encoded":
                patch_data["number"] = clean_str(row.get("number", ""), 60)

            elif prob == "title_encoded":
                patch_data["title_fr"] = clean_str(row.get("title_fr", ""))

            elif prob == "arabic_garbled":
                patch_data["title_ar"] = None

            elif prob in ("title_fr_garbled", "title_gibberish"):
                # title_fr corrompu ou illisible → effacer, LawCard affichera le numéro
                patch_data["title_fr"] = None

            elif prob == "adala_placeholder":
                title_ar = row.get("title_ar", "") or ""
                law_type = row.get("type", "") or ""
                number   = row.get("number", "") or ""
                date     = row.get("date", "") or ""
                if title_ar and OPENROUTER_KEY:
                    # Détection type par règles (gratuit, prioritaire)
                    detected_type = detect_type_from_ar(title_ar)
                    if detected_type and detected_type != law_type:
                        law_type = detected_type

                    # Traduction + détection type par IA si type encore générique
                    new_title, ai_type = ai_translate_from_ar(title_ar, law_type, number)
                    if ai_type and (not law_type or law_type.lower() in ('texte juridique', 'texte réglementaire', '')):
                        law_type = ai_type
                    if law_type != (row.get("type") or ""):
                        patch_data["type"] = law_type

                    if new_title:
                        patch_data["title_fr"] = new_title
                        new_slug = make_slug_from_law(law_type, number, new_title, date)
                        patch_data["canonical_slug"] = new_slug
                        ai_used += 1

            elif prob == "number_as_title":
                number   = row.get("number", "") or ""
                law_type = row.get("type", "") or ""
                date     = row.get("date", "") or ""
                title_ar = row.get("title_ar", "") or ""
                source   = row.get("source_name", "") or ""

                # 1. Normaliser le numéro (underscores → tirets)
                clean_num = _normalize_number(number)
                if clean_num != number:
                    patch_data["number"] = clean_num

                # 2. Générer un vrai titre via IA
                new_title = None
                if OPENROUTER_KEY:
                    # Récupérer un extrait du contenu si disponible
                    content = ""
                    try:
                        cr = requests.get(
                            f"{SUPABASE_URL}/rest/v1/laws",
                            headers=HEADERS,
                            params={"id": f"eq.{law_id}", "select": "content_fr,content_ar"},
                            timeout=15,
                        )
                        if cr.status_code == 200 and cr.json():
                            d = cr.json()[0]
                            content = (d.get("content_fr") or d.get("content_ar") or "")[:600]
                    except Exception:
                        pass
                        # Priorité 1 : chercher par numéro via LLM (Gemini Pro)
                    if clean_num and re.match(r'^\d+-\d+-\d+$', clean_num):
                        new_title, ai_type = ai_lookup_by_number(law_type, clean_num, date)
                        if ai_type and (not law_type or law_type.lower() in ('texte juridique','texte réglementaire','')):
                            law_type = ai_type
                            patch_data["type"] = law_type
                    # Priorité 1b : scraper Adala directement si LLM ne connaît pas
                    if not new_title and clean_num:
                        new_title, ai_type = adala_scrape_by_number(clean_num, law_type)
                        if new_title:
                            print(f"  [Adala] trouvé", flush=True)
                        if ai_type and (not law_type or law_type.lower() in ('texte juridique','texte réglementaire','')):
                            law_type = ai_type
                            patch_data["type"] = law_type
                    # Priorité 2 : traduire depuis le titre arabe si disponible
                    if not new_title and title_ar:
                        new_title, ai_type = ai_translate_from_ar(title_ar, law_type, clean_num)
                        if ai_type and (not law_type or law_type.lower() in ('texte juridique','texte réglementaire','')):
                            law_type = ai_type
                            patch_data["type"] = law_type
                    # Priorité 2b : utiliser le résumé arabe si le titre AR est vide
                    summary_ar = (row.get("simple_summary_ar") or "")[:400]
                    if not new_title and summary_ar:
                        new_title, ai_type = ai_translate_from_ar(summary_ar, law_type, clean_num)
                        if ai_type and (not law_type or law_type.lower() in ('texte juridique','texte réglementaire','')):
                            law_type = ai_type
                            patch_data["type"] = law_type
                    # Priorité 3 : fix depuis le contenu FR/AR
                    if not new_title:
                        new_title = ai_fix_title(clean_num, source, "", content)
                    if new_title:
                        ai_used += 1

                if not new_title:
                    # IA ne connaît pas ce texte → garder tel quel, ne pas masquer
                    # Le titre "Dahir n°1-17-26" reste cherchable par numéro
                    print(f"  ?? IA inconnue -> skip (titre conserve)", flush=True)
                    patch_data.clear()  # rien à patcher

                if new_title:
                    patch_data["title_fr"] = new_title
                    new_slug = make_slug_from_law(law_type, clean_num, new_title, date)
                    patch_data["canonical_slug"] = new_slug

            elif prob in ("title_filename", "title_numeric", "title_generic"):
                bad    = row.get("title_fr", "") or ""
                number = row.get("number", "") or ""
                source = row.get("source_name", "") or ""
                new_title = None

                if prob == "title_generic" and number:
                    # Formatage simple — pas besoin d'IA
                    new_title = f"Texte N° {number}"
                elif prob == "title_numeric" and number:
                    new_title = f"Texte N° {number}"
                else:
                    # Filename complexe → IA (récupérer content_fr ciblé)
                    content = ""
                    if OPENROUTER_KEY:
                        try:
                            cr = requests.get(
                                f"{SUPABASE_URL}/rest/v1/laws",
                                headers=HEADERS,
                                params={"id": f"eq.{law_id}", "select": "content_fr"},
                                timeout=15,
                            )
                            if cr.status_code == 200 and cr.json():
                                content = (cr.json()[0].get("content_fr", "") or "")[:600]
                        except Exception:
                            pass

                    if OPENROUTER_KEY and (content or number):
                        new_title = ai_fix_title(number, source, bad, content)
                        if new_title:
                            ai_used += 1

                    if not new_title:
                        new_title = humanize(bad) if prob == "title_filename" else f"Texte N° {number}" if number else bad

                if new_title and new_title != bad:
                    patch_data["title_fr"] = new_title

        if patch_data:
            # ── Quality gate : masquer si le résultat est encore trop pauvre ──
            if not patch_data:
                skipped_no_fix += 1
                continue

            final_title = patch_data.get("title_fr") or row.get("title_fr") or ""
            final_slug  = patch_data.get("canonical_slug") or row.get("canonical_slug") or ""
            final_type  = patch_data.get("type") or row.get("type") or ""
            if not is_quality_ok(final_title, final_type, final_slug):
                patch_data["is_published"] = False
                print(f"    !! Qualite insuffisante -> is_published=false", flush=True)
            else:
                patch_data.setdefault("is_published", True)

            ok = patch(law_id, patch_data)
            if ok:
                fixed += 1
                new_t = patch_data.get("title_fr", "")
                if new_t:
                    print(f"  -> {new_t}", flush=True)
            else:
                failed += 1
                print(f"  XX Echec PATCH", flush=True)
        else:
            fixed += 1  # détecté mais rien à changer (déjà propre)

        time.sleep(0.05)

    # ── 5. Résumé ───────────────────────────────────────────────────────────────
    print(f"\n=== TERMINE ===", flush=True)
    print(f"OK {fixed}/{total} textes corriges", flush=True)
    if ai_used:
        print(f"   IA {ai_used} titres generes par IA ({AI_MODEL})", flush=True)
    if failed:
        print(f"   ECHECS {failed} echecs (erreur Supabase)", flush=True)


if __name__ == "__main__":
    main()
