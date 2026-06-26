"""Test de la recherche Adala par numéro exact."""
import requests, re, time
from bs4 import BeautifulSoup

BASE = "https://adala.justice.gov.ma"
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0", "Accept-Language": "ar,fr;q=0.8"})

def normalize_num(n):
    return re.sub(r"[\.\-\s]+", ".", n.strip().lower())

def search_adala_by_number(number: str, max_pages: int = 3):
    """Cherche un texte sur Adala par numéro exact → (title_ar, pdf_url) ou (None, None)."""
    norm = normalize_num(number)
    query = number.replace("-", ".").replace(" ", ".")

    for page in range(1, max_pages + 1):
        url = f"{BASE}/search?q={query}&page={page}"
        try:
            r = s.get(url, timeout=15)
            r.raise_for_status()
        except Exception as e:
            print(f"  Erreur page {page}: {e}")
            break

        soup = BeautifulSoup(r.text, "html.parser")
        cards_processed = set()

        for a_tag in soup.find_all("a", href=re.compile(r"/api/uploads/.*\.pdf")):
            card = a_tag.parent
            for _ in range(8):
                if card is None:
                    break
                if card.name == "div" and "group" in (card.get("class") or []):
                    break
                card = getattr(card, "parent", None)

            if card is None or id(card) in cards_processed:
                continue
            cards_processed.add(id(card))

            # Extraire le numéro de la carte
            card_number = ""
            for p_el in card.find_all("p"):
                txt = p_el.get_text(strip=True)
                if txt.startswith("رقم:"):
                    card_number = txt.replace("رقم:", "").strip()
                    break

            card_norm = normalize_num(card_number) if card_number else ""

            # Correspondance exacte ou contenue dans le titre
            a_pdf = card.find("a", href=re.compile(r"/api/uploads/.*\.pdf"))
            title_ar = a_pdf.get_text(strip=True) if a_pdf else ""
            pdf_href = a_pdf["href"] if a_pdf else ""

            # Match : numéro normalisé exact OU numéro dans le titre arabe
            is_match = (card_norm and card_norm == norm) or \
                       (query in (title_ar or "")) or \
                       (number.replace("-", ".") in (title_ar or ""))

            print(f"  p{page} n°={card_number:20} norm={card_norm:20} match={is_match}")
            if title_ar:
                print(f"       titre: {title_ar[:70]}")

            if is_match and pdf_href:
                pdf_url = BASE + pdf_href if pdf_href.startswith("/") else pdf_href
                return title_ar, pdf_url

        # Vérifier s'il y a une page suivante
        next_btn = soup.find("a", string=re.compile(r"التالي|suivant|next", re.I))
        if not next_btn:
            break
        time.sleep(1)

    return None, None

# ── Tests ────────────────────────────────────────────────────────────────────
for num in ["2.03.530", "2-03-530", "2-84-93", "2-22-431"]:
    print(f"\n{'='*70}")
    print(f"Recherche: {num}")
    print(f"{'='*70}")
    title, pdf = search_adala_by_number(num, max_pages=2)
    print(f"\n→ title_ar : {title}")
    print(f"→ pdf_url  : {pdf}")
