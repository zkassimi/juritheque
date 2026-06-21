-- ============================================================
-- Migration 011 — 4 nouveaux domaines + colonne multi-domaine
-- ============================================================
-- Ajoute :
--   • transport          → routes, autoroutes, aviation, ports, rail, logistique
--   • environnement      → eau, forêts, déchets, pollution, chasse, pêche côtière
--   • sante              → hôpitaux, médicaments, pharmacie, santé publique
--   • energie            → mines, énergie électrique, pétrolière, renouvelables
--
-- Et :
--   • laws.domain_ids TEXT[]  → liste de TOUS les domaines d'une loi
--     (y compris domain_id primaire + domaines secondaires)
--   • Index GIN sur domain_ids pour requêtes rapides
-- ============================================================

-- ── 1. Nouveaux domaines ──────────────────────────────────────────────────────

INSERT INTO public.domains (id, name_fr, name_ar, icon, law_count, sub_domains)
VALUES
  (
    'transport',
    'Transport & Logistique',
    'النقل واللوجستيك',
    'Truck',
    0,
    '{"Transport routier","Transport ferroviaire","Aviation civile","Ports & Marine marchande","Logistique"}'
  ),
  (
    'environnement',
    'Environnement & Développement Durable',
    'البيئة والتنمية المستدامة',
    'Leaf',
    0,
    '{"Eau & Assainissement","Forêts & Chasse","Déchets & Pollution","Évaluation environnementale","Changements climatiques"}'
  ),
  (
    'sante',
    'Santé & Protection Sociale',
    'الصحة والحماية الاجتماعية',
    'Heart',
    0,
    '{"Santé publique","Hôpitaux & Cliniques","Médicaments & Pharmacie","Professions de santé","Couverture médicale"}'
  ),
  (
    'energie',
    'Énergie & Mines',
    'الطاقة والمعادن',
    'Zap',
    0,
    '{"Électricité","Hydrocarbures","Énergies renouvelables","Mines & Carrières","Efficacité énergétique"}'
  )
ON CONFLICT (id) DO UPDATE
  SET
    name_fr     = EXCLUDED.name_fr,
    name_ar     = EXCLUDED.name_ar,
    icon        = EXCLUDED.icon,
    sub_domains = EXCLUDED.sub_domains;

-- ── 2. Colonne domain_ids (multi-domaine) ────────────────────────────────────

ALTER TABLE public.laws
  ADD COLUMN IF NOT EXISTS domain_ids TEXT[] DEFAULT '{}';

-- Index GIN pour requêtes @> (contient) et && (intersection)
CREATE INDEX IF NOT EXISTS idx_laws_domain_ids_gin
  ON public.laws USING GIN (domain_ids);

-- ── 3. Backfill domain_ids depuis domain_id existant ─────────────────────────
-- Pour toutes les lois qui ont déjà un domain_id mais pas de domain_ids,
-- on initialise domain_ids avec leur domaine primaire.

UPDATE public.laws
SET domain_ids = ARRAY[domain_id]
WHERE domain_id IS NOT NULL
  AND (domain_ids IS NULL OR domain_ids = '{}');

-- ── 4. Trigger : maintenir domain_ids cohérent avec domain_id ────────────────
-- Quand domain_id change, s'assure que domain_ids contient au moins ce domaine.

CREATE OR REPLACE FUNCTION sync_domain_ids()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  -- Si domain_id vient d'être défini/changé, l'ajouter à domain_ids
  IF NEW.domain_id IS NOT NULL THEN
    IF NEW.domain_ids IS NULL OR NEW.domain_ids = '{}' THEN
      NEW.domain_ids := ARRAY[NEW.domain_id];
    ELSIF NOT (NEW.domain_ids @> ARRAY[NEW.domain_id]) THEN
      NEW.domain_ids := array_prepend(NEW.domain_id, NEW.domain_ids);
    END IF;
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_sync_domain_ids ON public.laws;
CREATE TRIGGER trg_sync_domain_ids
  BEFORE INSERT OR UPDATE OF domain_id ON public.laws
  FOR EACH ROW EXECUTE FUNCTION sync_domain_ids();

-- ── 5. Vue law_count par domaine (optionnelle, pour stats) ───────────────────
-- Compte les lois par domaine en utilisant domain_ids pour inclure multi-domaine.

CREATE OR REPLACE VIEW public.domain_law_counts AS
SELECT
  d.id,
  d.name_fr,
  COUNT(l.id) AS law_count
FROM public.domains d
LEFT JOIN public.laws l
  ON l.domain_ids @> ARRAY[d.id]
GROUP BY d.id, d.name_fr
ORDER BY d.name_fr;
