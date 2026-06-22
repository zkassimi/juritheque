/**
 * Synonymes de recherche — JuriThèque
 * Permet de trouver les mêmes lois via Darija, abréviations, variantes AR/FR.
 * Chaque clé est normalisée en minuscules sans accents.
 * La valeur est un tableau de termes additionnels injectés dans la requête.
 */

const RAW_SYNONYMS = {
  // ── Codes fondamentaux ──────────────────────────────────────────────────────
  'moudawana':          ['famille', 'أسرة', 'مدونة الأسرة'],
  'lmoudawana':         ['famille', 'أسرة', 'مدونة الأسرة'],
  'code famille':       ['moudawana', 'أسرة', 'مدونة الأسرة'],
  'مدونة الأسرة':       ['famille', 'moudawana'],
  'قانون الأسرة':       ['famille', 'moudawana'],

  'coc':                ['obligations', 'contrats', 'الالتزامات', 'العقود'],
  'dahir obligations':  ['obligations', 'contrats', 'الالتزامات'],
  'الالتزامات والعقود': ['obligations', 'contrats', 'coc'],

  'cpc':                ['procédure civile', 'مسطرة مدنية'],
  'msatara madaniya':   ['procédure civile', 'مسطرة مدنية'],
  'مسطرة مدنية':        ['procédure civile', 'cpc'],

  'cpp':                ['procédure pénale', 'مسطرة جنائية'],
  'msatara jina2iya':   ['procédure pénale', 'مسطرة جنائية'],
  'مسطرة جنائية':       ['procédure pénale', 'cpp'],

  'code pénal':         ['جنائي', 'قانون جنائي', 'penal'],
  'قانون جنائي':        ['pénal', 'code pénal', 'penal'],

  // ── Travail — Darija réelle : 3=ع, 9=ق ─────────────────────────────────────
  'l3amal':             ['travail', 'شغل', 'مدونة الشغل'],   // le plus cherché
  'lkhidma':            ['travail', 'شغل', 'مدونة الشغل'],   // "le boulot" en Darija
  'chghol':             ['travail', 'شغل', 'مدونة الشغل'],
  'shghol':             ['travail', 'شغل', 'مدونة الشغل'],
  'code travail':       ['شغل', 'مدونة الشغل', 'travail', '65-99'],
  'شغل':                ['travail', 'code du travail', 'مدونة الشغل'],
  'مدونة الشغل':        ['travail', 'code du travail', '65-99'],
  'fasl':               ['licenciement', 'فصل', 'travail'],  // "fasl" = licenciement
  'lfasl':              ['licenciement', 'فصل', 'travail'],
  'licenciement':       ['فصل', 'طرد', 'إنهاء عقد العمل', 'travail'],
  'طرد من العمل':       ['licenciement', 'فصل', 'travail'],

  // ── Commerce & Sociétés — Darija : sharika, lbay3 ──────────────────────────
  'code commerce':      ['تجارة', 'مدونة التجارة', '15-95'],
  'مدونة التجارة':      ['commerce', 'code de commerce', '15-95'],
  'sarl':               ['société responsabilité limitée', 'شركة ذات مسؤولية', 'société', '5-96'],
  'sharika':            ['société', 'شركة', 'commerce'],     // orthographe courante
  'charika':            ['société', 'شركة', 'commerce'],
  'lcharika':           ['société', 'شركة', 'commerce'],
  'شركة':               ['société', 'commerce', 'sarl'],
  'sa':                 ['société anonyme', 'شركة مساهمة', '17-95'],
  '3qod':               ['contrats', 'عقود', 'obligations'],  // عقود
  'l3qod':              ['contrats', 'عقود', 'obligations'],
  'عقد':                ['contrat', 'obligations', 'commerce'],

  // ── Marchés publics — Darija : safa9at ─────────────────────────────────────
  'marchés publics':    ['صفقات عمومية', 'صفقات', '2-22-431'],
  'safa9at':            ['marchés publics', 'صفقات عمومية', '2-22-431'], // 9=ق
  'safakat':            ['marchés publics', 'صفقات عمومية', '2-22-431'],
  'sfa9at':             ['marchés publics', 'صفقات عمومية'],
  'صفقات عمومية':       ['marchés publics', '2-22-431'],
  'صفقات':              ['marchés publics', 'صفقات عمومية'],

  // ── Collectivités territoriales — Darija : jma3a ───────────────────────────
  'collectivites':      ['communes', 'régions', 'جماعات', 'جماعات ترابية', '113-14'],
  'jma3a':              ['commune', 'collectivités', 'جماعة ترابية'],  // Darija courant
  'jama3at':            ['collectivités', 'communes', 'جماعات ترابية'],
  'جماعات ترابية':      ['collectivités territoriales', 'communes', 'régions'],
  'commune':            ['جماعة', 'collectivités', '113-14'],
  'region':             ['جهة', 'collectivités', '111-14'],

  // ── Foncier & Urbanisme — Darija : 3qar, lmlak, rkhsa ─────────────────────
  'immobilier':         ['foncier', 'عقار', 'عقاري', 'immatriculation'],
  '3qar':               ['immobilier', 'عقار', 'foncier'],   // عقار
  'l3qar':              ['immobilier', 'عقار', 'foncier'],
  'عقار':               ['immobilier', 'foncier', 'urbanisme'],
  'lmlak':              ['propriété', 'ملكية', 'foncier'],   // الملك
  'lmelk':              ['propriété', 'ملكية', 'foncier'],
  'immatriculation':    ['foncier', 'تحفيظ عقاري', 'عقار'],
  'tahfid':             ['immatriculation', 'تحفيظ', 'عقار'],
  'urbanisme':          ['تعمير', 'بناء', '12-90'],
  'ta3mir':             ['urbanisme', 'تعمير', 'construction'],
  'تعمير':              ['urbanisme', 'construction', '12-90'],
  'rkhsa':              ['permis', 'رخصة', 'urbanisme'],     // رخصة
  'rkhsat lbina':       ['permis construire', 'رخصة البناء', 'urbanisme'],
  'permis construire':  ['بناء', 'رخصة البناء', 'urbanisme'],

  // ── Fiscalité — Darija : dara2ib, lmakhzen ─────────────────────────────────
  'cgi':                ['impôts', 'fiscalité', 'المدونة العامة للضرائب', 'taxe'],
  'is':                 ['impôt société', 'impôts', 'fiscalité', 'taxe'],
  'tva':                ['taxe valeur ajoutée', 'ضريبة', 'fiscalité'],
  'dara2ib':            ['impôts', 'ضريبة', 'fiscalité'],    // ضرائب — le plus cherché
  'ldara2ib':           ['impôts', 'ضريبة', 'fiscalité'],
  'dara9ib':            ['impôts', 'ضريبة', 'fiscalité'],    // variante avec 9
  'ضريبة':              ['impôts', 'fiscalité', 'cgi'],
  'المدونة العامة للضرائب': ['impôts', 'fiscalité', 'cgi', 'taxe'],

  // ── Famille & Personnes — Darija : t-talaq, lkhol3, lhaddana ──────────────
  'divorce':            ['طلاق', 'خلع', 'شقاق', 'talaq', 'famille'],
  'ttalaq':             ['divorce', 'طلاق', 'famille'],      // "t-talaq"
  'talaq':              ['divorce', 'طلاق', 'famille'],
  'lkhol3':             ['divorce', 'خلع', 'famille'],       // الخلع
  'khol3':              ['divorce', 'خلع', 'famille'],
  'chi9a9':             ['divorce', 'شقاق', 'famille'],      // الشقاق avec 9
  'shiqaq':             ['divorce', 'شقاق', 'famille'],
  'طلاق':               ['divorce', 'famille', 'مدونة الأسرة'],
  'lhaddana':           ['garde', 'حضانة', 'enfant', 'famille'],
  'hadana':             ['garde', 'حضانة', 'enfant', 'famille'],
  'حضانة':              ['garde', 'famille', 'hadana'],
  'lnafaqa':            ['pension alimentaire', 'نفقة', 'famille'],
  'nafaqa':             ['pension alimentaire', 'نفقة', 'famille'],
  'نفقة':               ['pension', 'famille', 'nafaqa'],
  'lmiras':             ['héritage', 'succession', 'ميراث', 'إرث'],  // الميراث
  'miras':              ['héritage', 'succession', 'ميراث', 'إرث'],
  'ميراث':              ['héritage', 'succession', 'miras'],
  'إرث':                ['héritage', 'succession', 'miras'],
  'zawaj':              ['mariage', 'زواج', 'famille'],
  'lzwaj':              ['mariage', 'زواج', 'famille'],
  'زواج':               ['mariage', 'zawaj', 'famille'],

  // ── Justice & Procédure — Darija : lha9em, lma7kama ───────────────────────
  'mahkama':            ['tribunal', 'محكمة', 'justice'],
  'lma7kama':           ['tribunal', 'محكمة', 'justice'],
  'محكمة':              ['tribunal', 'justice', 'procédure'],
  'da3wa':              ['action judiciaire', 'دعوى', 'procédure civile'],
  'lda3wa':             ['action judiciaire', 'دعوى', 'procédure civile'],
  'دعوى':               ['action judiciaire', 'procédure civile'],
  '9adaa':              ['justice', 'قضاء', 'tribunal'],     // القضاء avec 9
  'lqadaa':             ['justice', 'قضاء', 'tribunal'],

  // ── Données personnelles & Numérique ───────────────────────────────────────
  'rgpd':               ['données personnelles', 'معطيات شخصية', '09-08', 'cndp'],
  'cndp':               ['données personnelles', 'معطيات شخصية', '09-08'],
  'données personnelles': ['معطيات شخصية', '09-08', 'rgpd', 'cndp'],
  'معطيات شخصية':       ['données personnelles', '09-08', 'cndp'],

  // ── Finances publiques ──────────────────────────────────────────────────────
  'lof':                ['loi organique finances', 'finances publiques', '130-13'],
  'loi finances':       ['ميزانية', 'مالية عمومية', 'budget'],
  'ميزانية':            ['budget', 'loi de finances', 'مالية عمومية'],

  // ── Justice & Professions — Darija : mouhami, mwathiq, 3adoul ─────────────
  'avocat':             ['محامي', 'محاماة', 'barreau'],
  'mouhami':            ['avocat', 'محامي', 'barreau'],       // orthographe cherchée
  'mouhamine':          ['avocat', 'محامي', 'barreau'],       // pluriel
  'محامي':              ['avocat', 'barreau', 'موثق'],
  'notaire':            ['موثق', 'توثيق', 'عدل'],
  'mwathiq':            ['notaire', 'موثق', 'توثيق'],         // موثق — Darija
  'muwathiq':           ['notaire', 'موثق', 'توثيق'],
  'عدل':                ['adoul', 'notaire', 'توثيق'],
  'adoul':              ['عدل', 'notaire', 'توثيق'],

  // ── Association & Liberté — Darija : jam3iya ───────────────────────────────
  'association':        ['جمعية', 'dahir 1958', 'liberté'],
  'jam3iya':            ['association', 'جمعية'],
  'ljam3iya':           ['association', 'جمعية'],
  'جمعية':              ['association', 'dahir 1958'],
  'presse':             ['صحافة', 'journal', 'médias'],
  'saha9a':             ['presse', 'صحافة', 'médias'],        // الصحافة avec 9
  'sahafa':             ['presse', 'صحافة', 'médias'],

  // ── Environnement & Énergie — Darija : lma, ta9a ───────────────────────────
  'eau':                ['ماء', 'hydraulique', '36-15'],
  'lma':                ['eau', 'ماء', 'hydraulique'],        // "lma" = l'eau en Darija
  'ماء':                ['eau', 'hydraulique', '36-15'],
  'énergie':            ['طاقة', 'électricité', 'renouvelable'],
  'ta9a':               ['énergie', 'طاقة', 'électricité'],   // طاقة avec 9
  'ta9at':              ['énergie', 'طاقة', 'électricité'],
  'طاقة':               ['énergie', 'électricité', 'renouvelable'],

  // ── MRE ─────────────────────────────────────────────────────────────────────
  'mre':                ['marocains résidant étranger', 'diaspora', 'expatriés'],
  'blad':               ['maroc', 'national', 'pays'],        // "blad" = le pays
  'maghreb':            ['maroc', 'maghreb', 'international'],
}

// ── Normalisation ────────────────────────────────────────────────────────────

function normalize(str) {
  return str
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')  // supprimer diacritiques latins
    .trim()
}

// Index normalisé (calculé une fois au chargement)
const SYNONYMS_INDEX = {}
for (const [key, values] of Object.entries(RAW_SYNONYMS)) {
  SYNONYMS_INDEX[normalize(key)] = values
}

/**
 * expandQuery(query) → string[]
 * Retourne un tableau de termes de recherche (original + synonymes).
 * Utilisé avant l'envoi à Supabase pour élargir la recherche.
 *
 * Exemple :
 *   expandQuery("moudawana") → ["moudawana", "famille", "أسرة", "مدونة الأسرة"]
 *   expandQuery("code du travail") → ["code du travail", "شغل", "مدونة الشغل"]
 */
export function expandQuery(query) {
  const q = query.trim()
  const qNorm = normalize(q)
  const extra = new Set()

  // Correspondance exacte
  if (SYNONYMS_INDEX[qNorm]) {
    for (const s of SYNONYMS_INDEX[qNorm]) extra.add(s)
  }

  // Correspondance partielle : si la requête contient une clé connue
  for (const [key, values] of Object.entries(SYNONYMS_INDEX)) {
    if (qNorm.includes(key) || key.includes(qNorm)) {
      for (const s of values) extra.add(s)
    }
  }

  // Retourner [requête originale, ...synonymes trouvés] dédupliqués
  const result = [q]
  for (const s of extra) {
    if (normalize(s) !== qNorm) result.push(s)
  }
  return result
}
