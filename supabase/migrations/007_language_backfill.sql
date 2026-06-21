-- ============================================================
-- Migration 007 — Backfill du champ language
-- ============================================================
-- Règles (seulement quand content est significatif > 10 chars) :
--   content_fr ET content_ar présents  → 'Bilingue'
--   seulement content_fr              → 'FR'
--   seulement content_ar              → 'AR'
--   aucun contenu extrait              → valeur existante conservée
--
-- Prudence : ne modifie QUE les lignes où language est NULL ou
-- hors des valeurs attendues ('FR','AR','Bilingue').
-- Ne modifie jamais le contenu textuel.
-- ============================================================

UPDATE public.laws
SET language = CASE
  WHEN  content_fr IS NOT NULL AND length(trim(content_fr)) > 10
    AND content_ar IS NOT NULL AND length(trim(content_ar)) > 10
  THEN 'Bilingue'
  WHEN  content_fr IS NOT NULL AND length(trim(content_fr)) > 10
  THEN 'FR'
  WHEN  content_ar IS NOT NULL AND length(trim(content_ar)) > 10
  THEN 'AR'
  ELSE language  -- conserver la valeur existante si aucun contenu extrait
END
WHERE language IS NULL
   OR language NOT IN ('FR', 'AR', 'Bilingue');

-- Récapitulatif après mise à jour (commenté pour migration idempotente)
-- SELECT language, count(*) FROM public.laws GROUP BY language ORDER BY count DESC;
