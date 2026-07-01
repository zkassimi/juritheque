# Regles d'audit de coherence

Le but est de detecter les incoherences avant correction automatique ou
publication.

## Niveaux de severite

- `info` : difference non bloquante.
- `warning` : a verifier, publication possible si score fort.
- `critical` : revue humaine obligatoire.
- `blocking` : ne pas publier/indexer avant resolution.

## Flags proposes

| Flag | Severite | Detection | Action |
| --- | --- | --- | --- |
| `title_mismatch_pdf_vs_record` | critical | titre PDF different du `title_fr/ar` DB | review |
| `type_mismatch_pdf_vs_record` | critical | PDF dit Dahir, DB dit Loi, ou inversement | review |
| `number_mismatch_pdf_vs_record` | critical | numero officiel different | review |
| `law_number_dahir_number_confused` | critical | numero de dahir stocke comme numero de loi | review |
| `date_mismatch_pdf_vs_record` | warning/critical | date DB differe des dates PDF | review |
| `bo_date_confused_with_signature_date` | warning | `date` egale BO alors que signature detectee | review |
| `source_pdf_missing` | warning | pas de PDF exploitable | metadata_only |
| `metadata_only_public` | warning | ligne publiee sans extraction texte | review |
| `low_extraction_text` | warning | contenu < seuil | OCR/review |
| `ocr_needed` | warning | PDF scanne ou texte faible | OCR |
| `arabic_garbled` | critical | arabe corrompu ou inverse | review/correction |
| `duplicate_official_number` | critical | meme numero sur plusieurs records incoherents | merge/review |
| `slug_not_based_on_canonical_identity` | info | slug hash ou trop generique | update apres validation |
| `seo_generated_before_validation` | warning | SEO present mais canonical non verifie | recalcul apres validation |
| `manual_field_conflict` | critical | patch auto toucherait un champ manuel | review |
| `public_indexing_too_risky` | blocking | score bas + indexable true | noindex/review |

## Scoring propose

Score initial : 100.

Penalites :

- PDF officiel absent : -20.
- Texte extrait < 500 caracteres : -15.
- Titre PDF absent : -10.
- Titre PDF vs DB divergent : -25.
- Type divergent : -25.
- Numero divergent : -30.
- Date divergente : -10 a -20 selon gravite.
- Confusion dahir/loi : -25.
- Ligne metadata_only : -20.
- Source non officielle : -20.
- OCR requis mais non fait : -15.
- Champ manuel en conflit : -30.

Bonus :

- PDF officiel SGG/BO analyse : +10, plafonne a 100.
- Fiche HTML et PDF coherents : +10, plafonne a 100.
- Titre FR et AR coherents : +5, plafonne a 100.
- Numero, type et date confirmes par deux sources : +10, plafonne a 100.

## Decisions

| Score | Decision | Effet |
| --- | --- | --- |
| 90-100 | `auto_update` possible | patch limite aux champs non manuels |
| 75-89 | `review` | pre-remplir proposition, humain valide |
| 50-74 | `review_high_priority` | pas de SEO/RAG definitif |
| 0-49 | `block` | noindex ou non publication jusqu'a correction |

## Regles speciales

### Conflit critique

Un conflit critique bloque l'auto-update meme si le score numerique est haut.

Conflits critiques :

- numero officiel different ;
- type formel different ;
- titre PDF manifestement different ;
- date FR/AR incompatible ;
- doublon de numero avec titres differents ;
- correction toucherait un champ manuel.

### Ligne Adala metadata_only

Une ligne Adala peut etre utile, mais ne doit pas etre declaree `verified` sans
analyse PDF ou validation humaine.

Decision cible :

- `canonical_validation_status = metadata_only`
- `needs_human_review = true`
- `is_publicly_indexable` selon politique SEO, mais avec badge qualite bas.

### SEO

`seo_title_fr`, `seo_description_fr`, `canonical_slug` et sitemap doivent etre
consideres "derives". Si la base canonique change, ils deviennent stale.

Flag : `derived_content_stale`.

