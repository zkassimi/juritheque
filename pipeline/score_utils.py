"""
score_utils.py — Scores de confiance multi-dimensionnels pour JuriThèque
=========================================================================
Calcule 7 scores (0-100) + un score global agrégé pour chaque texte importé.

Usage :
  from score_utils import compute_scores, apply_automation_rules

  scores = compute_scores(law_data)
  # → {"source_confidence": 85, "metadata_score": 90, ..., "global_confidence_score": 87}

  decision = apply_automation_rules(scores, mode="semi")
  # → {"publish": True, "needs_review": False, "pipeline_notes": "..."}
"""

import re

# ── Poids de chaque score dans le score global ─────────────────────────────
WEIGHTS = {
    "source_confidence":   0.20,   # Source officielle vérifiable ?
    "metadata_score":      0.25,   # Titre, numéro, date, domaine présents ?
    "duplicate_score":     0.15,   # Pas de doublon probable ?
    "legal_status_score":  0.15,   # Statut juridique détecté avec certitude ?
    "summary_score":       0.10,   # Résumé généré sur texte complet ?
    "seo_score":           0.10,   # SEO metadata complets ?
    "extraction_score":    0.05,   # Score d'extraction existant (normalisé)
}

# Seuils pour les règles d'automatisation
THRESHOLD_AUTO   = 85   # Score ≥ 85 → publication automatique
THRESHOLD_REVIEW = 70   # Score ≥ 70 → brouillon (pas de publication)
                        # Score < 70  → brouillon + flag review humaine


def compute_scores(law_data: dict) -> dict:
    """
    Calcule les 7 scores à partir des données d'un texte importé.

    Args:
        law_data: dict tel que construit par import_from_queue.py
                  (peut contenir des champs partiels — robuste aux None)

    Returns:
        dict avec source_confidence, metadata_score, duplicate_score,
        legal_status_score, summary_score, seo_score, global_confidence_score
    """
    scores = {}

    # ── 1. Source confidence (0-100) ─────────────────────────────────────────
    # Évalue si la source est officielle et vérifiable
    score = 0
    source_url = law_data.get("source_url") or law_data.get("pdf_url") or ""
    source_name = law_data.get("source_name") or ""

    if source_url:
        score += 40
        # Source gouvernementale marocaine = +30
        official_domains = [
            "sgg.gov.ma", "finances.gov.ma", "bkam.ma", "anrt.ma",
            "adala.justice.gov.ma", "chambredesrepresentants.ma",
            "mcinet.gov.ma", "cndp.ma", "lof.finances.gov.ma",
        ]
        if any(d in source_url for d in official_domains):
            score += 30
        # PDF hébergé chez nous (Storage) = +15 (preuve de récupération réelle)
        if "supabase" in source_url or "storage" in source_url.lower():
            score += 15
        # URL valide (https) = +15
        if source_url.startswith("https://"):
            score += 15
    elif source_name:
        score += 20  # Au moins on sait d'où ça vient
    scores["source_confidence"] = min(score, 100)

    # ── 2. Metadata score (0-100) ─────────────────────────────────────────────
    # Évalue la complétude des métadonnées
    score = 0
    title = law_data.get("title_fr") or ""
    number = law_data.get("number") or ""
    date_ = law_data.get("date") or law_data.get("bo_date") or ""
    domain = law_data.get("domain_id") or ""

    if title and len(title) > 10:
        score += 30
        if len(title) > 30:  # Titre descriptif = bonus
            score += 10
    if number and not re.match(r'^VEILLE-', number):  # Pas un fallback auto
        score += 25
    if date_:
        score += 20
    if domain and domain not in ("", "administratif"):  # Domaine bien détecté
        score += 10
    if law_data.get("title_ar"):
        score += 5
    scores["metadata_score"] = min(score, 100)

    # ── 3. Duplicate score (0-100) ────────────────────────────────────────────
    # 100 = pas de risque doublon détecté, 0 = doublon certain
    # Note : si on est ici, la vérification doublon a déjà passé dans import_from_queue.
    # Ce score est une estimation de la robustesse de l'unicité.
    score = 100
    if not number or re.match(r'^VEILLE-', number):
        score -= 30  # Sans numéro officiel, identification incertaine
    if not (law_data.get("canonical_slug")):
        score -= 20  # Sans slug, risque de collision
    if re.search(r'\d{4}$', number or ""):  # Numéro court = risque homonymes
        score -= 10
    scores["duplicate_score"] = max(score, 0)

    # ── 4. Legal status score (0-100) ─────────────────────────────────────────
    # Évalue si le statut juridique est correctement déterminé
    score = 0
    status = law_data.get("status") or ""
    law_type = law_data.get("type") or ""

    VALID_STATUSES = ["En vigueur", "Abrogé", "Modifié", "Suspendu", "Projet"]
    VALID_TYPES = [
        "Loi", "Dahir", "Décret", "Arrêté", "Circulaire", "Code",
        "Ordonnance", "Décision", "Texte réglementaire", "Convention"
    ]
    if status in VALID_STATUSES:
        score += 40
    if law_type in VALID_TYPES:
        score += 40
    if date_:
        score += 20  # Date = on peut vérifier si c'est encore en vigueur
    scores["legal_status_score"] = min(score, 100)

    # ── 5. Summary score (0-100) ──────────────────────────────────────────────
    # Évalue la qualité du résumé (sera mis à jour après enrichissement)
    score = 0
    summary = law_data.get("simple_summary_fr") or ""
    content = law_data.get("content_fr") or ""

    if summary:
        if len(summary) > 100:
            score += 60
        if len(summary) > 300:
            score += 20  # Résumé substantiel
        if content and len(summary) > 50:
            score += 20  # Résumé présent ET texte source présent
    elif content:
        score = 20  # Au moins le texte est là (résumé à générer)
    scores["summary_score"] = min(score, 100)

    # ── 6. SEO score (0-100) ─────────────────────────────────────────────────
    # Évalue la complétude des métadonnées SEO
    score = 0
    slug = law_data.get("canonical_slug") or ""

    if slug and len(slug) > 5 and not slug.startswith("texte-juridique-"):
        score += 40
    elif slug:
        score += 15  # Slug minimal
    if law_data.get("seo_title_fr"):
        score += 20
    if law_data.get("seo_description_fr"):
        score += 20
    if law_data.get("legal_keywords") or law_data.get("tags"):
        score += 20
    scores["seo_score"] = min(score, 100)

    # ── 7. Extraction score (normalisé depuis extraction_confidence_score) ─────
    extraction_raw = law_data.get("extraction_confidence_score")
    if extraction_raw is not None:
        scores["extraction_score"] = int(extraction_raw)
    else:
        # Estimer depuis la quantité de texte extrait
        content_len = len(law_data.get("content_fr") or "")
        if content_len > 5000:
            scores["extraction_score"] = 75
        elif content_len > 1000:
            scores["extraction_score"] = 50
        elif content_len > 100:
            scores["extraction_score"] = 30
        else:
            scores["extraction_score"] = 10

    # ── Score global (moyenne pondérée) ───────────────────────────────────────
    global_score = sum(
        scores[k] * w
        for k, w in WEIGHTS.items()
        if k in scores
    )
    scores["global_confidence_score"] = round(global_score)

    return scores


def apply_automation_rules(scores: dict, mode: str = "semi") -> dict:
    """
    Applique les règles d'automatisation selon le mode d'exécution.

    Args:
        scores: dict retourné par compute_scores()
        mode: "auto" | "semi" | "manual"
            - auto   : publie automatiquement si score ≥ THRESHOLD_AUTO
            - semi   : prépare les données mais n'auto-publie pas
            - manual : prépare uniquement, review humaine systématique

    Returns:
        dict avec les champs à écrire en base :
          - is_publicly_indexable (bool)
          - needs_human_review (bool)
          - pipeline_mode (str)
          - pipeline_notes (str)
    """
    g = scores.get("global_confidence_score", 0)
    notes_parts = []

    # Détails des scores pour les notes
    score_summary = (
        f"src={scores.get('source_confidence', 0)} "
        f"meta={scores.get('metadata_score', 0)} "
        f"dup={scores.get('duplicate_score', 0)} "
        f"status={scores.get('legal_status_score', 0)} "
        f"sum={scores.get('summary_score', 0)} "
        f"seo={scores.get('seo_score', 0)} "
        f"-> global={g}"
    )
    notes_parts.append(f"[{mode.upper()}] {score_summary}")

    if mode == "auto":
        if g >= THRESHOLD_AUTO:
            publish = True
            review = False
            notes_parts.append("Auto-publié (score ≥ 85)")
        elif g >= THRESHOLD_REVIEW:
            publish = False
            review = False
            notes_parts.append("Brouillon (score 70-84 — enrichissement en attente)")
        else:
            publish = False
            review = True
            notes_parts.append(f"Review requise (score < 70)")

    elif mode == "semi":
        # En mode semi : jamais auto-publish, mais on flag ce qui est prêt
        publish = False
        review = g < THRESHOLD_REVIEW
        if g >= THRESHOLD_AUTO:
            notes_parts.append("Prêt à publier (score ≥ 85 — validation manuelle requise)")
        elif g >= THRESHOLD_REVIEW:
            notes_parts.append("À enrichir puis valider (score 70-84)")
        else:
            notes_parts.append("Review requise (score < 70)")

    else:  # manual
        publish = False
        review = True
        notes_parts.append("Review systématique (mode manuel)")

    return {
        "is_publicly_indexable": publish,
        "needs_human_review": review,
        "pipeline_mode": mode,
        "pipeline_notes": " | ".join(notes_parts),
    }


def scores_to_db_fields(scores: dict) -> dict:
    """Formate les scores pour l'écriture dans Supabase (colnames sans 'extraction_score')."""
    return {
        "source_confidence":       scores.get("source_confidence"),
        "metadata_score":          scores.get("metadata_score"),
        "duplicate_score":         scores.get("duplicate_score"),
        "legal_status_score":      scores.get("legal_status_score"),
        "summary_score":           scores.get("summary_score"),
        "seo_score":               scores.get("seo_score"),
        "global_confidence_score": scores.get("global_confidence_score"),
    }
