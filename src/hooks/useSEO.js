/**
 * useSEO — Hook SEO dynamique pour JuriThèque
 * ─────────────────────────────────────────────
 * Gère dynamiquement : <title>, <meta description>, <link canonical>,
 * balises Open Graph et Twitter Card dans le <head>.
 *
 * Compatible React SPA sans SSR.
 * Google crawle le JS — les balises sont bien lues par Googlebot.
 * Pour les aperçus sociaux (WhatsApp/FB), seul le titre statique d'index.html
 * sera affiché ; ajouter un prerender-service pour aller plus loin.
 */

import { useEffect } from 'react'

// ── Constantes globales ────────────────────────────────────────────────────────
export const SITE_NAME    = 'JuriThèque'
export const BASE_URL     = 'https://juritheque.com'
export const DEFAULT_DESC = 'JuriThèque — Base de données de 7 400+ textes juridiques marocains bilingues (français/arabe). Lois, dahirs, décrets, codes et arrêtés accessibles gratuitement.'
export const OG_IMAGE     = `${BASE_URL}/og-image.png`    // À créer dans public/

// ── Helpers DOM ───────────────────────────────────────────────────────────────

/**
 * Crée ou met à jour une balise <meta>.
 * @param {string} attrName  - "name" | "property"
 * @param {string} attrValue - valeur de l'attribut (ex: "description", "og:title")
 * @param {string} content   - valeur de content
 */
function upsertMeta(attrName, attrValue, content) {
  if (!content) return
  const selector = `meta[${attrName}="${attrValue}"]`
  let el = document.querySelector(selector)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attrName, attrValue)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

/**
 * Crée ou met à jour un <link> dans le <head>.
 */
function upsertLink(rel, href) {
  if (!href) return
  let el = document.querySelector(`link[rel="${rel}"]`)
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', rel)
    document.head.appendChild(el)
  }
  el.setAttribute('href', href)
}

/**
 * Gère les balises hreflang (alternate).
 * Supprime les anciennes, insère les nouvelles.
 * @param {Array<{lang: string, url: string}>} items
 */
function upsertHreflang(items) {
  // Supprimer les hreflang existants
  document.querySelectorAll('link[rel="alternate"][hreflang]').forEach(el => el.remove())
  if (!items?.length) return
  items.forEach(({ lang, url }) => {
    const el = document.createElement('link')
    el.setAttribute('rel', 'alternate')
    el.setAttribute('hreflang', lang)
    el.setAttribute('href', url)
    document.head.appendChild(el)
  })
}

// ── Hook principal ─────────────────────────────────────────────────────────────

/**
 * @param {Object}  opts
 * @param {string}  opts.title        - Titre de la page (sans le suffixe " | JuriThèque")
 * @param {string}  [opts.description]- Description SEO (max ~155 chars)
 * @param {string}  [opts.canonical]  - Chemin relatif, ex: "/loi/42" (BASE_URL ajouté automatiquement)
 * @param {string}  [opts.type]       - og:type : "website" | "article"   (défaut "website")
 * @param {string}  [opts.image]      - URL absolue de l'image OG
 * @param {boolean} [opts.noindex]    - true pour empêcher l'indexation
 * @param {Object}  [opts.article]    - { publishedTime: "YYYY-MM-DD", section: "Droit Civil" }
 */
export function useSEO({
  title,
  description,
  canonical,
  type = 'website',
  image,
  noindex = false,
  article,
  lang = 'fr',
  hreflang,
} = {}) {
  useEffect(() => {
    // ── 0. <html lang> + dir (RTL pour l'arabe) — essentiel pour le SEO AR ────
    document.documentElement.lang = lang
    document.documentElement.dir  = lang === 'ar' ? 'rtl' : 'ltr'

    // ── 1. Titre complet ──────────────────────────────────────────────────────
    const pageTitle = title
      ? `${title} — ${SITE_NAME}`
      : `${SITE_NAME} | مكتبة القانون`

    const pageDesc = description
      ? String(description).slice(0, 160)   // tronquer à 160 chars max (String() protège contre non-string)
      : DEFAULT_DESC

    const pageUrl = canonical
      ? (canonical.startsWith('http') ? canonical : `${BASE_URL}${canonical}`)
      : BASE_URL + window.location.pathname

    const pageImage = image || OG_IMAGE

    // ── 2. <title> ────────────────────────────────────────────────────────────
    document.title = pageTitle

    // ── 3. Meta standard ──────────────────────────────────────────────────────
    upsertMeta('name', 'description',  pageDesc)
    upsertMeta('name', 'robots',       noindex ? 'noindex,nofollow' : 'index,follow')

    // ── 4. Canonical ─────────────────────────────────────────────────────────
    upsertLink('canonical', pageUrl)

    // ── 5. Open Graph ─────────────────────────────────────────────────────────
    upsertMeta('property', 'og:title',       pageTitle)
    upsertMeta('property', 'og:description', pageDesc)
    upsertMeta('property', 'og:url',         pageUrl)
    upsertMeta('property', 'og:type',        type)
    upsertMeta('property', 'og:site_name',   SITE_NAME)
    upsertMeta('property', 'og:image',       pageImage)
    upsertMeta('property', 'og:locale',      lang === 'ar' ? 'ar_MA' : 'fr_MA')

    // OG article (si type === 'article')
    if (article?.publishedTime) {
      upsertMeta('property', 'article:published_time', article.publishedTime)
    }
    if (article?.section) {
      upsertMeta('property', 'article:section', article.section)
    }

    // ── 6. Twitter Card ───────────────────────────────────────────────────────
    upsertMeta('name', 'twitter:card',        'summary_large_image')
    upsertMeta('name', 'twitter:title',       pageTitle)
    upsertMeta('name', 'twitter:description', pageDesc)
    upsertMeta('name', 'twitter:image',       pageImage)

    // ── 7. Hreflang ───────────────────────────────────────────────────────────
    upsertHreflang(hreflang)

  }, [title, description, canonical, type, image, noindex, lang, article?.publishedTime, article?.section, hreflang])
}
