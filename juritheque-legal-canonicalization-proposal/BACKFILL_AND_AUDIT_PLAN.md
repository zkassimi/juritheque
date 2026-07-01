# Plan de backfill et audit

Objectif : auditer les lignes `laws` existantes sans casser la base, puis
corriger progressivement les metadonnees critiques.

## Script futur

Nom propose : `audit_existing_legal_records.py`.

Mode par defaut :

```bash
python -X utf8 pipeline/audit_existing_legal_records.py --dry-run --limit 50
```

Modes futurs :

- `--dry-run` : aucun patch DB.
- `--id 123` : un texte.
- `--source Adala` : source cible.
- `--low-score-only` : textes a risque.
- `--write-audits` : ecrit seulement les audits, pas les corrections.
- `--apply-safe-patches` : applique uniquement les patches score >= 95.

## Selection prioritaire

Ordre recommande :

1. textes publics avec `global_confidence_score < 70`;
2. `needs_human_review = true`;
3. `metadata_only`;
4. textes sans `pdf_url` et sans `source_url`;
5. titres FR dupliques ;
6. slugs hash/generiques ;
7. textes tres consultes (`views` eleve) ;
8. textes utilises par pages SEO/guides.

## Champs analyses

- `id`
- `number`
- `type`
- `date`
- `title_fr`
- `title_ar`
- `content_fr`
- `content_ar`
- `pdf_url`
- `source_url`
- `source_name`
- `bo_number`
- `bo_date`
- `canonical_slug`
- `slug_history`
- `simple_summary_fr`
- `seo_title_fr`
- `seo_description_fr`
- `extraction_confidence_score`
- `global_confidence_score`
- `needs_human_review`
- `is_publicly_indexable`
- `verification_status`

## Etapes par ligne

1. Charger la ligne.
2. Resoudre le PDF.
3. Extraire premiere page.
4. OCR si necessaire.
5. Extraire identite juridique.
6. Construire `canonical_legal_record`.
7. Comparer avec la DB.
8. Calculer score et flags.
9. Produire patch propose.
10. Ecrire audit ou review item selon mode.

## Auto-correction autorisee

Uniquement si :

- source PDF officielle ;
- score >= 95 ;
- aucun flag `critical` ou `blocking` ;
- champ cible non manuel ;
- ancien slug conserve dans `slug_history` ;
- patch limite a un petit ensemble : `official_*`, `canonical_*`,
  `metadata_diff_summary`, scores.

Pour les champs publics `number`, `type`, `date`, `title_fr`, l'auto-update
doit etre encore plus strict ou necessiter validation humaine au debut.

## Review humaine obligatoire

Cas obligatoires :

- Dahir vs Loi confus ;
- numero PDF different du numero DB ;
- titre PDF et titre DB parlent de sujets differents ;
- date FR/AR contradictoire ;
- PDF absent ;
- source non officielle ;
- doublon de numero ;
- changement de slug d'une page indexee ;
- champ modifie manuellement.

## Sorties de rapport

Chaque run produit :

- `audit_summary.json`
- `safe_patches_preview.json`
- `human_review_queue_preview.json`
- `blocking_issues.csv`
- `slug_changes_preview.csv`

Dans cette proposition, les exemples sont dans `examples/`.

## Lot pilote recommande

Demarrer avec 20 textes :

- 5 SGG recents ;
- 5 Adala metadata_only ;
- 5 textes a score faible ;
- 3 textes avec slugs suspects ;
- 2 textes tres consultes.

Critere de succes : les auditeurs humains comprennent rapidement pourquoi un
champ est propose ou bloque.

