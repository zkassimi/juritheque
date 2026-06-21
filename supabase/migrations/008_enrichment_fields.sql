-- ============================================================
-- Migration 008 — Champs d'enrichissement des textes juridiques
-- ============================================================
-- Ajoute les champs pour :
--   • résumé simple (FR + AR)
--   • sommaire structuré (FR + AR)
--   • compteurs d'articles
--   • articles importants
--   • mots-clés juridiques
--   • champs SEO personnalisés
--   • score et statut de qualité d'extraction
--   • drapeaux de contrôle (review, publication, protection)
--
-- SÉCURITÉ : ne supprime ni content_fr ni content_ar.
-- Toutes les colonnes utilisent ADD COLUMN IF NOT EXISTS.
-- ============================================================

ALTER TABLE public.laws
  -- Résumés simples
  ADD COLUMN IF NOT EXISTS simple_summary_fr       text,
  ADD COLUMN IF NOT EXISTS simple_summary_ar       text,

  -- Sommaire structuré (JSON : { sections: [{titre, articles, resume}], textes_lies: [], notes: '' })
  ADD COLUMN IF NOT EXISTS table_of_contents_fr    jsonb,
  ADD COLUMN IF NOT EXISTS table_of_contents_ar    jsonb,

  -- Compteurs d'articles
  ADD COLUMN IF NOT EXISTS detected_article_count  integer,
  ADD COLUMN IF NOT EXISTS public_article_count    integer,

  -- Articles importants (JSON : [{number, title, text}])
  ADD COLUMN IF NOT EXISTS important_articles      jsonb,

  -- Mots-clés juridiques
  ADD COLUMN IF NOT EXISTS legal_keywords          text[]       DEFAULT '{}',

  -- Champs SEO personnalisés (< 60 chars title / < 155 chars description)
  ADD COLUMN IF NOT EXISTS seo_title_fr            text,
  ADD COLUMN IF NOT EXISTS seo_title_ar            text,
  ADD COLUMN IF NOT EXISTS seo_description_fr      text,
  ADD COLUMN IF NOT EXISTS seo_description_ar      text,

  -- Slug canonique URL-friendly (ex: loi-65-99-code-du-travail)
  ADD COLUMN IF NOT EXISTS canonical_slug          text,

  -- Score et statut de qualité d'extraction
  ADD COLUMN IF NOT EXISTS extraction_confidence_score numeric,      -- 0 à 100
  ADD COLUMN IF NOT EXISTS extraction_status            text,        -- success | partial | needs_review | failed

  -- Contrôle de publication et de revue
  ADD COLUMN IF NOT EXISTS needs_human_review           boolean      DEFAULT false,
  ADD COLUMN IF NOT EXISTS is_publicly_indexable        boolean      DEFAULT true,

  -- Métadonnées de génération
  ADD COLUMN IF NOT EXISTS extraction_version           text,
  ADD COLUMN IF NOT EXISTS raw_text_hash                text,        -- SHA-256 tronqué pour détecter les changements
  ADD COLUMN IF NOT EXISTS summary_generated_at         timestamptz,

  -- Protection contre l'écrasement des corrections humaines
  ADD COLUMN IF NOT EXISTS summary_updated_manually     boolean      DEFAULT false,
  ADD COLUMN IF NOT EXISTS toc_updated_manually         boolean      DEFAULT false;

-- ── Index utiles pour l'admin et le pipeline ─────────────────────────────────

CREATE INDEX IF NOT EXISTS laws_extraction_status_idx
  ON public.laws(extraction_status);

CREATE INDEX IF NOT EXISTS laws_needs_review_idx
  ON public.laws(needs_human_review)
  WHERE needs_human_review = true;

CREATE INDEX IF NOT EXISTS laws_not_indexable_idx
  ON public.laws(is_publicly_indexable)
  WHERE is_publicly_indexable = false;

CREATE UNIQUE INDEX IF NOT EXISTS laws_canonical_slug_idx
  ON public.laws(canonical_slug)
  WHERE canonical_slug IS NOT NULL;
