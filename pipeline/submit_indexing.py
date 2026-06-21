"""
Google Indexing API — Soumission automatique des URLs JuriThèque
================================================================
Prérequis :
  pip install google-auth requests rich

Configuration :
  1. Créer un projet Google Cloud → activer "Web Search Indexing API"
  2. Créer un compte de service → télécharger la clé JSON
  3. Ajouter le compte de service comme propriétaire dans GSC
  4. Mettre le chemin de la clé JSON dans SERVICE_ACCOUNT_FILE ci-dessous

Usage :
  python pipeline/submit_indexing.py            # soumet toutes les URLs
  python pipeline/submit_indexing.py --dry-run  # affiche sans soumettre
  python pipeline/submit_indexing.py --limit 50 # limite à 50 URLs/jour
"""

import json
import time
import argparse
from pathlib import Path
from datetime import date

import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# ── Configuration ─────────────────────────────────────────────────────────────

SERVICE_ACCOUNT_FILE = "pipeline/google-indexing-key.json"  # ← chemin vers votre clé JSON

BASE_URL = "https://juritheque.com"

SCOPES = ["https://www.googleapis.com/auth/indexing"]

API_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

DAILY_LIMIT = 200  # limite Google : 200 URLs/jour

# ── URLs à soumettre ───────────────────────────────────────────────────────────

STATIC_PAGES = [
    "/",
    "/base",
    "/domaines",
    "/fr/guides",
    "/ar/guides",
    "/fr/veille-juridique",
    "/ar/veille-juridique",
    "/fr/bulletins-officiels",
    "/ar/bulletins-officiels",
    "/glossaire",
    "/videos",
    "/assistant",
    "/a-propos",
    "/contact",
    "/methodologie",
    "/mentions-legales",
    "/politique-confidentialite",
]

GUIDE_SLUGS = [
    "code-du-travail-maroc",
    "licenciement-maroc",
    "code-de-commerce-maroc",
    "sarl-maroc",
    "bail-commercial-maroc",
    "recouvrement-maroc",
    "cheque-sans-provision-maroc",
    "creation-societe-maroc",
    "code-de-la-famille-maroc",
    "divorce-maroc",
    "delai-de-prescription-maroc",
    "procedure-civile-maroc",
    "collectivites-territoriales-maroc",
    "revocation-elu-maroc",
    "mre-droits-juridiques-maroc",
    "heritage-succession-mre-maroc",
    "investir-maroc-mre",
    "achat-immobilier-maroc-mre",
    "double-nationalite-droit-maroc",
    "investissement-etranger-maroc",
    "marches-publics-maroc",
    "urbanisme-maroc",
    "etat-civil-maroc",
    "depenses-personnel-maroc",
    "recouvrement-creances-publiques-maroc",
    "droit-sport-football-maroc",
    "droit-numerique-ia-maroc",
    "droit-influenceurs-maroc",
    "code-route-maroc",
    "protection-consommateur-maroc",
    "passation-marches-publics-maroc",
    "execution-marche-public-maroc",
    "controle-marches-publics-maroc",
    "protection-donnees-personnelles-maroc",
    "ecommerce-maroc",
    "permis-construire-maroc",
    "infractions-urbanistiques-maroc",
]


def build_url_list() -> list[str]:
    urls = [BASE_URL + p for p in STATIC_PAGES]
    for slug in GUIDE_SLUGS:
        urls.append(f"{BASE_URL}/fr/guides/{slug}")
        urls.append(f"{BASE_URL}/ar/guides/{slug}")
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


# ── Log des résultats ──────────────────────────────────────────────────────────

LOG_FILE = Path(f"pipeline/indexing_log_{date.today()}.json")


def load_log() -> dict:
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text(encoding="utf-8"))
    return {"submitted": [], "failed": []}


def save_log(log: dict):
    LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Google Indexing API — JuriThèque")
    parser.add_argument("--dry-run", action="store_true", help="Affiche les URLs sans soumettre")
    parser.add_argument("--limit", type=int, default=DAILY_LIMIT, help="Max URLs à soumettre")
    parser.add_argument("--key", default=SERVICE_ACCOUNT_FILE, help="Chemin clé JSON")
    args = parser.parse_args()

    console = Console()

    console.print("\n[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold]")
    console.print("[bold]  JuriThèque — Google Indexing API        [/bold]")
    console.print("[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold]\n")

    if args.dry_run:
        console.print("[yellow]⚠  DRY RUN — aucune URL ne sera soumise[/]\n")

    # Charger le log pour éviter les doublons
    log = load_log()
    already_submitted = set(log["submitted"])

    all_urls = build_url_list()
    pending = [u for u in all_urls if u not in already_submitted]

    console.print(f"  URLs totales   : [bold]{len(all_urls)}[/]")
    console.print(f"  Déjà soumises  : [dim]{len(already_submitted)}[/]")
    console.print(f"  À soumettre    : [bold cyan]{len(pending)}[/]")
    console.print(f"  Limite du jour : [bold]{args.limit}[/]\n")

    to_submit = pending[:args.limit]

    if not to_submit:
        console.print("[green]✓ Toutes les URLs ont déjà été soumises aujourd'hui.[/]")
        return

    if args.dry_run:
        for url in to_submit:
            console.print(f"  [dim]→[/] {url}")
        console.print(f"\n[yellow]→ {len(to_submit)} URLs seraient soumises[/]")
        return

    # Vérifier que la clé existe
    key_path = Path(args.key)
    if not key_path.exists():
        console.print(f"[red]✗ Clé JSON introuvable : {key_path}[/]")
        console.print("\n[bold]Comment obtenir la clé :[/]")
        console.print("  1. console.cloud.google.com → Nouveau projet")
        console.print("  2. APIs → Activer 'Web Search Indexing API'")
        console.print("  3. IAM → Comptes de service → Créer → Télécharger JSON")
        console.print("  4. GSC → Paramètres → Utilisateurs → Ajouter l'email du compte de service")
        console.print(f"  5. Placer le fichier JSON ici : [cyan]{key_path.absolute()}[/]\n")
        return

    # Obtenir le token
    console.print("  → Authentification Google...")
    try:
        token = get_access_token(str(key_path))
        console.print("  [green]✓ Token obtenu[/]\n")
    except Exception as e:
        console.print(f"[red]✗ Erreur auth : {e}[/]")
        return

    # Soumettre
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
                log["failed"].append({"url": url, "error": err})
                fail += 1
        except Exception as e:
            console.print(f"    [red]✗ Exception : {e}[/]")
            log["failed"].append({"url": url, "error": str(e)})
            fail += 1

        save_log(log)

        # Pause entre les requêtes pour éviter le rate limiting
        if i < len(to_submit):
            time.sleep(0.5)

    # Résumé
    console.print(f"\n[bold]━━━━ Résultats ━━━━[/]")
    console.print(f"  [green]✓ Soumis avec succès : {ok}[/]")
    if fail:
        console.print(f"  [red]✗ Échecs            : {fail}[/]")
    console.print(f"  Log sauvegardé    : {LOG_FILE}\n")


if __name__ == "__main__":
    main()
