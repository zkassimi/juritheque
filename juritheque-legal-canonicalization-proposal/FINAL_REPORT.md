# Rapport final

## Ce qui a ete fait

Un audit lecture seule du projet `lexbase` a ete realise, puis un dossier isole
`juritheque-legal-canonicalization-proposal/` a ete cree. Aucun fichier du
projet existant n'a ete modifie. Aucune migration, aucun serveur et aucune
ecriture en base n'ont ete lances.

## Ce qui existe deja dans JuriTheque

Le projet dispose deja de briques solides :

- extraction PDF avec `pdfplumber`, PyMuPDF et OCR optionnel dans `extract.py`;
- crawl SGG avec PDF officiel ;
- crawl Adala avec couverture large ;
- import queue et pipeline semi-automatise ;
- enrichissement IA : resumes, TOC, articles, mots-cles, SEO ;
- scores multidimensionnels ;
- `pipeline_runs` ;
- admin qualite, pipeline, veille et signalements ;
- page publique avec PDF, TOC, SEO, JSON-LD et badge qualite ;
- `slug_history` pour les redirections.

## Probleme principal

L'identite juridique officielle n'est pas encore arbitree par une couche unique.
Les champs `type`, `number`, `date`, `title_fr`, `title_ar`, `bo_date` et
`canonical_slug` peuvent etre derives de scripts differents, avec des niveaux de
preuve differents.

Cela peut creer des erreurs de fond :

- confusion Dahir/Loi ;
- confusion numero dahir/numero loi ;
- confusion date signature/date BO ;
- titre fiche different du titre PDF ;
- SEO et resumes produits avant validation juridique.

## Architecture proposee

Ajouter un moteur `LEGAL_DOCUMENT_CANONICALIZATION_ENGINE` qui produit :

- `canonical_legal_record`;
- `metadata_diff_report`;
- `consistency_audit_result`;
- `human_review_item` si necessaire.

Ce moteur doit s'executer avant :

- generation du slug ;
- generation des resumes ;
- generation SEO ;
- publication/indexation ;
- index RAG.

## Fichiers crees

Documents obligatoires :

- `README.md`
- `PROJECT_AUDIT.md`
- `EXISTING_PIPELINE_MAP.md`
- `PROPOSED_CANONICAL_PIPELINE.md`
- `DATABASE_SCHEMA_PROPOSAL.md`
- `LEGAL_RULES.md`
- `CONSISTENCY_AUDIT_RULES.md`
- `INTEGRATION_PLAN.md`
- `BACKFILL_AND_AUDIT_PLAN.md`
- `HUMAN_REVIEW_QUEUE.md`
- `DASHBOARD_PROPOSAL.md`
- `TEST_CASES.md`
- `SAMPLE_JSON_OUTPUTS.md`
- `FINAL_REPORT.md`

Fichiers supplementaires :

- schemas JSON ;
- exemples JSON ;
- prototype dry-run ;
- proposition SQL documentaire.

## Recommandation

Valider d'abord ce dossier, puis lancer un prototype dry-run sur un petit lot de
20 textes. Ne pas activer l'auto-correction au depart. La premiere version doit
se limiter a produire des diffs, des scores et des items de revue humaine.

La priorite est correcte : securiser l'identite juridique avant d'augmenter les
guides, le SEO et le RAG.

