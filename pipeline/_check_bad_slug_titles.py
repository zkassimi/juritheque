"""Vérifie les titres des textes avec mauvais slugs (texte-juridique-*)."""
import os, requests
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)
URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

r = requests.get(f"{URL}/rest/v1/laws", headers=H,
    params={"select": "number,title_fr,type,canonical_slug,date",
            "canonical_slug": "like.texte-juridique-%",
            "limit": "20", "order": "updated_at.desc"}, timeout=15)
rows = r.json()
print(f"{len(rows)} textes à mauvais slugs — titres actuels:\n")
for x in rows:
    t = x.get("title_fr","")
    words = [w for w in t.split() if len(w)>3 and w.lower() not in {"dahir","décret","n°","n°","loi","arrêté","du","de","la","le","les","des","au","aux","portant","fixant"}]
    quality = "✅ riche" if len(words)>=4 else "⚠ court"
    print(f"  [{quality}] {x.get('canonical_slug','')[:40]:<40} → {t[:80]}")
