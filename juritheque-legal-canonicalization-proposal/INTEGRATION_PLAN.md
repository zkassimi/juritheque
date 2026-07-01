# Plan d'integration futur

Ce plan est volontairement prudent. Aucune etape n'est executee dans cette
proposition.

## Phase 0 - Validation humaine du design

1. Relire cette proposition.
2. Valider la strategie de champs : hybride `laws` + tables d'audit.
3. Valider les seuils de score.
4. Choisir une petite liste de textes pilotes.

Livrable : decision "go/no-go" sur le moteur canonique.

## Phase 1 - Prototype dry-run

Fichiers futurs possibles :

- `lexbase/pipeline/legal_canonicalization/engine.py`
- `lexbase/pipeline/legal_canonicalization/pdf_extractors.py`
- `lexbase/pipeline/legal_canonicalization/rules.py`
- `lexbase/pipeline/legal_canonicalization/schemas.py`
- `lexbase/pipeline/audit_existing_legal_records.py`

Contraintes :

- lecture seule DB ;
- sortie JSON locale ;
- aucun patch Supabase ;
- tests sur 10 a 30 textes.

## Phase 2 - Migration idempotente

Creer les tables/colonnes proposees dans une migration dediee :

- `legal_canonicalization_audits`;
- `legal_human_review_queue`;
- colonnes minimales sur `laws`.

Rollback :

- ne pas supprimer les colonnes existantes ;
- desactiver l'utilisation frontend/pipeline suffit ;
- les tables d'audit peuvent rester dormantes.

## Phase 3 - Insertion dans import pipeline

Modifier plus tard :

- `import_from_queue.py` : canonicaliser avant `insert_law()`.
- `crawl_sgg.py` : canonicaliser avant construction du record.
- `crawl_adala.py` : canonicaliser si PDF accessible, sinon creer review item.
- `extract.py` : reutiliser l'objet canonique pour structurer la sortie IA.

Mode initial :

- `--dry-run` obligatoire ;
- `--mode manual` ou `semi` seulement ;
- auto-update desactive.

## Phase 4 - Enrichissement post-validation

Modifier plus tard :

- `enrich.py` doit verifier `canonical_validation_status`.
- `generate_sitemap.py` doit ignorer ou noindex les textes bloques.
- `build_site_search_index.py` doit exclure les textes non valides pour le RAG.

Regle :

SEO, resume et RAG apres validation, pas avant.

## Phase 5 - Admin

Modifier plus tard :

- `Admin.jsx` : nouvelle section "Controle juridique".
- API helper dans `src/lib/api.js` ou appels Supabase directs.
- Vues :
  - files `pending`;
  - diffs fiche vs PDF ;
  - preuves par champ ;
  - boutons approve/reject/needs_source.

## Phase 6 - Backfill progressif

1. Audit dry-run sur 50 textes.
2. Rapport manuel.
3. Auto-correction uniquement score >= 95 et aucune alerte critique.
4. Review manuelle pour le reste.
5. Extension par lots de 500.

## Risques

- Risque juridique : corriger automatiquement un champ officiel faux.
- Risque SEO : changement massif de slugs.
- Risque UX : trop de textes basculent en review/noindex.
- Risque cout : OCR/IA sur milliers de PDF.
- Risque source : serveurs officiels bloquent les telechargements.

## Mitigations

- Dry-run avant tout.
- Lots petits.
- Conservation `slug_history`.
- Pas d'ecrasement des champs manuels.
- `metadata_diff` auditable.
- Separateur strict entre preuve PDF et inference IA.

## Definition of done

Le chantier est pret si :

- les schemas JSON sont stables ;
- un lot pilote produit des diffs utiles ;
- l'admin permet de valider/rejeter ;
- les corrections sont reversibles ;
- les pages publiques affichent seulement des donnees assez fiables ;
- aucun contenu RAG n'utilise des textes bloques.

