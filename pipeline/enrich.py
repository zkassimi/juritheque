"""
JuriThèque — pipeline/enrich.py
════════════════════════════════════════════════════════════════════
Enrichissement des textes juridiques :
  • Score de qualité d'extraction (0-100)
  • Détection du nombre d'articles (FR + AR)
  • Extraction de mots-clés juridiques (règles)
  • Génération de résumé simple + sommaire (via Claude / OpenRouter)
  • Champs SEO personnalisés
  • Slug canonique
  • Protection des corrections humaines

Usage :
  python pipeline/enrich.py --dry-run              # Analyse sans écrire
  python pipeline/enrich.py --limit 20             # 20 textes max
  python pipeline/enrich.py --id 123               # Une seule loi
  python pipeline/enrich.py --only-missing         # Seulement sans résumé
  python pipeline/enrich.py --force                # Régénérer tout
  python pipeline/enrich.py --no-ai --limit 100    # Score + mots-clés uniquement
  python pipeline/enrich.py --limit 20 --dry-run   # Prévisualisation

Prérequis :
  pip install httpx python-dotenv rich anthropic
  Variables .env : SUPABASE_URL, SUPABASE_SERVICE_KEY
  Optionnel     : ANTHROPIC_API_KEY ou OPENROUTER_API_KEY
"""

import os, sys, re, json, hashlib, argparse, unicodedata, time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import httpx

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
    console = Console()
    def log(msg): console.print(msg)
    def log_err(msg): console.print(f"[red]{msg}[/]")
except ImportError:
    def log(msg): print(msg)
    def log_err(msg): print(f"ERROR: {msg}", file=sys.stderr)
    def track(it, description=""): return it

# ── Config ─────────────────────────────────────────────────────────────────────
load_dotenv()

SUPABASE_URL   = (os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL", "")).rstrip("/")
SUPABASE_KEY   = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")
ANTHROPIC_KEY  = os.getenv("ANTHROPIC_API_KEY", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("VITE_OPENROUTER_KEY", "")
PROVIDER       = os.getenv("PROVIDER", "anthropic").lower()   # anthropic | openrouter
MODEL          = os.getenv("MODEL", "claude-haiku-3-5")
ENRICH_VERSION = "1.0.0"

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

# ── Mots-clés juridiques par domaine ──────────────────────────────────────────
DOMAIN_KEYWORDS = {
    "civil":           ["contrat","famille","propriété","succession","mariage","divorce","bail","location","tutelle","héritage"],
    "penal":           ["crime","délit","peine","emprisonnement","amende","récidive","garde à vue","acquittement","condamnation"],
    "commercial":      ["société","commerce","faillite","entreprise","capital","actionnaire","liquidation","bilan","contrat commercial"],
    "administratif":   ["administration","service public","fonctionnaire","marchés publics","urbanisme","permis","recours"],
    "travail":         ["travail","salarié","licenciement","grève","syndicat","congé","retraite","indemnité","contrat de travail"],
    "fiscal":          ["impôt","taxe","TVA","IS","IR","douane","déclaration fiscale","cotisation","exonération"],
    "international":   ["traité","convention","accord","coopération","extradition","droit international","ambassade"],
    "numerique":       ["données personnelles","cybercriminalité","e-commerce","télécoms","CNDP","numérique","protection des données"],
    "constitutionnel": ["constitution","droits fondamentaux","parlement","élection","référendum","Roi","gouvernement"],
    "bancaire":        ["banque","crédit","BAM","banque participative","microfinance","dépôt","prêt","virement","change"],
    "finances_publiques": ["loi de finances","budget","marchés publics","comptabilité publique","dette","CGI","recette"],
}

GENERAL_LEGAL_KEYWORDS_FR = [
    "article","loi","décret","dahir","arrêté","circulaire","règlement","ordonnance",
    "obligation","interdiction","sanction","amende","peine","dérogation","application",
    "abrogation","modification","entrée en vigueur","publication","bulletin officiel",
]

GENERAL_LEGAL_KEYWORDS_AR = [
    "المادة","القانون","المرسوم","الظهير","القرار","المنشور","النظام",
    "الالتزام","العقوبة","الغرامة","الإلغاء","التطبيق","النفاذ",
]

# ── Patterns de détection d'articles ──────────────────────────────────────────
ARTICLE_PATTERNS_FR = [
    r'\bArticle\s+(?:premier|Premier|PREMIER|\d+)\b',
    r'\bArt\.\s*\d+\b',
    r'\bARTICLE\s+\d+\b',
    r'\bChapitre\s+(?:[IVXivx]+|\d+)\b',
]
ARTICLE_PATTERNS_AR = [
    r'المادة\s+(?:\d+|الأولى|الأول|الثانية|الثالثة|الرابعة|الخامسة)',
    r'الفصل\s+(?:\d+|الأول|الأولى|الثاني|الثالث)',
    r'البند\s+\d+',
]

# ── Helpers Supabase ───────────────────────────────────────────────────────────

def sb_get(endpoint: str, params: dict) -> list:
    if not SUPABASE_URL or not SUPABASE_KEY:
        log_err("SUPABASE_URL ou SUPABASE_SERVICE_KEY manquant.")
        return []
    try:
        r = httpx.get(f"{SUPABASE_URL}/rest/v1/{endpoint}", headers=HEADERS, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log_err(f"Supabase GET /{endpoint}: {e}")
        return []


def sb_patch(endpoint: str, params: dict, payload: dict) -> bool:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    try:
        r = httpx.patch(
            f"{SUPABASE_URL}/rest/v1/{endpoint}",
            headers={**HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
            params=params,
            json=payload,
            timeout=20,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        log_err(f"Supabase PATCH /{endpoint}: {e}")
        return False

# ── Helpers IA ─────────────────────────────────────────────────────────────────

def call_ai(prompt: str) -> str | None:
    """Appelle Claude (Anthropic ou OpenRouter) et retourne le texte généré."""
    try:
        if PROVIDER == "openrouter" and OPENROUTER_KEY:
            r = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "google/gemini-2.5-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1200,
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
                max_tokens=1200,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()

    except Exception as e:
        log_err(f"Erreur IA: {e}")
    return None


def ai_available() -> bool:
    return bool(ANTHROPIC_KEY or (PROVIDER == "openrouter" and OPENROUTER_KEY))

# ── Score de confiance ────────────────────────────────────────────────────────

def compute_confidence_score(law: dict) -> tuple[int, str, bool]:
    """
    Calcule le score de confiance d'extraction (0-100).
    Retourne (score, status, needs_human_review).
    """
    score = 0

    title_fr   = law.get("title_fr", "") or ""
    title_ar   = law.get("title_ar", "") or ""
    content_fr = law.get("content_fr", "") or ""
    content_ar = law.get("content_ar", "") or ""
    number     = law.get("number", "") or ""
    date       = law.get("date")

    # 1. Titre (15 pts)
    if title_fr or title_ar:
        score += 15

    # 2. Numéro de référence (5 pts)
    if number and len(number.strip()) > 2:
        score += 5

    # 3. Date (10 pts)
    if date:
        score += 10

    # 4. Longueur du contenu (30 pts max)
    content_len = len(content_fr) + len(content_ar)
    if content_len > 8000:
        score += 30
    elif content_len > 3000:
        score += 22
    elif content_len > 1000:
        score += 14
    elif content_len > 200:
        score += 6

    # 5. Présence de mots-clés juridiques (10 pts)
    combined = (content_fr + " " + content_ar).lower()
    kw_found = sum(1 for kw in GENERAL_LEGAL_KEYWORDS_FR if kw in combined)
    kw_found += sum(1 for kw in GENERAL_LEGAL_KEYWORDS_AR if kw in combined)
    if kw_found >= 5:
        score += 10
    elif kw_found >= 2:
        score += 5

    # 6. Articles détectés (15 pts)
    art_count, reliable = detect_articles(content_fr, content_ar)
    if art_count >= 3 and reliable:
        score += 15
    elif art_count >= 1:
        score += 7

    # 7. Pénalité : caractères illisibles dans content_fr (-15 max)
    if content_fr and len(content_fr) > 50:
        bad = sum(1 for c in content_fr if not c.isprintable() and c not in "\n\r\t ")
        noise_ratio = bad / len(content_fr)
        if noise_ratio > 0.15:
            score -= 15
        elif noise_ratio > 0.07:
            score -= 7

    # 8. Pénalité : répétitions anormales (-10)
    if content_fr and len(content_fr) > 200:
        chunks = [content_fr[i:i+60] for i in range(0, min(len(content_fr), 3000), 60)]
        if len(chunks) > 5:
            unique_ratio = len(set(chunks)) / len(chunks)
            if unique_ratio < 0.4:
                score -= 10

    # 9. Pénalité : texte trop court sans contenu informatif (-5)
    if content_len < 100 and not title_fr and not title_ar:
        score -= 5

    score = max(0, min(100, score))

    if score >= 75:
        return score, "success", False
    elif score >= 45:
        return score, "partial", True
    elif score > 0:
        return score, "needs_review", True
    else:
        return 0, "failed", True

# ── Détection d'articles ───────────────────────────────────────────────────────

def detect_articles(text_fr: str, text_ar: str) -> tuple[int, bool]:
    """
    Détecte le nombre d'articles/chapitres dans les textes.
    Retourne (count, reliable) — reliable=True si >= 3 articles trouvés.
    """
    numbers_fr = set()
    for pat in ARTICLE_PATTERNS_FR[:2]:  # Article N + Art. N seulement pour compter
        for m in re.finditer(pat, text_fr, re.IGNORECASE):
            # Extraire le numéro
            num_match = re.search(r'\d+', m.group())
            if num_match:
                numbers_fr.add(int(num_match.group()))
            elif "premier" in m.group().lower():
                numbers_fr.add(1)

    numbers_ar = set()
    for pat in ARTICLE_PATTERNS_AR[:2]:
        for m in re.finditer(pat, text_ar):
            num_match = re.search(r'\d+', m.group())
            if num_match:
                numbers_ar.add(int(num_match.group()))
            elif "الأول" in m.group() or "الأولى" in m.group():
                numbers_ar.add(1)

    count = max(len(numbers_fr), len(numbers_ar))

    # Fiabilité : vérifier la séquentialité partielle (au moins 3 numéros consécutifs)
    reliable = False
    for nums in [numbers_fr, numbers_ar]:
        if len(nums) >= 3:
            sorted_nums = sorted(nums)
            # Au moins 50% des numéros sont consécutifs ou proches
            consecutive = sum(1 for i in range(len(sorted_nums)-1) if sorted_nums[i+1] - sorted_nums[i] <= 2)
            if consecutive >= 2:
                reliable = True
                break

    return count, reliable

# ── Extraction de mots-clés ────────────────────────────────────────────────────

def extract_keywords(law: dict) -> list[str]:
    """Extraction règle-based de mots-clés juridiques pertinents."""
    keywords = set()
    text = " ".join(filter(None, [
        law.get("title_fr", ""),
        law.get("title_ar", ""),
        (law.get("content_fr", "") or "")[:1500],
        (law.get("content_ar", "") or "")[:1500],
    ])).lower()

    # Mots-clés du domaine
    domain = law.get("domain_id", "")
    if domain in DOMAIN_KEYWORDS:
        for kw in DOMAIN_KEYWORDS[domain]:
            if kw.lower() in text:
                keywords.add(kw)

    # Mots-clés juridiques généraux (FR)
    for kw in GENERAL_LEGAL_KEYWORDS_FR[:10]:
        if kw in text:
            keywords.add(kw)

    # Filtrer les trop génériques
    too_generic = {"article", "loi", "المادة", "القانون"}
    keywords -= too_generic

    return sorted(keywords)[:12]


# ── Génération du slug canonique ──────────────────────────────────────────────

_SLUG_STOPWORDS = {
    'le','la','les','du','de','des','au','aux','et','ou','un','une',
    'n','no','n°','par','sur','en','a','à','dans','pour','avec','sans',
    'relatif','relative','relatifs','relatives',
    'portant','fixant','instituant','modifiant','abrogeant','approuvant',
    'dahir','decret','loi','arrete','circulaire','texte','ordonnance',
    'code','reglement','avis','bulletin',
}

def make_canonical_slug(law: dict) -> str:
    """Convention : {type}-{number}-{mots-clés-titre} tout en minuscules sans accents."""

    def _s(t: str) -> str:
        norm = unicodedata.normalize("NFD", (t or "").lower())
        norm = "".join(c for c in norm if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z0-9]+", "-", norm).strip("-")

    type_slug   = _s(law.get("type") or "texte")
    number_slug = _s(law.get("number") or "")
    title       = (law.get("title_fr") or "").strip()

    # Extraire les mots significatifs du titre (sans stopwords, sans répétition du numéro, max 7 mots)
    num_tokens = set(number_slug.split("-")) if number_slug else set()
    words = re.sub(r"[^a-zA-Z\xc0-\xff0-9\s]", " ", title).lower().split()
    keywords = []
    for w in words:
        sw = _s(w)
        if sw and w not in _SLUG_STOPWORDS and len(w) > 2 and sw not in num_tokens:
            keywords.append(sw)
        if len(keywords) >= 7:
            break
    kw_slug = "-".join(keywords)

    parts = [p for p in [type_slug, number_slug, kw_slug] if p]
    slug  = re.sub(r"-+", "-", "-".join(parts)).strip("-")[:100]
    return slug or f"texte-{law.get('id', 'unknown')}"


# ── Hash du contenu brut ───────────────────────────────────────────────────────

def compute_hash(law: dict) -> str:
    raw = (law.get("content_fr") or "") + (law.get("content_ar") or "")
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:16]


# ── Génération SEO (règle-based) ──────────────────────────────────────────────

def generate_seo_fields(law: dict, summary: str | None = None) -> dict:
    """Génère seo_title_fr et seo_description_fr depuis les données disponibles."""
    type_   = law.get("type", "Texte juridique") or "Texte juridique"
    number  = law.get("number", "") or ""
    title   = law.get("title_fr", "") or law.get("title_ar", "") or ""
    date    = law.get("date", "") or ""
    year    = date[:4] if len(date) >= 4 else ""

    # SEO Title (< 60 chars)
    parts = [type_]
    if number:
        parts.append(number)
    raw_title = " ".join(parts) + (f" — {title}" if title else "")
    if len(raw_title) > 60:
        seo_title = raw_title[:57].rstrip() + "…"
    else:
        seo_title = raw_title

    # SEO Description (< 155 chars)
    if summary and len(summary) > 20:
        seo_desc = summary[:152].rstrip() + ("…" if len(summary) > 152 else "")
    else:
        desc_parts = [type_]
        if number:
            desc_parts.append(number)
        if year:
            desc_parts.append(f"({year})")
        if title:
            desc_parts.append(f"— {title[:80]}")
        seo_desc = " ".join(desc_parts)[:155]

    return {"seo_title_fr": seo_title, "seo_description_fr": seo_desc}


# ── Extraction de TOC sans IA ──────────────────────────────────────────────────

def extract_toc_no_ai(content_fr: str, content_ar: str) -> dict | None:
    """Extraction structurelle du sommaire sans IA (chapitres/titres)."""
    sections = []

    if content_fr:
        # Chercher les chapitres/titres principaux
        chap_matches = re.findall(
            r'(?:Chapitre|CHAPITRE|Titre|TITRE)\s+(?:[IVXivx]+|\d+)\s*[.:\-–]?\s*([^\n]{5,80})',
            content_fr
        )
        for m in chap_matches[:8]:
            s = m.strip()
            if s and len(s) > 3:
                sections.append({"titre": s})

    if not sections and content_ar:
        chap_ar = re.findall(r'(?:الباب|الفصل)\s+(?:الأول|الثاني|الثالث|\d+)\s*[:\-]?\s*([^\n]{5,60})', content_ar)
        for m in chap_ar[:6]:
            s = m.strip()
            if s:
                sections.append({"titre": s})

    return {"sections": sections} if sections else None


# ── Extraction d'articles importants sans IA ──────────────────────────────────

def extract_important_articles_no_ai(content_fr: str) -> list | None:
    """Extrait les articles ayant un titre explicite (Article N - Titre)."""
    if not content_fr:
        return None
    articles = []
    # Pattern : Article 1 - Titre : Texte court
    matches = re.findall(
        r'Article\s+(\d+)\s*[.:\-–]\s*([^\n]{5,70})\n+((?:(?!Article\s+\d).){10,300})',
        content_fr[:6000],
        re.IGNORECASE,
    )
    for num, titre, texte in matches[:5]:
        articles.append({
            "number":  f"Article {num}",
            "title":   titre.strip(),
            "text":    texte.strip()[:250],
        })
    return articles if articles else None


# ── Génération IA : résumé + sommaire ─────────────────────────────────────────

def generate_summary_ai(law: dict) -> str | None:
    """Génère un résumé structuré en 3 paragraphes (~200 mots) pour UX + SEO."""
    title_fr   = law.get("title_fr", "") or ""
    content_fr = (law.get("content_fr", "") or "")[:3000]
    title_ar   = law.get("title_ar", "") or ""
    type_      = law.get("type", "Texte juridique") or "Texte juridique"
    number     = law.get("number", "") or ""
    domain     = law.get("domain_id", "") or ""
    date_      = law.get("date", "") or ""
    has_content = bool(content_fr.strip())

    if not title_fr and not content_fr and not title_ar:
        return None

    # For title-only laws: build richer context hint from the title itself
    title_context = ""
    if not has_content and title_fr:
        title_context = f"\n\nINDICATION : Ce texte ne dispose pas de contenu extrait. Rédige le résumé en analysant attentivement le titre, le type ({type_}), le domaine ({domain or 'juridique'}), et la date ({date_ or 'non renseignée'}). Tu peux déduire l'objet et le champ d'application de ce type de texte en droit marocain. Ne pas inventer de numéros d'articles ou de chiffres précis non mentionnés, mais une analyse juridique déductive est attendue et correcte."

    prompt = f"""Tu es un expert juridique marocain. Rédige un résumé structuré de ce texte juridique en EXACTEMENT 3 paragraphes distincts, séparés chacun par une ligne vide.

STRUCTURE OBLIGATOIRE — 3 PARAGRAPHES :

PARAGRAPHE 1 — OBJET (2-3 phrases complètes) :
Expliquer ce que ce texte juridique régit et son objectif principal. Contextualiser dans le système juridique marocain.

PARAGRAPHE 2 — CHAMP D'APPLICATION (2-3 phrases complètes) :
Préciser qui est concerné (personnes, entités, secteurs). Décrire les principales obligations, droits ou procédures établies.

PARAGRAPHE 3 — POINTS CLÉS (1-2 phrases) :
Si des informations sur des sanctions, délais, organes compétents ou innovations notables peuvent être déduites, les mentionner. Sinon, résumer l'importance de ce texte dans l'ordre juridique marocain.

RÈGLES ABSOLUES :
- TOUJOURS rédiger les 3 paragraphes, même si le contenu est limité au titre
- Chaque paragraphe = minimum 2 phrases complètes
- Ne PAS inventer de numéros d'articles ou de chiffres précis non mentionnés
- L'analyse déductive à partir du type, domaine et titre est OBLIGATOIRE et correcte
- Compréhensible par un non-juriste, neutre, sans conseil personnel
- Total visé : 150-200 mots
- Ne PAS inclure les en-têtes "PARAGRAPHE 1", "OBJET" etc. dans le texte final{title_context}

Type : {type_}
Référence : {number}
Date : {date_ or "non renseignée"}
Domaine : {domain or "non renseigné"}
Titre FR : {title_fr}
Titre AR : {title_ar if title_ar else "(non disponible)"}
Contenu (début) : {content_fr[:2800] if has_content else "(non disponible — analyse déductive obligatoire à partir du titre et du contexte)"}

Résumé (3 paragraphes séparés par une ligne vide) :"""

    result = call_ai(prompt)
    if result and len(result.strip()) > 30:
        # Nettoyer les préfixes IA non désirés
        result = re.sub(r'^(Résumé\s*:?\s*|Voici\s+le\s+résumé\s*:?\s*)', '', result, flags=re.IGNORECASE).strip()
        # Supprimer les marqueurs de section si l'IA les a inclus quand même
        result = re.sub(r'^§\d+\s*[—–-]\s*\w+\s*:\s*', '', result, flags=re.MULTILINE).strip()
        # Smart truncation: keep full sentences up to 2000 chars
        if len(result) > 2000:
            # Find last sentence boundary before 2000 chars
            cut = result[:2000].rfind('. ')
            result = result[:cut + 1] if cut > 1000 else result[:2000]
        return result
    return None


def generate_toc_ai(law: dict) -> dict | None:
    """Génère un sommaire structuré en JSON via IA."""
    title_fr   = law.get("title_fr", "") or ""
    content_fr = (law.get("content_fr", "") or "")[:3500]

    if not content_fr:
        return None

    prompt = f"""Analyse ce texte juridique marocain et génère un sommaire structuré en JSON.

FORMAT JSON EXACT (ne génère que le JSON, rien d'autre) :
{{
  "sections": [
    {{"titre": "Objet du texte", "articles": "Art. 1", "resume": "..."}},
    {{"titre": "Champ d'application", "articles": "Art. 2-5", "resume": "..."}}
  ],
  "textes_lies": [],
  "notes": ""
}}

RÈGLES :
- Maximum 8 sections
- SEULEMENT les sections qui existent réellement dans le texte
- Ne PAS inventer de sections ou d'articles
- "articles" = plage d'articles couverts (ex: "Art. 1-10") ou vide si inconnu
- "resume" = 1 phrase courte max

Titre : {title_fr}
Texte : {content_fr[:3000]}

JSON :"""

    result = call_ai(prompt)
    if not result:
        return None

    # Extraire le JSON de la réponse
    try:
        # Chercher le JSON dans la réponse (peut être entouré de texte)
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            toc = json.loads(json_match.group())
            # Valider la structure minimale
            if "sections" in toc and isinstance(toc["sections"], list):
                # Nettoyer les sections vides
                toc["sections"] = [s for s in toc["sections"] if s.get("titre")][:8]
                return toc
    except (json.JSONDecodeError, ValueError):
        pass

    return None


def generate_summary_ar(law: dict, summary_fr: str) -> str | None:
    """Traduit le résumé français en arabe via IA (si disponible)."""
    if not summary_fr:
        return None

    # Si on a du contenu arabe, générer directement en arabe
    content_ar = (law.get("content_ar", "") or "")[:2500]
    title_ar   = law.get("title_ar", "") or ""

    if content_ar or title_ar:
        prompt = f"""أنت خبير قانوني مغربي. اكتب ملخصًا بسيطًا وقصيرًا (2-3 جمل كحد أقصى) لهذا النص القانوني.

القواعد :
- مبني على البيانات المقدمة فقط
- مفهوم لغير المختصين
- محايد، بدون نصيحة قانونية
- لا تخترع مواد أو عقوبات أو آجالًا غير مذكورة

العنوان : {title_ar}
بداية النص : {content_ar[:1500] if content_ar else "(غير متوفر)"}

الملخص البسيط (2-3 جمل، بالعربية) :"""

        result = call_ai(prompt)
        if result and len(result.strip()) > 10:
            return result.strip()[:500]

    # Fallback : traduire le résumé français
    prompt = f"""Traduis ce résumé juridique en arabe marocain standard. Garde le même sens.
Ne rajoute rien. Ne conseille pas.

Résumé français : {summary_fr}

Traduction arabe :"""
    result = call_ai(prompt)
    return result.strip()[:500] if result and len(result.strip()) > 5 else None


# ── Traitement d'une loi ───────────────────────────────────────────────────────

def process_law(law: dict, use_ai: bool = True, dry_run: bool = False, force: bool = False) -> dict:
    """
    Enrichit une loi. Retourne le dict des mises à jour à appliquer.
    """
    law_id  = law["id"]
    updates = {}
    result  = {"id": law_id, "status": "ok", "score": None, "updated_fields": [], "skipped": False}

    # ── Protéger les corrections humaines ─────────────────────────────────
    has_manual_summary = law.get("summary_updated_manually") is True
    has_manual_toc     = law.get("toc_updated_manually") is True

    # ── 1. Score de confiance (toujours calculé) ───────────────────────────
    score, ext_status, needs_review = compute_confidence_score(law)
    result["score"] = score

    updates["extraction_confidence_score"] = score
    updates["extraction_status"]           = ext_status
    updates["needs_human_review"]          = needs_review
    updates["extraction_version"]          = ENRICH_VERSION
    updates["raw_text_hash"]               = compute_hash(law)

    # ── 2. Compteur d'articles ─────────────────────────────────────────────
    art_count, reliable = detect_articles(
        law.get("content_fr", "") or "",
        law.get("content_ar", "") or ""
    )
    updates["detected_article_count"] = art_count if art_count > 0 else None
    if reliable and art_count >= 3:
        updates["public_article_count"] = art_count
    # Sinon public_article_count reste inchangé (ne pas écraser si déjà manuel)

    # ── 3. Mots-clés juridiques ────────────────────────────────────────────
    keywords = extract_keywords(law)
    if keywords:
        updates["legal_keywords"] = keywords

    # ── 4. Slug canonique ─────────────────────────────────────────────────
    current_slug = law.get("canonical_slug")
    if not current_slug or force:
        updates["canonical_slug"] = make_canonical_slug(law)

    # ── 5. Sommaire structuré (sans IA ou si contenu insuffisant) ─────────
    if not has_manual_toc or force:
        toc_no_ai = extract_toc_no_ai(
            law.get("content_fr", "") or "",
            law.get("content_ar", "") or ""
        )
        if toc_no_ai and not law.get("table_of_contents_fr"):
            updates["table_of_contents_fr"] = toc_no_ai

    # ── 6. Articles importants (sans IA) ──────────────────────────────────
    if not law.get("important_articles") or force:
        imp_arts = extract_important_articles_no_ai(law.get("content_fr", "") or "")
        if imp_arts:
            updates["important_articles"] = imp_arts

    # ── 7. Génération IA (résumé + sommaire amélioré) ─────────────────────
    summary_fr = law.get("simple_summary_fr")

    if use_ai and ai_available() and not dry_run and score >= 30:
        # Résumé FR
        if (not summary_fr or force) and not has_manual_summary:
            gen_summary = generate_summary_ai(law)
            if gen_summary:
                summary_fr = gen_summary
                updates["simple_summary_fr"] = gen_summary
                updates["summary_generated_at"] = datetime.now(timezone.utc).isoformat()

        # Résumé AR
        if not has_manual_summary or force:
            if not law.get("simple_summary_ar") or force:
                gen_summary_ar = generate_summary_ar(law, summary_fr or "")
                if gen_summary_ar:
                    updates["simple_summary_ar"] = gen_summary_ar

        # Sommaire IA (si pas déjà généré ou force)
        if (not law.get("table_of_contents_fr") or force) and not has_manual_toc:
            toc_ai = generate_toc_ai(law)
            if toc_ai:
                updates["table_of_contents_fr"] = toc_ai

    elif use_ai and ai_available() and not dry_run and score < 30:
        # Score trop faible → pas de résumé IA
        result["skipped_ai"] = True

    # ── 8. Champs SEO ──────────────────────────────────────────────────────
    seo = generate_seo_fields(law, summary_fr)
    if not law.get("seo_title_fr") or force:
        updates["seo_title_fr"] = seo["seo_title_fr"]
    if not law.get("seo_description_fr") or force:
        updates["seo_description_fr"] = seo["seo_description_fr"]

    # ── 9. Indexabilité publique ───────────────────────────────────────────
    # Ne pas rendre non-indexable automatiquement, mais signaler
    if score < 20 and ext_status == "failed":
        updates["is_publicly_indexable"] = False  # Très bas : masquer
    # Si déjà manuel, ne pas changer
    if law.get("is_publicly_indexable") is False and not force:
        updates.pop("is_publicly_indexable", None)

    result["updated_fields"] = list(updates.keys())
    result["ext_status"]     = ext_status
    result["needs_review"]   = needs_review

    # ── Score avant / après (complétude des champs clés) ──────────────────
    KEY_FIELDS = [
        "simple_summary_fr", "simple_summary_ar", "canonical_slug",
        "table_of_contents_fr", "seo_title_fr", "seo_description_fr",
        "legal_keywords", "important_articles",
    ]
    AI_FIELDS = {"simple_summary_fr", "simple_summary_ar", "table_of_contents_fr"}
    AI_LABELS = {
        "simple_summary_fr":    "résumé_FR",
        "simple_summary_ar":    "résumé_AR",
        "table_of_contents_fr": "TOC",
    }
    score_before = sum(1 for f in KEY_FIELDS if law.get(f))
    merged       = {**law, **updates}
    score_after  = sum(1 for f in KEY_FIELDS if merged.get(f))
    ai_added     = [AI_LABELS.get(f, f) for f in AI_FIELDS if f in updates and not law.get(f)]

    result["completeness_before"] = score_before
    result["completeness_after"]  = score_after
    result["ai_added"]            = ai_added

    return updates, result


# ── Rapport ───────────────────────────────────────────────────────────────────

def save_report(report_data: dict):
    """Sauvegarde le rapport JSON horodaté dans pipeline/reports/."""
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = reports_dir / f"enrich_report_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    log(f"\n[bold]📊 Rapport sauvegardé :[/] {path}")
    return path


# ── Point d'entrée ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="JuriThèque — Enrichissement des textes juridiques",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run",      action="store_true", help="Analyser sans écrire en base")
    parser.add_argument("--limit",        type=int,  default=None, metavar="N",  help="Nombre max de textes à traiter")
    parser.add_argument("--offset",       type=int,  default=0,    metavar="N",  help="Décalage de départ (pagination)")
    parser.add_argument("--id",           type=int,  default=None, metavar="ID", help="Traiter une seule loi (par ID)")
    parser.add_argument("--only-missing", action="store_true", help="Traiter seulement les textes sans résumé")
    parser.add_argument("--force",        action="store_true", help="Régénérer même si déjà rempli (ignore protection manuelle)")
    parser.add_argument("--no-ai",        action="store_true", help="Désactiver la génération IA (score + règles uniquement)")
    args = parser.parse_args()

    log("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log("[bold gold1]  JuriThèque — Enrichissement des textes      [/]")
    log("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")

    if args.dry_run:
        log("[yellow]⚠  MODE DRY-RUN — aucune écriture en base[/]")
    if args.no_ai:
        log("[yellow]⚠  MODE NO-AI — génération IA désactivée[/]")
    elif not ai_available():
        log("[yellow]⚠  Aucune clé IA trouvée — génération IA désactivée[/]")

    # ── Construire les params Supabase ────────────────────────────────────
    params = {
        "select": "id,number,title_fr,title_ar,type,status,date,domain_id,"
                  "language,content_fr,content_ar,excerpt_fr,excerpt_ar,"
                  "simple_summary_fr,simple_summary_ar,table_of_contents_fr,"
                  "summary_updated_manually,toc_updated_manually,"
                  "needs_human_review,is_publicly_indexable,canonical_slug,"
                  "seo_title_fr,seo_description_fr,important_articles",
        "order": "id.asc",
    }

    if args.id:
        params["id"] = f"eq.{args.id}"
    elif args.only_missing and not args.force:
        params["simple_summary_fr"] = "is.null"

    if args.limit:
        params["limit"] = str(args.limit)
    if args.offset:
        params["offset"] = str(args.offset)

    log(f"\n[dim]→ Récupération des textes depuis Supabase...[/]")
    laws = sb_get("laws", params)

    if not laws:
        log("[yellow]Aucun texte trouvé (vérifiez les filtres ou la connexion Supabase).[/]")
        sys.exit(0)

    log(f"[dim]→ {len(laws)} texte(s) à traiter[/]\n")

    # ── Traitement ────────────────────────────────────────────────────────
    use_ai = not args.no_ai and ai_available()
    report_items = []

    stats = {"total": len(laws), "updated": 0, "skipped": 0, "failed": 0,
             "needs_review": 0, "errors": []}

    for law in track(laws, description="Enrichissement…"):
        law_id = law["id"]
        try:
            updates, result = process_law(
                law,
                use_ai=use_ai,
                dry_run=args.dry_run,
                force=args.force,
            )

            if result.get("score") is not None:
                badge = (
                    "[green]✅ success[/]" if result["score"] >= 75 else
                    "[yellow]△ partial[/]" if result["score"] >= 45 else
                    "[red]✗ low[/]"
                )
                cb = result.get("completeness_before", 0)
                ca = result.get("completeness_after",  0)
                ai_added = result.get("ai_added", [])
                if ai_added:
                    ai_str = f"  [cyan]🤖 +{' +'.join(ai_added)}[/]"
                elif ca > cb:
                    ai_str = f"  [dim]+{ca - cb} champ(s) règles[/]"
                elif result["score"] < 30:
                    ai_str = "  [red]─ score<30 (IA ignorée)[/]"
                elif ca == len(["simple_summary_fr","simple_summary_ar","canonical_slug","table_of_contents_fr","seo_title_fr","seo_description_fr","legal_keywords","important_articles"]):
                    ai_str = "  [green]─ déjà complet[/]"
                else:
                    ai_str = "  [dim]─ rien ajouté[/]"
                completeness = (
                    f"[bold]{cb}→{ca}[/]" if ca > cb else f"[dim]{ca}/{len(['simple_summary_fr','simple_summary_ar','canonical_slug','table_of_contents_fr','seo_title_fr','seo_description_fr','legal_keywords','important_articles'])}[/]"
                )
                log(f"  #{law_id:>6}  conf={result['score']:3d}  complétude={completeness}  {badge}{ai_str}")

            if not args.dry_run and updates:
                ok = sb_patch("laws", {"id": f"eq.{law_id}"}, updates)
                if ok:
                    stats["updated"] += 1
                else:
                    stats["failed"] += 1
                    stats["errors"].append(law_id)
            elif args.dry_run:
                stats["updated"] += 1  # compté comme "aurait été mis à jour"

            if result.get("needs_review"):
                stats["needs_review"] += 1

            report_items.append({
                "id":      law_id,
                "score":   result.get("score"),
                "status":  result.get("ext_status"),
                "review":  result.get("needs_review"),
                "fields":  result.get("updated_fields", []),
            })

            # Petite pause pour éviter de surcharger l'API IA
            if use_ai and len(laws) > 1:
                time.sleep(0.8)

        except Exception as e:
            log_err(f"  #{law_id}: Erreur inattendue — {e}")
            stats["failed"] += 1
            stats["errors"].append(law_id)

    # ── Résumé final ──────────────────────────────────────────────────────
    log("\n[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log(f"[bold green]✅ Analysés      :[/] {stats['total']}")
    log(f"[bold blue]📝 Mis à jour    :[/] {stats['updated']}" + (" (DRY-RUN)" if args.dry_run else ""))
    log(f"[bold yellow]⚠  À vérifier   :[/] {stats['needs_review']}")
    log(f"[bold red]✗  Échecs        :[/] {stats['failed']}")
    if stats["errors"]:
        log(f"[red]IDs problématiques : {stats['errors']}[/]")

    # ── Rapport JSON ──────────────────────────────────────────────────────
    report_data = {
        "generated_at":  datetime.now(timezone.utc).isoformat(),
        "enrich_version": ENRICH_VERSION,
        "dry_run":       args.dry_run,
        "use_ai":        use_ai,
        "args": {
            "limit":        args.limit,
            "id":           args.id,
            "only_missing": args.only_missing,
            "force":        args.force,
        },
        "stats":   stats,
        "results": report_items,
    }
    save_report(report_data)


if __name__ == "__main__":
    main()
