/**
 * Synonymes de recherche — JuriThèque
 * Permet de trouver les mêmes lois via Darija, abréviations, variantes AR/FR.
 * Chaque clé est normalisée en minuscules sans accents.
 * La valeur est un tableau de termes additionnels injectés dans la requête.
 */

// RÈGLE IMPORTANTE : les synonymes ne doivent contenir que des identifiants
// PRÉCIS (numéro de loi, titre arabe complet) — jamais des mots génériques
// comme "famille", "travail", "commerce" qui matchent des centaines de lois.

const RAW_SYNONYMS = {
  // ── Codes fondamentaux ──────────────────────────────────────────────────────
  // Moudawana = Loi 70-03 = Code de la Famille
  'moudawana':          ['مدونة الأسرة', '70-03'],
  'lmoudawana':         ['مدونة الأسرة', '70-03'],
  'mudawwana':          ['مدونة الأسرة', '70-03'],
  'code de la famille': ['مدونة الأسرة', '70-03'],
  'مدونة الأسرة':       ['70-03', 'moudawana'],
  'قانون الأسرة':       ['مدونة الأسرة', '70-03'],

  // COC = Dahir des Obligations et Contrats
  'coc':                ['الالتزامات والعقود', '12-40'],
  'dahir obligations':  ['الالتزامات والعقود', '12-40'],
  'الالتزامات والعقود': ['coc', '12-40'],

  // CPC = Code de Procédure Civile
  'cpc':                ['مسطرة مدنية'],
  'msatara madaniya':   ['مسطرة مدنية'],
  'مسطرة مدنية':        ['cpc'],

  // CPP = Code de Procédure Pénale
  'cpp':                ['مسطرة جنائية'],
  'msatara jina2iya':   ['مسطرة جنائية'],
  'مسطرة جنائية':       ['cpp'],

  // Code pénal = Loi pénale
  'code pénal':         ['قانون جنائي'],
  'قانون جنائي':        ['pénal'],

  // ── Travail — Darija : l3amal, lkhidma, chghol ─────────────────────────────
  // Code du Travail = Loi 65-99
  'l3amal':             ['مدونة الشغل', '65-99'],
  'lkhidma':            ['مدونة الشغل', '65-99'],
  'chghol':             ['مدونة الشغل', '65-99'],
  'shghol':             ['مدونة الشغل', '65-99'],
  'مدونة الشغل':        ['65-99'],

  // Licenciement
  'fasl':               ['فصل تعسفي', 'إنهاء عقد العمل'],
  'lfasl':              ['فصل تعسفي', 'إنهاء عقد العمل'],

  // ── Commerce & Sociétés ─────────────────────────────────────────────────────
  // Code de Commerce = Loi 15-95
  'مدونة التجارة':      ['15-95'],

  // SARL = Loi 5-96
  'sarl':               ['شركة ذات مسؤولية محدودة', '5-96'],
  'sharika':            ['شركة'],
  'charika':            ['شركة'],
  'lcharika':           ['شركة'],

  // SA = Loi 17-95
  'sa':                 ['شركة مساهمة', '17-95'],

  // ── Marchés publics — Darija : safa9at ─────────────────────────────────────
  // Décret marchés publics = 2-22-431
  'safa9at':            ['صفقات عمومية', '2-22-431'],
  'safakat':            ['صفقات عمومية', '2-22-431'],
  'sfa9at':             ['صفقات عمومية', '2-22-431'],
  'صفقات عمومية':       ['2-22-431'],
  'صفقات':              ['صفقات عمومية'],

  // ── Collectivités territoriales — Darija : jma3a ───────────────────────────
  'jma3a':              ['جماعة ترابية', '113-14'],
  'jama3at':            ['جماعات ترابية', '113-14'],
  'جماعات ترابية':      ['113-14'],

  // ── Foncier & Urbanisme — Darija : 3qar, lmlak, rkhsa ─────────────────────
  '3qar':               ['عقار', 'تحفيظ عقاري'],
  'l3qar':              ['عقار', 'تحفيظ عقاري'],
  'lmlak':              ['ملكية عقارية', 'تحفيظ'],
  'lmelk':              ['ملكية عقارية', 'تحفيظ'],
  'tahfid':             ['تحفيظ عقاري'],
  'ta3mir':             ['تعمير', '12-90'],
  'تعمير':              ['12-90'],
  'rkhsa':              ['رخصة البناء'],
  'rkhsat lbina':       ['رخصة البناء'],

  // ── Fiscalité — Darija : dara2ib ───────────────────────────────────────────
  'cgi':                ['المدونة العامة للضرائب'],
  'dara2ib':            ['ضريبة', 'المدونة العامة للضرائب'],
  'ldara2ib':           ['ضريبة', 'المدونة العامة للضرائب'],
  'dara9ib':            ['ضريبة', 'المدونة العامة للضرائب'],
  'المدونة العامة للضرائب': ['cgi'],

  // ── Famille & Personnes — Darija : ttalaq, lkhol3, hadana ─────────────────
  'ttalaq':             ['طلاق', 'مدونة الأسرة'],
  'talaq':              ['طلاق'],
  'lkhol3':             ['خلع', 'مدونة الأسرة'],
  'khol3':              ['خلع'],
  'chi9a9':             ['شقاق', 'مدونة الأسرة'],
  'shiqaq':             ['شقاق'],
  'طلاق':               ['مدونة الأسرة', '70-03'],
  'lhaddana':           ['حضانة', 'مدونة الأسرة'],
  'hadana':             ['حضانة'],
  'حضانة':              ['مدونة الأسرة'],
  'lnafaqa':            ['نفقة', 'مدونة الأسرة'],
  'nafaqa':             ['نفقة'],
  'نفقة':               ['مدونة الأسرة'],
  'lmiras':             ['ميراث', 'إرث'],
  'miras':              ['ميراث', 'إرث'],
  'ميراث':              ['إرث'],
  'zawaj':              ['زواج', 'مدونة الأسرة'],
  'lzwaj':              ['زواج', 'مدونة الأسرة'],

  // ── Justice & Procédure ─────────────────────────────────────────────────────
  'mahkama':            ['محكمة'],
  'lma7kama':           ['محكمة'],
  'da3wa':              ['دعوى'],
  'lda3wa':             ['دعوى'],

  // ── Données personnelles ────────────────────────────────────────────────────
  'rgpd':               ['معطيات شخصية', '09-08'],
  'cndp':               ['معطيات شخصية', '09-08'],
  'données personnelles': ['معطيات شخصية', '09-08'],
  'معطيات شخصية':       ['09-08'],

  // ── Finances publiques ──────────────────────────────────────────────────────
  'lof':                ['مالية عمومية', '130-13'],

  // ── Justice & Professions — Darija : mouhami, mwathiq ─────────────────────
  'mouhami':            ['محامي', 'محاماة'],
  'mouhamine':          ['محامي', 'محاماة'],
  'mwathiq':            ['موثق', 'توثيق'],
  'muwathiq':           ['موثق'],
  'adoul':              ['عدل', 'توثيق'],

  // ── Association — Darija : jam3iya ──────────────────────────────────────────
  'jam3iya':            ['جمعية'],
  'ljam3iya':           ['جمعية'],
  'saha9a':             ['صحافة'],
  'sahafa':             ['صحافة'],

  // ── Environnement & Énergie — Darija : lma, ta9a ───────────────────────────
  'lma':                ['ماء', '36-15'],
  'ta9a':               ['طاقة'],
  'ta9at':              ['طاقة'],
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
