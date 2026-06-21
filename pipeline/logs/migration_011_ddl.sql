
-- Colonne multi-domaine
ALTER TABLE public.laws ADD COLUMN IF NOT EXISTS domain_ids TEXT[] DEFAULT '{}';

-- Index GIN
CREATE INDEX IF NOT EXISTS idx_laws_domain_ids_gin ON public.laws USING GIN (domain_ids);

-- Backfill domain_ids depuis domain_id existant
UPDATE public.laws
SET domain_ids = ARRAY[domain_id]
WHERE domain_id IS NOT NULL
  AND (domain_ids IS NULL OR domain_ids = '{}');

-- Trigger de sync
CREATE OR REPLACE FUNCTION sync_domain_ids()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
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
