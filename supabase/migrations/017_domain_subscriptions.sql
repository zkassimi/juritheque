-- ============================================================
-- Migration 017 — Abonnements par domaine juridique
-- ============================================================
-- À exécuter dans Supabase Dashboard → SQL Editor

-- 1. Ajouter la colonne domain_id à la table subscribers
ALTER TABLE public.subscribers
  ADD COLUMN IF NOT EXISTS domain_id text DEFAULT NULL;

-- 2. Supprimer l'ancienne contrainte UNIQUE sur email seul
ALTER TABLE public.subscribers
  DROP CONSTRAINT IF EXISTS subscribers_email_unique;

-- 3. Nouvelle contrainte UNIQUE sur (email, domain_id)
--    Permet à un même email de s'abonner à plusieurs domaines
--    NULL domain_id = abonnement général (footer)
ALTER TABLE public.subscribers
  ADD CONSTRAINT subscribers_email_domain_unique UNIQUE (email, domain_id);

-- 4. Policy SELECT pour les abonnés (déjà existante, rien à changer)
-- Policy INSERT "Anyone can subscribe" couvre déjà les nouvelles lignes
