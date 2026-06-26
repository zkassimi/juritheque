import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Grid3X3, List, SlidersHorizontal, ChevronLeft, ChevronRight, FileX, BookOpen, Bell, Bot, Building2, Newspaper, Mail, CheckCircle2, X, ChevronDown } from 'lucide-react'
import { useLang } from '../contexts/LangContext'
import { fetchLaws, fetchDomains, subscribeToDomain } from '../lib/api'
import LawCard from '../components/LawCard'
import FilterSidebar from '../components/FilterSidebar'
import { SkeletonGrid } from '../components/ui/SkeletonLoader'
import { useSEO } from '../hooks/useSEO'
import JsonLD, { datasetSchema } from '../components/JsonLD'
import { SEO_INTENT_PAGES } from '../data/seoIntentPages'

const PAGE_SIZE = 9

// ── Helpers URL ────────────────────────────────────────────────────────────────

/** Lit tous les filtres depuis les URLSearchParams */
function parseFiltersFromURL(params) {
  return {
    q:         params.get('q')        ?? '',
    types:     params.getAll('type'),
    domains:   params.getAll('domain'),
    statuses:  params.getAll('status'),
    languages: params.getAll('lang'),
    dateFrom:  params.get('dateFrom') ?? '',
    dateTo:    params.get('dateTo')   ?? '',
  }
}

/** Construit les URLSearchParams à partir de l'état courant */
function buildURLParams(filters, page, sort, view) {
  const p = new URLSearchParams()
  if (filters.q)         p.set('q', filters.q)
  if (page > 1)          p.set('page', String(page))
  if (sort !== 'date')   p.set('sort', sort)
  if (view !== 'grid')   p.set('view', view)
  filters.types.forEach(t     => p.append('type', t))
  filters.domains.forEach(d   => p.append('domain', d))
  filters.statuses.forEach(s  => p.append('status', s))
  filters.languages.forEach(l => p.append('lang', l))
  if (filters.dateFrom)  p.set('dateFrom', filters.dateFrom)
  if (filters.dateTo)    p.set('dateTo',   filters.dateTo)
  return p
}

// ── Composant principal ────────────────────────────────────────────────────────

export default function Database() {
  const { t, isRTL } = useLang()

  useSEO({
    title: 'Base de données juridiques — Lois et décrets du Maroc',
    description: 'Recherchez parmi 7 400+ textes juridiques marocains : lois, décrets, dahirs, arrêtés, codes et circulaires. Filtres par domaine, type, statut et date. Bilingue FR/AR.',
    canonical: '/base',
    type: 'website',
  })

  const [searchParams, setSearchParams] = useSearchParams()

  // ── État initialisé depuis l'URL (permet de partager/recharger une page filtrée)
  const [filters, setFilters] = useState(() => parseFiltersFromURL(searchParams))
  const [page, setPage]       = useState(() => Math.max(1, parseInt(searchParams.get('page') ?? '1', 10)))
  const [sort, setSort]       = useState(() => searchParams.get('sort') ?? 'date')
  const [view, setView]       = useState(() => searchParams.get('view') ?? 'grid')

  const [loading, setLoading]           = useState(true)
  const [laws, setLaws]                 = useState([])
  const [total, setTotal]               = useState(0)
  const [sidebarOpen, setSidebarOpen]   = useState(true)

  // Domaines depuis Supabase pour les compteurs réels dans la sidebar
  const [domains, setDomains]           = useState([])
  const [domainsLoading, setDomainsLoading] = useState(true)

  // Popup abonnement par domaine
  const [subPopup, setSubPopup]         = useState(false)
  const [subEmail, setSubEmail]         = useState('')
  const [subDomain, setSubDomain]       = useState('')
  const [subStatus, setSubStatus]       = useState('idle') // idle | loading | success | error | duplicate

  // ── Charger les domaines Supabase une seule fois ────────────────────────────
  useEffect(() => {
    fetchDomains()
      .then(data => setDomains(data))
      .catch(() => {}) // FilterSidebar se rabat sur mockData si vide
      .finally(() => setDomainsLoading(false))
  }, [])

  // ── Synchroniser l'URL quand filtres/page/sort/view changent ──────────────
  useEffect(() => {
    setSearchParams(buildURLParams(filters, page, sort, view), { replace: true })
  }, [filters, page, sort, view]) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Charger les lois depuis Supabase ───────────────────────────────────────
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetchLaws({ ...filters, sort, page, pageSize: PAGE_SIZE })
      .then(({ data, count }) => {
        if (!cancelled) { setLaws(data); setTotal(count); setLoading(false) }
      })
      .catch(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [filters, sort, page])

  // ── Changer les filtres remet la pagination à 1 ───────────────────────────
  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters)
    setPage(1)
  }

  const totalPages = Math.ceil(total / PAGE_SIZE)

  const SORTS = [
    { key: 'relevance', label: t('db.sort_relevance') },
    { key: 'date',      label: t('db.sort_date') },
    { key: 'alpha',     label: t('db.sort_alpha') },
  ]

  const handleSubscribe = async (e) => {
    e.preventDefault()
    if (!subEmail || subStatus === 'loading') return
    setSubStatus('loading')
    try {
      await subscribeToDomain(subEmail.trim(), subDomain || null)
      setSubStatus('success')
      setSubEmail('')
    } catch (err) {
      if (err?.code === '23505' || err?.message?.includes('unique')) {
        setSubStatus('duplicate')
      } else {
        setSubStatus('error')
      }
    }
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      <JsonLD data={datasetSchema(total)} />

      {/* ── Popup abonnement par domaine ─────────────────────────────────── */}
      {subPopup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => { setSubPopup(false); setSubStatus('idle'); setSubEmail('') }} />
          <div className="relative z-10 bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md border border-gray-100">
            {/* Fermer */}
            <button
              onClick={() => { setSubPopup(false); setSubStatus('idle'); setSubEmail('') }}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-navy hover:bg-gray-100 transition-colors"
            >
              <X size={16} />
            </button>

            {subStatus === 'success' ? (
              <div className="text-center py-4">
                <div className="w-14 h-14 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle2 size={28} className="text-emerald-500" />
                </div>
                <h3 className="font-playfair font-bold text-navy text-lg mb-2">{t('db.sub_confirmed')}</h3>
                <p className="text-sm text-navy-600">
                  {subDomain
                    ? t('db.sub_domain_msg').replace('{domain}', domains.find(d => d.id === subDomain)?.[lang === 'ar' ? 'name_ar' : 'name_fr'] || subDomain)
                    : t('db.sub_general_msg')}
                </p>
                <button
                  onClick={() => { setSubPopup(false); setSubStatus('idle'); setSubEmail(''); setSubDomain('') }}
                  className="mt-5 px-5 py-2.5 bg-navy text-white rounded-xl text-sm font-medium hover:bg-gold hover:text-navy transition-colors"
                >
                  {t('db.close')}
                </button>
              </div>
            ) : (
              <>
                <div className="flex items-center gap-3 mb-5">
                  <div className="w-10 h-10 bg-gold/10 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Bell size={18} className="text-gold" />
                  </div>
                  <div>
                    <h3 className="font-playfair font-bold text-navy text-lg">{t('db.subscribe_title')}</h3>
                    <p className="text-xs text-navy-500 mt-0.5">{t('db.subscribe_sub')}</p>
                  </div>
                </div>

                <form onSubmit={handleSubscribe} className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-navy-700 mb-1.5">{t('db.domain_label')}</label>
                    <div className="relative">
                      <select
                        value={subDomain}
                        onChange={e => setSubDomain(e.target.value)}
                        className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold appearance-none bg-white pr-8"
                      >
                        <option value="">{t('db.all_domains')}</option>
                        {domains.map(d => (
                          <option key={d.id} value={d.id}>{lang === 'ar' ? (d.name_ar || d.name_fr) : d.name_fr}</option>
                        ))}
                      </select>
                      <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-navy-700 mb-1.5">{t('db.email_label')}</label>
                    <div className="relative">
                      <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                      <input
                        type="email"
                        required
                        value={subEmail}
                        onChange={e => setSubEmail(e.target.value)}
                        placeholder={t('db.email_ph')}
                        className="w-full pl-9 pr-3 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20"
                      />
                    </div>
                  </div>

                  {subStatus === 'duplicate' && (
                    <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
                      {t('db.already_sub').replace('{ctx}', subDomain ? (lang === 'ar' ? ' في هذا المجال' : ' à ce domaine') : '')}
                    </p>
                  )}
                  {subStatus === 'error' && (
                    <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                      {t('db.sub_error')}
                    </p>
                  )}

                  <button
                    type="submit"
                    disabled={subStatus === 'loading'}
                    className="w-full py-2.5 bg-navy text-white rounded-xl text-sm font-bold hover:bg-gold hover:text-navy transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {subStatus === 'loading' ? (
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                      </svg>
                    ) : <Mail size={15} />}
                    {subStatus === 'loading' ? t('db.subscribing') : t('db.subscribe')}
                  </button>

                  <p className="text-[10px] text-center text-navy-400">
                    {t('db.sub_note')}
                  </p>
                </form>
              </>
            )}
          </div>
        </div>
      )}
      {/* Page header */}
      <div className="bg-navy text-white py-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <h1 className="font-playfair font-bold text-2xl sm:text-3xl mb-1">{t('db.title')}</h1>
          <p className="text-white/60 text-sm mb-4">
            <span className="text-gold font-semibold">{total}</span> {t('db.results')}
          </p>
          {/* Liens rapides */}
          <div className="flex flex-wrap gap-2">
            {[
              { to: `/${lang}/guides`,              icon: BookOpen,   key: 'db.link_guides' },
              { to: `/${lang}/veille-juridique`,    icon: Bell,       key: 'db.link_veille' },
              { to: `/${lang}/bulletins-officiels`, icon: Newspaper,  key: 'db.link_bo' },
              { to: '/domaines',                    icon: Building2,  key: 'db.link_domaines' },
              { to: '/assistant',                   icon: Bot,        key: 'db.link_ai' },
            ].map(({ to, icon: Icon, key }) => (
              <Link
                key={key}
                to={to}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-xs text-white/80 hover:bg-gold hover:border-gold hover:text-navy transition-colors font-medium"
              >
                <Icon size={12} /> {t(key)}
              </Link>
            ))}
            {/* Bouton abonnement domaine */}
            <button
              onClick={() => setSubPopup(true)}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-gold/20 border border-gold/40 rounded-lg text-xs text-gold font-semibold hover:bg-gold hover:border-gold hover:text-navy transition-colors"
            >
              <Mail size={12} /> {t('db.subscribe_btn')}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile filter drawer */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="absolute inset-0 bg-black/40" onClick={() => setSidebarOpen(false)} />
          <aside className="relative z-10 w-80 max-w-[85vw] bg-white h-full overflow-y-auto shadow-xl p-4">
            <div className="flex items-center justify-between mb-4">
              <span className="font-semibold text-navy text-sm">{t('db.filters')}</span>
              <button onClick={() => setSidebarOpen(false)} className="p-2.5 rounded-lg hover:bg-gray-100 text-navy-500">
                <ChevronLeft size={16} />
              </button>
            </div>
            <FilterSidebar filters={filters} onChange={f => { handleFiltersChange(f); setSidebarOpen(false) }} resultCount={total} domains={domains} domainsLoading={domainsLoading} />
          </aside>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex gap-6">

          {/* Sidebar — desktop only */}
          <div className={`hidden lg:block flex-shrink-0 transition-all duration-300 ${sidebarOpen ? 'w-72' : 'w-0 overflow-hidden'}`}>
            <FilterSidebar filters={filters} onChange={handleFiltersChange} resultCount={total} domains={domains} domainsLoading={domainsLoading} />
          </div>

          {/* Main content */}
          <div className="flex-1 min-w-0">
            {/* Sort bar */}
            <div className="flex flex-wrap items-center gap-3 mb-5">
              <button
                onClick={() => setSidebarOpen(v => !v)}
                className="hidden lg:flex items-center gap-1.5 px-3 py-2 rounded-lg border border-gray-200 bg-white text-xs text-navy-700 hover:border-gold hover:text-gold transition-colors"
              >
                <SlidersHorizontal size={13} />
                {sidebarOpen ? t('db.hide_filters') : t('db.show_filters')}
              </button>

              <button
                onClick={() => setSidebarOpen(v => !v)}
                className="lg:hidden flex items-center gap-1.5 px-3 py-2 rounded-lg border border-gray-200 bg-white text-xs text-navy-700"
              >
                <SlidersHorizontal size={13} />{t('db.filters')}
              </button>

              <div className="flex bg-white rounded-lg border border-gray-200 overflow-hidden">
                {SORTS.map(s => (
                  <button
                    key={s.key}
                    onClick={() => setSort(s.key)}
                    className={`px-3 py-2 text-xs font-medium transition-colors ${
                      sort === s.key ? 'bg-navy text-white' : 'text-navy-600 hover:text-navy'
                    }`}
                  >
                    {s.label}
                  </button>
                ))}
              </div>

              <div className="flex gap-1 ml-auto">
                <button
                  onClick={() => setView('grid')}
                  className={`p-2 rounded-lg transition-colors ${view === 'grid' ? 'bg-navy text-white' : 'bg-white border border-gray-200 text-navy-600'}`}
                >
                  <Grid3X3 size={14} />
                </button>
                <button
                  onClick={() => setView('list')}
                  className={`p-2 rounded-lg transition-colors ${view === 'list' ? 'bg-navy text-white' : 'bg-white border border-gray-200 text-navy-600'}`}
                >
                  <List size={14} />
                </button>
              </div>
            </div>

            {/* Mobile sidebar */}
            {sidebarOpen && (
              <div className="lg:hidden mb-4">
                <FilterSidebar filters={filters} onChange={handleFiltersChange} resultCount={total} domains={domains} domainsLoading={domainsLoading} />
              </div>
            )}

            {/* Results */}
            {loading ? (
              <SkeletonGrid count={PAGE_SIZE} />
            ) : laws.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-24 text-center">
                <FileX size={48} className="text-gray-300 mb-4" />
                <h3 className="font-semibold text-navy text-lg mb-2">{t('db.empty_title')}</h3>
                <p className="text-navy-600 text-sm mb-4">{t('db.empty_sub')}</p>
                <button
                  onClick={() => handleFiltersChange({ q: '', types: [], domains: [], statuses: [], languages: [], dateFrom: '', dateTo: '' })}
                  className="px-4 py-2 bg-navy text-white rounded-lg text-sm hover:bg-gold hover:text-navy transition-colors"
                >
                  {t('db.clear_filters')}
                </button>
              </div>
            ) : view === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {laws.map((law, i) => (
                  <div key={law.id} className="animate-fade-in" style={{ animationDelay: `${i * 50}ms` }}>
                    <LawCard law={law} view="grid" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {laws.map((law, i) => (
                  <div key={law.id} className="animate-fade-in" style={{ animationDelay: `${i * 40}ms` }}>
                    <LawCard law={law} view="list" />
                  </div>
                ))}
              </div>
            )}

            {/* Pagination — centrée sur la page courante */}
            {totalPages > 1 && !loading && (
              <div className="flex items-center justify-center gap-2 mt-8 flex-wrap">
                {/* Bouton Précédent */}
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="p-2.5 rounded-lg border border-gray-200 bg-white text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  {isRTL ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
                </button>

                {/* Pages : fenêtre glissante de 5 pages centrée sur la page courante */}
                {(() => {
                  const WINDOW = 5
                  let start = Math.max(1, page - Math.floor(WINDOW / 2))
                  let end   = Math.min(totalPages, start + WINDOW - 1)
                  if (end - start < WINDOW - 1) start = Math.max(1, end - WINDOW + 1)
                  const pages = Array.from({ length: end - start + 1 }, (_, i) => start + i)
                  return (
                    <>
                      {start > 1 && (
                        <>
                          <button onClick={() => setPage(1)} className="w-10 h-10 rounded-lg text-sm bg-white border border-gray-200 text-navy-600 hover:border-gold transition-colors">1</button>
                          {start > 2 && <span className="text-navy-400 text-sm px-1">…</span>}
                        </>
                      )}
                      {pages.map(p => (
                        <button
                          key={p}
                          onClick={() => setPage(p)}
                          className={`w-10 h-10 rounded-lg text-sm font-medium transition-colors ${
                            p === page ? 'bg-navy text-white' : 'bg-white border border-gray-200 text-navy-600 hover:border-gold'
                          }`}
                        >
                          {p}
                        </button>
                      ))}
                      {end < totalPages && (
                        <>
                          {end < totalPages - 1 && <span className="text-navy-400 text-sm px-1">…</span>}
                          <button onClick={() => setPage(totalPages)} className="w-10 h-10 rounded-lg text-sm bg-white border border-gray-200 text-navy-600 hover:border-gold transition-colors">{totalPages}</button>
                        </>
                      )}
                    </>
                  )
                })()}

                {/* Bouton Suivant */}
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="p-2.5 rounded-lg border border-gray-200 bg-white text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  {isRTL ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
                </button>

                <span className="text-xs text-navy-500 ml-2 whitespace-nowrap">
                  {t('common.page')} {page} {t('common.of')} {totalPages}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* ── Explorer par besoin juridique ──────────────────────────────── */}
        {(() => {
          const FEATURED = ['code-du-travail-maroc','sarl-maroc','divorce-maroc','bail-commercial-maroc','licenciement-maroc','recouvrement-maroc','cheque-sans-provision-maroc','code-de-la-famille-maroc','creation-societe-maroc','procedure-civile-maroc']
          const featured = SEO_INTENT_PAGES.filter(g => FEATURED.includes(g.slug))
          return (
            <div className="mt-12 pt-8 border-t border-gray-200">
              <p className="text-xs font-semibold uppercase tracking-widest text-gold mb-4 flex items-center gap-1.5">
                <BookOpen size={11} /> {t('db.explore_title')}
              </p>
              <div className="flex flex-wrap gap-2">
                {featured.map(guide => (
                  <Link
                    key={guide.slug}
                    to={`/${lang}/guides/${guide.slug}`}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-white border border-gray-200 rounded-xl text-xs text-navy-700 hover:border-gold hover:text-gold transition-colors"
                  >
                    <BookOpen size={11} className="text-gold flex-shrink-0" />
                    {lang === 'ar' && guide.h1_ar ? guide.h1_ar : guide.h1}
                  </Link>
                ))}
              </div>
            </div>
          )
        })()}
      </div>
    </div>
  )
}
