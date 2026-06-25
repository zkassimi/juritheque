"""Fix 5 exemples ciblés — textes à titre générique visibles sur le site."""
import os, re, sys, requests, time
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)

from fix_imported_titles import (
    ai_lookup_by_number, ai_translate_from_ar, is_number_as_title,
    is_filename_title, make_slug_from_law, is_quality_ok
)

URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
H   = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

# Numéros vus dans les screenshots
targets = ["2085.25", "3.26.26", "2.26.395", "2.25.970", "2.25.502"]

print("5 exemples — avant / après :\n")
for num in targets:
    r = requests.get(f"{URL}/rest/v1/laws", headers=H,
        params={"select": "id,number,title_fr,title_ar,type,canonical_slug,date,simple_summary_ar",
                "number": f"eq.{num}", "limit": "1"}, timeout=10)
    data = r.json()
    if not data:
        print(f"  {num} → non trouvé\n"); continue

    x = data[0]
    law_id    = x["id"]
    law_type  = x.get("type") or ""
    title_fr  = x.get("title_fr") or ""
    title_ar  = x.get("title_ar") or ""
    summary_ar= x.get("simple_summary_ar") or ""
    date      = x.get("date") or ""
    slug_old  = x.get("canonical_slug") or ""

    print(f"  [{law_type}] n°{num}")
    print(f"  AVANT  titre : {title_fr}")
    print(f"  AVANT  slug  : {slug_old}")

    # Lookup IA
    new_title, ai_type = ai_lookup_by_number(law_type, num, date)
    if not new_title and title_ar:
        new_title, ai_type = ai_translate_from_ar(title_ar, law_type, num)
    if not new_title and summary_ar:
        new_title, ai_type = ai_translate_from_ar(summary_ar[:400], law_type, num)

    if new_title:
        final_type = ai_type or law_type
        new_slug   = make_slug_from_law(final_type, num, new_title, date)
        published  = is_quality_ok(new_title, final_type, new_slug)
        print(f"  APRÈS  titre : {new_title}")
        print(f"  APRÈS  slug  : {new_slug}")
        print(f"  Qualité : {'✅ publié' if published else '🚫 masqué'}")
        # Appliquer en base
        patch = {"title_fr": new_title, "canonical_slug": new_slug, "is_published": published}
        if ai_type: patch["type"] = ai_type
        r2 = requests.patch(f"{URL}/rest/v1/laws?id=eq.{law_id}", headers=H, json=patch, timeout=10)
        print(f"  Sauvegardé : {'✅' if r2.status_code in (200,204) else '❌ ' + str(r2.status_code)}")
    else:
        print(f"  IA : inconnu → masqué")
        requests.patch(f"{URL}/rest/v1/laws?id=eq.{law_id}", headers=H,
                       json={"is_published": False}, timeout=10)
    print()
    time.sleep(0.5)
