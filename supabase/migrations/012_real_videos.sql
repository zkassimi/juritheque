-- ============================================================
-- Migration 012 — Vraies vidéos YouTube sur le droit marocain
-- ============================================================
-- Remplace les vidéos placeholder (dQw4w9WgXcQ) par de vraies
-- vidéos pédagogiques sur le droit marocain (FR + AR).
--
-- Sources :
--   • قانوني (Qanouny) — chaîne droit marocain
--   • النبراس القانونية — moudawwana & famille
--   • ثقافة قانونية — culture juridique
--   • Cours Droit Maroc — cours académiques
--   • 2M TV — émissions juridiques
-- ============================================================

-- Vider les anciennes vidéos placeholder (si présentes)
DELETE FROM public.videos WHERE youtube_id = 'dQw4w9WgXcQ';

-- Créer la table si elle n'existe pas encore
CREATE TABLE IF NOT EXISTS public.videos (
  id          SERIAL PRIMARY KEY,
  title_fr    TEXT NOT NULL,
  title_ar    TEXT,
  youtube_id  TEXT NOT NULL,
  thumbnail   TEXT,
  duration    TEXT,
  domain_id   TEXT REFERENCES public.domains(id),
  level       TEXT CHECK (level IN ('Débutant','Intermédiaire','Expert')) DEFAULT 'Débutant',
  author      TEXT,
  views       INTEGER DEFAULT 0,
  date        DATE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Ajouter la contrainte UNIQUE sur youtube_id si elle n'existe pas
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'videos_youtube_id_key'
      AND conrelid = 'public.videos'::regclass
  ) THEN
    ALTER TABLE public.videos ADD CONSTRAINT videos_youtube_id_key UNIQUE (youtube_id);
  END IF;
END $$;

-- Activer RLS
ALTER TABLE public.videos ENABLE ROW LEVEL SECURITY;

-- Politique : lecture publique
DROP POLICY IF EXISTS "videos_public_read" ON public.videos;
CREATE POLICY "videos_public_read" ON public.videos
  FOR SELECT USING (true);

-- ── Insertion des vraies vidéos ───────────────────────────────────────────────

INSERT INTO public.videos (title_fr, title_ar, youtube_id, duration, domain_id, level, author, views, date)
VALUES

  -- ── Droit du Travail ────────────────────────────────────────────────────────
  (
    'Cours Droit du Travail Marocain — Introduction',
    'مدونة الشغل المغربية — مدخل وتقديم',
    'WuLRuf6431g', '45:00', 'travail', 'Débutant', 'Cours Droit Maroc', 18400, '2023-07-15'
  ),
  (
    'Le Code du Travail Marocain — Analyse complète',
    'مدونة الشغل — التحليل الشامل للعلاقات المهنية',
    'nomU9japcSg', '38:00', 'travail', 'Intermédiaire', 'Droit Maroc', 9200, '2026-04-10'
  ),
  (
    'Contrat de Travail & Droit Social — Cours Darija',
    'عقد الشغل والقانون الاجتماعي — بالدارجة',
    'ePDem_QgFgw', '32:00', 'travail', 'Débutant', 'Législation Travail', 24600, '2020-08-10'
  ),
  (
    'Maroc — Vers une révision du Code du Travail',
    'المغرب — نحو مراجعة مدونة الشغل',
    '9XwjKVlZZKo', '12:00', 'travail', 'Débutant', 'Al Aoula', 15600, '2023-04-18'
  ),

  -- ── Droit de la Famille / Civil ────────────────────────────────────────────
  (
    'Moudawwana — Le Divorce en Droit Marocain',
    'مدونة الأسرة: الطلاق ومسطرة التطليق للشقاق',
    'wn8JEkNDvc0', '22:00', 'civil', 'Débutant', 'قانوني', 31500, '2023-05-18'
  ),
  (
    'Moudawwana — Mises à jour et nouveautés 2023',
    'شنو قال القانون — أهم مستجدات مدونة الأسرة',
    'P0IasF_fjp4', '18:00', 'civil', 'Débutant', 'ثقافة قانونية', 45800, '2023-02-12'
  ),
  (
    'Procédures de Divorce — Droit de la Famille',
    'الاجراءات القانونية للطلاق في المغرب',
    'e-A9j-iAI9Q', '20:00', 'civil', 'Débutant', 'النبراس القانونية', 28900, '2023-03-25'
  ),
  (
    'Héritage & Succession — Questions complexes',
    'الورث مشكلة: أصعب مسائل إرثية في مدونة الأسرة',
    'o3_NV1wD3aE', '35:00', 'civil', 'Expert', 'النبراس القانونية', 19700, '2023-09-02'
  ),
  (
    'Les Fiançailles en Droit Marocain (Khitba)',
    'الخِطبة من خلال القانون المغربي — مدونة الأسرة',
    'SoM62Cp8m4g', '25:00', 'civil', 'Débutant', 'النبراس القانونية', 12300, '2022-11-14'
  ),

  -- ── Droit Foncier / Immobilier ─────────────────────────────────────────────
  (
    'Droit Foncier au Maroc — 60 minutes pour comprendre',
    'القانون العقاري بالمغرب — فهم شامل في ساعة',
    'RzpKiYeQFL0', '60:00', 'civil', 'Intermédiaire', '2M Télévision', 67200, '2022-06-20'
  ),
  (
    'Droit Foncier — La Prénotation (Titre Foncier)',
    'القانون العقاري — التقييد الاحتياطي في الرسم العقاري',
    'UMo9Y-opFWE', '28:00', 'civil', 'Expert', 'Cours Droit Foncier', 8100, '2023-01-08'
  ),

  -- ── Droit Commercial ───────────────────────────────────────────────────────
  (
    'Droit des Sociétés — La SARL en pratique (Darija)',
    'قانون الشركات — الشركة ذات المسؤولية المحدودة بالدارجة',
    'jLz8Q5woTsI', '40:00', 'commercial', 'Intermédiaire', 'Cours Droit Commercial', 22400, '2022-09-05'
  ),

  -- ── Droit Pénal / Famille ──────────────────────────────────────────────────
  (
    'L''abandon de famille — Infraction pénale au Maroc',
    'كيف يتحول إهمال الأسرة إلى جريمة في المغرب؟',
    'dY-rxADcY98', '16:00', 'penal', 'Débutant', 'ثقافة قانونية', 33800, '2023-07-30'
  )

ON CONFLICT (youtube_id) DO UPDATE SET
  title_fr  = EXCLUDED.title_fr,
  title_ar  = EXCLUDED.title_ar,
  duration  = EXCLUDED.duration,
  domain_id = EXCLUDED.domain_id,
  level     = EXCLUDED.level,
  author    = EXCLUDED.author,
  views     = EXCLUDED.views,
  date      = EXCLUDED.date;
