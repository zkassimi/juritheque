/**
 * lawUtils.js — helpers partagés pour les textes juridiques
 */

/**
 * Retourne le chemin React Router vers une loi.
 * Priorité : canonical_slug (SEO) → id numérique (rétrocompatiblité)
 */
export const lawPath = (law) =>
  law?.canonical_slug ? `/loi/${law.canonical_slug}` : `/loi/${law?.id}`

/**
 * Retourne l'URL canonique absolue d'une loi.
 */
export const lawCanonical = (law, baseUrl = '') =>
  `${baseUrl}${lawPath(law)}`

/**
 * Mapping source_name → site officiel source
 * Utilisé pour afficher un lien vers le site (pas le PDF)
 */
export const SOURCE_SITE_MAP = {
  adala:      'https://adala.justice.gov.ma',
  sgg:        'https://www.sgg.gov.ma',
  'sgg-lois': 'https://www.sgg.gov.ma',
  bkam:       'https://www.bkam.ma',
  anrt:       'https://www.anrt.ma',
  mmsp:       'https://www.mmsp.gov.ma',
  mem:        'https://www.mem.gov.ma',
  cdr:        'https://www.chambredesrepresentants.ma',
  finances:   'https://www.finances.gov.ma',
  wipo:       'https://wipolex.wipo.int/fr/legislation/profile/MA',
  ism:        'https://www.ism.ma',
}

export const SOURCE_LABEL_MAP = {
  adala:      'Adala — Ministère de la Justice',
  sgg:        'SGG — Secrétariat Général du Gouvernement',
  'sgg-lois': 'SGG — Secrétariat Général du Gouvernement',
  bkam:       'Bank Al-Maghrib',
  anrt:       'ANRT',
  mmsp:       'Ministère de la Fonction Publique',
  mem:        'Ministère de l\'Énergie et des Mines',
  cdr:        'Chambre des Représentants',
  finances:   'Ministère des Finances',
  wipo:       'WIPO Lex',
  ism:        'ISM',
}

/**
 * Retourne l'URL du site source (pas le PDF direct) à partir du source_name ou source_url.
 */
export function getSourceSiteUrl(law) {
  if (!law) return null
  const key = (law.source_name || '').toLowerCase().trim()
  if (SOURCE_SITE_MAP[key]) return SOURCE_SITE_MAP[key]
  // Fallback : extraire le domaine de source_url
  if (law.source_url) {
    try { return new URL(law.source_url).origin } catch { /* ignore */ }
  }
  return null
}

/**
 * Retourne le label lisible de la source.
 */
export function getSourceLabel(law) {
  if (!law) return null
  const key = (law.source_name || '').toLowerCase().trim()
  return SOURCE_LABEL_MAP[key] || law.source_name || null
}
