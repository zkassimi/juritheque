"""
migrate_veille.py — Migration SQL pour le système de veille juridique
=====================================================================
Ajoute les colonnes needs_update, pending_bo, last_checked sur laws
et crée la table import_queue.

Usage :
  python pipeline/migrate_veille.py
  python pipeline/migrate_veille.py --dry-run
"""

import os, sys, argparse
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", ""))

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}

MIGRATIONS = [
    {
        "name": "add_needs_update_to_laws",
        "sql": """
ALTER TABLE laws
  ADD COLUMN IF NOT EXISTS needs_update  BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS pending_bo    TEXT,
  ADD COLUMN IF NOT EXISTS last_checked  DATE;
""",
    },
    {
        "name": "create_import_queue",
        "sql": """
CREATE TABLE IF NOT EXISTS import_queue (
  id             UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  detected_at    TIMESTAMPTZ DEFAULT now(),
  source         TEXT,
  bo_number      TEXT,
  bo_date        DATE,
  bo_url         TEXT,
  pdf_url        TEXT,
  title_fr       TEXT,
  law_number     TEXT,
  law_type       TEXT,
  domain_guess   TEXT,
  action         TEXT CHECK (action IN ('new','update','repeal')),
  related_law_id UUID REFERENCES laws(id) ON DELETE SET NULL,
  status         TEXT DEFAULT 'pending' CHECK (status IN ('pending','importing','done','rejected')),
  notes          TEXT
);
CREATE INDEX IF NOT EXISTS idx_import_queue_status ON import_queue(status);
CREATE INDEX IF NOT EXISTS idx_import_queue_detected ON import_queue(detected_at DESC);
""",
    },
]


def run_sql(sql: str, name: str) -> bool:
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
        headers=HEADERS,
        json={"query": sql},
        timeout=30,
    )
    # Supabase ne supporte pas exec_sql en REST — on utilise le endpoint SQL direct
    resp2 = requests.post(
        f"{SUPABASE_URL}/rest/v1/",
        headers={**HEADERS, "Prefer": "return=minimal"},
        params={"query": sql},
        timeout=30,
    )
    # Fallback : utiliser l'API SQL de Supabase Management
    resp3 = requests.post(
        f"{SUPABASE_URL.replace('/rest/v1','').replace('.supabase.co','')}.supabase.co/rest/v1/rpc/",
        headers=HEADERS,
        json={"query": sql},
        timeout=30,
    )
    return False


def run_via_pg_rest(sql: str) -> tuple[bool, str]:
    """Exécute du SQL via l'endpoint /rest/v1/rpc/ si disponible."""
    # Supabase REST ne permet pas d'exécuter du DDL directement.
    # On passe par le SDK JS côté client ou une Edge Function.
    # Pour ce script, on affiche le SQL et demande à l'utilisateur de le coller dans l'éditeur Supabase.
    return False, "REST API ne supporte pas DDL direct"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Migration — Système de veille juridique")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("  ❌ Variables SUPABASE_URL / SUPABASE_KEY manquantes dans .env")
        sys.exit(1)

    print("  ℹ️  Supabase REST API ne supporte pas le DDL direct.")
    print("  Colle ce SQL dans l'éditeur SQL de Supabase :\n")
    print("  ┌─ Supabase Dashboard → SQL Editor → Paste & Run ─────────────────┐")

    full_sql = "\n".join(m["sql"] for m in MIGRATIONS)
    for line in full_sql.strip().split("\n"):
        print(f"  │  {line}")

    print("  └──────────────────────────────────────────────────────────────────┘\n")

    if args.dry_run:
        print("  [DRY-RUN] Rien n'a été exécuté.")
        return

    print("  Vérification de la table import_queue...")
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/import_queue",
        headers=HEADERS,
        params={"select": "id", "limit": "1"},
        timeout=10,
    )
    if resp.status_code == 200:
        print("  ✅ Table import_queue déjà présente !")
    elif resp.status_code == 404 or "does not exist" in resp.text:
        print("  ⚠️  Table import_queue absente — applique le SQL ci-dessus dans Supabase.")
    else:
        print(f"  ℹ️  Statut : {resp.status_code} — {resp.text[:100]}")

    print("\n  Vérification des colonnes sur laws...")
    resp2 = requests.get(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={"select": "needs_update", "limit": "1"},
        timeout=10,
    )
    if resp2.status_code == 200:
        print("  ✅ Colonne needs_update déjà présente sur laws !")
    else:
        print("  ⚠️  Colonne needs_update absente — applique le SQL ci-dessus dans Supabase.")

    print()


if __name__ == "__main__":
    main()
