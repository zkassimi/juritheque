-- ============================================================
-- Migration 016 — Newsletter subscribers + Signalements
-- ============================================================

-- ── 1. Table subscribers ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.subscribers (
  id         bigserial   PRIMARY KEY,
  email      text        NOT NULL,
  source     text        DEFAULT 'footer',    -- footer | guide | popup
  lang       text        DEFAULT 'fr',
  created_at timestamptz DEFAULT now(),
  CONSTRAINT subscribers_email_unique UNIQUE (email)
);

ALTER TABLE public.subscribers ENABLE ROW LEVEL SECURITY;

-- Tout le monde peut s'abonner
CREATE POLICY "Anyone can subscribe"
  ON public.subscribers FOR INSERT
  WITH CHECK (true);

-- Seuls admin/editor peuvent lire
CREATE POLICY "Admins read subscribers"
  ON public.subscribers FOR SELECT
  USING (
    exists (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND role IN ('admin', 'editor')
    )
  );

-- ── 2. Table reports ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.reports (
  id             bigserial   PRIMARY KEY,
  content_type   text        NOT NULL,  -- 'law' | 'guide' | 'suggestion' | 'other'
  report_type    text        NOT NULL,  -- voir valeurs ci-dessous
  subject        text,                  -- Titre du texte / guide signalé
  subject_url    text,                  -- URL de la page concernée
  law_id         bigint      REFERENCES public.laws(id) ON DELETE SET NULL,
  guide_slug     text,                  -- slug du guide si applicable
  comment        text,
  reporter_email text,
  status         text        DEFAULT 'pending', -- pending | reviewed | fixed | dismissed
  admin_note     text,
  created_at     timestamptz DEFAULT now(),
  updated_at     timestamptz DEFAULT now()
);

-- report_type valeurs possibles :
--   'text_error'    → Texte incorrect ou incomplet
--   'outdated'      → Texte abrogé non signalé
--   'pdf_broken'    → Lien PDF cassé / introuvable
--   'translation'   → Erreur de traduction (FR↔AR)
--   'missing_text'  → Texte manquant à ajouter
--   'suggestion'    → Suggestion d'amélioration générale

ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

-- Tout le monde peut signaler
CREATE POLICY "Anyone can report"
  ON public.reports FOR INSERT
  WITH CHECK (true);

-- Seuls admin/editor peuvent lire + modifier
CREATE POLICY "Admins read reports"
  ON public.reports FOR SELECT
  USING (
    exists (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND role IN ('admin', 'editor')
    )
  );

CREATE POLICY "Admins update reports"
  ON public.reports FOR UPDATE
  USING (
    exists (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND role IN ('admin', 'editor')
    )
  );

-- ── 3. Index ──────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS reports_status_idx    ON public.reports (status);
CREATE INDEX IF NOT EXISTS reports_created_idx   ON public.reports (created_at DESC);
CREATE INDEX IF NOT EXISTS reports_law_id_idx    ON public.reports (law_id) WHERE law_id IS NOT NULL;
