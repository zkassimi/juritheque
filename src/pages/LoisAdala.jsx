/**
 * /fr/lois-complementaires
 * ──────────────────────────
 * Affiche les lois complémentaires issues d'Adala (Ministère de la Justice)
 * depuis le fichier JSON statique public/data/lois-adala.json
 *
 * Les PDF sont hébergés sur Cloudflare R2 (Adala).
 * Aucun PDF n'est stocké dans Supabase ni sur ce serveur.
 */
import { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
  ExternalLink, Calendar, Search, Scale, ChevronLeft, ChevronRight,
  FileText, Bot, Bell, Newspaper, Filter, X, BookOpen, Tag, Globe
} from 'lucide-react'
import { useSEO } from '../hooks/useSEO'
import { useLang } from '../contexts/LangContext'
import JsonLD, { breadcrumbSchema } from '../components/JsonLD'

const PAGE_SIZE = 24

// ── Badges ────────────────────────────────────────────────────────────────────
function TypeBadge({ type }) {
  if (!type) return null
  const colors = {
    'Loi':            'bg-blue-50 text-blue-700 border-blue-100',
    'Loi organique':  'bg-indigo-50 text-indigo-700 border-indigo-100',
    'Dahir':          'bg-amber-50 text-amber-700 border-amber-100',
    'Décret':         'bg-violet-50 text-violet-700 border-violet-100',
    'Décret royal':   'bg-purple-50 text-purple-700 border-purple-100',
    'Arrêté':         'bg-emerald-50 text-emerald-700 border-emerald-100',
    'Circulaire':     'bg-teal-50 text-teal-700 border-teal-100',
    'Code':           'bg-rose-50 text-rose-700 border-rose-100',
  }
  const cls = colors[type] || 'bg-gray-50 text-gray-600 border-gray-100'
  return (
    <span className={`inline-flex items-center text-[10px] font-semibold px-2 py-0.5 rounded-full border ${cls}`}>
      {type}
    </span>
  )
}

// ── Card ──────────────────────────────────────────────────────────────────────
function LoisCard({ loi }) {
  const dateFormatted = loi.date
    ? new Date(loi.date).toLocaleDateString('fr-MA', { day: 'numeric', month: 'long', year: 'numeric' })
    : loi.year ? String(loi.year) : '—'

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5 hover:shadow-md hover:border-gold/40 transition-all duration-200 flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-gold mb-0.5">
            n°&nbsp;{loi.number}
          </p>
          <p
            className="text-sm font-semibold text-navy leading-snug line-clamp-2 font-arabic text-right"
            dir="rtl"
          >
            {loi.title_ar}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1 flex-shrink-0">
          <TypeBadge type={loi.type_fr || loi.type_ar} />
        </div>
      </div>

      {/* Date + Domaine */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className="flex items-center gap-1 text-xs text-navy-500">
          <Calendar size={11} className="flex-shrink-0" />
          {dateFormatted}
        </span>
        {loi.domain && (
          <span className="flex items-center gap-1 text-[10px] text-navy-400 bg-gray-50 px-2 py-0.5 rounded-full">
            <Tag size={9} />
            {loi.domain}
          </span>
        )}
      </div>

      {/* Tags arabes */}
      {loi.tags && loi.tags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {loi.tags.slice(0, 3).map((tag, i) => (
            <span key={i} className="text-[9px] bg-navy/5 text-navy-500 px-1.5 py-0.5 rounded font-arabic" dir="rtl">
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="pt-3 border-t border-gray-50 flex items-center justify-between">
        <span className="flex items-center gap-1 text-[10px] text-navy-400">
          <Globe size={9} />
          Adala · Justice.gov.ma
        </span>
        {loi.pdfUrl ? (
          <a
            href={loi.pdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-navy text-white rounded-lg text-xs font-medium hover:bg-gold hover:text-navy transition-colors"
            onClick={e => e.stopPropagation()}
          >
            <ExternalLink size={11} />
            PDF officiel
          </a>
        ) : (
          <span className="text-[10px] text-navy-300 italic">Lien indisponible</span>
        )}
      </div>
    </div>
  )
}

// ── Page principale ───────────────────────────────────────────────────────────
export default function LoisAdala() {
  const { lang } = useLang()

  const [allLois, setAllLois]       = useState([])
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState(null)
  const [page, setPage]             = useState(1)

  // Filtres
  const [search, setSearch]         = useState('')
  const [filterYear, setFilterYear] = useState('')
  const [filterType, setFilterType] = useState('')
  const [filterDomain, setFilterDomain] = useState('')

  useSEO({
    title:       'Lois complémentaires — Adala Ministère de la Justice | JuriThèque',
    description: 'Accédez aux textes juridiques marocains issus d\'Adala, le portail officiel du Ministère de la Justice. Lois, décrets, dahirs — liens directs vers les PDF officiels.',
    canonical:   '/fr/lois-complementaires',
    type:        'website',
  })

  // Chargement du JSON statique
  useEffect(() => {
    setLoading(true)
    fetch('/data/lois-adala.json')
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(data => {
        setAllLois(Array.isArray(data) ? data : [])
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  // Réinitialiser page quand les filtres changent
  useEffect(() => { setPage(1) }, [search, filterYear, filterType, filterDomain])

  // Filtrage
  const filtered = useMemo(() => {
    return allLois.filter(loi => {
      if (filterYear   && String(loi.year)   !== filterYear)   return false
      if (filterType   && loi.type_fr        !== filterType)   return false
      if (filterDomain && loi.domain         !== filterDomain) return false
      if (search) {
        const q = search.toLowerCase()
        if (!String(loi.number).toLowerCase().includes(q) &&
            !(loi.title_ar || '').toLowerCase().includes(q) &&
            !(loi.type_fr  || '').toLowerCase().includes(q)) return false
      }
      return true
    })
  }, [allLois, search, filterYear, filterType, filterDomain])

  // Options de filtres dynamiques
  const years = useMemo(() =>
    [...new Set(allLois.map(l => l.year).filter(Boolean))].sort((a, b) => b - a),
    [allLois]
  )
  const types = useMemo(() =>
    [...new Set(allLois.map(l => l.type_fr).filter(Boolean))].sort(),
    [allLois]
  )
  const domains = useMemo(() =>
    [...new Set(allLois.map(l => l.domain).filter(Boolean))].sort(),
    [allLois]
  )

  // Pagination
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)
  const paginated  = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const hasFilters = search || filterYear || filterType || filterDomain
  const clearFilters = () => {
    setSearch(''); setFilterYear(''); setFilterType(''); setFilterDomain('')
  }

  // JSON-LD
  const breadcrumbs = [
    { name: 'Accueil',              url: '/' },
    { name: 'Lois complémentaires', url: '/fr/lois-complementaires' },
  ]

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      <JsonLD data={[breadcrumbSchema(breadcrumbs)]} />

      {/* ── Header ── */}
      <div className="bg-navy text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 mb-4 text-xs text-white/50">
            <Link to="/" className="hover:text-gold transition-colors">Accueil</Link>
            <ChevronRight size={10} />
            <span className="text-white/80">Lois complémentaires</span>
          </div>

          <div className="flex items-start gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center flex-shrink-0">
              <Scale size={22} className="text-gold" />
            </div>
            <div>
              <h1 className="font-playfair font-bold text-3xl mb-1">
                Lois complémentaires
              </h1>
              <p className="text-white/60 text-sm leading-relaxed max-w-xl">
                Textes juridiques issus d'
                <a href="https://adala.justice.gov.ma" target="_blank" rel="noopener noreferrer"
                   className="text-gold hover:underline">Adala</a>
                , le portail officiel du{' '}
                <strong className="text-white/80">Ministère de la Justice</strong>.
                Ces textes complètent la base de données JuriThèque.
                Les PDF sont accessibles via les liens officiels.
              </p>
              {allLois.length > 0 && (
                <p className="text-gold text-sm mt-2">{allLois.length} textes référencés</p>
              )}
            </div>
          </div>

          {/* Barre de recherche + filtres */}
          <div className="flex flex-wrap gap-2 items-center">
            {/* Recherche */}
            <div className="relative">
              <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Numéro, ex: 2.25.100…"
                className="pl-8 pr-3 py-2 bg-white/10 border border-white/20 rounded-xl text-sm text-white placeholder-white/40 focus:outline-none focus:border-gold w-48"
              />
            </div>

            {/* Filtre type */}
            <select
              value={filterType}
              onChange={e => setFilterType(e.target.value)}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-sm text-white focus:outline-none focus:border-gold"
            >
              <option value="">Tous types</option>
              {types.map(t => <option key={t} value={t}>{t}</option>)}
            </select>

            {/* Filtre année */}
            <select
              value={filterYear}
              onChange={e => setFilterYear(e.target.value)}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-sm text-white focus:outline-none focus:border-gold"
            >
              <option value="">Toutes années</option>
              {years.map(y => <option key={y} value={y}>{y}</option>)}
            </select>

            {/* Filtre domaine */}
            {domains.length > 0 && (
              <select
                value={filterDomain}
                onChange={e => setFilterDomain(e.target.value)}
                className="px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-sm text-white focus:outline-none focus:border-gold"
              >
                <option value="">Tous domaines</option>
                {domains.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            )}

            {hasFilters && (
              <button
                onClick={clearFilters}
                className="flex items-center gap-1 px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-xs text-white/70 hover:bg-white/20 transition-colors"
              >
                <X size={11} /> Effacer
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Contenu ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="bg-white rounded-xl border border-gray-100 p-5 h-44 animate-pulse">
                <div className="h-3 bg-gray-100 rounded w-1/3 mb-2" />
                <div className="h-4 bg-gray-100 rounded w-3/4 mb-3" />
                <div className="h-3 bg-gray-100 rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <Scale size={40} className="text-gray-200 mx-auto mb-4" />
            <p className="text-navy-500 text-sm mb-2">Erreur de chargement</p>
            <p className="text-navy-400 text-xs">
              Lance{' '}
              <code className="bg-gray-100 px-1.5 py-0.5 rounded text-navy-600">
                python pipeline/build_lois_adala.py
              </code>{' '}
              pour générer le fichier.
            </p>
          </div>
        ) : allLois.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-gray-100">
            <Scale size={40} className="text-gray-200 mx-auto mb-4" />
            <p className="text-navy-600 font-medium text-sm mb-2">Aucune loi disponible</p>
            <p className="text-navy-400 text-xs mb-4 max-w-sm mx-auto">
              Le fichier est vide. Génère-le avec le script Python :
            </p>
            <code className="bg-gray-100 text-navy-700 px-4 py-2 rounded-lg text-xs">
              python pipeline/build_lois_adala.py
            </code>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16">
            <Filter size={32} className="text-gray-200 mx-auto mb-3" />
            <p className="text-navy-500 text-sm">Aucun résultat pour ces filtres.</p>
            <button onClick={clearFilters} className="mt-3 text-xs text-gold hover:underline">
              Effacer les filtres
            </button>
          </div>
        ) : (
          <>
            {/* Résultats */}
            <div className="flex items-center justify-between mb-4">
              <p className="text-xs text-navy-500">
                {filtered.length} texte{filtered.length > 1 ? 's' : ''}
                {hasFilters ? ' (filtré)' : ''}
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {paginated.map((loi, i) => (
                <LoisCard key={`${loi.id || loi.number}-${i}`} loi={loi} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-10 flex-wrap">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="p-2 rounded-lg border border-gray-200 bg-white text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft size={16} />
                </button>

                {(() => {
                  const WINDOW = 5
                  let start = Math.max(1, page - Math.floor(WINDOW / 2))
                  let end   = Math.min(totalPages, start + WINDOW - 1)
                  if (end - start < WINDOW - 1) start = Math.max(1, end - WINDOW + 1)
                  return Array.from({ length: end - start + 1 }, (_, i) => start + i).map(p => (
                    <button
                      key={p}
                      onClick={() => setPage(p)}
                      className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${
                        p === page ? 'bg-navy text-white' : 'bg-white border border-gray-200 text-navy-600 hover:border-gold'
                      }`}
                    >
                      {p}
                    </button>
                  ))
                })()}

                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="p-2 rounded-lg border border-gray-200 bg-white text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight size={16} />
                </button>
                <span className="text-xs text-navy-400">Page {page}/{totalPages}</span>
              </div>
            )}
          </>
        )}

        {/* ── Info officielle ── */}
        <div className="mt-10 p-5 bg-white rounded-2xl border border-gray-100">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center flex-shrink-0">
              <FileText size={14} className="text-blue-500" />
            </div>
            <div>
              <p className="text-xs font-semibold text-navy mb-1">À propos de ces textes</p>
              <p className="text-xs text-navy-500 leading-relaxed">
                Ces textes juridiques sont issus d'
                <a href="https://adala.justice.gov.ma" target="_blank" rel="noopener noreferrer"
                   className="text-gold hover:underline font-medium">Adala</a>
                , le portail officiel du{' '}
                <strong>Ministère de la Justice du Maroc</strong>.
                Ils sont présentés ici à titre de référence complémentaire et ne font pas partie
                de la base de données principale JuriThèque. Les titres sont en arabe (langue d'origine).
                Les PDF sont accessibles directement via les liens officiels.
              </p>
            </div>
          </div>
        </div>

        {/* ── Maillage interne ── */}
        <div className="mt-6 pt-6 border-t border-gray-100 flex flex-wrap gap-3">
          <Link to="/base"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors">
            <FileText size={12} className="text-gold" /> Base de données
          </Link>
          <Link to="/fr/bulletins-officiels"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors">
            <Newspaper size={12} className="text-gold" /> Bulletins Officiels
          </Link>
          <Link to="/fr/veille-juridique"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors">
            <Bell size={12} className="text-gold" /> Veille juridique
          </Link>
          <Link to="/fr/guides"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors">
            <BookOpen size={12} className="text-gold" /> Guides juridiques
          </Link>
          <Link to="/assistant"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors">
            <Bot size={12} className="text-gold" /> Assistant IA
          </Link>
        </div>
      </div>
    </div>
  )
}
