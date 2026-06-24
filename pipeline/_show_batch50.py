"""Affiche les résultats des 50 textes qu'on vient de corriger (bad-slugs batch)."""
import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

# Numéros des textes qu'on vient de corriger (batch fix-bad-slugs 50 premiers)
# On filtre : slug ne commence plus par texte-juridique- ET type = Dahir/Décret/Loi/Arrêté
# En pratique : chercher les textes récemment mis à jour avec un bon slug
r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "number,title_fr,type,canonical_slug",
            "order": "updated_at.desc",
            "limit": "50",
            "canonical_slug": "not.like.texte-juridique-%",
            "type": "in.(Dahir,Décret,Loi,Arrêté,Circulaire,Décision,Note)"}, timeout=15)
rows = r.json()

print(f"Résultats des 50 textes corrigés :\n")
print(f"  {'N°':<15} {'Type':<10} {'Titre':<65} {'Slug'}")
print("  " + "-"*155)
for x in rows:
    num   = (x.get('number') or '')[:14]
    typ   = (x.get('type') or '')[:9]
    titre = (x.get('title_fr') or '')[:64]
    slug  = (x.get('canonical_slug') or '')[:70]
    print(f"  {num:<15} {typ:<10} {titre:<65} {slug}")
