# JuriTheque - proposition de canonicalisation juridique

Ce dossier est une proposition isolee. Il ne modifie pas le projet existant
`lexbase`, ne lance aucune migration, ne demarre aucun serveur et n'ecrit pas en
base de donnees.

## Probleme constate

Le projet dispose deja d'un pipeline riche : crawl SGG, crawl Adala, import de
veille, extraction PDF, OCR partiel, enrichissement IA, scores, slugs, SEO,
admin qualite et pipeline runs. Le risque principal n'est donc pas l'absence de
pipeline, mais l'absence d'un objet canonique juridique unique qui arbitre les
metadonnees avant publication.

Les erreurs probables sont classiques pour une base juridique bilingue :

- titre de fiche different du titre PDF officiel ;
- `Dahir` confondu avec `Loi` ou inversement ;
- `Code` utilise comme type alors que c'est souvent un titre usuel ;
- date de promulgation confondue avec date de publication au BO ;
- numero du dahir confondu avec numero de loi ;
- lignes Adala en `metadata_only` publiees avec confiance faible ;
- slugs et SEO generes avant validation juridique complete.

## Objectif

Introduire un futur moteur `LEGAL_DOCUMENT_CANONICALIZATION_ENGINE` qui produit
un `canonical_legal_record` avant enrichissement SEO/RAG. Ce moteur compare la
fiche existante, le PDF officiel, la source et les metadonnees extraites. Il
decide ensuite :

- correction automatique seulement si la confiance est tres haute ;
- file de revue humaine si les signaux sont contradictoires ;
- blocage SEO/indexation si le texte est trop incertain ;
- conservation des anciennes valeurs dans un audit diff.

## Contenu du dossier

- `PROJECT_AUDIT.md` : audit lecture seule du projet existant.
- `EXISTING_PIPELINE_MAP.md` : carte source -> PDF -> DB -> page publique.
- `PROPOSED_CANONICAL_PIPELINE.md` : architecture cible.
- `DATABASE_SCHEMA_PROPOSAL.md` : champs proposes, sans migration active.
- `LEGAL_RULES.md` : regles juridiques marocaines utiles.
- `CONSISTENCY_AUDIT_RULES.md` : drapeaux de coherence et scoring.
- `INTEGRATION_PLAN.md` : plan d'integration futur, prudent et reversible.
- `BACKFILL_AND_AUDIT_PLAN.md` : audit des donnees existantes.
- `HUMAN_REVIEW_QUEUE.md` : specification de la file de revue humaine.
- `DASHBOARD_PROPOSAL.md` : proposition d'interface admin qualite juridique.
- `TEST_CASES.md` : cas de test metier.
- `SAMPLE_JSON_OUTPUTS.md` : exemples de sorties JSON.
- `FINAL_REPORT.md` : synthese finale.
- `schemas/` : schemas JSON proposes.
- `examples/` : exemples JSON valides.
- `prototype/` : prototype non integre et non destructif.
- `migration-proposals/` : SQL documentaire uniquement.

## Decision recommandee

Priorite haute : traiter cette proposition avant d'augmenter massivement la
production de guides ou de contenus RAG. Une base juridique fausse ou confuse
empoisonne ensuite les resumes, les pages SEO, les liens internes et les
reponses IA.

