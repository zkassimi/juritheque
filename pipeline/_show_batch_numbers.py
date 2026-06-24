"""Affiche les résultats exacts des textes corrigés dans la batch fix-bad-slugs."""
import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# Les numéros qu'on avait dans le batch (affichés dans le dry-run)
numbers = [
    "1-11-75","018-201","1-21-64","2-24-963","1-21-72","1.09.43",
    "2-24-064","1701-25","2-25-965","2-21-530","2-22-139","1-25-50",
    "2-20-716","2-25-1030","1-99-262","1-18-36","2-22-911","2486-24",
    "2-23-919","1-99-123","2-24-960","1-24-26","1-01-41","1-75-242",
    "1-96-199","2.02.638","1-02-131","589-67","2-22-818","1-63-024",
    "1-29-30","1-15-134","1-21-62","1-21-72",
]
print(f"Résultats pour {len(numbers)} numéros ciblés :\n")
print(f"  {'N°':<14} {'Type':<10} {'Titre':<60} {'Slug'}")
print("  " + "-"*140)
for num in numbers:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "number,title_fr,type,canonical_slug",
                "number": f"eq.{num}", "limit": "1"}, timeout=8)
    data = r.json()
    if data:
        x = data[0]
        n = (x.get('number') or '')[:13]
        t = (x.get('type') or '')[:9]
        titre = (x.get('title_fr') or '')[:59]
        slug = (x.get('canonical_slug') or '')[:65]
        print(f"  {n:<14} {t:<10} {titre:<60} {slug}")
    else:
        print(f"  {num:<14} {'?':<10} {'non trouvé':<60}")
