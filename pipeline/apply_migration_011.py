"""
JuriThèque — Applique la migration 011 via l'API Supabase
══════════════════════════════════════════════════════════
À exécuter UNE SEULE FOIS pour :
  1. Ajouter les 4 nouveaux domaines (transport, environnement, sante, energie)
  2. Ajouter la colonne domain_ids TEXT[] sur laws
  3. Backfiller domain_ids depuis domain_id existant
  4. Créer le trigger de sync et l'index GIN

Prérequis : SUPABASE_SERVICE_KEY dans .env (droits DDL requis)

Usage :
  python pipeline/apply_migration_011.py
"""

import os
from dotenv import load_dotenv
import httpx

load_dotenv()

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY","")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ── 1. Insérer les 4 nouveaux domaines ───────────────────────────────────────
NEW_DOMAINS = [
    {
        "id": "transport",
        "name_fr": "Transport & Logistique",
        "name_ar": "النقل واللوجستيك",
        "icon": "Truck",
        "law_count": 0,
        "sub_domains": ["Transport routier","Transport ferroviaire","Aviation civile","Ports & Marine marchande","Logistique"],
    },
    {
        "id": "environnement",
        "name_fr": "Environnement & Développement Durable",
        "name_ar": "البيئة والتنمية المستدامة",
        "icon": "Leaf",
        "law_count": 0,
        "sub_domains": ["Eau & Assainissement","Forêts & Chasse","Déchets & Pollution","Évaluation environnementale","Changements climatiques"],
    },
    {
        "id": "sante",
        "name_fr": "Santé & Protection Sociale",
        "name_ar": "الصحة والحماية الاجتماعية",
        "icon": "Heart",
        "law_count": 0,
        "sub_domains": ["Santé publique","Hôpitaux & Cliniques","Médicaments & Pharmacie","Professions de santé","Couverture médicale"],
    },
    {
        "id": "energie",
        "name_fr": "Énergie & Mines",
        "name_ar": "الطاقة والمعادن",
        "icon": "Zap",
        "law_count": 0,
        "sub_domains": ["Électricité","Hydrocarbures","Énergies renouvelables","Mines & Carrières","Efficacité énergétique"],
    },
]

def upsert_domains():
    print("📁 Insertion des 4 nouveaux domaines...")
    r = httpx.post(
        f"{SUPABASE_URL}/rest/v1/domains",
        headers={**HEADERS, "Prefer": "resolution=merge-duplicates,return=minimal"},
        json=NEW_DOMAINS,
        timeout=30,
    )
    if r.status_code in (200, 201):
        print("  ✅ Domaines insérés / mis à jour")
    else:
        print(f"  ❌ Erreur {r.status_code}: {r.text}")

# ── 2. Ajouter la colonne domain_ids via SQL (nécessite service_key) ─────────
# Note : PostgREST ne supporte pas DDL directement.
# → Utilise l'endpoint /rest/v1/rpc si vous avez une fonction SQL,
# OU appliquer le fichier SQL manuellement via Supabase Dashboard > SQL Editor.

SQL_MIGRATION = """
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
"""

def main():
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  JuriThèque — Migration 011 (nouveaux domaines)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ SUPABASE_URL ou SUPABASE_SERVICE_KEY manquant dans .env")
        return

    # Étape 1 : Insérer les domaines (via REST, pas de DDL)
    upsert_domains()

    # Étape 2 : DDL — doit être fait via SQL Editor Supabase
    print("\n⚠  ÉTAPE MANUELLE REQUISE :")
    print("   Le script DDL ci-dessous doit être exécuté dans :")
    print("   Supabase Dashboard → SQL Editor\n")
    print("─" * 60)
    print(SQL_MIGRATION)
    print("─" * 60)

    # Sauvegarder le SQL dans un fichier pour copier-coller facile
    sql_path = "pipeline/logs/migration_011_ddl.sql"
    os.makedirs("pipeline/logs", exist_ok=True)
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write(SQL_MIGRATION)
    print(f"\n✅ SQL sauvegardé dans {sql_path}")
    print("   Copiez ce fichier dans Supabase > SQL Editor > Run\n")

    print("✅ Étape 1 terminée. Lancez ensuite :")
    print("   python pipeline/assign_domains.py --all --dry-run  # test")
    print("   python pipeline/assign_domains.py --all            # production\n")


if __name__ == "__main__":
    main()
