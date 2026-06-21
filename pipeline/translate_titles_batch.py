"""
translate_titles_batch.py
──────────────────────────
Version rapide — traduit 15 titres arabes par appel IA (batch).
~20x plus rapide que translate_titles_adala.py (appels séquentiels).

Cible : lois Adala avec title_fr = placeholder.

Usage :
  python pipeline/translate_titles_batch.py --dry-run      # prévisualisation
  python pipeline/translate_titles_batch.py --limit 100    # test
  python pipeline/translate_titles_batch.py                # tout (3 100 lois)
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

BATCH_SIZE = 15   # titres par appel IA

HEADERS_SB = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}

PLACEHOLDER_PATTERN = re.compile(
    r'^(Loi|Décret|Dahir|Arrêté|Circulaire|Convention|Code|Autre|Loi organique|Décret royal|Note circulaire|Règlement)'
    r'\s+n[°o][\w.\-/]+(\s+du\s+\d{4}-\d{2}-\d{2})?$',
    re.IGNORECASE,
)

def is_placeholder(title_fr: str) -> bool:
    return not title_fr or bool(PLACEHOLDER_PATTERN.match(title_fr.strip()))


def call_ai(prompt: str) -> str | None:
    try:
        if PROVIDER == "openrouter" and OPENROUTER_KEY:
            r = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "google/gemini-2.5-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 600,
                    "temperature": 0.1,
                },
                timeout=45,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        elif ANTHROPIC_KEY:
            import anthropic as _ant
            client = _ant.Anthropic(api_key=ANTHROPIC_KEY)
            msg = client.messages.create(
                model=MODEL,
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
    except Exception as e:
        print(f"[!] IA erreur: {type(e).__name__}: {str(e)[:80]}", flush=True)
    return None


def translate_batch(laws: list[dict]) -> dict[int, str]:
    """
    Traduit un batch de lois en 1 appel IA.
    Retourne {law_id: title_fr_traduit}.
    """
    if not laws:
        return {}

    # Construire le prompt avec numérotation
    lines = []
    for i, law in enumerate(laws, 1):
        lines.append(
            f"{i}. [Type: {law.get('type','?')} | N°: {law.get('number','?')}] {law.get('title_ar','')}"
        )

    prompt = f"""Tu es un juriste marocain bilingue. Traduis ces {len(laws)} titres de textes juridiques marocains de l'arabe vers le français.

RÈGLES :
- Une traduction par ligne, préfixée par son numéro (ex: "1. Décret...")
- Style officiel français (Journal officiel)
- Fidèle et concis — 1 ligne par titre
- Garder les numéros, dates et références intacts
- Si le titre est trop vague, utilise : "[Type] n°[N°]"
- Répondre UNIQUEMENT avec la liste numérotée, rien d'autre

Titres arabes :
{chr(10).join(lines)}

Traductions françaises :"""

    result = call_ai(prompt)
    if not result:
        return {}

    # Parser la réponse
    translations = {}
    for line in result.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        # Match "1. Titre" ou "1) Titre" ou "1 - Titre"
        m = re.match(r'^(\d+)[.):\-\s]+(.+)$', line)
        if m:
            idx = int(m.group(1)) - 1
            title = m.group(2).strip()
            # Supprimer guillemets éventuels
            title = re.sub(r'^["\']|["\']$', '', title).strip()
            if 0 <= idx < len(laws) and title and len(title) > 3:
                translations[laws[idx]["id"]] = title[:400]

    return translations


def fetch_adala_laws(client: httpx.Client, limit: int | None, skip_ids: set) -> list[dict]:
    """Récupère les lois Adala avec title_ar non null, en excluant skip_ids."""
    all_rows = []
    offset, batch = 0, 500

    print("-> Récupération des lois Adala depuis Supabase...", flush=True)
    while True:
        params = {
            "select":      "id,number,title_fr,title_ar,type",
            "source_name": "eq.Adala",
            "title_ar":    "not.is.null",
            "order":       "id.asc",
            "limit":       str(batch),
            "offset":      str(offset),
        }
        resp = client.get(f"{SUPABASE_URL}/rest/v1/laws", headers=HEADERS_SB, params=params)
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            break
        # Filtrer les placeholders uniquement
        for r in rows:
            if r["id"] not in skip_ids and is_placeholder(r.get("title_fr") or ""):
                all_rows.append(r)
        if len(rows) < batch:
            break
        offset += batch
        if limit and len(all_rows) >= limit:
            break

    if limit:
        all_rows = all_rows[:limit]
    print(f"-> {len(all_rows)} titres placeholder a traduire", flush=True)
    return all_rows


def patch_batch(client: httpx.Client, translations: dict[int, str], dry_run: bool) -> tuple[int, int]:
    """Envoie les PATCH en lot individuel."""
    ok, err = 0, 0
    for law_id, title_fr in translations.items():
        if dry_run:
            ok += 1
            continue
        try:
            r = client.patch(
                f"{SUPABASE_URL}/rest/v1/laws",
                headers=HEADERS_SB,
                params={"id": f"eq.{law_id}"},
                json={"title_fr": title_fr},
                timeout=15,
            )
            if r.status_code in (200, 204):
                ok += 1
            else:
                err += 1
        except Exception as e:
            err += 1
            print(f"[!] PATCH id={law_id}: {type(e).__name__}", flush=True)
    return ok, err


def main():
    parser = argparse.ArgumentParser(description="Traduction batch title_ar -> title_fr (Lois Adala)")
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--limit",    type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    args = parser.parse_args()

    if not ANTHROPIC_KEY and not (PROVIDER == "openrouter" and OPENROUTER_KEY):
        print("[!] ANTHROPIC_API_KEY ou OPENROUTER_API_KEY manquant dans .env")
        sys.exit(1)

    print(f"\n>> Traduction batch title_ar -> title_fr"
          f"  (batch={args.batch_size} titres/appel)"
          f"{'  [DRY-RUN]' if args.dry_run else ''}", flush=True)

    total_ok   = 0
    total_err  = 0
    batch_num  = 0

    with httpx.Client(timeout=30, limits=httpx.Limits(max_keepalive_connections=5)) as client:
        laws = fetch_adala_laws(client, args.limit, skip_ids=set())

        if not laws:
            print("Rien a traduire.", flush=True)
            return

        total = len(laws)
        for i in range(0, total, args.batch_size):
            batch = laws[i : i + args.batch_size]
            batch_num += 1
            done = min(i + args.batch_size, total)

            translations = translate_batch(batch)
            ok, err = patch_batch(client, translations, args.dry_run)
            total_ok  += ok
            total_err += err

            # Preview du 1er titre traduit du batch (ASCII safe)
            if translations:
                sample_id = next(iter(translations))
                sample = translations[sample_id].encode('ascii', errors='replace').decode('ascii')[:50]
            else:
                sample = "[aucune traduction]"

            print(
                f"  Batch {batch_num:>4} | {done:>5}/{total}"
                f"  OK={ok}/{len(batch)}"
                f"  ex: {sample}",
                flush=True,
            )

            time.sleep(0.3)   # pause légère entre les appels

    print(f"\n>> Termine : {total_ok} traduits, {total_err} erreurs", flush=True)
    if args.dry_run:
        print("[DRY-RUN] Aucune ecriture effectuee.", flush=True)

    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rp = report_dir / f"translate_batch_{ts}.json"
    with open(rp, "w", encoding="utf-8") as f:
        json.dump({"run_at": ts, "dry_run": args.dry_run,
                   "translated": total_ok, "errors": total_err}, f, indent=2)
    print(f"Rapport : {rp}\n", flush=True)


if __name__ == "__main__":
    main()
