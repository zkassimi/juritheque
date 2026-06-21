-- ============================================================
-- Migration 006 — Fonction RPC increment_views
-- ============================================================
-- Incrémente atomiquement le compteur views d'une loi.
-- Appelée côté client via supabase.rpc('increment_views', { law_id })
-- SECURITY DEFINER : exécutée avec les droits du propriétaire (bypass RLS)
-- ce qui permet aux visiteurs anonymes de déclencher l'incrément.
-- ============================================================

CREATE OR REPLACE FUNCTION public.increment_views(law_id bigint)
RETURNS void
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  UPDATE public.laws
  SET views = COALESCE(views, 0) + 1
  WHERE id = law_id;
$$;

-- Accorder l'exécution aux rôles anon et authenticated
GRANT EXECUTE ON FUNCTION public.increment_views(bigint) TO anon, authenticated;
