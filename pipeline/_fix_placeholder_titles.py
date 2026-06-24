"""Corrige les textes dont le titre contient des placeholders IA ('[sujet probable]' etc.)."""
import os, re, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

_PLACEHOLDER = re.compile(r'\[.*?\]|sujet probable|sujet inconnu|titre inconnu|non identifi|à préciser', re.IGNORECASE)

# Chercher tous les textes avec placeholders dans le titre
r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "id,number,title_fr,type,canonical_slug,date",
            "title_fr": "like.*sujet probable*",
            "limit": "100"}, timeout=15)
rows = r.json()
print(f"{len(rows)} textes avec placeholder '[sujet probable]' trouvés\n")

for x in rows:
    print(f"  → MASQUÉ: [{x.get('type')}] {x.get('number')} | {x.get('title_fr')[:60]}")
    # Masquer (is_published=false) — ils passeront en révision admin
    r2 = requests.patch(
        f"{URL}/rest/v1/laws?id=eq.{x['id']}",
        headers=H,
        json={"is_published": False},
        timeout=10
    )
    if r2.status_code in (200, 204):
        print(f"    ✅ Masqué")
    else:
        print(f"    ❌ Erreur: {r2.status_code}")
