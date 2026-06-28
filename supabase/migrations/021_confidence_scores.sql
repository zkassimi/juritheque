-- 021_confidence_scores.sql
-- Pipeline intelligent : 7 scores multidimensionnels + table pipeline_runs.
-- Toutes les colonnes avec DEFAULT NULL → aucun impact sur les données existantes.

-- ── Scores sur la table laws ─────────────────────────────────────────────────

ALTER TABLE laws
  ADD COLUMN IF NOT EXISTS source_confidence       SMALLINT DEFAULT NULL
    CHECK (source_confidence       BETWEEN 0 AND 100),
  ADD COLUMN IF NOT EXISTS metadata_score          SMALLINT DEFAULT NULL
    CHECK (metadata_score          BETWEEN 0 AND 100),
  ADD COLUMN IF NOT EXISTS duplicate_score         SMALLINT DEFAULT NULL
    CHECK (duplicate_score         BETWEEN 0 AND 100),
  ADD COLUMN IF NOT EXISTS legal_status_score      SMALLINT DEFAULT NULL
    CHECK (legal_status_score      BETWEEN 0 AND 100),
  ADD COLUMN IF NOT EXISTS summary_score           SMALLINT DEFAULT NULL
    CHECK (summary_score           BETWEEN 0 AND 100),
  ADD COLUMN IF NOT EXISTS seo_score               SMALLINT DEFAULT NULL
    CHECK (seo_score               BETWEEN 0 AND 100),
  ADD COLUMN IF NOT EXISTS global_confidence_score SMALLINT DEFAULT NULL
    CHECK (global_confidence_score BETWEEN 0 AND 100),
  ADD COLUMN IF NOT EXISTS pipeline_mode           TEXT DEFAULT NULL
    CHECK (pipeline_mode IN ('auto','semi','manual')),
  ADD COLUMN IF NOT EXISTS last_pipeline_run       TIMESTAMPTZ DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS pipeline_notes          TEXT DEFAULT NULL;

-- Index pour filtres qualité dans l'Admin
CREATE INDEX IF NOT EXISTS idx_laws_global_confidence ON laws(global_confidence_score);
CREATE INDEX IF NOT EXISTS idx_laws_pipeline_mode     ON laws(pipeline_mode);

-- ── Table pipeline_runs (logs des exécutions) ─────────────────────────────────

CREATE TABLE IF NOT EXISTS pipeline_runs (
  id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  started_at       TIMESTAMPTZ DEFAULT now(),
  finished_at      TIMESTAMPTZ,
  mode             TEXT CHECK (mode IN ('auto','semi','manual')),
  sources          TEXT[],
  dry_run          BOOLEAN DEFAULT false,
  -- Résultats compteurs
  sources_checked  INTEGER DEFAULT 0,
  items_detected   INTEGER DEFAULT 0,
  items_imported   INTEGER DEFAULT 0,
  items_published  INTEGER DEFAULT 0,
  items_draft      INTEGER DEFAULT 0,
  items_review     INTEGER DEFAULT 0,
  items_rejected   INTEGER DEFAULT 0,
  errors           INTEGER DEFAULT 0,
  warnings         INTEGER DEFAULT 0,
  ai_cost_usd      NUMERIC(8,4) DEFAULT 0,
  duration_seconds INTEGER DEFAULT 0,
  -- Détail complet en JSON
  report_json      JSONB,
  status           TEXT DEFAULT 'running'
    CHECK (status IN ('running','done','failed','cancelled'))
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started ON pipeline_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status  ON pipeline_runs(status);

-- RLS : admins et editors lisent, service_role (pipeline) écrit via bypass
ALTER TABLE pipeline_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "admin_editor_read_pipeline_runs"
  ON pipeline_runs FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role IN ('admin','editor')
    )
  );
