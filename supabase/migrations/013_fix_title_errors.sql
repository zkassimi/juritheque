-- ============================================================
-- Migration 013 — Nettoyage des titres mal formatés
-- ============================================================
-- Problèmes constatés :
--   1. Préfixe [Autre] dans title_fr  → ex: "[Autre] n° 1.00.200"
--   2. Titres = numéro seul          → ex: "6399"
--   3. Type "[Autre]" dans la colonne type → normaliser
--   4. Numéros cassés type "76::"   → nettoyer
-- ============================================================

-- ── 1. Supprimer le préfixe "[Autre]" au début de title_fr ──────────────────
UPDATE public.laws
SET title_fr = TRIM(REGEXP_REPLACE(title_fr, '^\[Autre\]\s*', '', 'i'))
WHERE title_fr ILIKE '[Autre]%';

-- ── 2. Supprimer le préfixe "[Autre]" au début de title_ar ──────────────────
UPDATE public.laws
SET title_ar = TRIM(REGEXP_REPLACE(title_ar, '^\[Autre\]\s*', '', 'i'))
WHERE title_ar ILIKE '[Autre]%';

-- ── 3. Corriger la colonne "type" qui contient "[Autre]" ────────────────────
-- On essaie de détecter le vrai type à partir du numéro, sinon on met "Loi"
UPDATE public.laws
SET type = CASE
  WHEN number ILIKE '%décret%' OR number ILIKE '2-%' OR number ILIKE '2.%' THEN 'Décret'
  WHEN number ILIKE '%arrêté%' OR number ILIKE 'arrêté%'                    THEN 'Arrêté'
  WHEN number ILIKE '%circulaire%'                                           THEN 'Circulaire'
  WHEN number ILIKE '%dahir%'   OR number ILIKE '1-%' OR number ILIKE '1.%' THEN 'Dahir'
  WHEN title_fr ILIKE '%code%'                                               THEN 'Code'
  ELSE 'Loi'
END
WHERE type = '[Autre]' OR type ILIKE '[Autre]%';

-- ── 4. Titres qui ne sont qu'un nombre (ex: "6399") ─────────────────────────
UPDATE public.laws
SET title_fr = 'Texte N° ' || COALESCE(NULLIF(TRIM(number), ''), id::text)
WHERE title_fr ~ '^\d+$';

-- ── 5. Nettoyer les numéros cassés contenant "::" ────────────────────────────
UPDATE public.laws
SET number = REGEXP_REPLACE(number, ':+$', '')
WHERE number ~ ':+$';

-- ── 6. Supprimer les espaces superflus dans les titres ──────────────────────
UPDATE public.laws
SET title_fr = TRIM(REGEXP_REPLACE(title_fr, '\s{2,}', ' ', 'g'))
WHERE title_fr ~ '\s{2,}';

UPDATE public.laws
SET title_ar = TRIM(REGEXP_REPLACE(title_ar, '\s{2,}', ' ', 'g'))
WHERE title_ar IS NOT NULL AND title_ar ~ '\s{2,}';

-- ── 7. Rapport post-nettoyage ────────────────────────────────────────────────
-- (Requête diagnostic — ne modifie rien)
SELECT
  COUNT(*) FILTER (WHERE title_fr ILIKE '[Autre]%')  AS still_autre_prefix,
  COUNT(*) FILTER (WHERE title_fr ~ '^\d+$')          AS still_number_only,
  COUNT(*) FILTER (WHERE type = '[Autre]')            AS still_autre_type,
  COUNT(*) FILTER (WHERE number ~ ':+$')              AS still_broken_number
FROM public.laws;
