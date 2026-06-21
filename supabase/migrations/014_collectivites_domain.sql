-- ============================================================
-- Migration 014 — Domaine "Collectivités Territoriales"
-- ============================================================
-- Ajoute le 16ème domaine juridique : collectivites
-- Reclassifie les textes liés (LOC, communes, régions...)
-- depuis le domaine "administratif"
-- ============================================================

-- ── 1. Insérer le nouveau domaine ────────────────────────────────────────────
INSERT INTO public.domains (id, name_fr, name_ar, icon, law_count, sub_domains)
VALUES (
  'collectivites',
  'Collectivités Territoriales',
  'الجماعات الترابية',
  'MapPin',
  0,
  ARRAY['Régions', 'Préfectures & Provinces', 'Communes', 'Élections locales', 'Finances locales']
)
ON CONFLICT (id) DO UPDATE SET
  name_fr     = EXCLUDED.name_fr,
  name_ar     = EXCLUDED.name_ar,
  icon        = EXCLUDED.icon,
  sub_domains = EXCLUDED.sub_domains;

-- ── 2. Reclassifier les textes liés aux collectivités ───────────────────────
-- LOC 111-14 (Régions), 112-14 (Préfectures/Provinces), 113-14 (Communes)
-- + textes sur communes, conseil communal, conseil régional, etc.

UPDATE public.laws
SET
  domain_id  = 'collectivites',
  domain_ids = CASE
    WHEN domain_ids IS NULL THEN ARRAY['collectivites']
    WHEN NOT ('collectivites' = ANY(domain_ids)) THEN domain_ids || ARRAY['collectivites']
    ELSE domain_ids
  END
WHERE
  -- Par numéro de loi (LOC de 2015)
  number ILIKE '%111-14%'
  OR number ILIKE '%112-14%'
  OR number ILIKE '%113-14%'
  -- Par contenu du titre
  OR title_fr ILIKE '%collectivité%territorial%'
  OR title_fr ILIKE '%commune%'
  OR title_fr ILIKE '%conseil communal%'
  OR title_fr ILIKE '%conseil régional%'
  OR title_fr ILIKE '%conseil préfectoral%'
  OR title_fr ILIKE '%conseil provincial%'
  OR title_fr ILIKE '%élu local%'
  OR title_fr ILIKE '%révocation%élu%'
  OR title_fr ILIKE '%régionalisation%'
  OR title_fr ILIKE '%charte communale%'
  OR title_fr ILIKE '%autonomie locale%'
  OR title_ar ILIKE '%الجماعات الترابية%'
  OR title_ar ILIKE '%المجلس الجماعي%'
  OR title_ar ILIKE '%المجلس الإقليمي%'
  OR title_ar ILIKE '%الجماعة الحضرية%'
  OR title_ar ILIKE '%الجماعة القروية%'
  OR title_ar ILIKE '%مجلس الجهة%';

-- ── 3. Ajouter aussi "administratif" comme domaine secondaire
--    pour ne pas perdre la classification existante
UPDATE public.laws
SET domain_ids = CASE
  WHEN NOT ('administratif' = ANY(domain_ids)) THEN domain_ids || ARRAY['administratif']
  ELSE domain_ids
END
WHERE domain_id = 'collectivites'
  AND (domain_ids IS NULL OR NOT ('administratif' = ANY(domain_ids)));

-- ── 4. Recalculer le compteur law_count ──────────────────────────────────────
UPDATE public.domains d
SET law_count = (
  SELECT COUNT(*)
  FROM public.laws l
  WHERE l.domain_id = d.id
    OR (l.domain_ids IS NOT NULL AND d.id = ANY(l.domain_ids))
)
WHERE d.id IN ('collectivites', 'administratif');

-- ── 5. Rapport ───────────────────────────────────────────────────────────────
SELECT
  id,
  name_fr,
  law_count
FROM public.domains
WHERE id IN ('collectivites', 'administratif')
ORDER BY id;
