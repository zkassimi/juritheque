/**
 * /fr/veille-juridique — Page de veille juridique
 * ─────────────────────────────────────────────────
 * Affiche les nouveaux textes et les textes modifiés récemment.
 * Filtres (domain, type) persistants dans l'URL.
 * Deux sections : Nouveaux textes · Récemment modifiés.
 */
import { useEffect, useState, useCallback } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  ChevronRight, ChevronLeft, Bot, Search, BookOpen,
  Sparkles, RefreshCw, FileText, Download, AlertCircle,
  Clock, CheckCircle, AlertTriangle, Newspaper
} from 'lucide-react'
import { useLang }      from '../contexts/LangContext'
import { useSEO }       from '../hooks/useSEO'
import { fetchWatchLaws, fetchDomains } from '../lib/api'
import JsonLD, { breadcrumbSchema } from '../components/JsonLD'
import TypeBadge   from '../components/ui/TypeBadge'
import StatusBadge from '../components/ui/StatusBadge'
import { SEO_INTENT_PAGES } from '../data/seoIntentPages'
import { lawPath, lawCanonical } from '../lib/lawUtils'

const BASE_URL  = 'https://juritheque.com'
const PAGE_SIZE = 12

// ── Calcul du badge temporel ──────────────────────────────────────────────────
const THIRTY_DAYS = 30 * 24 * 60 * 60 * 1000

const BADGE_LABELS = {
  new:       { fr: 'Nouveau',    ar: 'جديد' },
  modified:  { fr: 'Mis à jour', ar: 'محدَّث' },
  validated: { fr: 'Validé',     ar: 'موثَّق' },
  active:    { fr: 'En vigueur', ar: 'ساري المفعول' },
}

function getWatchBadge(law, lang = 'fr') {
  const now       = Date.now()
  const createdAt = law.created_at ? new Date(law.created_at).getTime() : 0
  const updatedAt = law.updated_at ? new Date(law.updated_at).getTime() : 0
  const isNew     = createdAt > 0 && (now - createdAt) < THIRTY_DAYS
  const isModified = law.status === 'Modifié' || (updatedAt > createdAt + 60_000)
  const score      = law.extraction_confidence_score != null
                     ? Number(law.extraction_confidence_score) : null
  const isValidated = score !== null && score >= 75 && !law.needs_human_review

  if (isNew)       return { label: BADGE_LABELS.new[lang],       bg: 'bg-emerald-100 text-emerald-700', dot: 'bg-emerald-500' }
  if (isModified)  return { label: BADGE_LABELS.modified[lang],  bg: 'bg-blue-100 text-blue-700',      dot: 'bg-blue-500' }
  if (isValidated) return { label: BADGE_LABELS.validated[lang], bg: 'bg-gold/20 text-yellow-700',     dot: 'bg-gold' }
  return               { label: BADGE_LABELS.active[lang],   bg: 'bg-gray-100 text-navy-600',       dot: 'bg-gray-400' }
}

// ── Carte d'un texte ──────────────────────────────────────────────────────────
function WatchCard({ law }) {
  const { lang, t } = useLang()
  const badge    = getWatchBadge(law, lang)
  const title    = (lang === 'ar' && law.title_ar) ? law.title_ar : (law.title_fr || law.title_ar || `Texte n°${law.id}`)
  const desc     = law.simple_summary_fr || law.excerpt_fr || law.excerpt_ar || null

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5 hover:border-gold hover:shadow-sm transition-all flex flex-col gap-3">
      {/* Badges ligne */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Badge veille */}
        <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full ${badge.bg}`}>
          <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${badge.dot}`} />
          {badge.label}
        </span>
        <TypeBadge   type={law.type} />
        <StatusBadge status={law.status} />
      </div>

      {/* Titre */}
      <Link to={lawPath(law)} className="group">
        <h3 className="text-sm font-semibold text-navy group-hover:text-gold transition-colors leading-snug line-clamp-2">
          {title}
        </h3>
      </Link>

      {/* Meta */}
      <div className="flex flex-wrap gap-3 text-xs text-navy-400">
        {law.number && <span className="font-medium text-navy-600">{law.number}</span>}
        {law.date   && <span className="flex items-center gap-1"><Clock size={10} />{law.date}</span>}
        {law.domain_id && (
          <Link to={`/domaine/${law.domain_id}`} className="hover:text-gold transition-colors capitalize">
            {law.domain_id}
          </Link>
        )}
      </div>

      {/* Résumé */}
      {desc && (
        <p className="text-xs text-navy-600 leading-relaxed line-clamp-3">
          {String(desc).slice(0, 220)}
        </p>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2 mt-auto pt-1">
        <Link
          to={lawPath(law)}
          className="flex items-center gap-1 text-xs text-gold font-medium hover:underline"
        >
          {t('watch.read')} <ChevronRight size={11} />
        </Link>
        {law.pdf_url && (
          <a
            href={law.pdf_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-navy-400 hover:text-gold transition-colors ml-auto"
          >
            <Download size={11} /> PDF
          </a>
        )}
      </div>
    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
function WatchSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5 animate-pulse flex flex-col gap-3">
      <div className="flex gap-2">
        <div className="h-5 w-16 bg-gray-100 rounded-full" />
        <div className="h-5 w-14 bg-gray-100 rounded-full" />
      </div>
      <div className="h-4 bg-gray-100 rounded w-4/5" />
      <div className="h-3 bg-gray-100 rounded w-2/5" />
      <div className="space-y-1.5">
        <div className="h-3 bg-gray-100 rounded w-full" />
        <div className="h-3 bg-gray-100 rounded w-3/4" />
      </div>
    </div>
  )
}

// ── Empty state ───────────────────────────────────────────────────────────────
function EmptyState({ label }) {
  const { t } = useLang()
  return (
    <div className="col-span-full flex flex-col items-center justify-center py-12 text-center">
      <FileText size={36} className="text-gray-200 mb-3" />
      <p className="text-sm text-navy-500 mb-2">{label}</p>
      <Link to="/base" className="text-xs text-gold hover:underline">
        {t('watch.search_base')}
      </Link>
    </div>
  )
}

// ── Pagination simple ─────────────────────────────────────────────────────────
function Pagination({ page, total, pageSize, onPage }) {
  const { t } = useLang()
  const totalPages = Math.ceil(total / pageSize)
  if (totalPages <= 1) return null
  return (
    <div className="flex items-center justify-center gap-2 mt-6">
      <button
        onClick={() => onPage(page - 1)}
        disabled={page === 1}
        className="p-2 rounded-lg border border-gray-200 bg-white text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
      >
        <ChevronLeft size={15} />
      </button>
      <span className="text-xs text-navy-500">{t('watch.page')} {page} / {totalPages}</span>
      <button
        onClick={() => onPage(page + 1)}
        disabled={page >= totalPages}
        className="p-2 rounded-lg border border-gray-200 bg-white text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
      >
        <ChevronRight size={15} />
      </button>
    </div>
  )
}

// ── Types de textes disponibles ───────────────────────────────────────────────
const LAW_TYPES_FR = ['Loi', 'Décret', 'Arrêté', 'Dahir', 'Circulaire', 'Code', 'Ordonnance']
const LAW_TYPES_AR = ['قانون', 'مرسوم', 'قرار', 'ظهير', 'دورية', 'مدونة', 'منشور']

// ── Page principale ───────────────────────────────────────────────────────────
export default function LegalWatch() {
  const { lang, t } = useLang()
  const [searchParams, setSearchParams] = useSearchParams()

  // Filtres depuis l'URL
  const domain  = searchParams.get('domain') || ''
  const type    = searchParams.get('type')   || ''
  const pageNew = Math.max(1, parseInt(searchParams.get('pageNew') || '1', 10))
  const pageMod = Math.max(1, parseInt(searchParams.get('pageMod') || '1', 10))

  const [domains,      setDomains]      = useState([])
  const [newLaws,      setNewLaws]      = useState([])
  const [newTotal,     setNewTotal]     = useState(0)
  const [modLaws,      setModLaws]      = useState([])
  const [modTotal,     setModTotal]     = useState(0)
  const [loadingNew,   setLoadingNew]   = useState(true)
  const [loadingMod,   setLoadingMod]   = useState(true)
  const [errorNew,     setErrorNew]     = useState(false)
  const [errorMod,     setErrorMod]     = useState(false)

  useSEO({
    title:       'Veille juridique au Maroc — Nouvelles lois et décrets',
    description: 'Veille juridique marocaine : suivez les nouvelles lois, dahirs et décrets dès leur publication au Bulletin Officiel. Alertes en temps réel pour juristes, entreprises et MRE.',
    canonical:   '/fr/veille-juridique',
    type:        'website',
  })

  // Charger les domaines
  useEffect(() => {
    fetchDomains().then(setDomains).catch(() => {})
  }, [])

  // Charger les nouveaux textes
  const loadNew = useCallback(() => {
    setLoadingNew(true); setErrorNew(false)
    fetchWatchLaws({ mode: 'recent', domain, type, page: pageNew, pageSize: PAGE_SIZE })
      .then(({ data, count }) => { setNewLaws(data); setNewTotal(count); setLoadingNew(false) })
      .catch(() => { setErrorNew(true); setLoadingNew(false) })
  }, [domain, type, pageNew])

  // Charger les textes modifiés
  const loadMod = useCallback(() => {
    setLoadingMod(true); setErrorMod(false)
    fetchWatchLaws({ mode: 'modified', domain, type, page: pageMod, pageSize: PAGE_SIZE })
      .then(({ data, count }) => { setModLaws(data); setModTotal(count); setLoadingMod(false) })
      .catch(() => { setErrorMod(true); setLoadingMod(false) })
  }, [domain, type, pageMod])

  useEffect(() => { loadNew() }, [loadNew])
  useEffect(() => { loadMod() }, [loadMod])

  // Mise à jour URL
  const setFilter = (key, value) => {
    const p = new URLSearchParams(searchParams)
    if (value) p.set(key, value); else p.delete(key)
    // Reset pagination quand on change filtre
    p.delete('pageNew'); p.delete('pageMod')
    setSearchParams(p, { replace: true })
  }

  const setPage = (key, val) => {
    const p = new URLSearchParams(searchParams)
    if (val > 1) p.set(key, String(val)); else p.delete(key)
    setSearchParams(p, { replace: true })
  }

  const clearFilters = () => setSearchParams({}, { replace: true })

  const hasFilters = domain || type
  const LAW_TYPES = lang === 'ar' ? LAW_TYPES_AR : LAW_TYPES_FR
  const LAW_TYPES_DISPLAY = LAW_TYPES_FR.map((fr, i) => ({ value: fr, label: lang === 'ar' ? LAW_TYPES_AR[i] : fr }))

  const breadcrumbs = [
    { name: 'Accueil',            url: '/' },
    { name: 'Veille juridique',   url: '/fr/veille-juridique' },
  ]

  const jsonLdData = [
    {
      '@context':   'https://schema.org',
      '@type':      'CollectionPage',
      name:         'Veille juridique au Maroc',
      description:  'Suivez les dernières lois, décrets et arrêtés publiés au Maroc.',
      url:          `${BASE_URL}/fr/veille-juridique`,
      inLanguage:   ['fr', 'ar'],
      isPartOf:     { '@type': 'WebSite', name: 'JuriThèque', url: BASE_URL },
    },
    breadcrumbSchema(breadcrumbs),
    newLaws.length > 0 && {
      '@context':      'https://schema.org',
      '@type':         'ItemList',
      name:            'Derniers textes juridiques publiés au Maroc',
      numberOfItems:   newTotal,
      itemListElement: newLaws.map((l, i) => ({
        '@type':   'ListItem',
        position:  i + 1,
        url:       lawCanonical(l, BASE_URL),
        name:      l.title_fr || l.title_ar || `Texte n°${l.id}`,
      })),
    },
  ].filter(Boolean)

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      <JsonLD data={jsonLdData} />

      {/* ── En-tête ────────────────────────────────────────────────────── */}
      <div className="bg-navy text-white py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          {/* Fil d'Ariane */}
          <nav className="flex items-center gap-1.5 text-xs text-white/50 mb-5" aria-label="Fil d'Ariane">
            <Link to="/"              className="hover:text-gold transition-colors">{t('watch.home')}</Link>
            <ChevronRight size={10} />
            <span className="text-white/80">{t('watch.breadcrumb')}</span>
          </nav>

          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-gold/20 flex items-center justify-center flex-shrink-0 mt-1">
              <Newspaper size={18} className="text-gold" />
            </div>
            <div>
              <h1 className="font-playfair font-bold text-2xl sm:text-3xl mb-2">
                {t('watch.title')}
              </h1>
              <p className="text-white/60 text-sm max-w-2xl leading-relaxed">
                {t('watch.subtitle')}
              </p>
            </div>
          </div>

          {/* Badges légende */}
          <div className="flex flex-wrap gap-2 mt-6">
            {[
              { labelKey: 'watch.badge_new',       bg: 'bg-emerald-500/20 text-emerald-300', dot: 'bg-emerald-400' },
              { labelKey: 'watch.badge_updated',    bg: 'bg-blue-500/20 text-blue-300',       dot: 'bg-blue-400' },
              { labelKey: 'watch.badge_validated',  bg: 'bg-gold/20 text-gold',               dot: 'bg-gold' },
              { labelKey: 'watch.badge_active',     bg: 'bg-white/10 text-white/50',          dot: 'bg-gray-400' },
            ].map(b => (
              <span key={b.labelKey} className={`inline-flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-1 rounded-full ${b.bg}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${b.dot}`} />
                {t(b.labelKey)}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ── Filtres ────────────────────────────────────────────────────── */}
      <div className="bg-white border-b border-gray-100 sticky top-16 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-wrap items-center gap-3">

          {/* Filtre domaine */}
          <select
            value={domain}
            onChange={e => setFilter('domain', e.target.value)}
            className="px-3 py-1.5 text-xs border border-gray-200 rounded-xl bg-white text-navy-700 focus:outline-none focus:border-gold"
          >
            <option value="">{t('watch.all_domains')}</option>
            {domains.map(d => (
              <option key={d.id} value={d.id}>
                {(lang === 'ar' && d.name_ar) ? d.name_ar : (d.name_fr || d.fr || d.id)}
              </option>
            ))}
          </select>

          {/* Filtre type */}
          <div className="flex bg-white rounded-xl border border-gray-200 overflow-hidden">
            <button
              onClick={() => setFilter('type', '')}
              className={`px-3 py-1.5 text-xs font-medium transition-colors ${!type ? 'bg-navy text-white' : 'text-navy-600 hover:text-navy'}`}
            >
              {t('watch.all_types')}
            </button>
            {LAW_TYPES_DISPLAY.map(({ value, label }) => (
              <button
                key={value}
                onClick={() => setFilter('type', type === value ? '' : value)}
                className={`px-3 py-1.5 text-xs font-medium border-l border-gray-200 transition-colors ${type === value ? 'bg-navy text-white' : 'text-navy-600 hover:text-navy'}`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Clear */}
          {hasFilters && (
            <button
              onClick={clearFilters}
              className="flex items-center gap-1 text-xs text-red-500 hover:text-red-700 transition-colors"
            >
              <RefreshCw size={11} /> {t('watch.reset')}
            </button>
          )}

          {/* Lien vers base complète */}
          <Link
            to={`/base?${domain ? `domain=${domain}&` : ''}${type ? `type=${type}&` : ''}sort=date`}
            className="ml-auto flex items-center gap-1 text-xs text-gold hover:underline whitespace-nowrap"
          >
            {t('watch.full_view')} <ChevronRight size={11} />
          </Link>
        </div>
      </div>

      {/* ── Contenu ────────────────────────────────────────────────────── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-10">

        {/* ── Section Nouveaux textes ──────────────────────────────────── */}
        <section>
          <div className="flex items-center gap-3 mb-5">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center flex-shrink-0">
              <Sparkles size={14} className="text-emerald-600" />
            </div>
            <div>
              <h2 className="font-playfair font-semibold text-navy text-lg">
                {t('watch.new_title')}
                {!loadingNew && newTotal > 0 && (
                  <span className="ml-2 text-sm font-normal text-navy-400">({newTotal})</span>
                )}
              </h2>
              <p className="text-xs text-navy-400">{t('watch.new_sub')}</p>
            </div>
          </div>

          {errorNew ? (
            <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-600">
              <AlertCircle size={14} />
              {t('watch.load_error')}
              <button onClick={loadNew} className="ml-auto text-xs hover:underline">{t('watch.retry')}</button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {loadingNew
                  ? [...Array(6)].map((_, i) => <WatchSkeleton key={i} />)
                  : newLaws.length === 0
                    ? <EmptyState label={t('watch.no_new')} />
                    : newLaws.map(law => <WatchCard key={law.id} law={law} />)
                }
              </div>
              <Pagination
                page={pageNew}
                total={newTotal}
                pageSize={PAGE_SIZE}
                onPage={p => setPage('pageNew', p)}
              />
            </>
          )}
        </section>

        {/* ── Section Textes modifiés ──────────────────────────────────── */}
        <section>
          <div className="flex items-center gap-3 mb-5">
            <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
              <RefreshCw size={14} className="text-blue-600" />
            </div>
            <div>
              <h2 className="font-playfair font-semibold text-navy text-lg">
                {t('watch.mod_title')}
                {!loadingMod && modTotal > 0 && (
                  <span className="ml-2 text-sm font-normal text-navy-400">({modTotal})</span>
                )}
              </h2>
              <p className="text-xs text-navy-400">{t('watch.mod_sub')}</p>
            </div>
          </div>

          {errorMod ? (
            <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-600">
              <AlertCircle size={14} />
              {t('watch.load_error')}
              <button onClick={loadMod} className="ml-auto text-xs hover:underline">{t('watch.retry')}</button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {loadingMod
                  ? [...Array(3)].map((_, i) => <WatchSkeleton key={i} />)
                  : modLaws.length === 0
                    ? <EmptyState label={t('watch.no_mod')} />
                    : modLaws.map(law => <WatchCard key={law.id} law={law} />)
                }
              </div>
              <Pagination
                page={pageMod}
                total={modTotal}
                pageSize={PAGE_SIZE}
                onPage={p => setPage('pageMod', p)}
              />
            </>
          )}
        </section>

        {/* ── CTA double ────────────────────────────────────────────────── */}
        <section className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Link
            to="/assistant"
            className="flex items-center gap-3 p-5 bg-navy text-white rounded-2xl hover:bg-gold hover:text-navy transition-colors group"
          >
            <Bot size={22} className="flex-shrink-0 group-hover:scale-110 transition-transform" />
            <div>
              <p className="font-semibold text-sm">{t('watch.cta_ai')}</p>
              <p className="text-xs opacity-70 mt-0.5">{t('watch.cta_ai_desc')}</p>
            </div>
          </Link>
          <Link
            to="/base"
            className="flex items-center gap-3 p-5 bg-white border border-gray-200 rounded-2xl hover:border-gold transition-colors group"
          >
            <Search size={22} className="flex-shrink-0 text-gold" />
            <div>
              <p className="font-semibold text-sm text-navy">{t('watch.cta_explore')}</p>
              <p className="text-xs text-navy-500 mt-0.5">{t('watch.cta_explore_desc')}</p>
            </div>
          </Link>
        </section>

        {/* ── Guides thématiques liés ────────────────────────────────────── */}
        <section>
          <h2 className="font-playfair font-semibold text-navy text-lg mb-4 flex items-center gap-2">
            <BookOpen size={16} className="text-gold" />
            {t('watch.guides_section')}
          </h2>
          <div className="flex flex-wrap gap-2">
            {SEO_INTENT_PAGES.slice(0, 8).map(guide => (
              <Link
                key={guide.slug}
                to={`/fr/guides/${guide.slug}`}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-white border border-gray-200 rounded-xl text-xs text-navy-700 hover:border-gold hover:text-gold transition-colors"
              >
                <BookOpen size={11} className="text-gold flex-shrink-0" />
                {(lang === 'ar' && guide.h1_ar) ? guide.h1_ar : guide.h1}
              </Link>
            ))}
            <Link
              to="/fr/guides"
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-gold/10 border border-gold/30 rounded-xl text-xs font-semibold text-gold hover:bg-gold hover:text-navy transition-colors"
            >
              {t('watch.all_guides')} <ChevronRight size={11} />
            </Link>
            <Link
              to="/fr/bulletins-officiels"
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors"
            >
              <Newspaper size={11} className="text-gold flex-shrink-0" />
              {t('watch.bo_link')}
            </Link>
            <Link
              to="/fr/lois-complementaires"
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors"
            >
              <FileText size={11} className="text-gold flex-shrink-0" />
              {t('watch.adala_link')}
            </Link>
          </div>
        </section>

        {/* ── Domaines ──────────────────────────────────────────────────── */}
        {domains.length > 0 && (
          <section>
            <h2 className="font-playfair font-semibold text-navy text-lg mb-4">
              {t('watch.domain_watch')}
            </h2>
            <div className="flex flex-wrap gap-2">
              {domains.map(d => (
                <Link
                  key={d.id}
                  to={`/fr/veille-juridique?domain=${d.id}`}
                  className={`inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium border transition-colors ${
                    domain === d.id
                      ? 'bg-navy text-white border-navy'
                      : 'bg-white text-navy-700 border-gray-200 hover:border-gold hover:text-gold'
                  }`}
                >
                  {d.name_fr || d.fr || d.id}
                </Link>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  )
}
