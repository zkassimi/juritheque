-- ============================================================
-- Migration 018 — Nettoyage des canonical_slug hash-ID (Adala, SGG, etc.)
-- ============================================================
-- Objectif : remplacer les slugs type "adala-1efb9bc5" par des URLs lisibles
-- Format cible : {type}-{annee}-{4-mots-titre}-{6hex}
-- Ex : texte-juridique-1999-lettre-royale-ministre-plan-1efb9bc5
--      decret-2004-portant-application-code-a3f8b2
--
-- ⚠️  À exécuter dans Supabase Dashboard → SQL Editor
-- ⚠️  Les anciens liens sont automatiquement redirigés via le champ `number`
--     (le code frontend (fetchLawBySlug) fait déjà le fallback par number)
-- ============================================================

-- ── 0. Activer l'extension unaccent ──────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS unaccent SCHEMA public;

-- ── 1. Fonction slugify ────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.jt_slugify(txt text)
RETURNS text LANGUAGE sql IMMUTABLE AS $$
  SELECT lower(trim(both '-' from
    regexp_replace(
      regexp_replace(
        regexp_replace(
          public.unaccent(coalesce(txt, '')),
          '[^a-zA-Z0-9\s\-]', ' ', 'g'   -- garder lettres, chiffres, espaces, tirets
        ),
        '\s+', '-', 'g'                   -- espaces → tirets
      ),
      '-{2,}', '-', 'g'                   -- tirets multiples → 1 tiret
    )
  ));
$$;

-- ── 2. Fonction : extraire les N premiers mots significatifs d'un texte ────────
CREATE OR REPLACE FUNCTION public.jt_slug_words(txt text, max_words int DEFAULT 5)
RETURNS text LANGUAGE sql IMMUTABLE AS $$
  SELECT string_agg(word, '-')
  FROM (
    SELECT w AS word
    FROM unnest(
      string_to_array(
        regexp_replace(public.unaccent(coalesce(txt, '')), '[^a-zA-Z0-9 ]', ' ', 'g'),
        ' '
      )
    ) AS w
    WHERE length(trim(w)) > 2                 -- ignorer les mots trop courts (le, la, du…)
      AND lower(trim(w)) NOT IN (             -- ignorer les mots vides
        'les', 'des', 'une', 'par', 'sur', 'pour', 'dans', 'avec',
        'qui', 'que', 'son', 'ses', 'aux', 'est', 'sur', 'non',
        'portant', 'relatif', 'relative', 'fixant', 'modifiant'
      )
    LIMIT max_words
  ) words;
$$;

-- ── 3. Mise à jour des canonical_slug hash-ID ─────────────────────────────────
-- Cible : lignes où canonical_slug ressemble à "adala-1efb9bc5" (préfixe-hexadécimal)
-- OU      lignes où number ressemble à ce pattern (source Adala, ISM, SGG…)

UPDATE public.laws
SET canonical_slug = concat_ws('-',
  -- Type court (sans accents)
  CASE lower(type)
    WHEN 'loi'             THEN 'loi'
    WHEN 'dahir'           THEN 'dahir'
    WHEN 'décret'          THEN 'decret'
    WHEN 'decret'          THEN 'decret'
    WHEN 'arrêté'          THEN 'arrete'
    WHEN 'arrete'          THEN 'arrete'
    WHEN 'circulaire'      THEN 'circulaire'
    WHEN 'code'            THEN 'code'
    WHEN 'règlement'       THEN 'reglement'
    WHEN 'texte juridique' THEN 'texte'
    WHEN 'note'            THEN 'note'
    ELSE 'texte'
  END,
  -- Année (si date connue)
  CASE WHEN date IS NOT NULL THEN to_char(date::date, 'YYYY') ELSE NULL END,
  -- 5 mots clés du titre français (si disponible)
  NULLIF(public.jt_slug_words(title_fr, 5), ''),
  -- Suffixe unique : 8 derniers caractères de l'ID (évite les doublons)
  right(replace(id::text, '-', ''), 8)
)
WHERE
  -- Cible 1 : canonical_slug est un hash-ID (ex: adala-1efb9bc5)
  canonical_slug ~ '^[a-z]+-[a-f0-9]{6,}$'
  OR
  -- Cible 2 : number est un hash-ID (au cas où canonical_slug serait null)
  number ~ '^[a-z]+-[a-f0-9]{6,}$';


-- ── 4. Vérification (affiche un échantillon des nouvelles URLs) ────────────────
-- Décommentez pour vérifier avant de committer :
-- SELECT number, canonical_slug, title_fr, date
-- FROM public.laws
-- WHERE number ~ '^[a-z]+-[a-f0-9]{6,}$'
-- LIMIT 20;


-- ── 5. Nettoyage des fonctions temporaires (optionnel) ────────────────────────
-- DROP FUNCTION IF EXISTS public.jt_slugify(text);
-- DROP FUNCTION IF EXISTS public.jt_slug_words(text, int);
