"""
JuriThèque — Assignation automatique des domaines juridiques (v2)
═══════════════════════════════════════════════════════════════════
Classe les lois sans domain_id ET reclasse les lois « administratif »
vers les 5 nouveaux domaines spécialisés.

Supporte le multi-domaine : une loi peut appartenir à plusieurs domaines
(domain_id = domaine primaire, domain_ids[] = tous les domaines).

Usage :
  python pipeline/assign_domains.py              # lois sans domaine seulement
  python pipeline/assign_domains.py --all        # inclure lois administratif
  python pipeline/assign_domains.py --dry-run    # simulation sans écriture
  python pipeline/assign_domains.py --limit 100  # tester sur 100 lois
  python pipeline/assign_domains.py --all --dry-run  # simulation complète

Domaines :
  civil · penal · commercial · administratif · travail
  fiscal · international · numerique · constitutionnel
  bancaire · finances_publiques
  transport · environnement · sante · energie · collectivites  ← NOUVEAUX
"""

import os, sys, re, json
from dotenv import load_dotenv
import httpx

try:
    from rich.console import Console
    from rich.table import Table
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
DRY_RUN    = "--dry-run" in sys.argv
RECLASSIFY = "--all" in sys.argv   # retraiter aussi les lois en "administratif"
LIMIT      = int(next((sys.argv[i+1] for i,a in enumerate(sys.argv) if a=="--limit"), 99999))

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

# ══════════════════════════════════════════════════════════════════════════════
# RÈGLES DE CLASSIFICATION — du plus spécifique au plus général
# Chaque règle est (domain_id, {fr: [...], ar: [...]})
# detect_domains() retourne TOUTES les correspondances (multi-domaine)
# ══════════════════════════════════════════════════════════════════════════════
DOMAIN_RULES = [

    # ── Domaines ultra-spécifiques (forte précision) ──────────────────────────

    ("constitutionnel", {
        "fr": [
            "cour constitutionnelle","conseil constitutionnel","constitution",
            "haute cour","droits de l'homme","droits fondamentaux",
            "liberté publique","libertés publiques","libertés fondamentales",
            "parlement","chambre des représentants","chambre des conseillers",
            "conseil supérieur du pouvoir judiciaire","cspj",
            "médiateur du royaume","conseil économique social",
            "instance nationale","haute autorité de la communication audiovisuelle",
            "hacp","conseil supérieur de l'enseignement",
            "commandeur des croyants",
            "parité et la lutte","autorité pour la parité","discrimination",
            "échéances législatives","élections législatives","élections communales",
            "commissions administratives locales","listes électorales",
        ],
        "ar": [
            "المحكمة الدستورية","الدستور","الحريات الأساسية","حقوق الإنسان",
            "مجلس النواب","مجلس المستشارين","البرلمان",
            "المجلس الأعلى للسلطة القضائية",
        ],
    }),

    ("international", {
        "fr": [
            "convention internationale","accord international","traité international",
            "extradition","coopération judiciaire internationale",
            "accord bilatéral","accord multilatéral","protocole d'accord",
            "organisation internationale","nations unies","onu","oit","oms","omc",
            "accord de pêche","coopération économique internationale",
            "aide au développement","prêt international",
            "banque mondiale","fmi","berd","bad","afd","pnud",
            "ambassade","consulat","mission diplomatique","consulaire",
            "visa","séjour étranger","immigration","ressortissant étranger",
            "accord douanier international","assistance mutuelle internationale",
            # Patterns élargis pour conventions non labellisées "internationale"
            "signée à rabat entre","signé à rabat entre","signée entre le gouvernement",
            "signé entre le gouvernement","entre le royaume du maroc et",
            "entre le maroc et","délimitation des frontières","frontières d'état",
            "recouvrement des aliments à l'étranger","légalisation des actes publics",
            "coopération militaire","coopération technique","centre africain",
            "centre international","marins réfugiés","réfugiés","convention de la haye",
            "convention n°1.","convention n°08.","convention n°41.",
            "politique migratoire","développement des ressources minérales",
            "statut du centre","addis-abeba","établissement entre le royaume",
        ],
        "ar": [
            "اتفاقية دولية","معاهدة دولية","التعاون الدولي","التسليم",
            "النقل البحري الدولي","الصيد البحري","السفارة","القنصلية",
            "التمويل الدولي","البنك الدولي",
            "المملكة المغربية و","اتفاقية","بروتوكول","معاهدة",
        ],
    }),

    # ── Transport (NOUVEAU) ──────────────────────────────────────────────────
    ("transport", {
        "fr": [
            "transport routier","transport en commun","transport de marchandises",
            "transport de voyageurs","transport ferroviaire","oncf","réseau ferré",
            "aviation civile","aéroport","onda","espace aérien","aéronef",
            "navigation aérienne","autorisation de vol",
            "marine marchande","port","portée portuaire","agence nationale des ports",
            "anp","marsa maroc","remorquage","pilotage portuaire",
            "logistique","plateforme logistique","zone logistique",
            "autoroute","route nationale","voirie","réseau routier",
            "permis de conduire","immatriculation","carte grise","véhicule",
            "code de la route","circulation routière","sécurité routière",
            "taxi","autocar","bus","transport urbain",
            "chemin de fer","voie ferrée","passage à niveau",
            "dangereux","matières dangereuses transport",
        ],
        "ar": [
            "النقل الطرقي","النقل الحضري","الطيران المدني","المطار",
            "الملاحة الجوية","الموانئ","البحرية التجارية","النقل بالسكة الحديدية",
            "اللوجستيك","الطريق السيار","قانون السير","رخصة السياقة",
            "السيارة","الحافلة","سيارة الأجرة","تسجيل المركبات",
        ],
    }),

    # ── Environnement (NOUVEAU) ───────────────────────────────────────────────
    ("environnement", {
        "fr": [
            "environnement","protection de l'environnement","impact environnemental",
            "étude d'impact","évaluation environnementale","audit environnemental",
            "pollution","pollution atmosphérique","pollution des eaux","pollution des sols",
            "déchets","gestion des déchets","déchets ménagers","déchets dangereux",
            "recyclage","mise en décharge","incinération",
            "eau","ressources en eau","hydraulique","barrage","irrigation",
            "assainissement","station d'épuration","réseau d'assainissement",
            "oued","nappe phréatique","eau potable","qualité de l'eau",
            "forêt","reboisement","domaine forestier","exploitation forestière",
            "chasse","faune sauvage","aires protégées","parc national","réserve",
            "biodiversité","espèces protégées","flore","écosystème",
            "littorale","côtière","mer","zone maritime",
            "changements climatiques","effet de serre","carbone","empreinte carbone",
        ],
        "ar": [
            "البيئة","حماية البيئة","التأثير البيئي","التلوث",
            "النفايات","إدارة النفايات","المياه","الموارد المائية",
            "السدود","السقي","الصرف الصحي","الغابات","التشجير",
            "الصيد البري","الحيوانات البرية","المناطق المحمية","الحديقة الوطنية",
            "التنوع البيولوجي","التغيرات المناخية","الساحل",
        ],
    }),

    # ── Santé (NOUVEAU) ───────────────────────────────────────────────────────
    ("sante", {
        "fr": [
            "santé","santé publique","santé mentale","sécurité sanitaire",
            "hôpital","clinique","établissement de soins","centre hospitalier",
            "chu","chu ibn rochd","chu avicenne","hospice",
            "médecin","médecine","exercice de la médecine","ordre des médecins",
            "pharmacie","pharmacien","médicament","produit pharmaceutique",
            "dispositif médical","produit de santé","vaccin","vaccination",
            "infirmier","sage-femme","kinésithérapeute","aide-soignant",
            "professions de santé","professions médicales","professions paramédicales",
            "couverture médicale","assurance maladie","ramed","amc","amo",
            "caisse nationale des organismes de prévoyance sociale","cnops",
            "caisse nationale de sécurité sociale","cnss maladie",
            "épidémie","pandémie","quarantaine","veille sanitaire",
            "sang","don du sang","transfusion","organes","transplantation",
            "addiction","stupéfiants médicaux","psychotropes médicaux",
        ],
        "ar": [
            "الصحة العامة","المستشفى","العيادة","الطبيب","الطب",
            "الصيدلي","الصيدلية","الدواء","المستلزمات الطبية",
            "التمريض","القابلة","التغطية الصحية","التأمين الصحي",
            "الوباء","الحجر الصحي","الدم","نقل الأعضاء","الإدمان",
            "المهن الطبية","المهن شبه الطبية",
        ],
    }),

    # ── Énergie & Mines (NOUVEAU) ─────────────────────────────────────────────
    ("energie", {
        "fr": [
            "énergie","énergie électrique","électricité","réseau électrique",
            "one","onee","production d'électricité","distribution d'électricité",
            "énergie renouvelable","éolien","solaire","photovoltaïque","masen",
            "hydrocarbures","pétrole","gaz naturel","raffinerie","pipeline",
            "exploration pétrolière","concession pétrolière",
            "mine","mines","carrière","exploitation minière","minerai",
            "office national des hydrocarbures","onhym",
            "office national de l'électricité","redevance minière",
            "efficacité énergétique","maîtrise de l'énergie",
            "biomasse","géothermie","hydroélectrique","cogénération",
            "tarif d'électricité","réseau de transport d'énergie",
        ],
        "ar": [
            "الطاقة","الكهرباء","الطاقة الكهربائية","شبكة الكهرباء",
            "الطاقات المتجددة","الطاقة الريحية","الطاقة الشمسية",
            "المحروقات","البترول","الغاز الطبيعي","المنجم","المناجم",
            "الاستكشاف المعدني","الرسوم المنجمية","الكفاءة الطاقية",
        ],
    }),

    # ── Collectivités Territoriales (NOUVEAU) ────────────────────────────────
    ("collectivites", {
        "fr": [
            "collectivité territoriale","collectivités territoriales",
            "conseil régional","conseil préfectoral","conseil provincial",
            "conseil communal","commune urbaine","commune rurale",
            "commune","communes","charte communale",
            "loi organique 111-14","loi organique 112-14","loi organique 113-14",
            "loc 111-14","loc 112-14","loc 113-14",
            "région","régions","préfecture","province",
            "régionalisation avancée","décentralisation",
            "élu local","élus locaux","mandat communal","mandat régional",
            "président du conseil","vice-président du conseil",
            "révocation élu","éviction élu","exclusion élu","déchéance mandat",
            "budget communal","finances locales","dotations de l'état",
            "taxe professionnelle communale","taxe d'habitation communale",
            "service communal","plan de développement communal",
            "pdc","plan de développement régional",
            "wilaya","wali","gouverneur","pacha","caïd",
            "tutelle administrative","contrôle de légalité",
            "autonomie locale","libre administration",
            "agence urbaine","syndicat de communes",
            "groupement de collectivités","fond de péréquation",
        ],
        "ar": [
            "الجماعات الترابية","الجماعة الترابية",
            "المجلس الجماعي","مجلس الجماعة","المجلس الإقليمي",
            "المجلس الجهوي","مجلس الجهة","الجهة",
            "الجماعة الحضرية","الجماعة القروية",
            "الميثاق الجماعي","اللاتمركز","اللامركزية",
            "المنتخب المحلي","رئيس المجلس",
            "عزل المنتخب","إقالة المنتخب",
            "الميزانية الجماعية","المالية المحلية",
            "التنمية الترابية","مخطط التنمية الجهوية",
            "الوالي","العامل","الباشا","القائد",
            "القانون التنظيمي 111-14","القانون التنظيمي 112-14","القانون التنظيمي 113-14",
        ],
    }),

    # ── Domaines financiers ───────────────────────────────────────────────────

    ("fiscal", {
        "fr": [
            "impôt","taxe sur la valeur ajoutée","tva","impôt sur les sociétés",
            "impôt sur le revenu","contribution sociale de solidarité",
            "code général des impôts","cgi","douane","droit de douane",
            "accise","redevance fiscale","prélèvement fiscal","exonération fiscale",
            "franchise fiscale","déclaration fiscale","assiette fiscale",
            "contrôle fiscal","vérification fiscale","redressement fiscal",
            "remboursement fiscal","crédit d'impôt","amortissement fiscal",
            "taxe professionnelle","taxe d'habitation","taxe de services communaux",
        ],
        "ar": [
            "الضريبة على القيمة المضافة","الضريبة على الشركات",
            "الضريبة على الدخل","المدونة العامة للضرائب","الجمارك",
            "رسم جمركي","الإعفاء الضريبي","التصريح الضريبي",
        ],
    }),

    ("finances_publiques", {
        "fr": [
            "loi de finances","budget général de l'état","crédit supplémentaire",
            "virement de crédits","ouverture de crédits","rectificative budgétaire",
            "comptabilité de l'état","trésorerie générale du royaume","payeur",
            "ordonnateur principal","contrôleur d'état","cour des comptes",
            "marchés publics","cahier des charges","appel d'offres",
            "délégation de signature budgétaire",
            "emprunt intérieur","emprunt extérieur","trésor public",
            "loi organique relative à la loi de finances","lolf",
        ],
        "ar": [
            "قانون المالية","الميزانية العامة للدولة","المحاسبة العمومية",
            "المجلس الأعلى للحسابات","الخزينة العامة للمملكة",
            "الصفقات العمومية","طلب العروض",
        ],
    }),

    ("bancaire", {
        "fr": [
            "établissement de crédit","bank al-maghrib","bkam","organisme bancaire",
            "société de financement","microfinance","fonds propres réglementaires",
            "ratio de solvabilité","liquidité bancaire","règlement interbancaire",
            "assurance","société d'assurance","réassurance","mutuelles d'assurance",
            "bourse des valeurs","valeurs mobilières","marché financier","opcvm",
            "titrisation","sukuk","finance islamique","banque participative",
            "service de paiement","monnaie électronique","fintech",
        ],
        "ar": [
            "بنك المغرب","مؤسسة الائتمان","التأمين","إعادة التأمين",
            "بورصة القيم","الأوراق المالية","التمويل التشاركي","الصكوك",
            "الخدمات المالية الرقمية",
        ],
    }),

    # ── Droit des affaires ────────────────────────────────────────────────────

    ("commercial", {
        "fr": [
            "code de commerce","société anonyme","société à responsabilité limitée",
            "sarl","société en nom collectif","snc","société en commandite",
            "fonds de commerce","bail commercial","locataire commercial",
            "registre du commerce","tribunal de commerce","redressement judiciaire",
            "liquidation judiciaire","procédure collective","insolvabilité",
            "acte de commerce","commerçant","artisan","franchise commerciale",
            "marque commerciale","brevet d'invention","propriété intellectuelle",
            "propriété industrielle","concurrence déloyale","pratiques anticoncurrentielles",
            "protection du consommateur","publicité commerciale",
            "investissement étranger","zone franche","zone d'accélération industrielle",
            "exportation","importation","commerce extérieur",
            "cinéma","audiovisuel","médias","presse","publication",
            "loterie nationale","jeux de hasard","paris sportifs",
        ],
        "ar": [
            "مدونة التجارة","الشركة المجهولة الاسم","الشركة ذات المسؤولية المحدودة",
            "سجل التجارة","المحكمة التجارية","التسوية القضائية","الإفلاس",
            "العلامة التجارية","براءة الاختراع","الملكية الفكرية",
            "الاستثمار الأجنبي","المنطقة الحرة","الاستيراد والتصدير",
        ],
    }),

    ("travail", {
        "fr": [
            "code du travail","contrat de travail","salarié","employeur",
            "licenciement","rupture abusive","préavis","indemnité de licenciement",
            "syndicat","grève","conflit collectif du travail","négociation collective",
            "convention collective","inspection du travail","anapec",
            "retraite","pension de retraite","pension d'invalidité","pension vieillesse",
            "accidents du travail","maladies professionnelles",
            "durée du travail","congés payés","repos hebdomadaire",
            "salaire minimum interprofessionnel garanti","smig","smag",
            "formation professionnelle","apprentissage","contrat de stage",
            "travailleurs immigrés","travailleurs domestiques",
            "égalité professionnelle","discrimination au travail",
            "horaires de travail","jours fériés","jours chômés","repos légal",
        ],
        "ar": [
            "مدونة الشغل","عقد الشغل","الأجير","المشغل","الفصل من العمل",
            "النقابة","الإضراب","الضمان الاجتماعي","التقاعد",
            "التكوين المهني","حوادث الشغل","الأمراض المهنية",
            "الأجر الأدنى","التمييز في الشغل",
        ],
    }),

    ("penal", {
        "fr": [
            "code pénal","infraction pénale","crime","délit pénal","contravention",
            "peine d'emprisonnement","amende pénale","récidive",
            "procédure pénale","instruction judiciaire","juge d'instruction",
            "ministère public","parquet général","procureur du roi","garde à vue",
            "détention provisoire","jugement pénal","tribunal pénal",
            "cour d'appel","cour criminelle","assises criminelles",
            "corruption","concussion","détournement de fonds","trafic d'influence",
            "terrorisme","financement du terrorisme","blanchiment de capitaux",
            "stupéfiants","substances psychotropes","trafic de drogue",
            "traite des êtres humains","traite des personnes","exploitation",
            "cybercriminalité","fraude informatique","escroquerie",
            "faux et usage de faux","abus de confiance",
            "usurpation de la profession","usurpation de titre","usurpation de fonction",
        ],
        "ar": [
            "القانون الجنائي","العقوبة الجنائية","الجريمة","السجن","المسطرة الجنائية",
            "النيابة العامة","الاعتقال الاحتياطي","الإرهاب","الفساد",
            "غسل الأموال","المخدرات","الاتجار بالبشر","جرائم الإنترنت",
        ],
    }),

    ("numerique", {
        "fr": [
            "numérique","transformation digitale","données personnelles",
            "protection des données personnelles","cndp","vie privée",
            "cybersécurité","sécurité des systèmes d'information","dircsi",
            "signature électronique","cachet électronique","certification électronique",
            "commerce électronique","transaction électronique","paiement électronique",
            "services numériques","administration électronique","e-gouvernement",
            "télécommunications","téléphonie mobile","internet haut débit","fibre optique",
            "anrt","fréquences radioélectriques","opérateur télécom",
            "intelligence artificielle","traitement automatisé","algorithme",
            "logiciel","licence logicielle","open source","cloud computing",
        ],
        "ar": [
            "الرقمي","التحول الرقمي","البيانات الشخصية","الأمن المعلوماتي",
            "التوقيع الإلكتروني","التجارة الإلكترونية","الإدارة الإلكترونية",
            "الاتصالات","الهاتف المحمول","الإنترنت","الذكاء الاصطناعي",
        ],
    }),

    ("civil", {
        "fr": [
            "code civil","droit des obligations","contrat civil","obligation civile",
            "responsabilité civile","dommages et intérêts",
            "famille","mariage","divorce","séparation","répudiation",
            "moudawwana","code de la famille","kafala",
            "filiation","garde d'enfant","tutelle légale","curatelle",
            "succession","héritage","testament","legs","donation",
            "propriété immobilière","immeuble","servitude","hypothèque",
            "usufruit","bail d'habitation","location","loyer","expulsion",
            "état civil","acte de naissance","acte de décès","acte d'état civil",
            "nationalité marocaine","naturalisation","apatride",
            "handicap","personne en situation de handicap",
            "aide sociale","assistance sociale",
        ],
        "ar": [
            "مدونة الأسرة","الزواج","الطلاق","الحضانة","النسب",
            "الإرث","الوصية","الوصاية","الأملاك العقارية","عقد الكراء",
            "الجنسية","الحالة المدنية","شهادة الميلاد","الوفاة",
            "الالتزامات المدنية","المسؤولية المدنية","التعويض",
        ],
    }),

    # ── Administratif (domaine par défaut — doit rester en dernier) ───────────
    ("administratif", {
        "fr": [
            "décret","arrêté","dahir","circulaire","instruction administrative",
            "organigramme","organisation","attributions","compétences",
            "ministère","direction générale","service","agence","établissement public",
            "office","société d'état","collectivité territoriale",
            "commune","région","province","préfecture","cercle",
            "fonction publique","fonctionnaire","agent public",
            "concours","recrutement","nomination","avancement",
            "discipline","sanction administrative",
            "urbanisme","construction","permis de construire",
            "éducation","enseignement","école","université",
            "agriculture","élevage","pêche","coopérative",
        ],
        "ar": [
            "مرسوم","وزارة","إدارة","مصلحة","وكالة","مؤسسة عمومية",
            "الوظيفة العمومية","التعيين","الترقية","التأديب",
            "التعمير","التعليم","الزراعة","الجهة","الإقليم","العمالة",
        ],
    }),
]

# ══════════════════════════════════════════════════════════════════════════════
# Domaines "spéciaux" qui peuvent être secondaires de administratif
# Si une loi est dans administratif ET correspond à un de ces domaines,
# on ajoute le domaine spécialisé en secondaire (ou en primaire si --all)
NEW_SPECIAL_DOMAINS = {"transport", "environnement", "sante", "energie", "collectivites"}
# ══════════════════════════════════════════════════════════════════════════════


def detect_domains(title_fr: str, title_ar: str, tags: list) -> list[str]:
    """
    Retourne la liste de TOUS les domaines correspondants (multi-domaine).
    Le premier domaine dans la liste est le domaine primaire.
    """
    text = " ".join(filter(None, [
        str(title_fr or "").lower(),
        str(title_ar or "").lower(),
        " ".join(tags or []).lower(),
    ]))

    matched = []
    for domain, rules in DOMAIN_RULES:
        found = False
        for kw in rules.get("fr", []):
            if kw.lower() in text:
                found = True
                break
        if not found:
            for kw in rules.get("ar", []):
                if kw in text:
                    found = True
                    break
        if found:
            matched.append(domain)

    # Dédupliquer en gardant l'ordre
    seen = set()
    unique = []
    for d in matched:
        if d not in seen:
            seen.add(d)
            unique.append(d)

    return unique  # premier = primaire, reste = secondaires


def detect_domain(title_fr: str, title_ar: str, tags: list) -> str | None:
    """Rétrocompat : retourne le domaine primaire uniquement."""
    domains = detect_domains(title_fr, title_ar, tags)
    return domains[0] if domains else None


# ══════════════════════════════════════════════════════════════════════════════
def fetch_laws(domain_filter: str | None = None) -> list[dict]:
    """
    Récupère les lois à traiter.
    - domain_filter=None → lois sans domain_id
    - domain_filter='administratif' → lois classées administratif (pour reclassification)
    """
    all_laws = []
    offset = 0
    while True:
        params = {
            "select":  "id,title_fr,title_ar,type,tags,domain_id,domain_ids",
            "order":   "id.asc",
            "limit":   "1000",
            "offset":  str(offset),
        }
        if domain_filter is None:
            params["domain_id"] = "is.null"
        else:
            params["domain_id"] = f"eq.{domain_filter}"

        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/laws",
            headers={**HEADERS, "Prefer": ""},
            params=params,
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
    return all_laws[:LIMIT]


def update_law_domains(law_id: int, domain_id: str, domain_ids: list[str]):
    """Met à jour domain_id (primaire) et domain_ids (tous les domaines)."""
    r = httpx.patch(
        f"{SUPABASE_URL}/rest/v1/laws",
        headers=HEADERS,
        params={"id": f"eq.{law_id}"},
        json={"domain_id": domain_id, "domain_ids": domain_ids},
        timeout=30,
    )
    r.raise_for_status()


# ══════════════════════════════════════════════════════════════════════════════
def process_batch(laws: list[dict], source_label: str) -> tuple[dict, list]:
    """Traite un lot de lois. Retourne (assigned_counts, undetected_list)."""
    assigned   = {}
    undetected = []

    for law in laws:
        domains = detect_domains(
            law.get("title_fr"),
            law.get("title_ar"),
            law.get("tags") or [],
        )

        if not domains:
            # Fallback 1 : type "Convention" → international
            law_type = (law.get("type") or "").strip()
            title_fr = (law.get("title_fr") or "").lower()
            if law_type == "Convention":
                domains = ["international"]
            # Fallback 2 : titre "Journal officiel" → administratif (BO brut)
            elif "journal officiel" in title_fr:
                domains = ["administratif"]
            # Fallback 3 : "accord entre" / "protocole" → international
            elif any(kw in title_fr for kw in ["accord entre", "protocole relatif", "accord maroc", "accord du maroc"]):
                domains = ["international"]
            # Fallback 4 : professions judiciaires réglementées → administratif
            elif any(kw in title_fr for kw in [
                "traducteur", "notaire", "huissier", "avocat", "expert",
                "jours fériés", "jours chômés", "liste des", "fonds de garantie",
                "commissions", "désignation des", "opérations de conservation",
                "durée de validité", "animaux domestiques", "animaux",
            ]):
                domains = ["administratif"]
            # Fallback 5 : loi/dahir sans titre informatif → administratif par défaut
            elif law_type in ("Loi", "Dahir", "Décret", "Arrêté", "Circulaire", "Autre"):
                domains = ["administratif"]
            else:
                undetected.append(law)
                continue

        primary = domains[0]

        # Pour les lois déjà dans "administratif" : on ne reclasse que si
        # un domaine spécialisé est trouvé en premier
        if source_label == "administratif":
            specialized = [d for d in domains if d in NEW_SPECIAL_DOMAINS]
            if not specialized:
                # Reste administratif, mais on peut ajouter un domaine secondaire
                # si administratif est le seul résultat → skip
                continue
            # Domaine primaire = premier domaine spécialisé trouvé
            primary = specialized[0]
            # domain_ids inclut le spécialisé + administratif en secondaire
            all_domains = [primary] + [d for d in domains if d != primary]
            # Assure administratif reste dans la liste (domaine secondaire)
            if "administratif" not in all_domains:
                all_domains.append("administratif")
        else:
            all_domains = domains

        # Dédupliquer
        seen = set()
        final_domains = []
        for d in all_domains:
            if d not in seen:
                seen.add(d)
                final_domains.append(d)

        assigned[primary] = assigned.get(primary, 0) + 1

        if not DRY_RUN:
            try:
                update_law_domains(law["id"], primary, final_domains)
            except Exception as e:
                log(f"[red]✗ #{law['id']}: {e}[/]")

    return assigned, undetected


# ══════════════════════════════════════════════════════════════════════════════
def main():
    log("\n[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]")
    log("[bold gold1]  JuriThèque — Assignation des domaines v2      [/]")
    log("[bold gold1]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]\n")

    if DRY_RUN:
        log("[yellow]⚠  MODE DRY-RUN — aucune écriture en base[/]\n")
    if RECLASSIFY:
        log("[cyan]ℹ  Mode --all : reclassification des lois 'administratif' incluse[/]\n")

    total_assigned = {}
    all_undetected = []

    # ── Phase 1 : Lois sans domaine ───────────────────────────────────────────
    log("[dim]Phase 1 — Lois sans domain_id...[/]")
    laws_null = fetch_laws(domain_filter=None)
    log(f"[bold]{len(laws_null)} lois sans domaine à traiter[/]")

    assigned1, undetected1 = process_batch(laws_null, source_label="null")
    for k, v in assigned1.items():
        total_assigned[k] = total_assigned.get(k, 0) + v
    all_undetected.extend(undetected1)

    # ── Phase 2 : Reclassification depuis administratif (si --all) ────────────
    if RECLASSIFY:
        log(f"\n[dim]Phase 2 — Reclassification depuis 'administratif'...[/]")
        laws_admin = fetch_laws(domain_filter="administratif")
        log(f"[bold]{len(laws_admin)} lois 'administratif' à analyser[/]")

        assigned2, _ = process_batch(laws_admin, source_label="administratif")
        for k, v in assigned2.items():
            total_assigned[k] = total_assigned.get(k, 0) + v
        log(f"[green]→ {sum(assigned2.values())} lois reclassées depuis administratif[/]")

    # ── Résumé ────────────────────────────────────────────────────────────────
    log(f"\n[bold green]━━━ Résumé ━━━[/]")
    log(f"✅ Domaines assignés : [bold green]{sum(total_assigned.values())}[/]")
    log(f"❓ Non classifiés   : [yellow]{len(all_undetected)}[/]\n")

    log("[bold]Répartition :[/]")
    for domain, count in sorted(total_assigned.items(), key=lambda x: -x[1]):
        bar = "█" * min(count // 5, 40)
        log(f"  [cyan]{domain:<22}[/] {bar} [bold]{count}[/]")

    if all_undetected:
        log(f"\n[yellow]━━━ {len(all_undetected)} lois non classifiées (exemples) ━━━[/]")
        for law in all_undetected[:20]:
            t = law.get("title_fr") or law.get("title_ar") or "???"
            log(f"  [dim]#{law['id']} [{law.get('type','?')}] {str(t)[:80]}[/]")

        os.makedirs("pipeline/logs", exist_ok=True)
        out_path = "pipeline/logs/undetected_domains.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(all_undetected, f, ensure_ascii=False, indent=2)
        log(f"\n[dim]Liste complète sauvegardée dans {out_path}[/]")

    log("\n[bold green]✓ Terminé.[/]")


if __name__ == "__main__":
    main()
