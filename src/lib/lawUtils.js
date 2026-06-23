/**
 * lawUtils.js — helpers partagés pour les textes juridiques
 */

/**
 * Retourne le chemin React Router vers une loi.
 * Priorité : canonical_slug (SEO) → id numérique (rétrocompatiblité)
 */
export const lawPath = (law, lang = 'fr') => {
  const id = law?.canonical_slug || law?.id
  return `/${lang}/loi/${id}`
}

/**
 * Retourne l'URL canonique absolue d'une loi.
 */
export const lawCanonical = (law, baseUrl = '', lang = 'fr') =>
  `${baseUrl}${lawPath(law, lang)}`

/**
 * Mapping source_name → site officiel source
 * Utilisé pour afficher un lien vers le site (pas le PDF)
 */
export const SOURCE_SITE_MAP = {
  adala:               'https://adala.justice.gov.ma',
  sgg:                 'https://www.sgg.gov.ma',
  'sgg-lois':          'https://www.sgg.gov.ma',
  sgg_home:            'https://www.sgg.gov.ma',
  sgg_bo_increment:    'https://www.sgg.gov.ma/BO/FR/',
  bkam:                'https://www.bkam.ma',
  anrt:                'https://www.anrt.ma',
  anrt_lois_telecom:   'https://www.anrt.ma',
  anrt_lois_autres:    'https://www.anrt.ma',
  anrt_decrets:        'https://www.anrt.ma',
  mmsp:                'https://www.mmsp.gov.ma',
  mem:                 'https://www.mem.gov.ma',
  cdr:                 'https://www.chambredesrepresentants.ma',
  finances:            'https://www.finances.gov.ma',
  lof:                 'https://www.finances.gov.ma',
  wipo:                'https://wipolex.wipo.int/fr/legislation/profile/MA',
  ism:                 'https://www.ism.ma',
  cndp:                'https://www.cndp.ma',
  mcinet:              'https://www.mcinet.gov.ma',
  environnement:       'https://www.environnement.gov.ma',
  emploi:              'https://www.emploi.gov.ma',
  sante:               'https://www.sante.gov.ma',
  agriculture:         'https://www.agriculture.gov.ma',
  ammc:                'https://www.ammc.ma',
}

export const SOURCE_LABEL_MAP = {
  adala:               'Adala — Ministère de la Justice',
  sgg:                 'SGG — Secrétariat Général du Gouvernement',
  'sgg-lois':          'SGG — Secrétariat Général du Gouvernement',
  sgg_home:            'SGG — Secrétariat Général du Gouvernement',
  sgg_bo_increment:    'SGG — Bulletin Officiel',
  bkam:                'Bank Al-Maghrib',
  anrt:                'ANRT — Télécommunications',
  anrt_lois_telecom:   'ANRT — Lois Télécom',
  anrt_lois_autres:    'ANRT — Législation',
  anrt_decrets:        'ANRT — Décrets',
  mmsp:                'Ministère de la Fonction Publique',
  mem:                 'Ministère de l\'Énergie et des Mines',
  cdr:                 'Chambre des Représentants',
  finances:            'Ministère des Finances',
  lof:                 'Ministère des Finances — Loi Organique des Finances',
  wipo:                'WIPO Lex',
  ism:                 'ISM',
  cndp:                'CNDP — Protection des Données Personnelles',
  mcinet:              'MCINET — Ministère du Commerce',
  environnement:       'Ministère de l\'Environnement',
  emploi:              'Ministère de l\'Emploi',
  sante:               'Ministère de la Santé',
  agriculture:         'Ministère de l\'Agriculture',
  ammc:                'AMMC — Autorité Marocaine du Marché des Capitaux',
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
