import { useState } from 'react'
import { ChevronDown, X, SlidersHorizontal } from 'lucide-react'
import { useLang } from '../contexts/LangContext'
import { LAW_TYPES, DOMAINS as DOMAINS_FALLBACK } from '../data/mockData'
import SearchBar from './SearchBar'

const STATUSES = ['En vigueur', 'Abrogé', 'Modifié']
const LANGUAGES = ['FR', 'AR', 'Bilingue']

function AccordionSection({ title, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="border-b border-gray-100 pb-4 mb-4 last:border-0 last:mb-0">
      <button
        onClick={() => setOpen(v => !v)}
        className="flex items-center justify-between w-full mb-3 group"
      >
        <span className="text-xs font-semibold uppercase tracking-widest text-navy-600 group-hover:text-gold transition-colors">{title}</span>
        <ChevronDown size={14} className={`text-navy-500 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && children}
    </div>
  )
}

/**
 * FilterSidebar
 * @param {Object}   filters      - état des filtres actifs
 * @param {Function} onChange     - callback quand un filtre change
 * @param {number}   resultCount  - total de résultats (affiché en haut)
 * @param {Array}    domains      - liste des domaines depuis Supabase (optionnel, fallback mockData)
 * @param {boolean}  domainsLoading - true pendant le chargement des domaines
 */
export default function FilterSidebar({ filters, onChange, resultCount, domains: domainsProp, domainsLoading = false }) {
  const { t, lang } = useLang()

  // Utilise les domaines Supabase s'ils sont disponibles, sinon mockData en fallback
  const domainList = domainsProp && domainsProp.length > 0 ? domainsProp : DOMAINS_FALLBACK

  const toggle = (key, value) => {
    const current = filters[key] ?? []
    const next = current.includes(value) ? current.filter(v => v !== value) : [...current, value]
    onChange({ ...filters, [key]: next })
  }

  const clearAll = () => onChange({ types: [], domains: [], statuses: [], languages: [], dateFrom: '', dateTo: '' })

  const hasFilters = (filters.types?.length + filters.domains?.length + filters.statuses?.length + filters.languages?.length) > 0

  return (
    <aside className="bg-white rounded-2xl border border-gray-100 p-5 h-fit sticky top-20">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <SlidersHorizontal size={15} className="text-gold" />
          <span className="font-semibold text-navy text-sm">{t('db.filters')}</span>
        </div>
        {hasFilters && (
          <button onClick={clearAll} className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1">
            <X size={11} />{t('db.clear_filters')}
          </button>
        )}
      </div>

      {/* Search */}
      <SearchBar size="sm" onSearch={q => onChange({ ...filters, q })} className="mb-4" />

      {/* Results count */}
      {resultCount !== undefined && (
        <p className="text-xs text-navy-500 mb-4">
          <strong className="text-gold">{resultCount}</strong> {t('db.results')}
        </p>
      )}

      {/* Type filter */}
      <AccordionSection title={t('db.type')}>
        <div className="flex flex-wrap gap-1.5">
          {Object.entries(LAW_TYPES).map(([type, cfg]) => {
            const active = filters.types?.includes(type)
            return (
              <button
                key={type}
                onClick={() => toggle('types', type)}
                className="px-2.5 py-1 rounded text-xs font-medium border transition-all duration-150"
                style={active
                  ? { backgroundColor: cfg.color, color: '#fff', borderColor: cfg.color }
                  : { backgroundColor: cfg.bg, color: cfg.color, borderColor: `${cfg.color}40` }
                }
              >
                {lang === 'ar' ? cfg.label_ar : type}
              </button>
            )
          })}
        </div>
      </AccordionSection>

      {/* Domain filter */}
      <AccordionSection title={t('db.domain')}>
        {domainsLoading ? (
          <div className="space-y-1">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-8 bg-gray-100 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-1">
            {domainList.map(d => {
              const active = filters.domains?.includes(d.id)
              const label  = lang === 'ar' ? (d.ar || d.name_ar || d.fr || d.name_fr) : (d.fr || d.name_fr || d.ar || d.name_ar)
              const count  = d.count ?? d.law_count ?? 0
              return (
                <button
                  key={d.id}
                  onClick={() => toggle('domains', d.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs transition-colors ${
                    active ? 'bg-navy text-white' : 'text-navy-700 hover:bg-gray-50'
                  }`}
                >
                  <span className="truncate text-start">{label}</span>
                  <span className={`flex-shrink-0 text-[10px] px-1.5 py-0.5 rounded ml-1 ${active ? 'bg-white/20 text-white' : 'bg-gray-100 text-navy-500'}`}>
                    {count}
                  </span>
                </button>
              )
            })}
          </div>
        )}
      </AccordionSection>

      {/* Status filter */}
      <AccordionSection title={t('db.status')}>
        <div className="space-y-1.5">
          {STATUSES.map(s => {
            const active = filters.statuses?.includes(s)
            const colors = {
              'En vigueur': 'emerald',
              'Abrogé': 'red',
              'Modifié': 'amber',
            }
            const c = colors[s]
            return (
              <button
                key={s}
                onClick={() => toggle('statuses', s)}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs transition-colors ${
                  active ? `bg-${c}-50 text-${c}-700 font-medium` : 'text-navy-700 hover:bg-gray-50'
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full bg-${c}-500`} />
                {t(`status.${s === 'En vigueur' ? 'active' : s === 'Abrogé' ? 'repealed' : 'modified'}`)}
              </button>
            )
          })}
        </div>
      </AccordionSection>

      {/* Date range */}
      <AccordionSection title={t('db.date_from') + ' / ' + t('db.date_to')} defaultOpen={false}>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-[10px] text-navy-500 mb-1 block">{t('db.date_from')}</label>
            <input
              type="date"
              value={filters.dateFrom ?? ''}
              onChange={e => onChange({ ...filters, dateFrom: e.target.value })}
              className="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
            />
          </div>
          <div>
            <label className="text-[10px] text-navy-500 mb-1 block">{t('db.date_to')}</label>
            <input
              type="date"
              value={filters.dateTo ?? ''}
              onChange={e => onChange({ ...filters, dateTo: e.target.value })}
              className="w-full px-2 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:border-gold"
            />
          </div>
        </div>
      </AccordionSection>

      {/* Language */}
      <AccordionSection title={t('db.language')} defaultOpen={false}>
        <div className="flex flex-wrap gap-1.5">
          {LANGUAGES.map(l => {
            const active = filters.languages?.includes(l)
            return (
              <button
                key={l}
                onClick={() => toggle('languages', l)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                  active ? 'bg-navy text-white border-navy' : 'border-gray-200 text-navy-700 hover:border-navy'
                }`}
              >
                {l}
              </button>
            )
          })}
        </div>
      </AccordionSection>
    </aside>
  )
}
