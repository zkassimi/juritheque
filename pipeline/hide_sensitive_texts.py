"""
JuriThèque — Masquage des textes sensibles / inutiles
═══════════════════════════════════════════════════════
Met is_publicly_indexable = false sur les textes à risque CNDP ou sans valeur.

CATÉGORIES CIBLÉES :
  1. "Liste des" + noms propres — données personnelles (CNDP)
     Ex: "liste des notaires", "liste des huissiers", "liste des architectes agréés"
  2. Textes militaires / secrets défense (classification)
     Ex: zones militaires, bases, munitions militaires classifiées
  3. Textes ultra-courts sans contenu utile (< 30 mots)
     Ex: décrets de nomination individuels sans intérêt général

Les textes NE SONT PAS SUPPRIMÉS — ils restent en base avec
is_publicly_indexable = false (masqués sur le site, restaurables).

Usage :
  python pipeline/hide_sensitive_texts.py --dry-run   # aperçu sans écriture
  python pipeline/hide_sensitive_texts.py             # application réelle
"""

import os, sys, re, json
from dotenv import load_dotenv
import httpx

try:
    from rich.console import Console
    console = Console()
    def log(msg): console.print(msg)
except ImportError:
    def log(msg): print(msg)

load_dotenv()

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL","")).rstrip("/")
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("VITE_SUPABASE_ANON_KEY","")
)
DRY_RUN = "--dry-run" in sys.argv

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

# ══════════════════════════════════════════════════════════════════════════════
# RÈGLES DE MASQUAGE
# Chaque règle : (raison, pattern_regex_sur_titre_fr_AR)
# ══════════════════════════════════════════════════════════════════════════════

# ── Catégorie 1 : Listes nominatives (données personnelles CNDP) ──────────────
# "Liste des X" ou "Arrêté portant liste" = risque CNDP si noms propres
LISTE_PATTERNS = [
    r"liste\s+des?\s+(notaires|huissiers?|avocats?|architectes?|comptables?|experts?|géomètres?|ingénieurs?|médecins?|pharmaciens?|infirmiers?|chirurgiens?|dentistes?|vétérinaires?|psychologues?|assistants?\s+sociaux?|kinésithérapeutes?|sages?-?femmes?)",
    r"liste\s+des?\s+bénéficiaires?",
    r"liste\s+nominative",
    r"tableau\s+(de\s+l.ordre|des?\s+notaires|des?\s+avocats?|des?\s+architectes?)",
    r"arrêté\s+portant\s+(inscription|radiation|suspension)\s+[a-zéèêàâùûîïôäëü\s]+\s+au\s+(tableau|registre|liste)",
    r"portant\s+nomination\s+de\s+m[mr]?\.",
    r"portant\s+nomination\s+de\s+madame",
    r"نمينة السيد",
    r"قائمة\s+ال(موثقين|محضرين|محامين|مهندسين|الأطباء)",
]

# ── Catégorie 2 : Textes militaires / sécurité nationale classifiés ───────────
MILITARY_PATTERNS = [
    r"secret[\s-]défense",
    r"zone\s+militaire\s+fermée",
    r"installation\s+(nucléaire|militaire)\s+classifi",
    r"munitions?\s+(militaires?|de\s+guerre)",
    r"armement\s+classifi",
    r"base\s+militaire\s+(de\s+)?[a-zéèêàâùûîïôäëü\s]+classifi",
    r"renseignements?\s+militaires?\s+secrets?",
]

# ── Catégorie 3 : Nominations individuelles sans portée normative ─────────────
# Décrets/arrêtés qui nomment UNE SEULE personne à un poste — sans intérêt
# pour la base juridique (ex: "décret portant nomination de M. X en qualité de...")
NOMINATION_INDIVIDUAL_PATTERNS = [
    r"^décret\s+portant\s+nomination\s+de\s+(m\.|mme\.|monsieur|madame|dr\.|pr\.)\s+[A-ZÀÂÉÈÊÎÏÔÙÛÄËÜ][a-zàâéèêîïôùûäëü\-']+\s+[A-ZÀÂÉÈÊÎÏÔÙÛÄËÜ]",
    r"^arrêté\s+portant\s+nomination\s+de\s+(m\.|mme\.|monsieur|madame)\s+[A-Z]",
    r"^décision\s+portant\s+nomination\s+de\s+(m\.|mme\.)\s+[A-Z]",
    r"^arrêté\s+portant\s+(détachement|mise\s+en\s+disponibilité|réintégration|révocation)\s+de\s+(m\.|mme\.)\s+[A-Z]",
]

ALL_RULES = [
    ("Données personnelles CNDP — liste nominative",   LISTE_PATTERNS),
    ("Sécurité nationale — texte classifié",           MILITARY_PATTERNS),
    ("Nomination individuelle — sans portée normative", NOMINATION_INDIVIDUAL_PATTERNS),
]

# ══════════════════════════════════════════════════════════════════════════════
def is_sensitive(title_fr: str, title_ar: str) -> tuple[bool, str]:
    """Retourne (True, raison) si le texte doit être masqué, sinon (False, '')."""
    text_fr = str(title_fr or "").lower().strip()
    text_ar = str(title_ar or "").lower().strip()
    full    = text_fr + " " + text_ar

    for reason, patterns in ALL_RULES:
        for pat in patterns:
            if re.search(pat, full, re.IGNORECASE):
                return True, reason

    return False, ""


def fetch_all_public_laws() -> list[dict]:
    """Récupère toutes les lois publiques pour analyse."""
    log("[dim]Récupération des textes publics...[/]")
    all_laws = []
    offset = 0
    while True:
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers={**HEADERS, "Prefer": ""},
            params={
                "select":                "id,title_fr,title_ar,type,number",
                "is_publicly_indexable": "not.eq.false",   # récupère les non-masqués
                "order":                 "id.asc",
                "limit":                 "1000",
                "offset":                str(offset),
            },
            timeout=30,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        all_laws.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000
    return all_laws


def hide_law(law_id: int):
    """Met is_publicly_indexable = false."""
    r = httpx.patch(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={"id": f"eq.{law_id}"},
        json={"is_publicly_indexable": False},
        timeout=30,
    )
    r.raise_for_status()


# ══════════════════════════════════════════════════════════════════════════════
def main():
    log("\n[bold red]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log("[bold red]  JuriThèque — Masquage des textes sensibles    [/]")
    log("[bold red]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

    if DRY_RUN:
        log("[yellow]⚠  MODE DRY-RUN — aucune écriture en base[/]\n")

    laws = fetch_all_public_laws()
    log(f"[bold]{len(laws)} textes publics analysés[/]\n")

    to_hide = []   # [(law, reason)]
    by_reason = {}

    for law in laws:
        sensitive, reason = is_sensitive(law.get("title_fr"), law.get("title_ar"))
        if sensitive:
            to_hide.append((law, reason))
            by_reason[reason] = by_reason.get(reason, 0) + 1

    # ── Résumé avant action ───────────────────────────────────────────────────
    log(f"[bold red]🔍 {len(to_hide)} textes à masquer :[/]")
    for reason, count in sorted(by_reason.items(), key=lambda x: -x[1]):
        log(f"  [red]•[/] {reason}: [bold]{count}[/]")

    log(f"\n[dim]Exemples :[/]")
    for law, reason in to_hide[:25]:
        t = law.get("title_fr") or law.get("title_ar") or "???"
        log(f"  [dim]#{law['id']} [{law.get('type','?')}] {str(t)[:90]}[/]")
        log(f"       [red italic]→ {reason}[/]")

    if len(to_hide) > 25:
        log(f"  [dim]... et {len(to_hide) - 25} autres[/]")

    # ── Sauvegarder la liste pour audit ──────────────────────────────────────
    os.makedirs("pipeline/logs", exist_ok=True)
    audit_path = "pipeline/logs/hidden_texts_audit.json"
    audit_data = [{"id": l["id"], "title_fr": l.get("title_fr"), "title_ar": l.get("title_ar"),
                   "type": l.get("type"), "reason": r} for l, r in to_hide]
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, ensure_ascii=False, indent=2)
    log(f"\n[dim]Liste sauvegardée dans {audit_path} (pour audit et restauration si besoin)[/]")

    if DRY_RUN:
        log(f"\n[yellow]DRY-RUN terminé. Lancez sans --dry-run pour appliquer.[/]")
        return

    # ── Application ───────────────────────────────────────────────────────────
    log(f"\n[bold]Masquage en cours...[/]")
    ok = 0
    errors = 0
    for law, reason in to_hide:
        try:
            hide_law(law["id"])
            ok += 1
        except Exception as e:
            log(f"[red]✗ #{law['id']}: {e}[/]")
            errors += 1

    log(f"\n[bold green]━━━ Résultat ━━━[/]")
    log(f"✅ Masqués  : [bold green]{ok}[/]")
    if errors:
        log(f"❌ Erreurs  : [bold red]{errors}[/]")
    log(f"\n[dim]Ces textes ne sont plus visibles sur le site.[/]")
    log(f"[dim]Pour restaurer un texte : PATCH laws?id=eq.X → is_publicly_indexable=true[/]\n")


if __name__ == "__main__":
    main()
