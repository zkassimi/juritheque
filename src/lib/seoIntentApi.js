/**
 * JuriThèque — Récupération des textes liés pour les pages guides
 * ─────────────────────────────────────────────────────────────────
 * Stratégie :
 *   1. Par domain_id (priorité principale) + is_publicly_indexable
 *   2. Par Full-Text Search sur le premier searchTerm (FTS français)
 *   3. Fusion, déduplication, tri : résumé d'abord, puis score décroissant
 */
import { supabase } from './supabase'

const SELECT_FIELDS = [
  'id', 'number', 'title_fr', 'title_ar',
  'type', 'status', 'date', 'domain_id',
  'excerpt_fr', 'excerpt_ar',
  'simple_summary_fr',
  'public_article_count',
  'pdf_url',
  'extraction_confidence_score',
].join(',')

export async function getRelatedLawsForIntent(intent) {
  if (!intent) return []
  const { legalDomain, searchTerms = [], specificNumbers = [] } = intent

  const seen    = new Set()
  const results = []

  const addAll = (rows) => {
    if (!Array.isArray(rows)) return
    rows.forEach(l => {
      if (l && !seen.has(l.id)) { seen.add(l.id); results.push(l) }
    })
  }

  // ── Stratégie 0 : lois spécifiques par numéro (priorité absolue) ───
  if (specificNumbers.length > 0) {
    try {
      const { data } = await supabase
        .from('laws')
        .select(SELECT_FIELDS)
        .in('number', specificNumbers)
        .eq('is_publicly_indexable', true)
        .order('extraction_confidence_score', { ascending: false, nullsFirst: false })
      addAll(data)
    } catch (_) { /* silencieux */ }
  }

  // ── Stratégie 1 : Full-Text Search sur tous les searchTerms ─────────
  for (const term of searchTerms.slice(0, 3)) {
    if (results.length >= 15) break
    try {
      const { data } = await supabase
        .from('laws')
        .select(SELECT_FIELDS)
        .eq('is_publicly_indexable', true)
        .textSearch('search_vector', term, { type: 'websearch', config: 'french' })
        .order('extraction_confidence_score', { ascending: false, nullsFirst: false })
        .limit(6)
      addAll(data)
    } catch (_) { /* silencieux */ }
  }

  // ── Stratégie 2 : par domain_id (fallback si pas assez de résultats) ─
  if (legalDomain && results.length < 6) {
    try {
      const { data } = await supabase
        .from('laws')
        .select(SELECT_FIELDS)
        .eq('domain_id', legalDomain)
        .eq('is_publicly_indexable', true)
        .order('extraction_confidence_score', { ascending: false, nullsFirst: false })
        .limit(12)
      addAll(data)
    } catch (_) { /* silencieux */ }
  }

  // ── Tri final : spécifiques d'abord, résumé, puis score décroissant ─
  return results.sort((a, b) => {
    const aSpec = specificNumbers.includes(a.number) ? 1 : 0
    const bSpec = specificNumbers.includes(b.number) ? 1 : 0
    if (aSpec !== bSpec) return bSpec - aSpec
    const aS = a.simple_summary_fr ? 1 : 0
    const bS = b.simple_summary_fr ? 1 : 0
    if (aS !== bS) return bS - aS
    return (Number(b.extraction_confidence_score) || 0) -
           (Number(a.extraction_confidence_score) || 0)
  }).slice(0, 15)
}
