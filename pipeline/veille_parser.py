"""
veille_parser.py — Détection des relations entre textes juridiques
===================================================================
Analyse le texte extrait d'un BO ou PDF pour détecter :
  - 'new'    : nouveau texte juridique autonome
  - 'update' : texte qui modifie/complète un texte existant
  - 'repeal' : texte qui abroge un texte existant

Usage :
  from veille_parser import parse_relations
  results = parse_relations("Décret modifiant le décret n° 2-15-426 ...")
  # → [{"action": "update", "related_number": "2-15-426", "pattern": "modifie"}]
"""

import re
from dataclasses import dataclass, field


@dataclass
class Relation:
    action:         str   # 'update' | 'repeal' | 'apply'
    related_number: str   # numéro du texte parent (ex: "2-15-426")
    pattern:        str   # pattern matched (ex: "modifie")
    context:        str   # extrait de texte autour du match


# Patterns de détection (FR + AR)
_PATTERNS = {
    "update": [
        r"modif(?:iant|ie|ication|ications?)\s+et\s+complétan[t]?.{0,120}n[°o°]?\s*([\d]+-[\d]+)",
        r"modif(?:iant|ie|ication|ications?).{0,120}n[°o°]?\s*([\d]+-[\d]+)",
        r"complétan[t]?.{0,120}n[°o°]?\s*([\d]+-[\d]+)",
        r"portant\s+(?:modification|révision).{0,120}n[°o°]?\s*([\d]+-[\d]+)",
        r"يغير\s+ويتمم.{0,80}رقم\s+([\d]+-[\d]+)",  # AR: يغير ويتمم
        r"يتمم.{0,80}رقم\s+([\d]+-[\d]+)",
    ],
    "repeal": [
        r"abrog(?:eant|é|ation|er).{0,120}n[°o°]?\s*([\d]+-[\d]+)",
        r"portant\s+(?:abrogation).{0,120}n[°o°]?\s*([\d]+-[\d]+)",
        r"sont?\s+(?:abrogé[es]?|supprimé[es]?).{0,120}n[°o°]?\s*([\d]+-[\d]+)",
        r"ينسخ.{0,80}رقم\s+([\d]+-[\d]+)",  # AR: ينسخ
    ],
    "apply": [
        r"(?:application|exécution)\s+(?:de\s+)?(?:la\s+)?(?:loi|dahir|décret).{0,80}n[°o°]?\s*([\d]+-[\d]+)",
        r"pris\s+pour\s+l[''']application.{0,80}n[°o°]?\s*([\d]+-[\d]+)",
        r"تطبيق.{0,80}رقم\s+([\d]+-[\d]+)",  # AR: تطبيق
    ],
}

# Patterns d'extraction du numéro de loi depuis un titre ou nom de fichier
_NUMBER_PATTERNS = [
    r"(?:loi|décret|dahir|arrêté|circulaire|ordonnance)\s+n[°o°]?\s*([\d]+-[\d]+)",
    r"n[°o°]\s*([\d]+-[\d]+)",
    r"([\d]+-[\d]+)",  # fallback générique
]

# Patterns d'extraction du type de texte
_TYPE_PATTERNS = {
    "Loi":        r"\bloi\b",
    "Décret":     r"\bdécret\b",
    "Dahir":      r"\bdahir\b",
    "Arrêté":     r"\barrêté\b",
    "Circulaire": r"\bcirculaire\b",
    "Décret royal": r"\bdécret royal\b",
    "Ordonnance": r"\bordonnance\b",
}


def parse_relations(text: str) -> list[Relation]:
    """
    Analyse le texte et retourne la liste des relations détectées.
    """
    relations = []
    text_lower = text[:3000]  # limiter aux 3000 premiers chars

    for action, patterns in _PATTERNS.items():
        for pattern in patterns:
            for m in re.finditer(pattern, text_lower, re.IGNORECASE | re.DOTALL):
                number = m.group(1).strip()
                if not _is_valid_number(number):
                    continue
                start = max(0, m.start() - 40)
                end   = min(len(text_lower), m.end() + 40)
                relations.append(Relation(
                    action=action,
                    related_number=number,
                    pattern=pattern[:30],
                    context=text_lower[start:end].replace("\n", " ").strip(),
                ))

    # Dédoublonner
    seen = set()
    unique = []
    for r in relations:
        key = (r.action, r.related_number)
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


def extract_law_number(text: str) -> str | None:
    """
    Extrait le numéro de loi depuis un titre ou nom de fichier.
    Ex: "Décret n° 2-22-431 relatif aux marchés publics" → "2-22-431"
    """
    for pattern in _NUMBER_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            number = m.group(1).strip()
            if _is_valid_number(number):
                return number
    return None


def extract_law_type(text: str) -> str:
    """
    Extrait le type de texte (Loi, Décret, Dahir...) depuis un titre.
    """
    text_lower = text.lower()
    for law_type, pattern in _TYPE_PATTERNS.items():
        if re.search(pattern, text_lower):
            return law_type
    return "Texte réglementaire"


def _is_valid_number(number: str) -> bool:
    """Valide qu'un numéro ressemble à un numéro de loi marocain (ex: 2-22-431, 36-15)."""
    parts = number.split("-")
    return 2 <= len(parts) <= 3 and all(p.isdigit() for p in parts)


def determine_action(title: str, text: str = "") -> str:
    """
    Détermine l'action principale d'un texte : 'new', 'update', ou 'repeal'.
    """
    combined = (title + " " + text[:500]).lower()
    if any(kw in combined for kw in ["modifiant", "complétant", "modifié", "يغير", "يتمم"]):
        return "update"
    if any(kw in combined for kw in ["abrogeant", "abrogé", "abrogation", "ينسخ"]):
        return "repeal"
    return "new"
