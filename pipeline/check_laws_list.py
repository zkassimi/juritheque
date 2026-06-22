"""
Vérification des lois prioritaires dans la base Supabase
=========================================================
Compare une liste de lois (CSV) avec la base de données et indique :
  ✅ Trouvée  — la loi est dans la base
  ❌ Manquante — introuvable par numéro ni titre

Usage :
  python pipeline/check_laws_list.py --csv pipeline/laws_priority_list.csv
  python pipeline/check_laws_list.py --csv pipeline/laws_priority_list.csv --export pipeline/laws_report.csv
"""

import os, sys, re, csv, json, argparse
from pathlib import Path
from dotenv import load_dotenv
import requests
from rich.console import Console
from rich.table import Table

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", ""))

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Accept": "application/json",
}

console = Console()


# ── Requêtes Supabase ──────────────────────────────────────────────────────────

def search_by_number(number: str) -> list:
    """Cherche par numéro de loi (ex: 103-12, 2-22-431, 65-99)."""
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={
            "select": "id,number,title_fr,title_ar,type,canonical_slug",
            "number": f"ilike.*{number}*",
            "limit": "5",
        },
        timeout=10,
    )
    return resp.json() if resp.status_code == 200 and isinstance(resp.json(), list) else []


def search_by_title(title_fr: str, title_ar: str = "") -> list:
    """Cherche par mots-clés du titre FR ou AR."""
    # Prendre les 3 premiers mots significatifs du titre
    words = [w for w in title_fr.split() if len(w) > 3][:3]
    if not words:
        return []
    keyword = words[0]  # mot le plus discriminant

    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={
            "select": "id,number,title_fr,title_ar,type,canonical_slug",
            "title_fr": f"ilike.*{keyword}*",
            "limit": "5",
        },
        timeout=10,
    )
    results = resp.json() if resp.status_code == 200 and isinstance(resp.json(), list) else []

    # Filtrer par pertinence : vérifier que d'autres mots matchent aussi
    if len(results) > 1 and len(words) > 1:
        filtered = []
        for r in results:
            tf = (r.get("title_fr") or "").lower()
            score = sum(1 for w in words if w.lower() in tf)
            if score >= min(2, len(words)):
                filtered.append(r)
        return filtered if filtered else results[:1]

    return results


def find_law(numero: str, titre_fr: str, titre_ar: str) -> tuple[str, list]:
    """Retourne (méthode_de_recherche, résultats)."""
    # 1. Recherche par numéro si disponible
    if numero and numero.strip():
        results = search_by_number(numero.strip())
        if results:
            return "numéro", results

    # 2. Recherche par titre FR
    if titre_fr:
        results = search_by_title(titre_fr, titre_ar)
        if results:
            return "titre", results

    return "non trouvée", []


# ── Lecture du CSV ─────────────────────────────────────────────────────────────

BUILTIN_LIST = """Priorité;Domaine;Type;Numéro;Titre_FR;Titre_AR;Règle_de_vérification
1;Constitution et institutions;Constitution;2011;Constitution du Royaume du Maroc;دستور المملكة المغربية;Vérifier texte constitutionnel principal
1;Constitution et institutions;Loi organique;130-13;Loi organique relative à la loi de finances;القانون التنظيمي لقانون المالية;Vérifier version consolidée
1;Constitution et institutions;Loi organique;;Loi organique relative à la Chambre des représentants;القانون التنظيمي المتعلق بمجلس النواب;Vérifier par titre et variantes
1;Constitution et institutions;Loi organique;;Loi organique relative à la Chambre des conseillers;القانون التنظيمي المتعلق بمجلس المستشارين;Vérifier par titre et variantes
1;Constitution et institutions;Loi organique;;Loi organique relative aux partis politiques;القانون التنظيمي المتعلق بالأحزاب السياسية;Vérifier par titre et variantes
1;Justice;Loi organique;;Loi organique relative au Conseil supérieur du pouvoir judiciaire;القانون التنظيمي المتعلق بالمجلس الأعلى للسلطة القضائية;Vérifier version consolidée
1;Justice;Loi organique;;Loi organique portant statut des magistrats;القانون التنظيمي المتعلق بالنظام الأساسي للقضاة;Vérifier version consolidée
1;Codes fondamentaux;Code;;Code des obligations et des contrats;قانون الالتزامات والعقود;Texte indispensable
1;Codes fondamentaux;Code;;Code pénal;القانون الجنائي;Vérifier version consolidée
1;Codes fondamentaux;Code;;Code de procédure pénale;قانون المسطرة الجنائية;Vérifier version consolidée
1;Codes fondamentaux;Code;;Code de procédure civile;قانون المسطرة المدنية;Vérifier version consolidée
1;Codes fondamentaux;Code;;Code de la famille / Moudawana;مدونة الأسرة;Vérifier version consolidée
1;Codes fondamentaux;Code;65-99;Code du travail;مدونة الشغل;Vérifier version consolidée
1;Codes fondamentaux;Code;15-95;Code de commerce;مدونة التجارة;Vérifier version consolidée
1;Codes fondamentaux;Code;39-08;Code des droits réels;مدونة الحقوق العينية;Vérifier version consolidée
1;Codes fondamentaux;Code;15-97;Code de recouvrement des créances publiques;مدونة تحصيل الديون العمومية;Vérifier version consolidée
1;Fiscalité;Code;;Code général des impôts;المدونة العامة للضرائب;Vérifier par année + version consolidée
1;Fiscalité;Code;;Code des douanes et impôts indirects;مدونة الجمارك والضرائب غير المباشرة;Vérifier version consolidée
1;Circulation;Code;52-05;Code de la route;مدونة السير على الطرق;Vérifier version consolidée
2;Assurances;Code;;Code des assurances;مدونة التأمينات;Vérifier version consolidée
2;Santé;Code;;Code du médicament et de la pharmacie;مدونة الأدوية والصيدلة;Vérifier version consolidée
1;Collectivités territoriales;Loi organique;111-14;Loi organique relative aux régions;القانون التنظيمي المتعلق بالجهات;Très prioritaire
1;Collectivités territoriales;Loi organique;112-14;Loi organique relative aux préfectures et provinces;القانون التنظيمي المتعلق بالعمالات والأقاليم;Très prioritaire
1;Collectivités territoriales;Loi organique;113-14;Loi organique relative aux communes;القانون التنظيمي المتعلق بالجماعات;Très prioritaire
1;Collectivités territoriales;Loi;47-06;Fiscalité des collectivités territoriales;جبايات الجماعات الترابية;Vérifier version consolidée
1;Marchés publics;Décret;2-22-431;Décret relatif aux marchés publics;مرسوم الصفقات العمومية;Très prioritaire
1;Comptabilité publique;Décret royal;330-66;Règlement général de comptabilité publique;النظام العام للمحاسبة العمومية;Vérifier version consolidée
1;Finances publiques;Loi;69-00;Contrôle financier de l'État sur les entreprises publiques;المراقبة المالية للدولة على المنشآت العامة;Vérifier version consolidée
1;Finances publiques;Loi;15-97;Code de recouvrement des créances publiques;مدونة تحصيل الديون العمومية;Vérifier version consolidée
2;Finances publiques;Loi;86-12;Contrats de partenariat public-privé;عقود الشراكة بين القطاعين العام والخاص;Vérifier version consolidée
1;Justice;Loi;38-15;Organisation judiciaire;التنظيم القضائي;Très prioritaire
1;Justice;Loi;;Tribunaux administratifs;المحاكم الإدارية;Vérifier texte fondateur + modifications
1;Justice;Loi;;Tribunaux de commerce;المحاكم التجارية;Vérifier texte fondateur + modifications
1;Professions juridiques;Loi;;Profession d'avocat;مهنة المحاماة;Vérifier version consolidée
1;Professions juridiques;Loi;;Profession de notaire;مهنة التوثيق;Vérifier version consolidée
1;Professions juridiques;Loi;;Huissiers de justice;المفوضون القضائيون;Vérifier version consolidée
1;Administration publique;Dahir;;Statut général de la fonction publique;النظام الأساسي العام للوظيفة العمومية;Très prioritaire
1;Administration publique;Loi;;Droit d'accès à l'information;الحق في الحصول على المعلومات;Très prioritaire
1;Administration publique;Loi;7-81;Expropriation pour cause d'utilité publique;نزع الملكية لأجل المنفعة العامة;Très prioritaire
1;Urbanisme et foncier;Loi;12-90;Urbanisme;التعمير;Très prioritaire
1;Urbanisme et foncier;Loi;25-90;Lotissements, groupes d'habitations et morcellements;التجزئات العقارية;Très prioritaire
1;Urbanisme et foncier;Loi;39-08;Code des droits réels;مدونة الحقوق العينية;Vérifier version consolidée
1;Urbanisme et foncier;Dahir;;Immatriculation foncière;التحفيظ العقاري;Très prioritaire
1;Urbanisme et foncier;Loi;18-00;Copropriété des immeubles bâtis;نظام الملكية المشتركة للعقارات المبنية;Très prioritaire
1;Affaires et entreprises;Code;15-95;Code de commerce;مدونة التجارة;Très prioritaire
1;Affaires et entreprises;Loi;17-95;Sociétés anonymes;شركات المساهمة;Très prioritaire
1;Affaires et entreprises;Loi;5-96;Sociétés commerciales autres que les sociétés anonymes;باقي الشركات التجارية;Très prioritaire
1;Concurrence;Loi;104-12;Liberté des prix et de la concurrence;حرية الأسعار والمنافسة;Très prioritaire
1;Concurrence;Loi;20-13;Conseil de la concurrence;مجلس المنافسة;Très prioritaire
1;Consommation;Loi;31-08;Protection du consommateur;حماية المستهلك;Très prioritaire
1;Banque et finance;Loi;103-12;Établissements de crédit et organismes assimilés;مؤسسات الائتمان;Très prioritaire
1;Investissement;Loi;47-18;Réforme des centres régionaux d'investissement;إصلاح المراكز الجهوية للاستثمار;Vérifier version consolidée
2;Propriété intellectuelle;Loi;2-00;Droits d'auteur et droits voisins;حقوق المؤلف والحقوق المجاورة;Vérifier version consolidée
1;Travail et social;Code;65-99;Code du travail;مدونة الشغل;Très prioritaire
1;Protection sociale;Loi;98-15;AMO des travailleurs indépendants;التأمين الإجباري الأساسي عن المرض;Vérifier version consolidée
1;Protection sociale;Loi;60-22;Régime de l'AMO;نظام التأمين الإجباري الأساسي عن المرض;Vérifier version consolidée
1;Protection sociale;Loi;58-23;Régime d'aide sociale directe;نظام الدعم الاجتماعي المباشر;Vérifier version consolidée
1;Libertés publiques;Dahir;1958;Droit d'association;حق تأسيس الجمعيات;Très prioritaire
1;Libertés publiques;Loi;;Presse et édition;الصحافة والنشر;Très prioritaire
1;Libertés publiques;Loi;;Droit d'accès à l'information;الحق في الحصول على المعلومات;Très prioritaire
1;Données personnelles;Loi;09-08;Protection des données personnelles;حماية المعطيات ذات الطابع الشخصي;Très prioritaire
1;Citoyenneté;Code;;Code de la nationalité marocaine;قانون الجنسية المغربية;Très prioritaire
1;État civil;Loi;;État civil;الحالة المدنية;Très prioritaire
1;Étrangers;Loi;;Entrée et séjour des étrangers au Maroc;دخول وإقامة الأجانب بالمغرب;Très prioritaire
1;Environnement;Loi;36-15;Eau;الماء;Très prioritaire
1;Environnement;Loi;28-00;Gestion des déchets et élimination;تدبير النفايات والتخلص منها;Très prioritaire
1;Énergie;Loi;13-09;Énergies renouvelables;الطاقات المتجددées;Très prioritaire
1;Énergie;Loi;48-15;Régulation du secteur de l'électricité;ضبط قطاع الكهرباء;Vérifier version consolidée
"""

def parse_builtin() -> list[dict]:
    rows = []
    lines = BUILTIN_LIST.strip().split("\n")
    headers = lines[0].split(";")
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split(";")
        if len(parts) >= 6:
            rows.append({
                "priorite":  parts[0].strip(),
                "domaine":   parts[1].strip(),
                "type":      parts[2].strip(),
                "numero":    parts[3].strip(),
                "titre_fr":  parts[4].strip(),
                "titre_ar":  parts[5].strip(),
                "regle":     parts[6].strip() if len(parts) > 6 else "",
            })
    return rows


def parse_csv(filepath: str) -> list[dict]:
    rows = []
    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            rows.append({
                "priorite": row.get("Priorité", "").strip(),
                "domaine":  row.get("Domaine", "").strip(),
                "type":     row.get("Type", "").strip(),
                "numero":   row.get("Numéro", "").strip(),
                "titre_fr": row.get("Titre_FR", "").strip(),
                "titre_ar": row.get("Titre_AR", "").strip(),
                "regle":    row.get("Règle_de_vérification", "").strip(),
            })
    return rows


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", help="Fichier CSV source (optionnel — liste intégrée utilisée par défaut)")
    parser.add_argument("--export", help="Exporter le rapport en CSV")
    parser.add_argument("--missing-only", action="store_true", help="Afficher seulement les lois manquantes")
    args = parser.parse_args()

    laws = parse_csv(args.csv) if args.csv else parse_builtin()

    console.print(f"\n[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    console.print(f"[bold]  Vérification des lois prioritaires       [/]")
    console.print(f"[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")
    console.print(f"  {len(laws)} lois à vérifier...\n")

    results = []
    found = 0
    missing = 0

    for i, law in enumerate(laws, 1):
        method, matches = find_law(law["numero"], law["titre_fr"], law["titre_ar"])
        status = "✅" if matches else "❌"
        match_title = matches[0].get("title_fr", "")[:60] if matches else ""
        match_slug  = matches[0].get("canonical_slug", "") if matches else ""
        match_num   = matches[0].get("number", "") if matches else ""

        if matches:
            found += 1
        else:
            missing += 1

        result = {
            **law,
            "statut": "TROUVÉE" if matches else "MANQUANTE",
            "methode": method,
            "match_titre": match_title,
            "match_numero": match_num,
            "match_slug": match_slug,
        }
        results.append(result)

        if not args.missing_only or not matches:
            color = "green" if matches else "red"
            num_str = f"[{law['numero']}] " if law['numero'] else ""
            console.print(
                f"  {status} [{color}]P{law['priorite']} · {law['domaine']}[/] — "
                f"{num_str}{law['titre_fr'][:55]}"
            )
            if matches:
                console.print(f"     [dim]→ {match_title} ({method})[/]")

    # ── Résumé ──────────────────────────────────────────────────────────────
    console.print(f"\n[bold]━━━━ Résumé ━━━━[/]")
    console.print(f"  [green]✅ Trouvées   : {found}[/]")
    console.print(f"  [red]❌ Manquantes : {missing}[/]")
    console.print(f"  Total        : {len(laws)}")

    # ── Lois manquantes groupées par domaine ────────────────────────────────
    if missing > 0:
        console.print(f"\n[bold red]Lois manquantes à importer :[/]")
        missing_by_domain: dict = {}
        for r in results:
            if r["statut"] == "MANQUANTE":
                dom = r["domaine"]
                missing_by_domain.setdefault(dom, []).append(r)

        for dom, items in sorted(missing_by_domain.items()):
            console.print(f"\n  [yellow]{dom}[/] ({len(items)})")
            for r in items:
                num = f" [{r['numero']}]" if r['numero'] else ""
                console.print(f"    • {r['type']}{num} — {r['titre_fr'][:60]}")

    # ── Export CSV ──────────────────────────────────────────────────────────
    if args.export:
        out = Path(args.export)
        with open(out, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()), delimiter=";")
            writer.writeheader()
            writer.writerows(results)
        console.print(f"\n[green]✓ Rapport exporté : {out.absolute()}[/]\n")


if __name__ == "__main__":
    main()
