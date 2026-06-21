-- 019_verification_status.sql
-- Ajoute les champs de fiabilité juridique à la table laws.
-- verification_status : usage interne admin uniquement (ne jamais afficher publiquement).
-- effective_from / effective_to : dates d'entrée en vigueur / d'abrogation.
-- replaces_id : texte abrogé par celui-ci (relation directe).

ALTER TABLE laws
  ADD COLUMN IF NOT EXISTS verification_status TEXT NOT NULL DEFAULT 'unverified'
    CHECK (verification_status IN ('verified', 'unverified', 'outdated')),
  ADD COLUMN IF NOT EXISTS effective_from DATE,
  ADD COLUMN IF NOT EXISTS effective_to DATE,
  ADD COLUMN IF NOT EXISTS replaces_id BIGINT REFERENCES laws(id) ON DELETE SET NULL;

-- Index pour accélérer les filtres admin sur statut de vérification
CREATE INDEX IF NOT EXISTS idx_laws_verification_status ON laws(verification_status);

-- Index pour les relations entre textes (recherche du texte remplacé)
CREATE INDEX IF NOT EXISTS idx_laws_replaces_id ON laws(replaces_id) WHERE replaces_id IS NOT NULL;

COMMENT ON COLUMN laws.verification_status IS
  'Statut de vérification éditoriale. verified = contenu confirmé depuis source officielle. unverified = non encore contrôlé. outdated = remplacé/abrogé confirmé. Usage interne admin uniquement.';

COMMENT ON COLUMN laws.effective_from IS
  'Date d''entrée en vigueur du texte (BO ou date de signature si BO non daté).';

COMMENT ON COLUMN laws.effective_to IS
  'Date d''abrogation ou de remplacement. NULL = texte potentiellement en vigueur.';

COMMENT ON COLUMN laws.replaces_id IS
  'UUID du texte que ce texte remplace ou abroge directement.';
