-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration 009 — site_search_index
-- Table d'index léger pour l'assistant IA et la recherche interne.
-- Indexe les lois, guides SEO, domaines et pages statiques sans stocker
-- le texte intégral (content_fr / content_ar).
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS site_search_index (
  id            bigserial PRIMARY KEY,
  source_type   text        NOT NULL CHECK (source_type IN ('law','guide','domain','static_page','watch')),
  source_id     text,                        -- ID loi (bigint as text), slug domaine/guide
  url           text        NOT NULL,        -- URL relative : /loi/123, /fr/guides/sarl-maroc
  title         text        NOT NULL,
  description   text,                        -- excerpt ou metaDescription
  summary       text,                        -- simple_summary_fr ou intro guide
  keywords      text[]      DEFAULT '{}',
  legal_domain  text,                        -- domain_id (civil, travail…)
  document_type text,                        -- Loi | Dahir | Guide | Domaine…
  language      text        DEFAULT 'fr',
  priority      numeric     DEFAULT 0.5,     -- 0.0 → 1.0
  is_public     boolean     DEFAULT true,
  updated_at    timestamptz DEFAULT now(),

  -- Full-text search français
  search_vector tsvector GENERATED ALWAYS AS (
    to_tsvector(
      'french',
      coalesce(title,       '') || ' ' ||
      coalesce(description, '') || ' ' ||
      coalesce(summary,     '') || ' ' ||
      coalesce(array_to_string(keywords, ' '), '')
    )
  ) STORED
);

-- ── Index ────────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS site_search_index_fts      ON site_search_index USING gin(search_vector);
CREATE INDEX IF NOT EXISTS site_search_index_type     ON site_search_index (source_type);
CREATE INDEX IF NOT EXISTS site_search_index_domain   ON site_search_index (legal_domain);
CREATE INDEX IF NOT EXISTS site_search_index_priority ON site_search_index (priority DESC);
CREATE INDEX IF NOT EXISTS site_search_index_public   ON site_search_index (is_public);

-- ── RLS ──────────────────────────────────────────────────────────────────────
ALTER TABLE site_search_index ENABLE ROW LEVEL SECURITY;

-- Lecture publique (is_public = true)
CREATE POLICY "public_read_site_search_index"
  ON site_search_index FOR SELECT
  USING (is_public = true);

-- Écriture réservée au service_role (pipeline Python)
CREATE POLICY "service_write_site_search_index"
  ON site_search_index FOR ALL
  USING (auth.role() = 'service_role');

-- ── Commentaires ─────────────────────────────────────────────────────────────
COMMENT ON TABLE  site_search_index             IS 'Index léger pour assistant IA — pas de texte intégral.';
COMMENT ON COLUMN site_search_index.source_type IS 'law | guide | domain | static_page | watch';
COMMENT ON COLUMN site_search_index.priority    IS '0.0 (faible) → 1.0 (haute). Calculé depuis extraction_confidence_score.';
COMMENT ON COLUMN site_search_index.summary     IS 'simple_summary_fr pour les lois, intro pour les guides. Jamais content_fr.';
