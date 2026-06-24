"""Test rapide : montrer les titres traduits + slugs générés pour 5 textes adala."""
import os, re, requests, unicodedata as _ud
from dotenv import load_dotenv
load_dotenv(); load_dotenv("pipeline/.env", override=True)

URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY","")
OAK = os.getenv("OPENROUTER_API_KEY","")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

SLUG_STOP = {
    'le','la','les','du','de','des','au','aux','et','ou','un','une','n','no','par','sur','en','dans','pour','avec','sans',
    'relatif','relative','relatifs','relatives','portant','fixant','instituant','modifiant','abrogeant','approuvant',
    'dahir','decret','loi','arrete','circulaire','texte','ordonnance','code','reglement','adala','sgg',
}

def _s(t):
    norm = _ud.normalize("NFD", (t or "").lower())
    norm = "".join(c for c in norm if _ud.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", norm).strip("-")

def make_slug(law_type, number, title_fr, date=""):
    raw_num = (number or "").strip()
    if re.match(r'^adala-[0-9a-f]+$', raw_num.lower()) or not raw_num:
        clean_num = ""  # ID interne sans sens → pas dans le slug
    else:
        m = re.search(r'(\d[\d\.\-/]+)', raw_num)
        clean_num = re.sub(r'[.\s/]+', '-', m.group(1)).strip('-') if m else _s(raw_num)
    type_slug = _s(law_type or "texte")
    number_slug = _s(clean_num)
    excluded = SLUG_STOP | set(type_slug.split("-")) | set(number_slug.split("-")) | {''}
    words = re.sub(r"[^a-zA-Z\xc0-\xff0-9\s]", " ", title_fr or "").lower().split()
    kw = [_s(w) for w in words if _s(w) and w not in excluded and _s(w) not in excluded and len(w)>2 and not re.match(r'^\d+$',_s(w))][:6]
    year = ""
    if date:
        import re as _re
        m = _re.match(r"(\d{4})", str(date))
        if m: year = m.group(1)
    if year and year not in kw:
        kw.append(year)
    parts = [p for p in [type_slug, number_slug, "-".join(kw)] if p]
    return re.sub(r"-+", "-", "-".join(parts)).strip("-")[:100]

def detect_type(title_ar):
    t = title_ar or ""
    if "خطاب صاحب الجلالة" in t or "خطاب الملك" in t: return "Discours Royal"
    if "الرسالة الملكية السامية" in t or "الرسالة الملكية" in t: return "Lettre Royale"
    if "رسالة ملكية" in t or "رسالة سامية" in t: return "Message Royal"
    if "رأي المجلس الاقتصادي" in t or "رأي مجلس" in t: return "Avis"
    if "تقرير" in t[:30]: return "Rapport"
    if "قرار" in t[:30]: return "Décision"
    if "منشور" in t[:30] or "دورية" in t[:30]: return "Circulaire"
    if "ظهير" in t[:20]: return "Dahir"
    if "مرسوم" in t[:20]: return "Décret"
    if "قانون" in t[:20]: return "Loi"
    return "Texte juridique"

def translate(title_ar, law_type, number):
    if not OAK: return None
    r = requests.post("https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OAK}", "Content-Type": "application/json", "HTTP-Referer": "https://juritheque.com"},
        json={"model": "google/gemini-2.5-flash", "max_tokens": 100, "temperature": 0.1,
              "messages": [{"role": "user", "content": f"Tu es expert en droit marocain. Traduis ce titre juridique arabe en français concis (max 120 caractères). Réponds UNIQUEMENT avec le titre traduit.\n\nType : {law_type or 'Texte juridique'}\nTitre arabe : {title_ar[:300]}"}]},
        timeout=20)
    if r.status_code == 200:
        t = r.json()["choices"][0]["message"]["content"].strip()
        return re.sub(r'^[«"\']+|[»"\']+$', '', t).strip()
    return None

# Fetch 8 textes avec placeholder adala qui ont un title_ar
r = requests.get(f"{URL}/rest/v1/laws", headers={**H, "Range": "0-7"},
    params={"select": "id,number,title_fr,title_ar,type,canonical_slug,date",
            "title_fr": "like.Texte N° adala-%", "title_ar": "not.is.null",
            "title_ar": "neq.", "order": "created_at.desc"}, timeout=20)
rows = [x for x in r.json() if x.get("title_ar")][:8]

print(f"{'─'*100}")
print(f"TEST TRADUCTION : {len(rows)} textes adala → titre FR + slug")
print(f"{'─'*100}\n")

for x in rows:
    title_ar = x.get("title_ar","")
    law_type = x.get("type","")
    number   = x.get("number","")
    old_slug = x.get("canonical_slug","")
    old_title = x.get("title_fr","")

    print(f"TYPE : {law_type}")
    print(f"AR   : {title_ar[:90]}")
    print(f"AVANT type  : {law_type}")
    print(f"AVANT titre : {old_title}")
    print(f"AVANT slug  : {old_slug}")

    detected_type = detect_type(title_ar)
    final_type = detected_type if detected_type != law_type else law_type
    date = x.get("date", "") or ""
    new_title = translate(title_ar, final_type, number)
    if new_title:
        new_slug = make_slug(final_type, number, new_title, date)
        print(f"APRÈS type  : {final_type}")
        print(f"APRÈS titre : {new_title}")
        print(f"APRÈS slug  : {new_slug}")
    else:
        print(f"❌ Traduction échouée")
    print()
