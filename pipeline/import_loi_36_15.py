"""
Import manuel — Loi 36-15 relative à l'eau
===========================================
Insère directement dans Supabase sans PDF (métadonnées connues).
Source officielle : sgg.gov.ma — BO n° 6490 du 20 hija 1437 (22 septembre 2016)

Usage :
  python pipeline/import_loi_36_15.py
  python pipeline/import_loi_36_15.py --dry-run
"""

import os, sys, json, argparse
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", ""))

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Prefer": "return=representation",
}

LAW_DATA = {
    "number":     "36-15",
    "type":       "Loi",
    "domain_id":  "environnement",
    "status":     "En vigueur",
    "date":       "2016-09-22",
    "title_fr":   "Loi n° 36-15 relative à l'eau",
    "title_ar":   "القانون رقم 36-15 المتعلق بالماء",
    "excerpt_fr": (
        "Loi n° 36-15 relative à l'eau, promulguée par le Dahir n° 1-16-113 du 6 kaada 1437 "
        "(10 août 2016). Elle régit le domaine public hydraulique, la planification des ressources "
        "en eau, la prévention des inondations et la protection des eaux contre la pollution. "
        "Publiée au Bulletin Officiel n° 6490 du 20 hija 1437 (22 septembre 2016)."
    ),
    "excerpt_ar": (
        "القانون رقم 36-15 المتعلق بالماء، الصادر بتنفيذه الظهير الشريف رقم 1-16-113 بتاريخ "
        "6 ذي القعدة 1437 (10 غشت 2016). يضبط هذا القانون الملك العام المائي وتخطيط الموارد المائية "
        "والوقاية من الفيضانات وحماية المياه من التلوث. نُشر في الجريدة الرسمية عدد 6490 بتاريخ "
        "20 ذي الحجة 1437 (22 شتنبر 2016)."
    ),
    "language":   "Bilingue",
    "tags":       ["eau", "domaine hydraulique", "ressources en eau", "pollution", "inondations",
                   "agences de bassin", "redevances hydrauliques", "planification"],
    "pdf_url":    "https://www.sgg.gov.ma/BO/fr/2016/bo_6490_fr.pdf",
    "bo_number":  "6490",
    "canonical_slug": "loi-36-15-relative-a-l-eau",
}


def check_exists() -> bool:
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers={**HEADERS, "Content-Type": "application/json"},
        params={"number": "ilike.*36-15*", "select": "id,number,title_fr", "limit": "3"},
        timeout=10,
    )
    rows = resp.json() if resp.status_code == 200 and isinstance(resp.json(), list) else []
    if rows:
        print(f"  ⚠️  Déjà présente : {rows[0].get('title_fr')} (id={rows[0].get('id')})")
        return True
    return False


def insert() -> dict:
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        json=LAW_DATA,
        timeout=15,
    )
    if resp.status_code in (200, 201):
        rows = resp.json()
        return rows[0] if isinstance(rows, list) else rows
    else:
        raise RuntimeError(f"Erreur {resp.status_code} : {resp.text[:300]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Afficher sans insérer")
    args = parser.parse_args()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Import — Loi 36-15 relative à l'eau")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("  ❌ Variables SUPABASE_URL / SUPABASE_KEY manquantes dans .env")
        sys.exit(1)

    print("  Données à insérer :")
    print(f"    Numéro  : {LAW_DATA['number']}")
    print(f"    Titre   : {LAW_DATA['title_fr']}")
    print(f"    Titre AR: {LAW_DATA['title_ar']}")
    print(f"    Domaine : {LAW_DATA['domain_id']}")
    print(f"    Date    : {LAW_DATA['date']}")
    print(f"    BO      : {LAW_DATA['bo_number']}\n")

    if args.dry_run:
        print("  [DRY-RUN] Rien n'a été inséré.")
        print(f"\n  JSON complet :\n{json.dumps(LAW_DATA, ensure_ascii=False, indent=2)}")
        return

    print("  Vérification doublon...")
    if check_exists():
        print("  ✅ La loi est déjà dans la base — rien à faire.")
        return

    print("  Insertion en cours...")
    try:
        row = insert()
        print(f"\n  ✅ Loi 36-15 insérée avec succès !")
        print(f"     ID   : {row.get('id')}")
        print(f"     Slug : {row.get('canonical_slug')}")
        print(f"     URL  : /loi/{row.get('canonical_slug') or row.get('id')}")
    except RuntimeError as e:
        print(f"\n  ❌ Erreur d'insertion : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
