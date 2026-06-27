-- Migration 011 : slug_history pour redirections 301
-- Exécuter dans Supabase Dashboard → SQL Editor

ALTER TABLE laws
  ADD COLUMN IF NOT EXISTS slug_history TEXT[] DEFAULT '{}';

CREATE INDEX IF NOT EXISTS idx_laws_slug_history
  ON laws USING GIN(slug_history);
