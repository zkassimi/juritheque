"""
import_lois_adala.py
─────────────────────
Importe les lois Adala (public/data/lois-adala.json) dans la table
Supabase `laws` avec toutes les métadonnées disponibles.

- NE télécharge PAS les PDF
- source_url pointe vers le PDF Cloudflare R2 (Adala)
- Les résumés (title_fr, simple_summary_fr) sont laissés null
  → à générer ensuite avec enrich.py

Usage :
  python pipeline/import_lois_adala.py                # importe tout
  python pipeline/import_lois_adala.py --dry-run       # sans écriture
  python pipeline/import_lois_adala.py --limit 100     # 100 lois max
  python pipeline/import_lois_adala.py --batch 25      # taille des lots
  python pipeline/import_lois_adala.py --input public/data/lois-adala.json
"""

import os, sys, json, argparse, time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import httpx

load_dotenv()

SUPABASE_URL = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("VITE_SUPABASE_ANON_KEY", "")
)

# Domaines valides dans la table domains (migrations 003 + 005)
VALID_DOMAINS = {
    "civil", "penal", "commercial", "administratif", "travail",
    "fiscal", "international", "numerique", "constitutionnel",
    "bancaire", "finances_publiques",
}

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def log(msg):
    """Print safe pour Windows cp1252 — remplace les caractères non-encodables."""
    safe = str(msg).encode('cp1252', errors='replace').decode('cp1252')
    print(safe, flush=True)


def fetch_existing_numbers(client: httpx.Client) -> set[str]:
    """Récupère tous les laws.number existants dans Supabase."""
    existing = set()
    offset, batch = 0, 1000
    log("-> Récupération des numéros existants depuis Supabase...")
    while True:
        resp = client.get(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers=HEADERS,
            params={"select": "number", "limit": str(batch), "offset": str(offset)},
        )
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            break
        for r in rows:
            n = (r.get("number") or "").strip().lower()
            if n:
                existing.add(n)
        if len(rows) < batch:
            break
        offset += batch
    log(f"-> {len(existing)} lois déjà dans Supabase")
    return existing


def loi_to_row(loi: dict) -> dict:
    """
    Convertit une entrée du JSON statique en row Supabase.
    Tous les champs présents dans la table laws sont inclus
    (avec None pour les champs non disponibles → garantit clés identiques).
    """
    domain_id = loi.get("domain")
    if domain_id not in VALID_DOMAINS:
        domain_id = None

    # date: doit être "YYYY-MM-DD" ou null
    date_val = loi.get("date") or None

    # Titre français de base (enrich.py le remplacera par un vrai résumé IA)
    type_fr = loi.get("type_fr") or "Texte"
    number  = loi["number"]
    date_str = f" du {date_val}" if date_val else ""
    title_fr_placeholder = f"{type_fr} n°{number}{date_str}"

    return {
        # ── Identité ──
        "number":      number,
        "title_ar":    loi.get("title_ar") or None,
        "title_fr":    title_fr_placeholder,   # placeholder → à enrichir
        # ── Classification ──
        "type":        loi.get("type_fr") or "Autre",
        "status":      "En vigueur",
        "date":        date_val,
        "domain_id":   domain_id,
        "language":    "Arabe",
        # ── Contenu (vide — pas de PDF téléchargé) ──
        "content_fr":  None,
        "content_ar":  None,
        # ── Tags ──
        "tags":        loi.get("tags") or [],
        # ── Source officielle ──
        "source_name": "Adala",
        "source_url":  loi.get("pdfUrl") or None,
        "bo_number":   None,
        "bo_date":     None,
    }


def insert_batch(client: httpx.Client, batch: list[dict],
                 dry_run: bool) -> tuple[int, int]:
    """
    Insère un lot de rows dans laws.
    Retourne (nb_insérés, nb_erreurs).
    """
    if dry_run:
        return len(batch), 0

    try:
        resp = client.post(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers=HEADERS,
            json=batch,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            return len(batch), 0

        # Afficher le code HTTP réel avant fallback
        log(f"   [batch {resp.status_code}] -> fallback ligne par ligne")

        # Erreur batch → essayer ligne par ligne
        errors = 0
        inserted = 0
        for row in batch:
            try:
                r = client.post(
                    f"{SUPABASE_URL}/rest/v1/laws",
                    headers=HEADERS,
                    json=row,
                    timeout=20,
                )
                if r.status_code in (200, 201):
                    inserted += 1
                else:
                    errors += 1
                    # Afficher seulement les champs ASCII de l'erreur
                    code = r.json().get("code", "?") if r.headers.get("content-type","").startswith("application/json") else r.status_code
                    log(f"   [!] n={row['number']} -> HTTP {r.status_code} code={code}")
            except Exception as row_err:
                errors += 1
                log(f"   [!] n={row['number']} -> exception: {type(row_err).__name__}")
        return inserted, errors

    except Exception as e:
        log(f"   [!] Exception batch: {type(e).__name__}: {str(e)[:80]}")
        return 0, len(batch)


# ── Point d'entrée ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Importe lois-adala.json dans Supabase laws"
    )
    parser.add_argument("--dry-run",  action="store_true",
                        help="Simule l'import sans écriture")
    parser.add_argument("--limit",    type=int, default=None,
                        help="Nombre max de lois à importer")
    parser.add_argument("--batch",    type=int, default=50,
                        help="Taille des lots (défaut: 50)")
    parser.add_argument("--input",    default="public/data/lois-adala.json",
                        help="Chemin vers le JSON Adala")
    args = parser.parse_args()

    if not SUPABASE_URL or not SUPABASE_KEY:
        log("[!] SUPABASE_URL / SUPABASE_SERVICE_KEY manquants dans .env")
        sys.exit(1)

    # ── Charger le JSON ──
    script_dir   = Path(__file__).parent
    project_root = script_dir.parent
    input_path   = project_root / args.input

    if not input_path.exists():
        log(f"[!] Fichier introuvable : {input_path}")
        log("    Lance d'abord : python pipeline/build_lois_adala.py")
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        all_lois = json.load(f)

    log(f"\n>> Import Lois Adala -> Supabase{'  [DRY-RUN]' if args.dry_run else ''}")
    log(f"-> {len(all_lois)} lois dans {input_path.name}")

    with httpx.Client(
        timeout=30,
        limits=httpx.Limits(max_keepalive_connections=5),
    ) as client:

        # ── Déduplication ──
        existing = fetch_existing_numbers(client)
        to_insert = [
            l for l in all_lois
            if (l.get("number") or "").strip().lower() not in existing
        ]

        if args.limit:
            to_insert = to_insert[:args.limit]

        log(f"-> {len(to_insert)} nouvelles lois à insérer "
            f"({len(all_lois) - len(to_insert)} doublons ignorés)\n")

        if not to_insert:
            log("Rien à importer. Toutes les lois sont déjà dans Supabase.")
            return

        # ── Conversion en rows ──
        rows = [loi_to_row(l) for l in to_insert]

        # ── Import par lots ──
        total_inserted = 0
        total_errors   = 0
        batch_size     = args.batch

        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            n_done = min(i + batch_size, len(rows))

            ins, err = insert_batch(client, batch, args.dry_run)
            total_inserted += ins
            total_errors   += err

            status = "DRY" if args.dry_run else ("OK" if err == 0 else f"ERR:{err}")
            print(
                f"  Lot {i // batch_size + 1:>4} | "
                f"{n_done:>5}/{len(rows)} | "
                f"{status}",
                flush=True
            )

            time.sleep(0.05)  # politesse

    # ── Résumé ──
    print()
    if args.dry_run:
        log(f"[DRY-RUN] {len(rows)} lois auraient été insérées.")
    else:
        log(f"Import terminé : {total_inserted} insérées, {total_errors} erreurs")
        if total_errors == 0:
            log(f"Lance maintenant : python pipeline/enrich.py --no-ai")
            log(f"Puis             : python pipeline/enrich.py  (avec IA pour les résumés)")

    # ── Rapport ──
    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "run_at":    ts,
        "dry_run":   args.dry_run,
        "input":     str(input_path),
        "total_json":  len(all_lois),
        "skipped":   len(all_lois) - len(to_insert),
        "attempted": len(rows),
        "inserted":  total_inserted,
        "errors":    total_errors,
    }
    rp = report_dir / f"import_adala_{ts}.json"
    with open(rp, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    log(f"Rapport : {rp}\n")


if __name__ == "__main__":
    main()
