"""Migration : ajoute is_published (BOOLEAN DEFAULT true) à la table laws."""
import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

# Supabase REST ne supporte pas DDL — on utilise le endpoint /rest/v1/rpc ou on vérifie
# si la colonne existe déjà en tentant un fetch avec select=is_published
r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,is_published", "limit": "1"}, timeout=10)

if r.status_code == 200:
    print("✅ Colonne is_published déjà présente en base.")
elif "column" in r.text.lower() and "is_published" in r.text.lower():
    print("❌ Colonne is_published absente — à créer via le dashboard Supabase SQL Editor :")
    print()
    print("ALTER TABLE laws ADD COLUMN IF NOT EXISTS is_published BOOLEAN NOT NULL DEFAULT true;")
    print("CREATE INDEX IF NOT EXISTS idx_laws_is_published ON laws(is_published);")
    print()
    print("UPDATE laws SET is_published = false")
    print("WHERE title_fr ~ '^Texte\\s+N[°o]?\\s+adala-[0-9a-f]+\\s*$'")
    print("   OR (title_fr ~ '^[\\d\\s\\-_\\.]+$');")
else:
    print(f"Statut: {r.status_code}")
    print(r.text[:300])
