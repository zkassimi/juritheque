"""
title_lookup.py — Module partagé de recherche de titres juridiques marocains
═══════════════════════════════════════════════════════════════════════════════
Fournit les fonctions pour trouver le titre officiel d'un texte juridique :
  1. Via l'IA (Gemini 2.5 Pro) par numéro officiel
  2. Via l'index Adala local (number → title_ar → traduction FR)
  3. Via traduction du titre arabe existant
  4. Via extraction depuis le contenu FR du PDF

Importé par :
  - fix_imported_titles.py  (correction post-import)
  - crawl_adala.py          (import Adala → plus de placeholders)
  - import_from_queue.py    (import queue → titre propre dès le départ)
  - extract.py              (extraction PDF → fallback AI avant filename)

Usage :
  from title_lookup import get_best_title

  title_fr = get_best_title(
      law_type="Dahir",
      number="1-02-172",
      date="2004-05-11",
      title_ar=None,       # optionnel
      content_fr=None,     # optionnel
  )
"""

import os, re, json
from pathlib import Path
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    requests = None  # type: ignore

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

OPENROUTER_KEY  = os.getenv("OPENROUTER_API_KEY", "")
_MODEL_LOOKUP   = "google/gemini-2.5-pro"   # Plus précis pour identifier les lois
_MODEL_FAST     = "google/gemini-2.5-flash"  # Pour la traduction AR→FR
_OR_REFERER     = "https://juritheque.com"

_PLACEHOLDER_RE = re.compile(
    r'\[.*?\]|sujet probable|sujet inconnu|titre inconnu|non identifi|'
    r'non trouvé|introuvable|à préciser|à compléter|indisponible',
    re.IGNORECASE,
)

# ── Cache mémoire de l'index Adala ────────────────────────────────────────────
_ADALA_INDEX: dict | None = None


def _load_adala_index() -> dict:
    """Charge l'index Adala local (number → title_ar). Construit via _build_adala_index.py."""
    global _ADALA_INDEX
    if _ADALA_INDEX is not None:
        return _ADALA_INDEX
    idx_path = Path(__file__).parent / "adala_index.json"
    if idx_path.exists():
        with open(idx_path, encoding="utf-8") as f:
            _ADALA_INDEX = json.load(f)
    else:
        _ADALA_INDEX = {}
    return _ADALA_INDEX


def _normalize_num(n: str) -> str:
    """2.72.274 / 2-72-274 → 2-72-274 (clé index Adala)."""
    return re.sub(r'[\.\s]+', '-', (n or "").strip()).strip('-').lower()


def _or_post(model: str, prompt: str, max_tokens: int = 150) -> str | None:
    """POST vers OpenRouter → contenu texte ou None."""
    if not OPENROUTER_KEY or requests is None:
        return None
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type":  "application/json",
                "HTTP-Referer":  _OR_REFERER,
            },
            json={
                "model": model, "max_tokens": max_tokens, "temperature": 0.1,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  [title_lookup] OpenRouter error: {e}", flush=True)
    return None


def _parse_json_safe(raw: str) -> dict:
    """Parse JSON depuis une réponse LLM (avec éventuels backticks/fences)."""
    raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw.strip()).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
        return json.loads(m.group()) if m else {}


# ── Fonction 1 : Lookup par numéro officiel via IA ────────────────────────────

def ai_lookup_by_number(law_type: str, number: str, date: str = "") -> tuple[str | None, str | None]:
    """Identifie un texte juridique marocain par son numéro officiel → (titre_fr, type)."""
    if not number:
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
    raw = _or_post(_MODEL_LOOKUP, prompt, max_tokens=150)
    if not raw:
        return None, None
    data     = _parse_json_safe(raw)
    titre    = re.sub(r'^[«"\'`]+|[»"\'`]+$', '', (data.get("titre") or "")).strip()
    detected = (data.get("type") or "").strip()
    known    = data.get("known", True)

    if not known or not titre or _PLACEHOLDER_RE.search(titre):
        return None, (detected or None)
    return (titre if 5 < len(titre) < 200 else None), (detected or None)


# ── Fonction 2 : Traduction titre arabe → français via IA ────────────────────

def ai_translate_from_ar(title_ar: str, law_type: str = "", number: str = "") -> tuple[str | None, str | None]:
    """Traduit un titre arabe → (titre_fr, type_détecté)."""
    if not title_ar:
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
        raw = _or_post(_MODEL_FAST, prompt, max_tokens=120)
        if raw:
            data = _parse_json_safe(raw)
            titre = re.sub(r'^[«"\']+|[»"\']+$', '', (data.get("titre") or "")).strip()
            detected = (data.get("type") or "").strip()
            return (titre if 5 < len(titre) < 200 else None), (detected or None)
    else:
        prompt = (
            "Tu es un expert en droit marocain. "
            "Traduis ce titre juridique arabe en français clair et concis (max 120 caractères). "
            "Réponds UNIQUEMENT avec le titre traduit, sans guillemets, sans explication.\n\n"
            f"Type : {law_type}\n"
            f"Numéro : {number or 'N/A'}\n"
            f"Titre arabe : {title_ar[:300]}"
        )
        raw = _or_post(_MODEL_FAST, prompt, max_tokens=120)
        if raw:
            titre = re.sub(r'^[«"\'`]+|[»"\'`]+$', '', raw).strip()
            if 5 < len(titre) < 200:
                return titre, None
    return None, None


# ── Fonction 3 : Lookup dans l'index Adala local ─────────────────────────────

def adala_lookup_by_number(number: str, law_type: str = "") -> tuple[str | None, str | None]:
    """Cherche dans l'index Adala local par numéro → titre_fr via titre_ar."""
    if not number:
        return None, None
    index = _load_adala_index()
    if not index:
        return None, None

    key = _normalize_num(number)
    title_ar = index.get(key)
    if not title_ar:
        parts = key.split('-')
        if len(parts) >= 2:
            title_ar = index.get('-'.join(parts[1:]))
    if not title_ar or len(title_ar) < 5:
        return None, None

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
            title_fr = f"{words[0]} n° {num_dot} {' '.join(words[1:])}"
        else:
            title_fr = f"{title_fr} (n° {num_dot})"
    return title_fr, detected_type


# ── Fonction 4 : Extraction depuis le contenu du PDF ─────────────────────────

def extract_title_from_content(content_fr: str, law_type: str = "", number: str = "") -> str | None:
    """Extrait le titre depuis les premières lignes du texte du PDF."""
    if not content_fr:
        return None
    lines = [l.strip() for l in content_fr[:2000].splitlines() if l.strip()]
    type_words = {'bulletin', 'officiel', 'page', 'article', 'vu', 'considérant',
                  'annexe', 'avis', 'arrêté', 'section', 'chapitre', 'décret',
                  'dahir', 'loi', 'circulaire'}
    candidates = []
    for line in lines[:20]:
        if 10 < len(line) < 180:
            low = line.lower()
            first_word = low.split()[0] if low.split() else ''
            if first_word not in type_words:
                candidates.append(line)
    return candidates[0] if candidates else None


# ── Orchestrateur principal ───────────────────────────────────────────────────

def get_best_title(
    law_type: str,
    number: str,
    date: str = "",
    title_ar: str | None = None,
    content_fr: str | None = None,
    fast: bool = False,
) -> str | None:
    """
    Retourne le meilleur titre français disponible pour un texte juridique.

    Ordre de priorité :
      1. AI lookup par numéro (Gemini 2.5 Pro) — le plus fiable
      2. Index Adala local (number → title_ar → traduction)
      3. Traduction du titre arabe existant
      4. Extraction depuis le contenu du PDF
      Retourne None si aucun titre fiable — jamais de fallback filename.

    Args:
        law_type:   Type du texte (Dahir, Décret, Loi, Arrêté…)
        number:     Numéro officiel (ex: "2-22-431", "103-12")
        date:       Date du texte (optionnel, améliore la précision AI)
        title_ar:   Titre arabe existant (optionnel)
        content_fr: Texte extrait du PDF (optionnel, fallback)
        fast:       Si True, saute les appels AI (mode bulk rapide)
    """
    # Priorité 1 : AI lookup par numéro
    if not fast and number:
        title, _ = ai_lookup_by_number(law_type, number, date)
        if title:
            return title

    # Priorité 2 : Index Adala local
    if number:
        title, _ = adala_lookup_by_number(number, law_type)
        if title:
            return title

    # Priorité 3 : Traduction du titre arabe
    if not fast and title_ar:
        title, _ = ai_translate_from_ar(title_ar, law_type, number)
        if title:
            return title

    # Priorité 4 : Extraction depuis le contenu du PDF
    if content_fr:
        title = extract_title_from_content(content_fr, law_type, number)
        if title:
            return title

    return None
