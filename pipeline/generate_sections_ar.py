"""
JuriThèque — Génération de sections_ar pour les guides SEO
═══════════════════════════════════════════════════════════
Pour chaque guide sans sections_ar dans seoIntentPages.js :
  - Si sections FR existantes → traduire + adapter en arabe
  - Si aucune section → générer 3 sections AR depuis le droit marocain

Usage :
  python -X utf8 pipeline/generate_sections_ar.py --slug licenciement-maroc
  python -X utf8 pipeline/generate_sections_ar.py --all --dry-run
  python -X utf8 pipeline/generate_sections_ar.py --all --limit 5
"""

import argparse, json, os, re, sys, time
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_KEY = os.environ.get('OPENROUTER_API_KEY', '')
MODEL = 'google/gemini-2.5-pro'
SEO_FILE = Path(__file__).parent.parent / 'src' / 'data' / 'seoIntentPages.js'

HEADERS = {
    'Authorization': f'Bearer {OPENROUTER_KEY}',
    'Content-Type': 'application/json',
    'HTTP-Referer': 'https://juritheque.com',
    'X-Title': 'JuriTheque',
}


# ── Extraction d'un guide depuis seoIntentPages.js ────────────────────────────

def read_guide(slug: str) -> dict | None:
    content = SEO_FILE.read_text(encoding='utf-8')
    m = re.search(rf"slug:\s*['\"]({re.escape(slug)})['\"]", content)
    if not m:
        return None
    start = m.start()
    # Trouver la fin du bloc (prochain slug ou fin du fichier)
    next_m = re.search(r"slug:\s*['\"][^'\"]+['\"]", content[start + 10:])
    end = (start + 10 + next_m.start()) if next_m else len(content)
    block = content[start:end]

    def field(name):
        m2 = re.search(rf"{name}:\s*['\"]([^'\"]*)['\"]", block)
        return m2.group(1) if m2 else ''

    def lst(name):
        m2 = re.search(rf"{name}:\s*\[([^\]]*)\]", block, re.DOTALL)
        return re.findall(r"['\"]([^'\"]{4,})['\"]", m2.group(1)) if m2 else []

    # Extraire sections FR
    sections_fr = []
    for sm in re.finditer(r'\{\s*h2:\s*[\'"]([^\'"]+)[\'"][\s\S]{0,3000}?(?=\},\s*\{|\}\s*\])', block):
        sec_block = sm.group(0)
        h2 = re.search(r"h2:\s*['\"]([^'\"]+)['\"]", sec_block)
        content_m = re.search(r"content:\s*['\"]([^'\"]{10,})['\"]", sec_block, re.DOTALL)
        bullets = re.findall(r"['\"]([^'\"]{15,})['\"]", sec_block)
        if h2:
            sections_fr.append({
                'h2': h2.group(1),
                'content': content_m.group(1) if content_m else '',
                'bullets': bullets[:8],
            })

    has_ar = 'sections_ar' in block
    has_faq_ar = 'faq_ar' in block

    # Extraire faq FR pour contexte
    faq_fr = []
    for qm in re.finditer(r"q:\s*['\"]([^'\"]{10,})['\"]", block):
        faq_fr.append(qm.group(1))

    return {
        'slug': slug,
        'h1': field('h1'),
        'h1_ar': field('h1_ar'),
        'intro': field('intro'),
        'intro_ar': field('intro_ar'),
        'domain': field('legalDomain') or field('category'),
        'keywords': lst('keywords'),
        'keywords_ar': lst('keywords_ar'),
        'sections_fr': sections_fr,
        'faq_fr': faq_fr[:6],
        'has_sections_ar': has_ar,
        'has_faq_ar': has_faq_ar,
    }


def list_missing(only_with_fr=False, check_faq=False):
    content = SEO_FILE.read_text(encoding='utf-8')
    slugs = re.findall(r"slug:\s*['\"]([^'\"]+)['\"]", content)
    missing = []
    for slug in slugs:
        g = read_guide(slug)
        if not g:
            continue
        needs_sections = not g['has_sections_ar']
        needs_faq = check_faq and not g['has_faq_ar']
        if needs_sections or needs_faq:
            if only_with_fr and not g['sections_fr']:
                continue
            missing.append(g)
    return missing


# ── Appel API Gemini ──────────────────────────────────────────────────────────

def call_gemini(prompt: str) -> str | None:
    payload = {
        'model': MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 8192,
        'temperature': 0.3,
    }
    with httpx.Client(timeout=120) as client:
        r = client.post('https://openrouter.ai/api/v1/chat/completions',
                        headers=HEADERS, json=payload)
        if not r.is_success:
            print(f'  ✗ API HTTP {r.status_code}: {r.text[:300]}')
            return None
        data = r.json()
        choices = data.get('choices') or []
        if not choices:
            print(f'  ✗ API réponse vide: {str(data)[:300]}')
            return None
        return choices[0]['message']['content']


# ── Construction du prompt ────────────────────────────────────────────────────

def build_prompt(guide: dict) -> str:
    has_fr = bool(guide['sections_fr'])

    fr_sections_text = ''
    if has_fr:
        for i, s in enumerate(guide['sections_fr'], 1):
            fr_sections_text += f"\nSection {i}: {s['h2']}\n"
            if s['content']:
                fr_sections_text += f"Contenu: {s['content'][:500]}\n"
            if s['bullets']:
                fr_sections_text += "Points: " + ' | '.join(s['bullets'][:5]) + '\n'

    task = (
        "Traduis et adapte les sections françaises ci-dessus en arabe juridique marocain clair."
        if has_fr else
        "Génère 3 sections arabes riches sur ce guide, basées sur le droit marocain réel."
    )

    return f"""Tu es un juriste marocain expert en droit marocain, spécialisé en rédaction bilingue FR/AR.

GUIDE : {guide['h1'] or guide['slug']}
H1 AR : {guide['h1_ar'] or ''}
DOMAINE : {guide['domain']}
MOTS-CLÉS FR : {', '.join(guide['keywords'][:8])}
MOTS-CLÉS AR : {', '.join(guide['keywords_ar'][:8])}
{('INTRO AR : ' + guide['intro_ar'][:300]) if guide['intro_ar'] else ''}
{('SECTIONS FR EXISTANTES :' + fr_sections_text) if has_fr else ''}

TÂCHE : {task}

RÈGLES IMPÉRATIVES :
- Arabe standard juridique marocain (fuṣḥā), pas de darija
- Références exactes aux lois marocaines (numéros de dahirs, décrets, codes)
- 3 sections minimum, 5 maximum
- Chaque section : h2 (titre) + content (1-2 phrases intro) + bullets (4-6 points précis)
- Les bullets doivent être concrets et actionnables, pas vagues
- Ne pas mentionner d'autres systèmes juridiques (droit français, etc.) sauf comparaison explicite
- Longueur totale : 600-1000 mots en arabe

RETOURNE UNIQUEMENT ce JSON valide (sans markdown, sans explications) :
{{
  "sections_ar": [
    {{
      "h2": "عنوان القسم",
      "content": "جملة تمهيدية للقسم...",
      "bullets": [
        "نقطة محددة ومفصلة 1",
        "نقطة محددة ومفصلة 2",
        "نقطة محددة ومفصلة 3",
        "نقطة محددة ومفصلة 4"
      ]
    }}
  ]
}}"""


# ── Patch seoIntentPages.js ───────────────────────────────────────────────────

def esc(s):
    s = str(s)
    s = s.replace('\\', '\\\\')   # backslashes d'abord
    s = s.replace("'", "\\'")     # apostrophes
    s = s.replace('\n', ' ')      # newlines → espace
    s = s.replace('\r', '')       # CR
    s = s.replace('**', '')       # markdown bold
    s = s.replace('`', '')        # backticks
    return s

def sections_ar_to_js(sections: list) -> str:
    lines = ['  sections_ar: [']
    for s in sections:
        lines.append('    {')
        lines.append(f"      h2: '{esc(s['h2'])}',")
        lines.append(f"      content: '{esc(s.get('content',''))}',")
        lines.append('      bullets: [')
        for b in s.get('bullets', []):
            lines.append(f"        '{esc(b)}',")
        lines.append('      ],')
        lines.append('    },')
    lines.append('  ],')
    return '\n'.join(lines)

def faq_ar_to_js(faq: list) -> str:
    lines = ['  faq_ar: [']
    for item in faq:
        lines.append(f"    {{ q: '{esc(item['q'])}', a: '{esc(item['a'])}' }},")
    lines.append('  ],')
    return '\n'.join(lines)


def patch_file(slug: str, sections_ar: list, dry_run: bool, faq_ar: list = None) -> bool:
    content = SEO_FILE.read_text(encoding='utf-8')
    m = re.search(rf"slug:\s*['\"]({re.escape(slug)})['\"]", content)
    if not m:
        print(f'  ✗ slug introuvable dans le fichier')
        return False

    # Trouver la fin du bloc = position juste avant le '},' qui ferme l'entrée du guide
    start = m.start()
    next_m = re.search(r"slug:\s*['\"][^'\"]+['\"]", content[start + 10:])
    end = (start + 10 + next_m.start()) if next_m else len(content)
    block = content[start:end]

    # Chercher la position de l'accolade fermante du guide
    # On insère sections_ar juste avant la dernière },
    close_m = list(re.finditer(r'\n\s*\},?\s*\n', block))
    if not close_m:
        print('  ✗ impossible de localiser la fin du bloc')
        return False

    insert_pos = start + close_m[-1].start()
    js_parts = []
    if sections_ar:
        js_parts.append(sections_ar_to_js(sections_ar))
    if faq_ar:
        js_parts.append(faq_ar_to_js(faq_ar))
    js_code = '\n' + '\n'.join(js_parts) + '\n'

    new_content = content[:insert_pos] + js_code + content[insert_pos:]

    if dry_run:
        if sections_ar:
            print(f'  [dry-run] sections_ar ({len(sections_ar)}) — non écrites')
        if faq_ar:
            print(f'  [dry-run] faq_ar ({len(faq_ar)}) — non écrites')
        return True

    SEO_FILE.write_text(new_content, encoding='utf-8')
    if sections_ar:
        print(f'  ✓ sections_ar insérées')
    if faq_ar:
        print(f'  ✓ faq_ar insérée')
    return True


# ── Parsing JSON robuste ──────────────────────────────────────────────────────

def parse_response(raw: str, key: str = 'sections_ar') -> list | None:
    clean = re.sub(r'^```(?:json)?\s*', '', raw.strip())
    clean = re.sub(r'\s*```$', '', clean.strip())
    try:
        data = json.loads(clean)
        return data.get(key, [])
    except json.JSONDecodeError:
        m = re.search(r'\{[\s\S]*\}', clean)
        if m:
            try:
                data = json.loads(m.group())
                return data.get(key, [])
            except Exception:
                pass
        try:
            from json_repair import repair_json
            data = repair_json(clean, return_objects=True)
            if isinstance(data, dict):
                return data.get(key, [])
        except Exception:
            pass
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def build_faq_prompt(guide: dict) -> str:
    faq_fr_text = '\n'.join([f"Q: {q}" for q in guide['faq_fr']]) if guide['faq_fr'] else ''
    return f"""Tu es un juriste marocain expert. Génère une FAQ en arabe pour ce guide juridique.

GUIDE : {guide['h1'] or guide['slug']}
H1 AR : {guide['h1_ar'] or ''}
DOMAINE : {guide['domain']}
{('FAQ FR (à traduire/adapter) :\n' + faq_fr_text) if faq_fr_text else ''}

TÂCHE : Génère 5 questions-réponses en arabe juridique marocain clair.
- Questions pratiques que se posent les citoyens/professionnels
- Réponses précises avec références aux textes marocains
- Arabe standard (fuṣḥā), pas de darija

RETOURNE UNIQUEMENT ce JSON valide :
{{
  "faq_ar": [
    {{ "q": "السؤال؟", "a": "الجواب المفصل..." }},
    {{ "q": "السؤال؟", "a": "الجواب المفصل..." }},
    {{ "q": "السؤال؟", "a": "الجواب المفصل..." }},
    {{ "q": "السؤال؟", "a": "الجواب المفصل..." }},
    {{ "q": "السؤال؟", "a": "الجواب المفصل..." }}
  ]
}}"""


def process_guide(slug: str, dry_run: bool, gen_faq: bool = False) -> bool:
    print(f'\n🔷 {slug}')
    guide = read_guide(slug)
    if not guide:
        print('  ✗ guide introuvable')
        return False

    needs_sections = not guide['has_sections_ar']
    needs_faq = gen_faq and not guide['has_faq_ar']

    if not needs_sections and not needs_faq:
        print('  ✓ déjà complet, skip')
        return True

    mode = 'traduction FR→AR' if guide['sections_fr'] else 'génération depuis 0'
    if needs_sections:
        print(f'  → sections_ar : {mode} ({len(guide["sections_fr"])} sections FR)')

    sections_ar = []
    faq_ar = []

    if needs_sections:
        prompt = build_prompt(guide)
        print('  → appel Gemini (sections)...')
        raw = call_gemini(prompt)
        if raw is None:
            return False
        sections_ar = parse_response(raw, 'sections_ar') or []
        if not sections_ar:
            print('  ✗ sections invalides:', raw[:200])
            return False
        print(f'  ✓ {len(sections_ar)} sections générées')

    if needs_faq:
        print('  → appel Gemini (faq_ar)...')
        faq_raw = call_gemini(build_faq_prompt(guide))
        if faq_raw:
            faq_ar = parse_response(faq_raw, 'faq_ar') or []
            if faq_ar:
                print(f'  ✓ {len(faq_ar)} Q/R générées')
            else:
                print('  ✗ faq_ar invalide')

    return patch_file(slug, sections_ar, dry_run, faq_ar)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--slug', help='Slug du guide à traiter')
    parser.add_argument('--all', action='store_true', help='Traiter tous les guides manquants')
    parser.add_argument('--with-fr-only', action='store_true', help='Seulement ceux qui ont sections FR')
    parser.add_argument('--faq', action='store_true', help='Générer aussi faq_ar si manquante')
    parser.add_argument('--dry-run', action='store_true', help='Aperçu sans écrire')
    parser.add_argument('--limit', type=int, default=999, help='Nombre max de guides')
    parser.add_argument('--delay', type=float, default=3.0, help='Délai entre requêtes (s)')
    args = parser.parse_args()

    if not OPENROUTER_KEY:
        print('✗ OPENROUTER_API_KEY manquant dans .env')
        sys.exit(1)

    gen_faq = args.faq
    if args.slug:
        process_guide(args.slug, args.dry_run, gen_faq=gen_faq)
    elif args.all:
        guides = list_missing(only_with_fr=args.with_fr_only, check_faq=gen_faq)
        label = 'incomplets' if gen_faq else 'sans sections_ar'
        print(f'📋 {len(guides)} guides {label} trouvés')
        count = 0
        for g in guides[:args.limit]:
            ok = process_guide(g['slug'], args.dry_run, gen_faq=gen_faq)
            count += 1
            if count < min(args.limit, len(guides)) and not args.dry_run:
                time.sleep(args.delay)
        print(f'\n✅ Traités : {count}/{len(guides)}')
    else:
        print('Usage: --slug <slug> | --all [--faq] [--dry-run] [--limit N]')
        guides = list_missing(check_faq=True)
        print(f'\n{len(guides)} guides incomplets :')
        for g in guides:
            s = '✓' if g['has_sections_ar'] else '✗'
            f = '✓' if g['has_faq_ar'] else '✗'
            print(f'  sec_ar:{s} faq_ar:{f}  {g["slug"]}')


if __name__ == '__main__':
    main()
