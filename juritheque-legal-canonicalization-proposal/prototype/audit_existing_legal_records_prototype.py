"""
Prototype non integre pour l'audit canonique JuriTheque.

Ce fichier ne se connecte pas a Supabase et ne modifie rien. Il illustre la
forme d'un futur moteur dry-run : record DB -> canonical record -> diff -> audit.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any
import json
import re


@dataclass
class Evidence:
    field: str
    value: str | None
    source: str
    page: int | None = None
    quote: str | None = None
    confidence: int | None = None


def detect_numbers(first_page_text: str) -> dict[str, str | None]:
    """Very small placeholder parser for future rule implementation."""
    dahir = None
    law = None

    dahir_match = re.search(r"\bDahir\s+n\s*([0-9][0-9.\-]*)", first_page_text, re.I)
    if dahir_match:
        dahir = dahir_match.group(1).replace(".", "-")

    law_match = re.search(r"\bLoi\s+n\s*([0-9][0-9.\-]*)", first_page_text, re.I)
    if law_match:
        law = law_match.group(1).replace(".", "-")

    return {"dahir_number": dahir, "law_number": law}


def build_canonical_record(law: dict[str, Any], first_page_text: str) -> dict[str, Any]:
    numbers = detect_numbers(first_page_text)
    flags: list[str] = []
    evidence: list[Evidence] = []

    formal_type = law.get("type")
    if re.search(r"\bDahir\b", first_page_text, re.I):
        formal_type = "Dahir"
        evidence.append(Evidence("formal_instrument_type", "Dahir", "pdf_page_1", 1, "Dahir", 95))

    subject_type = "Loi" if numbers.get("law_number") else law.get("type")
    official_number = numbers.get("law_number") or law.get("number")

    if numbers.get("dahir_number") and numbers.get("law_number"):
        if law.get("number") == numbers["dahir_number"]:
            flags.append("law_number_dahir_number_confused")

    if numbers.get("law_number"):
        evidence.append(Evidence("law_number", numbers["law_number"], "pdf_page_1", 1, "Loi n ...", 98))

    score = 95 if not flags else 82

    return {
        "law_id": law.get("id"),
        "canonical_validation_status": "high_confidence" if score >= 85 else "low_confidence",
        "canonical_confidence_score": score,
        "official_title_fr": law.get("title_fr"),
        "official_title_ar": law.get("title_ar"),
        "formal_instrument_type": formal_type,
        "subject_text_type": subject_type,
        "official_number": official_number,
        "dahir_number": numbers.get("dahir_number"),
        "law_number": numbers.get("law_number"),
        "source_priority": "pdf_page_1",
        "flags": flags,
        "evidence": [asdict(item) for item in evidence],
    }


def diff_metadata(law: dict[str, Any], canonical: dict[str, Any]) -> dict[str, Any]:
    diffs: list[dict[str, Any]] = []
    comparisons = [
        ("type", "formal_instrument_type"),
        ("number", "official_number"),
        ("title_fr", "official_title_fr"),
    ]
    for current_field, proposed_field in comparisons:
        current = law.get(current_field)
        proposed = canonical.get(proposed_field)
        if proposed and current != proposed:
            diffs.append(
                {
                    "field": current_field,
                    "current_value": current,
                    "proposed_value": proposed,
                    "severity": "critical" if current_field in {"type", "number"} else "warning",
                    "action": "review",
                }
            )
    return {"law_id": law.get("id"), "diffs": diffs, "safe_to_auto_update": not diffs}


def audit(law: dict[str, Any], first_page_text: str) -> dict[str, Any]:
    canonical = build_canonical_record(law, first_page_text)
    diff = diff_metadata(law, canonical)
    critical = any(item["severity"] == "critical" for item in diff["diffs"])
    return {
        "canonical_legal_record": canonical,
        "metadata_diff_report": diff,
        "consistency_audit_result": {
            "law_id": law.get("id"),
            "score": canonical["canonical_confidence_score"] - (20 if critical else 0),
            "decision": "review" if critical else "auto_update",
            "flags": [
                {
                    "code": flag,
                    "severity": "critical",
                    "message": "A human reviewer must confirm this legal identity issue.",
                    "field": None,
                }
                for flag in canonical["flags"]
            ],
            "blocking": False,
            "auto_update_allowed": not critical,
        },
    }


if __name__ == "__main__":
    sample_law = {
        "id": 123,
        "type": "Loi",
        "number": "1-24-00",
        "title_fr": "Loi n 59-24 relative a un dispositif de soutien",
        "title_ar": "[titre arabe officiel extrait du PDF]",
    }
    sample_first_page = "Dahir n 1-24-00 portant promulgation de la Loi n 59-24"
    print(json.dumps(audit(sample_law, sample_first_page), ensure_ascii=False, indent=2))

