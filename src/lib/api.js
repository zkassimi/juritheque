/**
 * LexBase — Supabase API helpers
 * All data fetching goes through here.
 */
import { supabase } from './supabase'
import { expandQuery } from '../data/searchSynonyms'

// ── Laws ──────────────────────────────────────────────────────────────────────

export async function fetchLaws({ q = '', types = [], domains = [], statuses = [],
  languages = [], dateFrom = '', dateTo = '', sort = 'date',
  page = 1, pageSize = 9 } = {}) {

  let query = supabase.from('laws').select('*', { count: 'exact' })
    .eq('is_published', true)

  if (q) {
    const isArabic = /[؀-ۿ]/.test(q)
    const expanded = expandQuery(q)
    const hasSynonyms = expanded.length > 1

    const terms = q.trim().split(/\s+/).filter(t => t.length >= 1)

    if (isArabic) {
      if (hasSynonyms) {
        // Synonymes précis (numéros, titres arabes) : OR original + synonymes
        const synParts = expanded.slice(1).map(s => `title_ar.ilike.%${s.trim()}%,number.ilike.%${s.trim()}%`).join(',')
        query = query.or(`title_ar.ilike.%${q}%,number.ilike.%${q}%,${synParts}`)
      } else {
        query = query.or(
          `title_ar.ilike.%${q}%,excerpt_ar.ilike.%${q}%,number.ilike.%${q}%`
        )
      }
    } else if (hasSynonyms) {
      // Synonymes précis trouvés : (termes originaux en AND) OR (synonymes spécifiques)
      const synParts = expanded.slice(1).map(s => {
        const t = s.trim()
        return `title_fr.ilike.%${t}%,title_ar.ilike.%${t}%,number.ilike.%${t}%`
      }).join(',')

      if (terms.length <= 1) {
        // Terme unique : OR simple
        query = query.or(`title_fr.ilike.%${q}%,title_ar.ilike.%${q}%,number.ilike.%${q}%,${synParts}`)
      } else {
        // Multi-termes : and(terme1,terme2) OR synonymes
        const andTerms = terms.map(t => `title_fr.ilike.%${t}%`).join(',')
        query = query.or(`and(${andTerms}),${synParts}`)
      }
    } else {
      if (terms.length === 1 && q.length >= 4) {
        // Mot unique suffisamment long : FTS pour un meilleur ranking
        query = query.textSearch('search_vector', q, { type: 'websearch', config: 'french' })
      } else {
        // Plusieurs mots : ILIKE par terme ANDé (gère "marché pu" → "marchés publics")
        for (const term of terms) {
          query = query.or(`title_fr.ilike.%${term}%,number.ilike.%${term}%,title_ar.ilike.%${term}%`)
        }
      }
    }
  }
  if (types.length)     query = query.in('type', types)
  if (domains.length) {
    // Multi-domaine : cherche dans domain_ids[] (contient le domaine demandé)
    // OU domain_id pour rétrocompat avec les lois sans domain_ids rempli
    if (domains.length === 1) {
      // Filtre précis : domain_ids contient CE domaine (loi principale ou secondaire)
      query = query.or(`domain_ids.cs.{${domains[0]}},domain_id.eq.${domains[0]}`)
    } else {
      // Plusieurs domaines sélectionnés : OR de containments
      const orParts = domains.map(d => `domain_ids.cs.{${d}},domain_id.eq.${d}`).join(',')
      query = query.or(orParts)
    }
  }
  if (statuses.length)  query = query.in('status', statuses)
  if (languages.length) query = query.in('language', languages)
  if (dateFrom)         query = query.gte('date', dateFrom)
  if (dateTo)           query = query.lte('date', dateTo)

  if (sort === 'date')  query = query.order('date', { ascending: false, nullsFirst: false })
  if (sort === 'alpha') query = query.order('title_fr', { ascending: true })
  if (sort === 'views') query = query.order('views', { ascending: false })

  const from = (page - 1) * pageSize
  query = query.range(from, from + pageSize - 1)

  const { data, error, count } = await query
  if (error) throw error
  return { data: data || [], count: count || 0 }
}

export async function fetchLawById(id) {
  const { data, error } = await supabase
    .from('laws')
    .select('*')
    .eq('id', id)
    .single()
  if (error) throw error
  return data
}

/**
 * fetchLawBySlug — résout un slug canonique, un ID numérique ou un slug approché.
 * Retourne la loi ou lève une erreur.
 *
 * Ordre de résolution :
 *  1. canonical_slug exact
 *  2. ID numérique (rétrocompatibilité)
 *  3. Slug approché : le slug de la DB contient le slug demandé (résout les
 *     anciens slugs générés avec le numéro dupliqué)
 */
export async function fetchLawBySlug(slug) {
  // 1. Essai par canonical_slug exact
  const { data, error } = await supabase
    .from('laws')
    .select('*')
    .eq('canonical_slug', slug)
    .maybeSingle()
  if (data) return data

  // 2. Fallback : ID numérique (anciens liens)
  if (/^\d+$/.test(slug)) {
    const { data: byId } = await supabase
      .from('laws')
      .select('*')
      .eq('id', parseInt(slug, 10))
      .maybeSingle()
    if (byId) return byId
  }

  // 3. Fallback approché : le slug demandé est contenu dans canonical_slug
  //    (ex: ancien slug "dahir-n-1-21-65-du-..." correspond à
  //     canonical_slug "1-21-65-dahir-n-1-21-65-du-..." ou inversement)
  //    On cherche aussi le cas dupliqué : slug contient lui-même deux fois
  const deduped = (() => {
    // Si le slug commence par un préfixe qui se répète (slug dupliqué),
    // extraire uniquement la partie unique (à partir du 2e segment)
    const half = Math.ceil(slug.length / 2)
    const firstHalf = slug.slice(0, half)
    const idx = slug.indexOf(firstHalf, 1)
    if (idx > 0 && idx <= half + 2) return slug.slice(idx)
    return null
  })()

  if (deduped && deduped.length > 8) {
    const { data: byDedup } = await supabase
      .from('laws')
      .select('*')
      .eq('canonical_slug', deduped)
      .maybeSingle()
    if (byDedup) return byDedup

    // Recherche LIKE si le déduplication n'est pas exacte
    const { data: byLike } = await supabase
      .from('laws')
      .select('*')
      .ilike('canonical_slug', `%${deduped.slice(0, 40)}%`)
      .maybeSingle()
    if (byLike) return byLike
  }

  // 4. Fallback : recherche par champ number (compatibilité après migration des slugs)
  //    Permet aux anciens liens /loi/adala-xxx de rediriger vers le nouveau slug
  const { data: byNumber } = await supabase
    .from('laws')
    .select('*')
    .eq('number', slug)
    .maybeSingle()
  if (byNumber) return byNumber

  // 5. Fallback : ancien slug dans slug_history (après correction des slugs)
  //    LawDetail.jsx fait navigate(canonical_slug, {replace:true}) → redirect silencieuse
  const { data: byHistory } = await supabase
    .from('laws')
    .select('*')
    .contains('slug_history', [slug])
    .maybeSingle()
  if (byHistory) return byHistory

  throw error || new Error('Texte introuvable')
}

export async function fetchLawsByDomain(domainId, { page = 1, pageSize = 18 } = {}) {
  const from = (page - 1) * pageSize
  const { data, error, count } = await supabase
    .from('laws')
    .select('*', { count: 'exact' })
    .eq('is_published', true)
    .or(`domain_ids.cs.{${domainId}},domain_id.eq.${domainId}`)
    .order('date', { ascending: false, nullsFirst: false })
    .range(from, from + pageSize - 1)
  if (error) throw error
  return { data: data || [], count: count || 0 }
}

export async function fetchRecentLaws(limit = 6) {
  const { data, error } = await supabase
    .from('laws')
    .select('*')
    .eq('is_published', true)
    .order('created_at', { ascending: false })
    .limit(limit)
  if (error) throw error
  return data || []
}

/**
 * fetchWatchLaws — Pour la page /fr/veille-juridique
 * mode 'recent'   → triés par created_at DESC (nouveaux textes)
 * mode 'modified' → filtre status='Modifié' OU updated_at récent
 */
export async function fetchWatchLaws({
  mode     = 'recent',   // 'recent' | 'modified'
  domain   = '',
  type     = '',
  page     = 1,
  pageSize = 12,
} = {}) {
  const WATCH_FIELDS = [
    'id', 'number', 'title_fr', 'title_ar', 'type', 'status', 'date',
    'domain_id', 'excerpt_fr', 'excerpt_ar', 'simple_summary_fr',
    'pdf_url', 'created_at', 'updated_at',
    'extraction_confidence_score', 'needs_human_review', 'extraction_status',
  ].join(',')

  let query = supabase
    .from('laws')
    .select(WATCH_FIELDS, { count: 'exact' })
    .eq('is_published', true)
    .eq('is_publicly_indexable', true)

  if (domain) query = query.or(`domain_ids.cs.{${domain}},domain_id.eq.${domain}`)
  if (type)   query = query.eq('type', type)

  if (mode === 'modified') {
    query = query.eq('status', 'Modifié')
    query = query.order('updated_at', { ascending: false, nullsFirst: false })
  } else {
    query = query.order('created_at', { ascending: false, nullsFirst: false })
  }

  const from = (page - 1) * pageSize
  query = query.range(from, from + pageSize - 1)

  const { data, error, count } = await query
  if (error) throw error
  return { data: data || [], count: count || 0 }
}

const LAW_REF_FIELDS = 'id,number,title_fr,title_ar,type,date,canonical_slug,status'

export async function fetchLawRelations(lawId, replacesId) {
  const out = { replacedLaw: null, successorLaws: [] }
  await Promise.all([
    replacesId
      ? supabase.from('laws').select(LAW_REF_FIELDS).eq('id', replacesId).maybeSingle()
          .then(({ data }) => { out.replacedLaw = data })
          .catch(() => {})
      : Promise.resolve(),
    supabase.from('laws').select(LAW_REF_FIELDS).eq('replaces_id', lawId)
      .order('date', { ascending: false }).limit(3)
      .then(({ data }) => { out.successorLaws = data || [] })
      .catch(() => {}),
  ])
  return out
}

export async function fetchRelatedLaws(domainId, excludeId, limit = 3) {
  const { data, error } = await supabase
    .from('laws')
    .select('*')
    .eq('is_published', true)
    .or(`domain_ids.cs.{${domainId}},domain_id.eq.${domainId}`)
    .neq('id', excludeId)
    .order('date', { ascending: false, nullsFirst: false })
    .limit(limit)
  if (error) throw error
  return data || []
}

export async function incrementLawViews(id) {
  await supabase.rpc('increment_views', { law_id: id }).catch(() => {})
}

// ── Domains ───────────────────────────────────────────────────────────────────

export async function fetchDomains() {
  const { data, error } = await supabase
    .from('domains')
    .select('*')
    .order('name_fr')
  if (error) throw error
  // Normalise Supabase shape → shape expected by DomainCard
  // (Supabase: name_fr/name_ar/sub_domains/law_count  →  DomainCard: fr/ar/sub/count)
  return (data || []).map(d => ({
    ...d,
    fr:    d.name_fr   ?? d.fr   ?? '',
    ar:    d.name_ar   ?? d.ar   ?? '',
    sub:   Array.isArray(d.sub_domains) ? d.sub_domains : (Array.isArray(d.sub) ? d.sub : []),
    count: d.law_count ?? d.count ?? 0,
  }))
}

export async function fetchDomainById(id) {
  const { data, error } = await supabase
    .from('domains')
    .select('*')
    .eq('id', id)
    .single()
  if (error) throw error
  return data
}

// ── Stats ─────────────────────────────────────────────────────────────────────

export async function fetchStats() {
  const [lawsRes, domainsRes] = await Promise.all([
    supabase.from('laws').select('*', { count: 'exact', head: true }).eq('is_published', true),
    supabase.from('domains').select('*', { count: 'exact', head: true }),
  ])
  return {
    lawsCount:    lawsRes.count    || 0,
    domainsCount: domainsRes.count || 0,
  }
}

// ── Newsletter ────────────────────────────────────────────────────────────────

export async function subscribeEmail(email, source = 'footer', lang = 'fr') {
  const { error } = await supabase
    .from('subscribers')
    .upsert({ email, source, lang, domain_id: null }, { onConflict: 'email,domain_id', ignoreDuplicates: true })
  if (error) throw error
}

export async function subscribeToDomain(email, domain_id, lang = 'fr') {
  const { error } = await supabase
    .from('subscribers')
    .upsert({ email, source: 'domain', lang, domain_id }, { onConflict: 'email,domain_id', ignoreDuplicates: true })
  if (error) throw error
}

// ── Reports / Signalements ────────────────────────────────────────────────────

export async function submitReport({
  content_type,   // 'law' | 'guide' | 'suggestion' | 'other'
  report_type,    // 'text_error' | 'outdated' | 'pdf_broken' | 'translation' | 'missing_text' | 'suggestion'
  subject,
  subject_url,
  law_id,
  guide_slug,
  comment,
  reporter_email,
}) {
  const { error } = await supabase.from('reports').insert({
    content_type,
    report_type,
    subject:        subject        || null,
    subject_url:    subject_url    || null,
    law_id:         law_id         || null,
    guide_slug:     guide_slug     || null,
    comment:        comment        || null,
    reporter_email: reporter_email || null,
  })
  if (error) throw error
}

// ── Favorites ─────────────────────────────────────────────────────────────────

export async function fetchFavorites(userId) {
  const { data, error } = await supabase
    .from('favorites')
    .select('law_id, laws(*)')
    .eq('user_id', userId)
  if (error) throw error
  return (data || []).map(f => f.laws)
}

export async function addFavorite(userId, lawId) {
  const { error } = await supabase
    .from('favorites')
    .insert({ user_id: userId, law_id: lawId })
  if (error) throw error
}

export async function removeFavorite(userId, lawId) {
  const { error } = await supabase
    .from('favorites')
    .delete()
    .eq('user_id', userId)
    .eq('law_id', lawId)
  if (error) throw error
}

// ── Assistant IA — Recherche interne ─────────────────────────────────────────

// Mots trop génériques (partagé par les deux fonctions de recherche)
const AI_GENERIC_WORDS = new Set([
  'loi','lois','droit','droits','texte','textes','juridique','juridiques',
  'maroc','marocain','marocaine','marocains','cherche','trouve','montre',
  'donner','article','articles','code','codes','disposition','dispositions',
  'القانون','المغرب','النص','المادة','الحقوق',
])

/**
 * findRelevantLaws — cherche les textes juridiques dans la table laws
 */
export async function findRelevantLaws(query, { limit = 3 } = {}) {
  const keywords = query
    .replace(/[?!،؟]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length >= 3 && !AI_GENERIC_WORDS.has(w.toLowerCase()))
    .join(' ')
    .trim()

  if (!keywords) return []

  try {
    // FTS sur title_fr
    const { data: fts } = await supabase
      .from('laws')
      .select('id, title_fr, canonical_slug, type, domain_id, simple_summary_fr')
      .textSearch('title_fr', keywords, { type: 'websearch', config: 'french' })
      .limit(limit)

    if (fts?.length) return fts.map(lawToPage)

    // Fallback ilike sur les mots-clés
    const topWord = keywords.split(' ').sort((a, b) => b.length - a.length)[0]
    if (!topWord) return []
    const { data: ilike } = await supabase
      .from('laws')
      .select('id, title_fr, canonical_slug, type, domain_id, simple_summary_fr')
      .ilike('title_fr', `%${topWord}%`)
      .limit(limit)
    return (ilike || []).map(lawToPage)
  } catch { return [] }
}

function lawToPage(law) {
  return {
    title: law.title_fr,
    url: `/fr/loi/${law.canonical_slug || law.id}`,
    source_type: 'law',
    description: (law.simple_summary_fr || '').slice(0, 150),
    legal_domain: law.domain_id,
    document_type: law.type || 'Texte juridique',
    priority: 5,
  }
}

/**
 * retrieveRelevantSitePages
 * Cherche dans site_search_index les pages internes pertinentes
 * pour une question utilisateur.
 *
 * Stratégie :
 *  1. Full-Text Search (websearch français) sur search_vector
 *  2. Fallback ilike sur title + description si FTS < 2 résultats
 *
 * Retourne max `limit` résultats triés par pertinence + priorité.
 * Ne retourne JAMAIS content_fr / content_ar.
 *
 * @param {string} query  — question utilisateur brute
 * @param {object} opts
 * @param {number} opts.limit     — max résultats (défaut 6)
 * @param {string} opts.domain    — filtrer par legal_domain (optionnel)
 * @returns {Array<{title,url,source_type,description,summary,keywords,legal_domain,document_type,priority}>}
 */
export async function retrieveRelevantSitePages(query, { limit = 6, domain = '' } = {}) {
  if (!query || query.trim().length < 2) return []

  const FIELDS = 'title,url,source_type,description,summary,keywords,legal_domain,document_type,priority'
  const q = query.trim()

  // Détecte si la requête est majoritairement en arabe
  const isArabic = (s) => (s.match(/[؀-ۿ]/g) || []).length > s.length * 0.3

  // ── Stratégie 1 : FTS websearch (FR ou simple pour l'arabe) ──────────────
  let ftsResults = []
  const ftsConfig = isArabic(q) ? 'simple' : 'french'

  // Mots trop génériques qui faussent le FTS (matchent tout)
  const FTS_GENERIC = new Set([
    'loi','lois','droit','droits','texte','textes','juridique','juridiques',
    'maroc','marocain','marocaine','cherche','trouve','montre','donner',
    'article','articles','code','codes','disposition','dispositions',
    'القانون','المغرب','النص','المادة','الحقوق',
  ])

  try {
    // Enlever termes génériques + caractères spéciaux
    const ftsQuery_str = q
      .replace(/[?!،؟]/g, ' ')
      .split(/\s+/)
      .filter(w => w.length >= 2 && !FTS_GENERIC.has(w.toLowerCase()))
      .join(' ')
      .trim() || q.replace(/[?!،؟]/g, ' ').trim()
    let ftsQuery = supabase
      .from('site_search_index')
      .select(FIELDS)
      .eq('is_public', true)
      .textSearch('search_vector', ftsQuery_str, { type: 'websearch', config: ftsConfig })
      .order('priority', { ascending: false })
      .limit(limit + 4)

    if (domain) ftsQuery = ftsQuery.eq('legal_domain', domain)

    const { data } = await ftsQuery
    ftsResults = data || []
  } catch (_) {}

  // ── Stratégie 2 : ilike sur mots-clés extraits ───────────────────────────
  let ilikeResults = []
  if (ftsResults.length < 2) {
    const STOP_WORDS = new Set([
      // Français
      'moi','les','des','une','que','qui','pour','dans','avec','sur','par',
      'est','sont','ont','mais','tout','cette','quels','quelles','comment',
      'quand','combien','quoi','dont','donc','aussi','textes','liés','lié',
      'texte','concernant','relatif','montre','donne','cherche','trouve',
      // Arabe
      'ما','هل','كيف','متى','من','في','على','عن','مع','أو','إلى','هي',
      'هو','هذا','هذه','التي','الذي','يمكن','كان','كانت',
    ])

    // Nettoyer les préfixes arabes courants (بـ، وـ، فـ، كـ، لـ)
    const stripArabicPrefix = (w) => w.replace(/^[بوفكلال]+/, '') || w

    const keywords = q
      .split(/[\s,;?!.،؟]+/)
      .map(w => w.trim())
      .filter(w => w.length >= 3 && !STOP_WORDS.has(w))
      .map(w => isArabic(w) ? stripArabicPrefix(w) : w.toLowerCase())
      .filter(w => w.length >= 3)

    const topKeywords = [...new Set(keywords)]
      .sort((a, b) => b.length - a.length)
      .slice(0, 4)

    if (topKeywords.length > 0) {
      try {
        const orFilters = topKeywords
          .map(kw => `title.ilike.%${kw}%,description.ilike.%${kw}%,summary.ilike.%${kw}%`)
          .join(',')

        let ilikeQuery = supabase
          .from('site_search_index')
          .select(FIELDS)
          .eq('is_public', true)
          .or(orFilters)
          .order('priority', { ascending: false })
          .limit(limit + 4)

        if (domain) ilikeQuery = ilikeQuery.eq('legal_domain', domain)

        const { data } = await ilikeQuery
        ilikeResults = data || []
      } catch (_) {}
    }
  }

  // ── Fusion & déduplication ────────────────────────────────────────────────
  const seen = new Set()
  const merged = [...ftsResults, ...ilikeResults].filter(r => {
    if (seen.has(r.url)) return false
    seen.add(r.url)
    return true
  })

  // Tri : guides et lois avec résumé d'abord, puis par priorité
  merged.sort((a, b) => {
    const aHasSummary = a.summary ? 1 : 0
    const bHasSummary = b.summary ? 1 : 0
    if (bHasSummary !== aHasSummary) return bHasSummary - aHasSummary
    return (b.priority || 0) - (a.priority || 0)
  })

  return merged.slice(0, limit)
}
