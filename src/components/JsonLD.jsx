/**
 * JsonLD — Composant d'injection JSON-LD (Schema.org)
 * ──────────────────────────────────────────────────────
 * Injecte un ou plusieurs blocs <script type="application/ld+json"> dans <head>.
 * Se nettoie automatiquement au démontage du composant (changement de route).
 *
 * Usage :
 *   <JsonLD data={{ "@context": "https://schema.org", "@type": "WebSite", ... }} />
 *   <JsonLD data={[schemaA, schemaB]} />
 */

import { useEffect, useRef } from 'react'
import { lawCanonical } from '../lib/lawUtils'

export default function JsonLD({ data }) {
  const scriptRef = useRef(null)

  useEffect(() => {
    // Créer le script au montage
    const script = document.createElement('script')
    script.type = 'application/ld+json'
    document.head.appendChild(script)
    scriptRef.current = script

    // Nettoyage au démontage (changement de page)
    return () => {
      if (scriptRef.current && document.head.contains(scriptRef.current)) {
        document.head.removeChild(scriptRef.current)
        scriptRef.current = null
      }
    }
  }, []) // Seulement au montage/démontage

  // Mettre à jour le contenu quand les données changent
  useEffect(() => {
    if (!scriptRef.current) return
    const payload = Array.isArray(data) ? data : [data]
    scriptRef.current.textContent = JSON.stringify(payload.length === 1 ? payload[0] : payload)
  })

  return null
}

// ── Schémas réutilisables ──────────────────────────────────────────────────────

const BASE_URL  = 'https://juritheque.com'
const SITE_NAME = 'JuriThèque'

/** WebSite schema — pour la page d'accueil */
export function websiteSchema() {
  return {
    '@context':  'https://schema.org',
    '@type':     'WebSite',
    name:        SITE_NAME,
    alternateName: 'مكتبة القانون',
    url:         BASE_URL,
    description: 'Base de données de 7 400+ textes juridiques marocains bilingues (français/arabe) : lois, dahirs, décrets, codes et arrêtés. Gratuit.',
    inLanguage:  ['fr', 'ar'],
    potentialAction: {
      '@type':       'SearchAction',
      target:        `${BASE_URL}/base?q={search_term_string}`,
      'query-input': 'required name=search_term_string',
    },
  }
}

/** Organization schema — pour la page d'accueil */
export function organizationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type':    'Organization',
    name:       SITE_NAME,
    url:        BASE_URL,
    logo:       `${BASE_URL}/logo.png`,
    contactPoint: {
      '@type':             'ContactPoint',
      email:               'contact@juritheque.com',
      contactType:         'customer service',
      availableLanguage:   ['French', 'Arabic'],
      areaServed:          'MA',
    },
    sameAs: [],
  }
}

/**
 * LegalDocument schema — pour chaque page /loi/:id
 * @param {Object} law    - objet loi depuis Supabase
 * @param {Object} domain - objet domaine (peut être null)
 */
export function legalDocumentSchema(law, domain) {
  if (!law) return null
  return {
    '@context':        'https://schema.org',
    '@type':           'Legislation',
    name:              law.title_fr || law.title_ar || undefined,
    alternateName:     law.title_ar || law.title_fr || undefined,
    identifier:        law.number || undefined,
    description:       law.excerpt_fr || law.excerpt_ar || law.title_fr || law.title_ar || undefined,
    datePublished:     law.date     || undefined,
    inLanguage:        law.language === 'AR' ? 'ar' : (law.language === 'FR' ? 'fr' : ['fr', 'ar']),
    legislationType:   law.type,
    jurisdiction:      'Maroc',
    url:               lawCanonical(law, BASE_URL),
    ...(law.pdf_url ? { encoding: { '@type': 'MediaObject', contentUrl: law.pdf_url, encodingFormat: 'application/pdf' } } : {}),
    ...(domain ? { about: { '@type': 'Thing', name: domain.name_fr } } : {}),
    publisher: {
      '@type': 'Organization',
      name:    SITE_NAME,
      url:     BASE_URL,
    },
  }
}

/**
 * FAQPage schema — pour les sections FAQ des guides
 * @param {Array<{question: string, answer: string}>} faq
 */
export function faqSchema(faq) {
  if (!faq?.length) return null
  return {
    '@context': 'https://schema.org',
    '@type':    'FAQPage',
    mainEntity: faq.map(({ question, answer }) => ({
      '@type':          'Question',
      name:             question,
      acceptedAnswer: {
        '@type': 'Answer',
        text:    answer,
      },
    })),
  }
}

/**
 * Dataset schema — pour la page /base
 * @param {number} total - nombre de textes
 */
export function datasetSchema(total) {
  return {
    '@context':   'https://schema.org',
    '@type':      'Dataset',
    name:         'Base de données juridique marocaine — JuriThèque',
    description:  `Collection de ${total || '7 400'}+ textes juridiques officiels du Maroc : lois, dahirs, décrets, arrêtés et codes. Bilingue français-arabe.`,
    url:          `${BASE_URL}/base`,
    creator: {
      '@type': 'Organization',
      name:    SITE_NAME,
      url:     BASE_URL,
    },
    inLanguage:      ['fr', 'ar'],
    keywords:        ['droit marocain', 'loi maroc', 'dahir', 'décret', 'textes juridiques', 'القانون المغربي'],
    spatialCoverage: { '@type': 'Place', name: 'Maroc' },
    license:         'https://creativecommons.org/licenses/by/4.0/',
  }
}

/**
 * BreadcrumbList schema
 * @param {Array} items - [{ name, url }]
 */
export function breadcrumbSchema(items) {
  return {
    '@context':        'https://schema.org',
    '@type':           'BreadcrumbList',
    itemListElement:   items.map((item, i) => ({
      '@type':    'ListItem',
      position:   i + 1,
      name:       item.name,
      item:       item.url.startsWith('http') ? item.url : `${BASE_URL}${item.url}`,
    })),
  }
}

/**
 * CollectionPage schema — pour /domaine/:slug
 * @param {Object} domain - objet domaine
 * @param {number} count  - nombre de textes
 */
export function collectionPageSchema(domain, count) {
  if (!domain) return null
  return {
    '@context':   'https://schema.org',
    '@type':      'CollectionPage',
    name:         `${domain.name_fr || domain.name_ar || 'Domaine'} — ${SITE_NAME}`,
    description:  `Consultez les textes juridiques marocains en matière de ${(domain.name_fr || domain.name_ar || 'droit').toLowerCase()}. ${count ? count + ' textes disponibles.' : ''}`,
    url:          `${BASE_URL}/domaine/${domain.id}`,
    inLanguage:   ['fr', 'ar'],
    isPartOf: {
      '@type': 'WebSite',
      name:    SITE_NAME,
      url:     BASE_URL,
    },
  }
}
