# Proposition de schema de donnees

Ce document n'est pas une migration active. Il decrit les champs a ajouter ou a
normaliser plus tard, apres validation humaine et tests.

## Strategie

Ne pas casser la table `laws`. Ajouter une couche de canonicalisation qui peut
cohabiter avec les champs existants.

Deux options :

1. Colonnes supplementaires sur `laws` pour les champs les plus consultes.
2. Tables dediees pour audit, diffs et revue humaine.

Recommandation : option hybride.

## Colonnes proposees sur `laws`

| Champ | Type SQL propose | But | Index |
| --- | --- | --- | --- |
| `canonical_validation_status` | text | `unverified`, `metadata_only`, `low_confidence`, `high_confidence`, `verified`, `rejected` | oui |
| `canonical_confidence_score` | smallint | score 0-100 propre a l'identite juridique | oui |
| `canonicalized_at` | timestamptz | derniere canonicalisation | non |
| `canonicalized_by` | text | `pipeline`, `human`, `backfill`, `import` | non |
| `canonical_source_priority` | text | source gagnante : `pdf_page_1`, `official_html`, etc. | non |
| `canonical_record_hash` | text | hash de l'objet canonique | oui |
| `official_title_fr` | text | titre officiel arbitre FR | oui, optionnel |
| `official_title_ar` | text | titre officiel arbitre AR | oui, optionnel |
| `formal_instrument_type` | text | type du document publie, ex. `Dahir` | oui |
| `subject_text_type` | text | type du texte promulgue, ex. `Loi` | oui |
| `official_number` | text | numero principal pour la fiche publique | oui |
| `dahir_number` | text | numero du dahir si present | oui |
| `law_number` | text | numero de loi si distinct | oui |
| `signature_date` | date | date de signature/promulgation | oui |
| `bo_publication_date` | date | date de publication au BO | oui |
| `legal_effective_date_detected` | date | entree en vigueur detectee si explicite | oui |
| `pdf_text_hash` | text | hash texte PDF extrait | oui |
| `pdf_first_page_hash` | text | hash premiere page | non |
| `pdf_page_count` | integer | nombre de pages | non |
| `source_pdf_url_resolved` | text | PDF officiel effectivement analyse | non |
| `metadata_diff_summary` | jsonb | dernier diff synthetique | gin optionnel |
| `legal_flags` | text[] | flags courts : `title_mismatch`, `date_conflict` | gin |

## Table `legal_canonicalization_audits`

Historique complet des audits.

```sql
CREATE TABLE legal_canonicalization_audits (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  law_id BIGINT REFERENCES laws(id) ON DELETE CASCADE,
  run_id UUID REFERENCES pipeline_runs(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  mode TEXT CHECK (mode IN ('import','backfill','manual','dry_run')),
  source_name TEXT,
  source_url TEXT,
  pdf_url TEXT,
  canonical_record JSONB NOT NULL,
  metadata_diff JSONB NOT NULL,
  consistency_result JSONB NOT NULL,
  proposed_patch JSONB,
  applied_patch JSONB,
  decision TEXT CHECK (decision IN ('auto_update','review','block','no_change')),
  reviewer_id UUID,
  reviewer_notes TEXT
);
```

Index proposes :

```sql
CREATE INDEX idx_lca_law_id ON legal_canonicalization_audits(law_id);
CREATE INDEX idx_lca_created ON legal_canonicalization_audits(created_at DESC);
CREATE INDEX idx_lca_decision ON legal_canonicalization_audits(decision);
CREATE INDEX idx_lca_flags ON legal_canonicalization_audits USING GIN ((consistency_result->'flags'));
```

## Table `legal_human_review_queue`

File explicite de revue humaine juridique.

```sql
CREATE TABLE legal_human_review_queue (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  law_id BIGINT REFERENCES laws(id) ON DELETE CASCADE,
  audit_id UUID REFERENCES legal_canonicalization_audits(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  priority SMALLINT DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
  status TEXT DEFAULT 'pending'
    CHECK (status IN ('pending','in_review','approved','rejected','needs_source')),
  reason TEXT NOT NULL,
  flags TEXT[] DEFAULT '{}',
  current_metadata JSONB NOT NULL,
  proposed_metadata JSONB NOT NULL,
  evidence JSONB,
  assigned_to UUID,
  reviewed_by UUID,
  reviewed_at TIMESTAMPTZ,
  resolution_notes TEXT
);
```

Index proposes :

```sql
CREATE INDEX idx_lhrq_status_priority ON legal_human_review_queue(status, priority);
CREATE INDEX idx_lhrq_law_id ON legal_human_review_queue(law_id);
CREATE INDEX idx_lhrq_flags ON legal_human_review_queue USING GIN(flags);
```

## Relation avec les champs existants

Champs existants a conserver :

- `number`, `type`, `date`, `title_fr`, `title_ar` restent les champs publics
  de compatibilite.
- `bo_number`, `bo_date`, `source_name`, `source_url`, `pdf_url` restent utiles.
- `verification_status` continue a representer la verification editoriale.
- `global_confidence_score` reste un score general pipeline.

Nouveaux champs proposes :

- `canonical_confidence_score` mesure seulement l'identite juridique.
- `canonical_validation_status` pilote la publication SEO/RAG.
- `metadata_diff_summary` donne au frontend/admin le dernier diagnostic.

## Contraintes recommandees

- `canonical_confidence_score BETWEEN 0 AND 100`.
- `canonical_validation_status` enum controle.
- Ne jamais rendre `official_title_fr` obligatoire au debut.
- Ne jamais supprimer les anciens champs.
- Conserver `slug_history` a chaque changement de `canonical_slug`.
- Ajouter une policy RLS : lecture admin/editor uniquement pour audits et review.

## Migration future

La migration future doit etre idempotente :

- `ADD COLUMN IF NOT EXISTS`.
- tables creees avec `CREATE TABLE IF NOT EXISTS`.
- index avec `CREATE INDEX IF NOT EXISTS`.
- aucun `DROP`.
- aucun backfill automatique dans la migration.

