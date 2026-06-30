-- Migration 025 — Table audit_queue
-- Stocke les corrections proposées par l'audit canonique
-- pour validation manuelle dans Admin → Corrections.

CREATE TABLE IF NOT EXISTS audit_queue (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  law_id      INTEGER NOT NULL,
  law_title   TEXT,
  law_number  TEXT,
  field       TEXT NOT NULL,        -- 'number' | 'date' | 'type' | 'title_fr'
  current_val TEXT,
  proposed    TEXT,
  severity    TEXT NOT NULL DEFAULT 'warning',  -- 'critical' | 'warning'
  decision    TEXT NOT NULL DEFAULT 'review',   -- 'review' | 'review_high_priority' | 'block'
  score       INTEGER,
  flags       TEXT[],
  pdf_source  TEXT,
  status      TEXT NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending', 'approved', 'rejected', 'applied')),
  created_at  TIMESTAMPTZ DEFAULT now(),
  reviewed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_aq_law_id  ON audit_queue(law_id);
CREATE INDEX IF NOT EXISTS idx_aq_status  ON audit_queue(status);
CREATE INDEX IF NOT EXISTS idx_aq_severity ON audit_queue(severity);
CREATE INDEX IF NOT EXISTS idx_aq_field   ON audit_queue(field);

ALTER TABLE audit_queue ENABLE ROW LEVEL SECURITY;

-- Lecture et mise à jour pour les utilisateurs authentifiés (admins/editors)
CREATE POLICY "auth_read_audit_queue"
  ON audit_queue FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "auth_update_audit_queue"
  ON audit_queue FOR UPDATE
  USING (auth.role() = 'authenticated');

-- Insert et Delete réservés au service role (pipeline Python)
CREATE POLICY "service_insert_audit_queue"
  ON audit_queue FOR INSERT
  WITH CHECK (true);

CREATE POLICY "service_delete_audit_queue"
  ON audit_queue FOR DELETE
  USING (true);
