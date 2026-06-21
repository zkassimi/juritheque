-- ── Migration 010 : Sources officielles + Bulletins Officiels ────────────────

-- 1. Nouveaux champs sur laws
ALTER TABLE laws
  ADD COLUMN IF NOT EXISTS source_name  text,       -- "SGG" | "Adala" | "ANRT" | "BKAM" | ...
  ADD COLUMN IF NOT EXISTS source_url   text,       -- URL de la source officielle
  ADD COLUMN IF NOT EXISTS bo_number    text,       -- "7432"  (uniquement si BO)
  ADD COLUMN IF NOT EXISTS bo_date      date;       -- date de parution au BO

-- 2. Table bulletins_officiels
CREATE TABLE IF NOT EXISTS bulletins_officiels (
  id          bigserial PRIMARY KEY,
  number      text        NOT NULL,         -- ex: "7432"
  date        date,                         -- date de parution
  title       text,                         -- "Bulletin Officiel n° 7432"
  url         text,                         -- lien officiel sgg.gov.ma
  description text,
  created_at  timestamptz DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS bulletins_officiels_number_idx
  ON bulletins_officiels(number);

-- 3. RLS
ALTER TABLE bulletins_officiels ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public_read_bulletins"
  ON bulletins_officiels FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "service_write_bulletins"
  ON bulletins_officiels FOR ALL
  TO service_role
  USING (true) WITH CHECK (true);
