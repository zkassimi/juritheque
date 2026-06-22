"""
Google Indexing API — Soumission automatique des URLs JuriThèque
================================================================
Soumet pages statiques + guides FR/AR + domaines + toutes les lois (via Supabase).
Limite : 200 URLs/jour. Le script reprend là où il s'est arrêté (log persistant).

Usage :
  python pipeline/submit_indexing.py            # soumet jusqu'à 200 URLs en attente
  python pipeline/submit_indexing.py --dry-run  # affiche sans soumettre
  python pipeline/submit_indexing.py --limit 50 # limite à 50 URLs ce lancer
  python pipeline/submit_indexing.py --reset    # remet à zéro le log (tout re-soumettre)
"""

import json, os, time, argparse, re
from pathlib import Path
from datetime import date

import requests
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from rich.console import Console

load_dotenv()
load_dotenv(Path(__file__).parent / ".env", override=True)

# ── Configuration ──────────────────────────────────────────────────────────────

SERVICE_ACCOUNT_FILE = "pipeline/google-indexing-key.json"
BASE_URL    = "https://juritheque.com"
SCOPES      = ["https://www.googleapis.com/auth/indexing"]
API_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
DAILY_LIMIT  = 200

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", ""))

# ── Pages statiques ────────────────────────────────────────────────────────────

STATIC_PAGES = [
    "/", "/base", "/domaines", "/glossaire", "/videos", "/assistant",
    "/fr/guides", "/ar/guides",
    "/fr/veille-juridique", "/ar/veille-juridique",
    "/fr/bulletins-officiels", "/ar/bulletins-officiels",
    "/a-propos", "/contact", "/methodologie",
    "/mentions-legales", "/politique-confidentialite",
]

GUIDE_SLUGS = [
    "code-du-travail-maroc", "licenciement-maroc", "code-de-commerce-maroc",
    "sarl-maroc", "bail-commercial-maroc", "recouvrement-maroc",
    "cheque-sans-provision-maroc", "creation-societe-maroc",
    "code-de-la-famille-maroc", "divorce-maroc", "delai-de-prescription-maroc",
    "procedure-civile-maroc", "collectivites-territoriales-maroc",
    "revocation-elu-maroc", "mre-droits-juridiques-maroc",
    "heritage-succession-mre-maroc", "investir-maroc-mre",
    "achat-immobilier-maroc-mre", "double-nationalite-droit-maroc",
    "investissement-etranger-maroc", "marches-publics-maroc",
    "urbanisme-maroc", "etat-civil-maroc", "depenses-personnel-maroc",
    "recouvrement-creances-publiques-maroc", "droit-sport-football-maroc",
    "droit-numerique-ia-maroc", "droit-influenceurs-maroc", "code-route-maroc",
    "protection-consommateur-maroc", "passation-marches-publics-maroc",
    "execution-marche-public-maroc", "controle-marches-publics-maroc",
    "protection-donnees-personnelles-maroc", "ecommerce-maroc",
    "permis-construire-maroc", "infractions-urbanistiques-maroc",
]

DOMAIN_IDS = [
    "civil", "penal", "commercial", "administratif", "travail", "fiscal",
    "international", "numerique", "constitutionnel", "bancaire",
    "finances_publiques", "transport", "environnement", "sante",
    "energie", "collectivites",
]

# ── Fetch lois depuis Supabase ─────────────────────────────────────────────────

def fetch_law_slugs(console: Console) -> list[str]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        console.print("[yellow]⚠  SUPABASE_URL/KEY non configurés — lois ignorées[/]")
        return []

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Accept": "application/json",
    }

    slugs = []
    offset = 0
    batch = 1000

    console.print("  → Récupération des lois depuis Supabase...")
    while True:
        params = {
            "select": "canonical_slug",
            "canonical_slug": "not.is.null",
            "order": "canonical_slug.asc",
            "limit": str(batch),
            "offset": str(offset),
        }
        try:
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/laws",
                headers=headers, params=params, timeout=30
            )
            data = resp.json()
            if not isinstance(data, list) or not data:
                break
            for row in data:
                slug = row.get("canonical_slug", "")
                # Exclure slugs purement numériques ou vides
                if slug and not re.fullmatch(r'\d+', slug):
                    slugs.append(slug)
            if len(data) < batch:
                break
            offset += batch
        except Exception as e:
            console.print(f"[red]✗ Erreur Supabase : {e}[/]")
            break

    console.print(f"  [green]✓ {len(slugs)} lois récupérées[/]")
    return slugs


# ── Construction de la liste complète ─────────────────────────────────────────

def build_url_list(law_slugs: list[str]) -> list[str]:
    urls = [BASE_URL + p for p in STATIC_PAGES]

    for slug in GUIDE_SLUGS:
        urls.append(f"{BASE_URL}/fr/guides/{slug}")
        urls.append(f"{BASE_URL}/ar/guides/{slug}")

    for domain_id in DOMAIN_IDS:
        urls.append(f"{BASE_URL}/domaine/{domain_id}")

    for slug in law_slugs:
        urls.append(f"{BASE_URL}/loi/{slug}")

    return urls


# ── Auth ───────────────────────────────────────────────────────────────────────

def get_access_token(key_file: str) -> str:
    credentials = service_account.Credentials.from_service_account_file(
        key_file, scopes=SCOPES
    )
    credentials.refresh(Request())
    return credentials.token


# ── Soumission ─────────────────────────────────────────────────────────────────

def submit_url(url: str, token: str) -> dict:
    resp = requests.post(
        API_ENDPOINT,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"url": url, "type": "URL_UPDATED"},
        timeout=10,
    )
    return {"status": resp.status_code, "body": resp.json()}


# ── Log persistant ─────────────────────────────────────────────────────────────

LOG_FILE = Path("pipeline/indexing_log.json")


def load_log() -> dict:
    if not LOG_FILE.exists():
        # Migrer les anciens logs datés
        merged: dict = {"submitted": [], "failed": []}
        for old in Path("pipeline").glob("indexing_log_2*.json"):
            try:
                data = json.loads(old.read_text(encoding="utf-8"))
                for u in data.get("submitted", []):
                    if u not in merged["submitted"]:
                        merged["submitted"].append(u)
                merged["failed"].extend(data.get("failed", []))
            except Exception:
                pass
        if merged["submitted"]:
            LOG_FILE.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
        return merged
    return json.loads(LOG_FILE.read_text(encoding="utf-8"))


def save_log(log: dict):
    LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Google Indexing API — JuriThèque")
    parser.add_argument("--dry-run", action="store_true", help="Affiche les URLs sans soumettre")
    parser.add_argument("--limit", type=int, default=DAILY_LIMIT, help="Max URLs à soumettre")
    parser.add_argument("--key", default=SERVICE_ACCOUNT_FILE, help="Chemin clé JSON")
    parser.add_argument("--reset", action="store_true", help="Remet à zéro le log (tout re-soumettre)")
    args = parser.parse_args()

    console = Console()

    console.print("\n[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold]")
    console.print("[bold]  JuriThèque — Google Indexing API        [/bold]")
    console.print("[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold]\n")

    if args.reset:
        LOG_FILE.write_text(json.dumps({"submitted": [], "failed": []}, indent=2), encoding="utf-8")
        console.print("[yellow]⚠  Log remis à zéro — toutes les URLs seront re-soumises[/]\n")

    if args.dry_run:
        console.print("[yellow]⚠  DRY RUN — aucune URL ne sera soumise[/]\n")

    # Récupérer les slugs de lois
    law_slugs = fetch_law_slugs(console)

    # Charger le log
    log = load_log()
    already_submitted = set(log["submitted"])

    all_urls = build_url_list(law_slugs)
    pending = [u for u in all_urls if u not in already_submitted]

    console.print(f"\n  URLs totales   : [bold]{len(all_urls)}[/]  "
                  f"([dim]{len(STATIC_PAGES)} statiques · "
                  f"{len(GUIDE_SLUGS)*2} guides · "
                  f"{len(DOMAIN_IDS)} domaines · "
                  f"{len(law_slugs)} lois[/])")
    console.print(f"  Déjà soumises  : [dim]{len(already_submitted)}[/]")
    console.print(f"  À soumettre    : [bold cyan]{len(pending)}[/]")
    console.print(f"  Ce lancement   : [bold]{min(len(pending), args.limit)}[/]  "
                  f"[dim](limite {args.limit}/jour)[/]\n")

    to_submit = pending[:args.limit]

    if not to_submit:
        console.print("[green]✓ Toutes les URLs ont déjà été soumises.[/]")
        if pending:
            jours = -(-len(pending) // args.limit)
            console.print(f"[dim]  ({len(pending)} URLs restantes — {jours} jour(s) à {args.limit}/jour)[/]")
        return

    if args.dry_run:
        for url in to_submit[:20]:
            console.print(f"  [dim]→[/] {url}")
        if len(to_submit) > 20:
            console.print(f"  [dim]... et {len(to_submit)-20} autres[/]")
        console.print(f"\n[yellow]→ {len(to_submit)} URLs seraient soumises[/]")
        return

    # Vérifier la clé
    key_path = Path(args.key)
    if not key_path.exists():
        console.print(f"[red]✗ Clé JSON introuvable : {key_path}[/]")
        return

    # Authentification
    console.print("  → Authentification Google...")
    try:
        token = get_access_token(str(key_path))
        console.print("  [green]✓ Token obtenu[/]\n")
    except Exception as e:
        console.print(f"[red]✗ Erreur auth : {e}[/]")
        return

    # Soumission
    ok = 0
    fail = 0

    for i, url in enumerate(to_submit, 1):
        console.print(f"  [{i}/{len(to_submit)}] {url}")
        try:
            result = submit_url(url, token)
            if result["status"] == 200:
                console.print(f"    [green]✓ Soumis[/]")
                log["submitted"].append(url)
                ok += 1
            else:
                err = result["body"].get("error", {}).get("message", str(result["body"]))
                console.print(f"    [red]✗ Erreur {result['status']} : {err[:80]}[/]")
                log["failed"].append({"url": url, "error": err, "date": str(date.today())})
                fail += 1
        except Exception as e:
            console.print(f"    [red]✗ Exception : {e}[/]")
            log["failed"].append({"url": url, "error": str(e), "date": str(date.today())})
            fail += 1

        save_log(log)

        if i < len(to_submit):
            time.sleep(0.5)

    # Résumé
    remaining = len(pending) - len(to_submit)
    console.print(f"\n[bold]━━━━ Résultats ━━━━[/]")
    console.print(f"  [green]✓ Soumis avec succès : {ok}[/]")
    if fail:
        console.print(f"  [red]✗ Échecs            : {fail}[/]")
    if remaining > 0:
        jours = -(-remaining // args.limit)
        console.print(f"  [yellow]⏳ Restantes         : {remaining} URLs ({jours} jour(s) à relancer)[/]")
    console.print(f"  Log sauvegardé    : {LOG_FILE}\n")


if __name__ == "__main__":
    main()
