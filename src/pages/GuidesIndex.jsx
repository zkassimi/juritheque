import { useState } from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, ChevronRight, ArrowRight, Bot, Search, Bell, X } from 'lucide-react'
import { useSEO } from '../hooks/useSEO'
import { useLang } from '../contexts/LangContext'
import JsonLD, { breadcrumbSchema } from '../components/JsonLD'
import { getIntentsByCategory, SEO_INTENT_PAGES } from '../data/seoIntentPages'

const BASE_URL = 'https://juritheque.com'

function GuideGrid({ guides }) {
  const { lang, t } = useLang()
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
      {guides.map(guide => (
        <Link
          key={guide.slug}
          to={`/${lang}/guides/${guide.slug}`}
          className="group flex flex-col bg-white rounded-xl border border-gray-100 p-3 hover:border-gold hover:shadow-md transition-all"
        >
          <div className="flex items-start gap-2.5 mb-2">
            <div className="w-7 h-7 rounded-lg bg-gold/10 flex items-center justify-center flex-shrink-0 group-hover:bg-gold/20 transition-colors">
              <BookOpen size={12} className="text-gold" />
            </div>
            <h2 className="font-semibold text-navy text-xs leading-snug group-hover:text-gold transition-colors line-clamp-2">
              {(lang === 'ar' && guide.h1_ar) ? guide.h1_ar : guide.h1}
            </h2>
          </div>
          <p className="text-[11px] text-navy-500 leading-relaxed flex-1 line-clamp-2 mb-2">
            {(lang === 'ar' && guide.metaDescription_ar) ? guide.metaDescription_ar : guide.metaDescription}
          </p>
          {guide.keywords?.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {((lang === 'ar' && guide.keywords_ar?.length) ? guide.keywords_ar : guide.keywords).slice(0, 2).map(kw => (
                <span key={kw} className="text-[9px] bg-gray-50 text-navy-400 px-1.5 py-0.5 rounded-full border border-gray-100">
                  {kw}
                </span>
              ))}
            </div>
          )}
          <div className="flex items-center gap-0.5 text-[11px] text-gold font-semibold group-hover:gap-1.5 transition-all">
            {t('guides.view_guide')} <ChevronRight size={10} />
          </div>
        </Link>
      ))}
    </div>
  )
}

const CATEGORY_META = {
  mre:            { labelKey: 'guides.cat_mre',            badge: 'bg-indigo-50 text-indigo-700 border-indigo-200',   dot: 'bg-indigo-400' },
  investissement: { labelKey: 'guides.cat_investissement',  badge: 'bg-gold/10 text-amber-800 border-amber-200',       dot: 'bg-amber-400' },
  travail:        { labelKey: 'guides.cat_travail',         badge: 'bg-blue-50 text-blue-700 border-blue-200',         dot: 'bg-blue-400' },
  commercial:     { labelKey: 'guides.cat_commercial',      badge: 'bg-amber-50 text-amber-700 border-amber-200',      dot: 'bg-amber-400' },
  famille:        { labelKey: 'guides.cat_famille',         badge: 'bg-pink-50 text-pink-700 border-pink-200',         dot: 'bg-pink-400' },
  civil:          { labelKey: 'guides.cat_civil',           badge: 'bg-emerald-50 text-emerald-700 border-emerald-200', dot: 'bg-emerald-400' },
  penal:          { labelKey: 'guides.cat_penal',           badge: 'bg-red-50 text-red-700 border-red-200',            dot: 'bg-red-400' },
  administratif:  { labelKey: 'guides.cat_administratif',   badge: 'bg-violet-50 text-violet-700 border-violet-200',   dot: 'bg-violet-400' },
  collectivites:  { labelKey: 'guides.cat_collectivites',   badge: 'bg-purple-50 text-purple-700 border-purple-200',   dot: 'bg-purple-400' },
  societe:        { labelKey: 'guides.cat_societe',         badge: 'bg-teal-50 text-teal-700 border-teal-200',         dot: 'bg-teal-400' },
}

export default function GuidesIndex() {
  const { t, lang } = useLang()

  useSEO({
    title:       'Guides juridiques marocains — JuriThèque',
    description: 'Guides pratiques sur le droit marocain : droits des MRE, investir au Maroc, héritage, immobilier, droit du travail, droit commercial. Avec les textes officiels liés.',
    canonical:   '/fr/guides',
    type:        'website',
  })

  const [searchQ, setSearchQ] = useState('')
  const grouped = getIntentsByCategory()

  const ql = searchQ.toLowerCase().trim()
  const searchResults = ql
    ? SEO_INTENT_PAGES.filter(g =>
        g.h1.toLowerCase().includes(ql) ||
        (g.keywords || []).some(k => k.toLowerCase().includes(ql)) ||
        (g.intro || '').toLowerCase().includes(ql) ||
        (g.category || '').toLowerCase().includes(ql)
      )
    : null

  const breadcrumbs = [
    { name: 'Accueil',           url: '/' },
    { name: 'Guides juridiques', url: '/fr/guides' },
  ]

  // JSON-LD — CollectionPage + BreadcrumbList
  const jsonLdData = [
    {
      '@context':   'https://schema.org',
      '@type':      'CollectionPage',
      name:         'Guides juridiques marocains — JuriThèque',
      description:  'Guides thématiques sur le droit marocain basés sur les textes officiels.',
      url:          `${BASE_URL}/fr/guides`,
      inLanguage:   'fr',
      isPartOf:     { '@type': 'WebSite', name: 'JuriThèque', url: BASE_URL },
    },
    breadcrumbSchema(breadcrumbs),
  ]

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      <JsonLD data={jsonLdData} />

      {/* ── En-tête ───────────────────────────────────────────────────── */}
      <div className="bg-navy text-white py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <nav className="flex items-center gap-1.5 text-xs text-white/50 mb-4" aria-label="Fil d'Ariane">
            <Link to="/" className="hover:text-gold transition-colors">{t('guides.home')}</Link>
            <ChevronRight size={10} />
            <span className="text-white/80">{t('guides.breadcrumb')}</span>
          </nav>
          <p className="text-gold text-xs font-semibold uppercase tracking-widest mb-3">
            {t('guides.section_label')}
          </p>
          <h1 className="font-playfair font-bold text-3xl sm:text-4xl mb-3">
            {t('guides.title')}
          </h1>
          <p className="text-white/60 text-sm max-w-xl leading-relaxed mb-6">
            {t('guides.desc')}
          </p>
          {/* Barre de recherche */}
          <div className="relative max-w-md">
            <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/40" />
            <input
              type="text"
              value={searchQ}
              onChange={e => setSearchQ(e.target.value)}
              placeholder={t('guides.search_placeholder')}
              className="w-full pl-9 pr-9 py-2.5 rounded-xl bg-white/10 border border-white/20 text-sm text-white placeholder-white/40 focus:outline-none focus:border-gold focus:bg-white/15 transition-all"
            />
            {searchQ && (
              <button
                onClick={() => setSearchQ('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white transition-colors"
              >
                <X size={13} />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Contenu ───────────────────────────────────────────────────── */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 space-y-10">

        {/* ── Résultats de recherche (mode plat) ───────────────────── */}
        {searchResults !== null ? (
          <section>
            <p className="text-xs text-navy-500 mb-4">
              <strong className="text-gold">{searchResults.length}</strong> {t('guides.found').replace('{n}', searchResults.length)}
            </p>
            {searchResults.length === 0 ? (
              <p className="text-sm text-navy-400 text-center py-10">{t('guides.no_results')}</p>
            ) : (
              <GuideGrid guides={searchResults} />
            )}
          </section>
        ) : (
          /* ── Affichage par catégories (mode normal) ────────────── */
          Object.entries(grouped).map(([cat, pages]) => {
            const meta = CATEGORY_META[cat] || { labelKey: null, badge: 'bg-gray-50 text-gray-700 border-gray-200', dot: 'bg-gray-400' }
            const catLabel = meta.labelKey ? t(meta.labelKey) : cat
            return (
              <section key={cat}>
                <div className="flex items-center gap-3 mb-4">
                  <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full border ${meta.badge}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${meta.dot}`} />
                    {catLabel}
                  </span>
                  <div className="h-px flex-1 bg-gray-200" />
                  <span className="text-xs text-navy-400">{pages.length} guide{pages.length > 1 ? 's' : ''}</span>
                </div>
                <GuideGrid guides={pages} />
              </section>
            )
          })
        )}

        {/* ── Bloc CTA final ─────────────────────────────────────────── */}
        <div className="bg-navy rounded-2xl p-6 sm:p-10 text-center text-white">
          <h3 className="font-playfair font-bold text-xl sm:text-2xl mb-2">
            {t('guides.cta_title')}
          </h3>
          <p className="text-white/60 text-sm mb-6 max-w-md mx-auto">
            {t('guides.cta_desc')}
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link
              to="/base"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-navy rounded-xl text-sm font-semibold hover:bg-gold transition-colors"
            >
              <Search size={14} /> {t('guides.cta_database')}
            </Link>
            <Link
              to="/assistant"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-gold text-navy rounded-xl text-sm font-semibold hover:bg-gold/80 transition-colors"
            >
              <Bot size={14} /> {t('guides.cta_ai')}
            </Link>
          </div>
        </div>

        {/* ── Liens secondaires ─────────────────────────────────────── */}
        <div className="flex flex-wrap items-center justify-center gap-6 pb-4 text-sm text-navy-500">
          <Link
            to={`/${lang}/veille-juridique`}
            className="inline-flex items-center gap-2 hover:text-gold transition-colors"
          >
            <Bell size={14} />
            {t('guides.link_watch')}
          </Link>
          <Link
            to="/domaines"
            className="inline-flex items-center gap-2 hover:text-gold transition-colors"
          >
            <ArrowRight size={14} />
            {t('guides.link_domains')}
          </Link>
        </div>
      </div>
    </div>
  )
}
