-- ============================================================
-- Migration 015 — Correction des slugs canoniques dupliqués
-- ============================================================
-- Problème : make_canonical_slug() concaténait number + title_fr,
-- mais title_fr commence souvent déjà par le numéro.
-- Résultat : "dahir-n-1-21-65-dahir-n-1-21-65-du-8-ramadan-..."
--
-- Correction : on NULL-ise les slugs où le numéro apparaît deux fois,
-- puis on régénère via enrich.py --force.
-- ============================================================

-- ── 1. Diagnostic : compter les slugs suspects ───────────────────────────────
-- Un slug est considéré dupliqué si le fragment de numéro apparaît deux fois.
-- Heuristique : slug de longueur > 50 ET contient un tiret-groupe répété.
-- On détecte via la correspondance number-slug au début du canonical_slug.

WITH normalized_numbers AS (
  SELECT
    id,
    canonical_slug,
    -- Normaliser le numéro en slug (remplacer accents et caractères spéciaux)
    lower(
      regexp_replace(
        replace(replace(replace(replace(replace(replace(
          replace(replace(replace(replace(replace(replace(
            replace(coalesce(number, ''), 'n°', 'n'), '°', ''),
          'é', 'e'), 'è', 'e'), 'ê', 'e'), 'à', 'a'), 'â', 'a'),
          'ô', 'o'), 'û', 'u'), 'ç', 'c'), 'î', 'i'), 'ï', 'i'), 'ù', 'u'),
        '[^a-z0-9]+', '-', 'g'
      )
    ) AS num_slug_raw
  FROM laws
  WHERE canonical_slug IS NOT NULL
),
with_clean_num AS (
  SELECT
    id,
    canonical_slug,
    trim(both '-' from num_slug_raw) AS num_slug
  FROM normalized_numbers
  WHERE length(trim(both '-' from num_slug_raw)) >= 4
)
SELECT
  count(*) AS slugs_dupliques_detectes
FROM with_clean_num
WHERE canonical_slug LIKE (num_slug || '-' || num_slug || '%');


-- ── 2. Correction : mettre canonical_slug à NULL pour les slugs dupliqués ────
-- (ils seront régénérés correctement par enrich.py --force)

WITH normalized_numbers AS (
  SELECT
    id,
    lower(
      regexp_replace(
        replace(replace(replace(replace(replace(replace(
          replace(replace(replace(replace(replace(replace(
            replace(coalesce(number, ''), 'n°', 'n'), '°', ''),
          'é', 'e'), 'è', 'e'), 'ê', 'e'), 'à', 'a'), 'â', 'a'),
          'ô', 'o'), 'û', 'u'), 'ç', 'c'), 'î', 'i'), 'ï', 'i'), 'ù', 'u'),
        '[^a-z0-9]+', '-', 'g'
      )
    ) AS num_slug_raw
  FROM laws
  WHERE canonical_slug IS NOT NULL
),
with_clean_num AS (
  SELECT
    id,
    trim(both '-' from num_slug_raw) AS num_slug
  FROM normalized_numbers
  WHERE length(trim(both '-' from num_slug_raw)) >= 4
),
ids_to_fix AS (
  SELECT l.id
  FROM laws l
  JOIN with_clean_num n ON l.id = n.id
  WHERE l.canonical_slug LIKE (n.num_slug || '-' || n.num_slug || '%')
)
UPDATE laws
SET
  canonical_slug = NULL,
  updated_at = now()
WHERE id IN (SELECT id FROM ids_to_fix);


-- ── 3. Vérification post-correction ─────────────────────────────────────────
SELECT
  (SELECT count(*) FROM laws WHERE canonical_slug IS NULL)  AS sans_slug,
  (SELECT count(*) FROM laws WHERE canonical_slug IS NOT NULL) AS avec_slug,
  (SELECT count(*) FROM laws) AS total;
