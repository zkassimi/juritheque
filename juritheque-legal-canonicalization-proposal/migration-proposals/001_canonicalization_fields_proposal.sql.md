# Migration proposee - documentaire uniquement

Ce fichier n'est pas une migration active. Ne pas l'executer sans validation.

```sql
ALTER TABLE laws
  ADD COLUMN IF NOT EXISTS canonical_validation_status TEXT DEFAULT 'unverified'
    CHECK (canonical_validation_status IN (
      'unverified',
      'metadata_only',
      'low_confidence',
      'high_confidence',
      'verified',
      'rejected'
    )),
  ADD COLUMN IF NOT EXISTS canonical_confidence_score SMALLINT
    CHECK (canonical_confidence_score BETWEEN 0 AND 100),
  ADD COLUMN IF NOT EXISTS canonicalized_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS canonicalized_by TEXT,
  ADD COLUMN IF NOT EXISTS canonical_source_priority TEXT,
  ADD COLUMN IF NOT EXISTS canonical_record_hash TEXT,
  ADD COLUMN IF NOT EXISTS official_title_fr TEXT,
  ADD COLUMN IF NOT EXISTS official_title_ar TEXT,
  ADD COLUMN IF NOT EXISTS formal_instrument_type TEXT,
  ADD COLUMN IF NOT EXISTS subject_text_type TEXT,
  ADD COLUMN IF NOT EXISTS official_number TEXT,
  ADD COLUMN IF NOT EXISTS dahir_number TEXT,
  ADD COLUMN IF NOT EXISTS law_number TEXT,
  ADD COLUMN IF NOT EXISTS signature_date DATE,
  ADD COLUMN IF NOT EXISTS bo_publication_date DATE,
  ADD COLUMN IF NOT EXISTS legal_effective_date_detected DATE,
  ADD COLUMN IF NOT EXISTS pdf_text_hash TEXT,
  ADD COLUMN IF NOT EXISTS pdf_first_page_hash TEXT,
  ADD COLUMN IF NOT EXISTS pdf_page_count INTEGER,
  ADD COLUMN IF NOT EXISTS source_pdf_url_resolved TEXT,
  ADD COLUMN IF NOT EXISTS metadata_diff_summary JSONB,
  ADD COLUMN IF NOT EXISTS legal_flags TEXT[] DEFAULT '{}';

CREATE INDEX IF NOT EXISTS idx_laws_canonical_validation_status
  ON laws(canonical_validation_status);

CREATE INDEX IF NOT EXISTS idx_laws_canonical_confidence_score
  ON laws(canonical_confidence_score);

CREATE INDEX IF NOT EXISTS idx_laws_official_number
  ON laws(official_number);

CREATE INDEX IF NOT EXISTS idx_laws_legal_flags
  ON laws USING GIN(legal_flags);

CREATE TABLE IF NOT EXISTS legal_canonicalization_audits (
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

CREATE TABLE IF NOT EXISTS legal_human_review_queue (
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

