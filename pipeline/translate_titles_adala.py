"""
translate_titles_adala.py
──────────────────────────
Traduit title_ar → title_fr pour les lois Adala dont le title_fr
est encore un placeholder (ex: "Décret n°2.22.64 du 2025-09-18").

Utilise Claude (Anthropic API) ou OpenRouter.
Coût estimé : ~$0.80 pour 3 100 lois (Claude Haiku).

Usage :
  python pipeline/translate_titles_adala.py --dry-run      # prévisualisation
  python pipeline/translate_titles_adala.py --limit 100    # test 100 lois
  python pipeline/translate_titles_adala.py                # tout traduire
  python pipeline/translate_titles_adala.py --force        # même si title_fr non-placeholder
"""

import os, re, sys, json, argparse, time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import httpx

load_dotenv()

SUPABASE_URL   = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY   = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")
ANTHROPIC_KEY  = os.getenv("ANTHROPIC_API_KEY", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("VITE_OPENROUTER_KEY", "")
PROVIDER       = os.getenv("PROVIDER", "anthropic").lower()
MODEL          = os.getenv("MODEL", "claude-haiku-3-5")

HEADERS_SB = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}

# Pattern qui identifie un title_fr placeholder généré par import_lois_adala.py
PLACEHOLDER_PATTERN = re.compile(
    r'^(Loi|Décret|Dahir|Arrêté|Circulaire|Convention|Code|Autre|Loi organique|Décret royal|Note circulaire|Règlement)'
    r'\s+n[°o][\w.\-/]+(\s+du\s+\d{4}-\d{2}-\d{2})?$',
    re.IGNORECASE,
)

def is_placeholder(title_fr: str) -> bool:
    """Retourne True si title_fr est un placeholder généré automatiquement."""
    if not title_fr:
        return True
    return bool(PLACEHOLDER_PATTERN.match(title_fr.strip()))


def call_ai(prompt: str) -> str | None:
    """Appelle Claude (Anthropic) ou OpenRouter."""
    try:
        if PROVIDER == "openrouter" and OPENROUTER_KEY:
            r = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "google/gemini-2.5-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200,
                    "temperature": 0.1,
                },
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()

        elif ANTHROPIC_KEY:
            import anthropic as _ant
            client = _ant.Anthropic(api_key=ANTHROPIC_KEY)
            msg = client.messages.create(
                model=MODEL,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()

    except Exception as e:
        print(f"[!] IA erreur: {type(e).__name__}: {str(e)[:80]}", flush=True)
    return None


def translate_title(title_ar: str, type_fr: str, number: str) -> str | None:
    """Traduit un titre arabe en français via IA."""
    if not title_ar:
        return None

    prompt = f"""Tu es un juriste marocain bilingue. Traduis ce titre de texte juridique marocain de l'arabe vers le français.

RÈGLES :
- Traduction fidèle et concise (1 ligne max)
- Style officiel français (comme le Journal officiel français)
- Ne pas inventer de contenu
- Garder les numéros, dates et références tels quels
- Si le titre est trop générique, retourne: "{type_fr} n°{number}"

Type : {type_fr}
Numéro : {number}
Titre arabe : {title_ar}

Titre français (1 ligne, sans guillemets) :"""

    result = call_ai(prompt)
    if not result or len(result.strip()) < 5:
        return None

    # Nettoyer la réponse
    result = result.strip()
    # Supprimer les guillemets éventuels
    result = re.sub(r'^["\']|["\']$', '', result).strip()
    # Supprimer les préfixes IA
    result = re.sub(r'^(Titre\s*:\s*|Traduction\s*:\s*)', '', result, flags=re.IGNORECASE).strip()
    # Limiter la longueur
    return result[:400] if result else None


def fetch_adala_laws(client: httpx.Client, limit: int | None) -> list[dict]:
    """Récupère les lois avec title_ar non null (toutes sources)."""
    all_rows = []
    offset, batch = 0, 500

    print("-> Récupération des lois avec title_ar depuis Supabase...", flush=True)
    while True:
        params = {
            "select":   "id,number,title_fr,title_ar,type",
            "title_ar": "not.is.null",
            "order":    "id.asc",
            "limit":    str(batch),
            "offset":   str(offset),
        }
        resp = client.get(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers=HEADERS_SB,
            params=params,
        )
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < batch:
            break
        offset += batch
        if limit and len(all_rows) >= limit:
            break

    if limit:
        all_rows = all_rows[:limit]

    print(f"-> {len(all_rows)} lois Adala trouvées", flush=True)
    return all_rows


def patch_law(client: httpx.Client, law_id: int, title_fr: str, dry_run: bool) -> bool:
    """Met à jour title_fr dans Supabase."""
    if dry_run:
        return True
    try:
        r = client.patch(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers=HEADERS_SB,
            params={"id": f"eq.{law_id}"},
            json={"title_fr": title_fr},
            timeout=15,
        )
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"[!] PATCH erreur id={law_id}: {e}", flush=True)
        return False


def main():
    parser = argparse.ArgumentParser(description="Traduit title_ar -> title_fr pour les lois Adala")
    parser.add_argument("--dry-run",  action="store_true", help="Sans écriture Supabase")
    parser.add_argument("--limit",    type=int, default=None, help="Nombre max de lois")
    parser.add_argument("--force",    action="store_true", help="Traduire même les title_fr non-placeholder")
    args = parser.parse_args()

    if not ANTHROPIC_KEY and not (PROVIDER == "openrouter" and OPENROUTER_KEY):
        print("[!] ANTHROPIC_API_KEY ou OPENROUTER_API_KEY manquant dans .env")
        sys.exit(1)

    print(f"\n>> Traduction title_ar -> title_fr (toutes sources)"
          f"{'  [DRY-RUN]' if args.dry_run else ''}", flush=True)

    translated = 0
    skipped    = 0
    errors     = 0

    with httpx.Client(
        timeout=30,
        limits=httpx.Limits(max_keepalive_connections=5),
    ) as client:
        laws = fetch_adala_laws(client, args.limit)

        # Filtrer uniquement les placeholders (sauf si --force)
        to_translate = [
            l for l in laws
            if args.force or is_placeholder(l.get("title_fr") or "")
        ]
        print(f"-> {len(to_translate)} titres a traduire "
              f"({len(laws) - len(to_translate)} deja traduits ignores)\n", flush=True)

        for i, law in enumerate(to_translate, 1):
            law_id   = law["id"]
            number   = law.get("number") or "?"
            title_ar = law.get("title_ar") or ""
            type_fr  = law.get("type") or "Texte"
            old_title = law.get("title_fr") or ""

            # Traduire
            new_title = translate_title(title_ar, type_fr, number)

            if not new_title:
                errors += 1
                print(f"  [{i:>5}/{len(to_translate)}] ERR  n={number}", flush=True)
                continue

            # Afficher apercu (ASCII safe)
            preview = new_title.encode('ascii', errors='replace').decode('ascii')[:70]
            print(f"  [{i:>5}/{len(to_translate)}] OK   n={number:12} -> {preview}", flush=True)

            # Mettre a jour
            if patch_law(client, law_id, new_title, args.dry_run):
                translated += 1
            else:
                errors += 1

            # Pause pour ne pas surcharger l'API
            if i % 10 == 0:
                time.sleep(0.2)

    # Rapport
    print(f"\n>> Termine : {translated} traduits, {skipped} ignores, {errors} erreurs", flush=True)
    if args.dry_run:
        print("[DRY-RUN] Aucune ecriture effectuee.", flush=True)

    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rp = report_dir / f"translate_titles_{ts}.json"
    with open(rp, "w", encoding="utf-8") as f:
        json.dump({
            "run_at": ts,
            "dry_run": args.dry_run,
            "translated": translated,
            "skipped": skipped,
            "errors": errors,
        }, f, ensure_ascii=False, indent=2)
    print(f"Rapport : {rp}\n", flush=True)


if __name__ == "__main__":
    main()
