-- 020_import_queue_rls.sql
-- Active RLS sur import_queue et autorise les admins/editors à lire et gérer la queue.
-- La table était accessible uniquement via service_key (pipeline Python) mais pas via
-- le client frontend (clé anon + JWT utilisateur).

-- Activer RLS
ALTER TABLE import_queue ENABLE ROW LEVEL SECURITY;

-- Admins et editors peuvent tout lire
CREATE POLICY "admin_editor_select_import_queue"
  ON import_queue FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role IN ('admin', 'editor')
    )
  );

-- Admins et editors peuvent mettre à jour le statut (traité / rejeté)
CREATE POLICY "admin_editor_update_import_queue"
  ON import_queue FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role IN ('admin', 'editor')
    )
  );

-- Admins peuvent supprimer des items
CREATE POLICY "admin_delete_import_queue"
  ON import_queue FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Le pipeline Python utilise la service_key (bypass RLS) pour les INSERT —
-- pas besoin de politique INSERT pour les utilisateurs authentifiés.
