"""
fix_title_fr_from_ar.py — Corrige les 545 records avec title_fr ≠ title_ar (mismatch de date)

Stratégie (après analyse) :
  - title_ar en base = CORRECT (vient d'Adala, source officielle)
  - title_fr en base = FAUX (IA a halluciné lors du lookup par numéro, confusion avec décret adjacent)
  - FIX : traduire title_ar → nouveau title_fr via AI, régénérer canonical_slug, sauver ancien slug dans slug_history

Usage :
  python pipeline/fix_title_fr_from_ar.py --preview 10   # affiche 10 corrections sans écrire
  python pipeline/fix_title_fr_from_ar.py --apply        # applique toutes les corrections
  python pipeline/fix_title_fr_from_ar.py --apply --limit 50  # par batch
"""

import os, re, sys, time, json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True); load_dotenv()

import requests
from rich.console import Console
from rich.table import Table

console = Console()
def log(m): console.print(m)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
KEY          = os.getenv("SUPABASE_SERVICE_KEY", "")
OPENROUTER   = os.getenv("OPENROUTER_API_KEY", "")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

AR_MONTHS = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "أبريل": 4, "ماي": 5, "يونيو": 6,
    "يوليو": 7, "يوليوز": 7, "غشت": 8, "أغسطس": 8, "شتنبر": 9, "سبتمبر": 9,
    "أكتوبر": 10, "نونبر": 11, "نوفمبر": 11, "دجنبر": 12, "ديسمبر": 12,
}
FR_MONTHS = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12,
}


def extract_ym(text, months):
    text = (text or "").lower()
    years = re.findall(r'\b(1[89]\d\d|20\d\d)\b', text)
    year = int(years[0]) if years else None
    month = None
    for m_name, m_num in months.items():
        if m_name in text:
            month = m_num
            break
    return year, month


def is_date_mismatch(title_fr, title_ar):
    yr_fr, mo_fr = extract_ym(title_fr, FR_MONTHS)
    yr_ar, mo_ar = extract_ym(title_ar, AR_MONTHS)
    if not yr_fr or not yr_ar:
        return False
    year_diff  = abs(yr_fr - yr_ar) > 1
    month_diff = (mo_fr and mo_ar and mo_fr != mo_ar and yr_fr == yr_ar)
    return year_diff or month_diff


def ai_translate_ar_to_fr(title_ar: str, law_type: str, number: str) -> str | None:
    """Traduit un titre arabe en titre français officiel via Gemini Flash."""
    if not OPENROUTER or not title_ar:
        return None
    prompt = (
        "Tu es un juriste marocain expert en traduction juridique officielle. "
        "Traduis ce titre arabe de texte juridique marocain en français, dans le style exact du Bulletin Officiel.\n"
        "Réponds UNIQUEMENT avec le titre traduit, sans explication ni guillemets.\n"
        "Inclus le numéro et la date s'ils sont présents dans le titre arabe.\n\n"
        f"Type : {law_type or 'Texte juridique'}\n"
        f"Numéro : {number or 'inconnu'}\n"
        f"Titre arabe : {title_ar}"
    )
    try:
        for attempt in range(2):
            try:
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENROUTER}", "Content-Type": "application/json"},
                    json={"model": "google/gemini-2.5-flash", "max_tokens": 300, "temperature": 0.1,
                          "messages": [{"role": "user", "content": prompt}]},
                    timeout=30,
                )
                if r.status_code == 200:
                    title = r.json()["choices"][0]["message"]["content"].strip().strip('"\'«»').split("\n")[0]
                    if len(title) > 10:
                        return title[:280]
                break
            except Exception as e:
                if attempt == 0:
                    time.sleep(3)
                else:
                    log(f"  [red]Erreur traduction: {e}[/]")
    except Exception as e:
        log(f"  [red]Erreur traduction: {e}[/]")
    return None


def ai_translate_fr_to_ar(title_fr: str, law_type: str, number: str) -> str | None:
    """Traduit un titre français en titre arabe officiel via Gemini Flash."""
    if not OPENROUTER or not title_fr:
        return None
    prompt = (
        "Tu es un juriste marocain expert en traduction juridique officielle. "
        "Traduis ce titre français de texte juridique marocain en arabe, dans le style du Bulletin Officiel marocain.\n"
        "Réponds UNIQUEMENT avec le titre traduit en arabe, sans explication.\n\n"
        f"Type : {law_type or 'Texte juridique'}\n"
        f"Numéro : {number or 'inconnu'}\n"
        f"Titre français : {title_fr}"
    )
    try:
        for attempt in range(2):
            try:
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENROUTER}", "Content-Type": "application/json"},
                    json={"model": "google/gemini-2.5-flash", "max_tokens": 300, "temperature": 0.1,
                          "messages": [{"role": "user", "content": prompt}]},
                    timeout=30,
                )
                if r.status_code == 200:
                    title = r.json()["choices"][0]["message"]["content"].strip().split("\n")[0]
                    if len(title) > 10:
                        return title[:300]
                break
            except Exception:
                if attempt == 0:
                    time.sleep(3)
    except Exception as e:
        log(f"  [red]Erreur traduction FR→AR: {e}[/]")
    return None


def make_slug(law_type, number, title_fr):
    """Génère un canonical_slug {type}-{number}-{keywords}."""
    import unicodedata
    STOPWORDS = {
        'le','la','les','du','de','des','au','aux','et','ou','n','sur',
        'relatif','relative','portant','fixant','instituant','modifiant',
        'dahir','decret','loi','arrete','circulaire','texte','par',
        'une','un','est','en','dans','pour','avec','sans',
        # mois hégiriens et grégoriens
        'moharrem','safar','rabii','joumada','rajab','chaabane','ramadan',
        'chaoual','kaada','hija','rejeb','chaaban','rebia','moharram',
        'janvier','fevrier','mars','avril','mai','juin','juillet','aout',
        'septembre','octobre','novembre','decembre',
        'promulgation','publication','promulguant','publiant','approbation',
        'portant','pris','faite','fait','signe','signe','entre',
    }

    def normalize(t):
        """Supprime les accents AVANT de retirer les non-ASCII."""
        norm = unicodedata.normalize("NFD", (t or "").lower())
        norm = "".join(c for c in norm if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z0-9\s]", " ", norm)

    def slugify(t):
        norm = normalize(t)
        return re.sub(r"\s+", "-", norm).strip("-")

    type_slug   = slugify(law_type or "texte")
    number_slug = slugify(number or "")

    # Extraire keywords : normaliser d'abord les accents, puis filtrer
    clean_title = normalize(title_fr or "")
    words       = clean_title.split()
    keywords    = [
        w for w in words
        if w not in STOPWORDS
        and len(w) > 2
        and not re.match(r'^\d+$', w)   # pas de chiffres seuls (années, n°)
    ][:7]

    kw_slug = "-".join(keywords)
    parts   = [p for p in [type_slug, number_slug, kw_slug] if p]
    slug    = re.sub(r"-+", "-", "-".join(parts)).strip("-")[:120]
    return slug


# ── Fetch des mismatches ────────────────────────────────────────────────────
def fetch_mismatches(limit=None):
    """Récupère tous les records avec date FR ≠ date AR."""
    all_laws, offset = [], 0
    while True:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/laws", headers=H,
            params={"select": "id,number,title_fr,title_ar,canonical_slug,type,date,slug_history",
                    "title_fr": "not.is.null", "title_ar": "not.is.null",
                    "limit": "1000", "offset": str(offset)})
        batch = r.json()
        if not batch: break
        all_laws.extend(batch)
        offset += len(batch)
        if len(batch) < 1000: break

    mismatches = []
    for x in all_laws:
        if is_date_mismatch(x.get("title_fr",""), x.get("title_ar","")):
            mismatches.append(x)
        if limit and len(mismatches) >= limit:
            break

    return mismatches


# ── Main ────────────────────────────────────────────────────────────────────
preview_n = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--preview=")), "0"))
if "--preview" in sys.argv and not preview_n:
    preview_n = int(sys.argv[sys.argv.index("--preview") + 1]) if sys.argv.index("--preview") + 1 < len(sys.argv) else 10
apply     = "--apply" in sys.argv
limit_arg = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--limit=")), "0"))

mode = "apply" if apply else ("preview" if preview_n else "preview")
if not preview_n and not apply:
    preview_n = 10  # défaut : afficher 10

log(f"\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
log(f"[bold gold1]  fix_title_fr_from_ar.py  mode={mode}[/]")
log(f"[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

log("[dim]Chargement des mismatches depuis Supabase...[/]")
fetch_limit = preview_n if not apply else (limit_arg or None)
mismatches  = fetch_mismatches(limit=fetch_limit if not apply else None)
log(f"→ {len(mismatches)} records avec date FR ≠ date AR\n")

if not mismatches:
    log("[green]Aucun mismatch détecté.[/]")
    sys.exit(0)

to_process = mismatches[:preview_n] if not apply else (mismatches[:limit_arg] if limit_arg else mismatches)

results = []
errors  = 0

for i, law in enumerate(to_process, 1):
    lid      = law["id"]
    number   = law.get("number") or ""
    law_type = law.get("type") or "Texte juridique"
    title_ar = law.get("title_ar") or ""
    old_fr   = law.get("title_fr") or ""
    old_slug = law.get("canonical_slug") or ""
    slug_hist= law.get("slug_history") or []

    log(f"  [{i}/{len(to_process)}] ID {lid}  n°={number}")
    log(f"    AR (correct): {title_ar[:80]}")
    log(f"    FR (faux)   : {old_fr[:80]}")

    # Détecter si title_ar est en fait en français (pas de caractères arabes)
    has_arabic = bool(re.search(r'[؀-ۿ]', title_ar))

    # Traduction AR → nouveau FR (depuis le vrai titre arabe)
    new_fr = ai_translate_ar_to_fr(title_ar, law_type, number)
    if not new_fr:
        log(f"    [red]✗ Traduction échouée — skip[/]")
        errors += 1
        continue

    # Si title_ar était en français → le corriger aussi (traduire le nouveau title_fr → AR)
    new_ar = None
    if not has_arabic:
        log(f"    [yellow]⚠ title_ar est en français → traduction vers arabe[/]")
        new_ar = ai_translate_fr_to_ar(new_fr, law_type, number)

    # Nouveau slug
    new_slug = make_slug(law_type, number, new_fr)

    # Slug history : ajouter ancien slug si pas déjà dedans
    new_hist = list(slug_hist) if slug_hist else []
    if old_slug and old_slug not in new_hist:
        new_hist.append(old_slug)

    log(f"    FR (nouveau): [green]{new_fr[:80]}[/]")
    log(f"    Slug        : {old_slug} → [cyan]{new_slug}[/]")

    results.append({
        "id":             lid,
        "number":         number,
        "old_title_fr":   old_fr,
        "new_title_fr":   new_fr,
        "new_title_ar":   new_ar,
        "old_slug":       old_slug,
        "new_slug":       new_slug,
        "new_slug_history": new_hist,
    })

    if apply:
        patch = {
            "title_fr":       new_fr,
            "canonical_slug": new_slug,
            "slug_history":   new_hist,
        }
        if new_ar:
            patch["title_ar"] = new_ar
            log(f"    title_ar → [green]{new_ar[:60]}[/]")
        patched = False
        for attempt in range(3):
            try:
                r = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/laws?id=eq.{lid}",
                    headers=H, json=patch, timeout=20,
                )
                if r.status_code in (200, 204):
                    log(f"    [green]✓ PATCHÉ[/]")
                    patched = True
                else:
                    log(f"    [red]✗ PATCH échoué: {r.status_code} {r.text[:100]}[/]")
                    errors += 1
                break
            except Exception as e:
                if attempt < 2:
                    log(f"    [yellow]Réseau: {e} — retry {attempt+2}/3[/]")
                    time.sleep(5)
                else:
                    log(f"    [red]✗ Abandon après 3 tentatives: {e}[/]")
                    errors += 1

    time.sleep(0.3)

# ── Tableau récap ────────────────────────────────────────────────────────────
log(f"\n[bold]━━━ Résumé ━━━[/]")
log(f"  Traités : {len(results)}/{len(to_process)}")
if errors: log(f"  [red]Erreurs  : {errors}[/]")

if not apply and results:
    t = Table(title=f"Aperçu {len(results)} corrections (mode preview)", show_lines=True)
    t.add_column("n°", style="dim", width=12)
    t.add_column("AR (correct)", width=40)
    t.add_column("Nouveau title_fr", width=45)
    t.add_column("Nouveau slug (extrait)", width=35)
    for r in results:
        t.add_row(
            r["number"],
            r["old_title_fr"][:38] + "…" if len(r["old_title_fr"]) > 38 else r["old_title_fr"],
            r["new_title_fr"][:43] + "…" if len(r["new_title_fr"]) > 43 else r["new_title_fr"],
            r["new_slug"][:33] + "…" if len(r["new_slug"]) > 33 else r["new_slug"],
        )
    console.print(t)
    log(f"\n[dim]→ Valider puis lancer : python pipeline/fix_title_fr_from_ar.py --apply[/]")

if apply:
    log(f"\n[bold green]✅ {len(results) - errors} records corrigés[/]")
    if errors:
        log(f"[yellow]⚠ {errors} erreurs — relancer pour les records manquants[/]")
