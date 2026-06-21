"""
JuriThèque — Fix batch lois Adala
══════════════════════════════════
1. Nettoyer titres "— portail Adala"
2. Générer résumés SEO pour les lois sans résumé

Usage:
  python -X utf8 pipeline/fix_adala_batch.py            # tout faire
  python -X utf8 pipeline/fix_adala_batch.py --titles   # titres seulement
  python -X utf8 pipeline/fix_adala_batch.py --summaries # résumés seulement
"""

import os, sys, re, time, argparse
from datetime import date
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or ""

# ── Session requests avec retry auto ─────────────────────────────────────────
def make_session():
    s = requests.Session()
    retry = Retry(total=5, backoff_factor=1.5,
                  status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({
        "apikey":        KEY,
        "Authorization": f"Bearer {KEY}",
        "Content-Type":  "application/json",
    })
    return s

# ── Domaines → labels ─────────────────────────────────────────────────────────
DOMAIN_LABELS = {
    "civil":             "du droit civil",
    "penal":             "du droit pénal",
    "commercial":        "du droit commercial",
    "administratif":     "du droit administratif",
    "travail":           "du droit du travail",
    "fiscal":            "du droit fiscal",
    "constitutionnel":   "du droit constitutionnel",
    "numerique":         "du droit numérique",
    "bancaire":          "du droit bancaire",
    "international":     "du droit international",
    "finances_publiques":"des finances publiques",
    "collectivites":     "des collectivités territoriales",
    "transport":         "du droit des transports",
    "environnement":     "du droit de l'environnement",
    "sante":             "du droit de la santé",
    "education":         "du droit de l'éducation",
    "agriculture":       "du droit agricole",
    "energie":           "du droit de l'énergie",
    "immobilier":        "du droit immobilier",
}

MOIS = {1:"janvier",2:"février",3:"mars",4:"avril",5:"mai",6:"juin",
        7:"juillet",8:"août",9:"septembre",10:"octobre",11:"novembre",12:"décembre"}

TYPE_PREFIX = {
    "Dahir":              "Ce dahir royal",
    "Loi":                "Cette loi",
    "Loi organique":      "Cette loi organique",
    "Loi-cadre":          "Cette loi-cadre",
    "Décret":             "Ce décret",
    "Décret royal":       "Ce décret royal",
    "Arrêté":             "Cet arrêté",
    "Arrêté ministériel": "Cet arrêté ministériel",
    "Arrêté conjoint":    "Cet arrêté conjoint",
    "Circulaire":         "Cette circulaire",
    "Code":               "Ce code",
    "Convention":         "Cette convention",
    "Traité":             "Ce traité",
}

def fmt_date(d):
    if not d: return ""
    try:
        p = d.split("-")
        return f"{int(p[2])} {MOIS[int(p[1])]} {int(p[0])}"
    except: return d

def clean_title(t):
    if not t: return ""
    return t.replace(" — portail Adala","").replace("— portail Adala","").strip(" —–-")

def generate_summary(law):
    type_fr   = law.get("type") or "Texte juridique"
    title_fr  = clean_title(law.get("title_fr") or "")
    title_ar  = law.get("title_ar") or ""
    domain_id = law.get("domain_id") or ""
    domain_ids = law.get("domain_ids") or []
    date_str  = law.get("date") or ""

    all_domains = list(dict.fromkeys([domain_id] + (domain_ids if isinstance(domain_ids,list) else [])))
    all_domains = [d for d in all_domains if d]
    primary    = all_domains[0] if all_domains else ""

    date_fr  = fmt_date(date_str)
    year     = date_str[:4] if date_str else ""
    prefix   = TYPE_PREFIX.get(type_fr, "Ce texte juridique")

    is_generic = (not title_fr or title_fr.lower().startswith("texte juridique")
                  or title_fr.lower() in ("loi","dahir","décret","arrêté"))

    # Contexte domaine(s)
    if len(all_domains) > 1:
        labs = [DOMAIN_LABELS[d] for d in all_domains[:3] if d in DOMAIN_LABELS]
        domain_ctx = "relevant " + ", ".join(labs) if labs else ""
    else:
        domain_ctx = f"relevant {DOMAIN_LABELS[primary]}" if primary in DOMAIN_LABELS else ""

    sentences = []

    # Phrase 1 — identification
    if not is_generic:
        sentences.append(f"{title_fr}.")
    elif law.get("number") and date_fr:
        sentences.append(f"{type_fr} n°{law['number']} du {date_fr}.")
    elif law.get("number"):
        sentences.append(f"{type_fr} n°{law['number']}.")
    else:
        sentences.append(f"{type_fr} marocain publié par le portail officiel Adala du Ministère de la Justice.")

    # Phrase 2 — domaine + date
    if domain_ctx and date_fr:
        sentences.append(f"{prefix} {domain_ctx} a été promulgué le {date_fr}.")
    elif domain_ctx and year:
        sentences.append(f"{prefix} {domain_ctx} a été promulgué en {year}.")
    elif domain_ctx:
        sentences.append(f"{prefix} constitue un texte de référence {domain_ctx}.")
    elif date_fr:
        sentences.append(f"Ce texte a été publié le {date_fr}.")

    # Phrase 3 — disponibilité
    if title_ar and not is_generic:
        sentences.append(
            "Disponible en version arabe sur le portail officiel du Ministère de la Justice "
            "marocain (Adala), ce texte est consultable et téléchargeable en format PDF."
        )
    else:
        sentences.append(
            "Ce texte fait partie de la base de données juridique JuriThèque, "
            "regroupant les lois, dahirs, décrets et arrêtés publiés au Bulletin Officiel du Royaume du Maroc."
        )

    summary = " ".join(sentences)
    if len(summary) < 280:
        summary += " Retrouvez l'intégralité de ce texte ainsi que les textes liés dans la base JuriThèque."

    # SEO title
    if not is_generic and len(title_fr) <= 60:
        seo_title = f"{title_fr} | JuriThèque"
    elif not is_generic:
        seo_title = f"{title_fr[:57]}… | JuriThèque"
    elif law.get("number"):
        seo_title = f"{type_fr} n°{law['number']} — Droit marocain | JuriThèque"
    else:
        dom_short = DOMAIN_LABELS.get(primary,"droit marocain").replace("du ","").replace("de la ","").replace("de l'","").replace("des ","").title()
        seo_title = f"{type_fr} — {dom_short} marocain | JuriThèque"

    # SEO desc (150-158 chars)
    seo_desc = " ".join(sentences[:2])
    if len(seo_desc) > 158: seo_desc = seo_desc[:155] + "…"
    elif len(seo_desc) < 100: seo_desc = summary[:158]

    return {
        "simple_summary_fr":    summary[:600],
        "seo_title_fr":         seo_title[:200],
        "seo_description_fr":   seo_desc[:300],
        "summary_generated_at": date.today().isoformat(),
    }

# ── FIX TITRES ────────────────────────────────────────────────────────────────
def fix_titles(session):
    print("\n=== FIX TITRES 'portail Adala' ===")
    offset, total = 0, 0
    while True:
        r = session.get(f"{URL}/rest/v1/laws", params={
            "source_name": "eq.Adala",
            "title_fr":    "ilike.*portail Adala*",
            "select":      "id,title_fr",
            "limit":       "500",
            "offset":      str(offset),
        }, timeout=30)
        batch = r.json()
        if not batch or not isinstance(batch, list): break

        for law in batch:
            new_title = clean_title(law["title_fr"])
            resp = session.patch(
                f"{URL}/rest/v1/laws?id=eq.{law['id']}",
                json={"title_fr": new_title},
                timeout=30
            )
            if resp.status_code in (200, 204):
                total += 1
            else:
                print(f"  ERR id={law['id']}: {resp.text[:60]}")

        print(f"  {total} titres corrigés (batch offset={offset})...", flush=True)
        if len(batch) < 500: break
        offset += 500
        time.sleep(0.3)

    print(f"  ✅ TOTAL titres nettoyés: {total}")
    return total

# ── GÉNÉRATION RÉSUMÉS ────────────────────────────────────────────────────────
def gen_summaries(session):
    print("\n=== GÉNÉRATION RÉSUMÉS SEO ===")

    # Compter
    r = session.get(f"{URL}/rest/v1/laws", params={
        "source_name": "eq.Adala", "simple_summary_fr": "is.null",
        "select": "id", "limit": "1",
    }, headers={**session.headers, "Prefer":"count=exact","Range-Unit":"items","Range":"0-0"}, timeout=30)
    total_todo = int(r.headers.get("content-range","0/0").split("/")[-1])
    print(f"  {total_todo:,} lois sans résumé à traiter")

    done, errors = 0, 0
    while True:
        # Toujours offset=0 : les lois updatées n'ont plus simple_summary_fr=is.null
        # donc la prochaine requête retourne automatiquement le batch suivant
        r = session.get(f"{URL}/rest/v1/laws", params={
            "source_name":       "eq.Adala",
            "simple_summary_fr": "is.null",
            "select":            "id,number,type,title_fr,title_ar,domain_id,domain_ids,date",
            "limit":             "300",
            "order":             "id.asc",
        }, timeout=30)
        batch = r.json()
        if not batch or not isinstance(batch, list): break

        for law in batch:
            try:
                patch = generate_summary(law)
                resp = session.patch(
                    f"{URL}/rest/v1/laws?id=eq.{law['id']}",
                    json=patch,
                    timeout=30
                )
                if resp.status_code in (200, 204):
                    done += 1
                else:
                    errors += 1
                    print(f"  ERR id={law['id']}: {resp.text[:60]}")
            except Exception as e:
                errors += 1
                print(f"  EXC id={law.get('id')}: {e}")

        remaining = total_todo - done
        pct = int(done / total_todo * 100) if total_todo else 0
        print(f"  {done:,}/{total_todo:,} ({pct}%) résumés générés | {errors} erreurs | restants ~{remaining:,}", flush=True)

        if len(batch) < 300: break
        time.sleep(0.1)

    print(f"  ✅ TOTAL résumés: {done} | erreurs: {errors}")
    return done

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--titles",   action="store_true")
    parser.add_argument("--summaries",action="store_true")
    args = parser.parse_args()

    do_all = not args.titles and not args.summaries
    session = make_session()

    print("JuriThèque — Fix batch lois Adala")
    print(f"URL: {URL[:40]}...")

    if do_all or args.titles:
        fix_titles(session)

    if do_all or args.summaries:
        gen_summaries(session)

    print("\n🎉 Terminé !")

if __name__ == "__main__":
    main()
