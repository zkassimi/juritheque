"""Affiche les résultats des textes qu'on vient de corriger (était texte-juridique-*)."""
import os, re, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Prefer": "count=exact"}

# Numéros de la batch (les textes qui avaient "texte-juridique-1-xx-xxx" comme slug)
# On cherche les dahirs/décrets qui ont été récemment mis à jour
# et qui n'ont plus un slug texte-juridique-*
r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "number,title_fr,type,canonical_slug",
            "order": "updated_at.desc",
            "limit": "60",
            "type": "in.(Dahir,Décret,Loi,Arrêté)",
            "canonical_slug": "not.like.texte-juridique-%"}, timeout=15)

rows = r.json()
# Garder uniquement ceux dont le numéro ressemble à X-XX-XXX (dahir/décret standard)
clean = [x for x in rows if re.match(r'^\d[-\.]\d{2}[-\.]\d+', x.get("number",""))]

print(f"{len(clean)} textes corrigés (type + numéro + keywords + année) :\n")
print(f"  {'N°':<14} {'Type':<10} {'Titre':<60} {'Slug'}")
print("  " + "-"*140)
for x in clean[:50]:
    num   = (x.get('number') or '')[:13]
    typ   = (x.get('type') or '')[:9]
    titre = (x.get('title_fr') or '')[:59]
    slug  = (x.get('canonical_slug') or '')[:65]
    print(f"  {num:<14} {typ:<10} {titre:<60} {slug}")
