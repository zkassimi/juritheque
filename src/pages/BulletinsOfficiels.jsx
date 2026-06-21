/**
 * /fr/bulletins-officiels
 * ────────────────────────
 * Affiche les Bulletins Officiels du Maroc depuis le fichier JSON statique
 * public/data/bulletins-officiels.json
 *
 * Les PDF sont hébergés sur le site officiel du SGG (sgg.gov.ma).
 * Aucun PDF n'est stocké dans Supabase ni sur ce serveur.
 */
import { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
  ExternalLink, Calendar, Search, Newspaper, ChevronLeft, ChevronRight,
  FileText, Bot, Bell, BookOpen, Filter, X
} from 'lucide-react'
import { useSEO } from '../hooks/useSEO'
import { useLang } from '../contexts/LangContext'
import JsonLD, { breadcrumbSchema } from '../components/JsonLD'

const PAGE_SIZE = 24

// ── Badges ────────────────────────────────────────────────────────────────────
function LangBadge({ lang }) {
  if (lang === 'fr') return (
    <span className="inline-flex items-center text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 border border-blue-100">FR</span>
  )
  if (lang === 'ar') return (
    <span className="inline-flex items-center text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-100">AR</span>
  )
  return null
}

function EditionBadge({ edition }) {
  const cfg = {
    traduction_officielle: { label: 'Trad. officielle', cls: 'bg-violet-50 text-violet-600 border-violet-100' },
    edition_generale:      { label: 'Éd. générale',     cls: 'bg-amber-50 text-amber-600 border-amber-100' },
    unknown:               { label: 'Édition',          cls: 'bg-gray-50 text-gray-500 border-gray-100' },
  }
  const c = cfg[edition] || cfg.unknown
  return (
    <span className={`inline-flex items-center text-[10px] font-medium px-2 py-0.5 rounded-full border ${c.cls}`}>
      {c.label}
    </span>
  )
}

// ── Card ──────────────────────────────────────────────────────────────────────
function BOCard({ bo }) {
  const dateFormatted = bo.date
    ? new Date(bo.date).toLocaleDateString('fr-MA', { day: 'numeric', month: 'long', year: 'numeric' })
    : bo.year ? String(bo.year) : '—'

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5 hover:shadow-md hover:border-gold/40 transition-all duration-200 flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-widest text-gold mb-0.5">BO</p>
          <p className="font-playfair font-bold text-navy text-2xl leading-none">
            n°&nbsp;{bo.number}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <LangBadge lang={bo.language} />
          <EditionBadge edition={bo.edition} />
        </div>
      </div>

      {/* Date */}
      <p className="flex items-center gap-1.5 text-xs text-navy-500">
        <Calendar size={11} className="flex-shrink-0" />
        {dateFormatted}
      </p>

      {/* Title */}
      <p className="text-xs text-navy-600 leading-relaxed line-clamp-2 flex-1">
        {bo.title}
      </p>

      {/* Footer */}
      <div className="pt-3 border-t border-gray-50 flex items-center justify-between">
        <span className="text-[10px] text-navy-400 uppercase tracking-wide">SGG.gov.ma</span>
        <a
          href={bo.officialUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-navy text-white rounded-lg text-xs font-medium hover:bg-gold hover:text-navy transition-colors"
          onClick={e => e.stopPropagation()}
        >
          <ExternalLink size={11} />
          PDF officiel
        </a>
      </div>
    </div>
  )
}

// ── Page principale ───────────────────────────────────────────────────────────
export default function BulletinsOfficiels() {
  const { lang } = useLang()

  const [allBOs, setAllBOs]         = useState([])
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState(null)
  const [page, setPage]             = useState(1)

  // Filtres
  const [search, setSearch]         = useState('')
  const [filterYear, setFilterYear] = useState('')
  const [filterLang, setFilterLang] = useState('')
  const [filterEd, setFilterEd]     = useState('')

  useSEO({
    title:       'Bulletins Officiels du Maroc | JuriThèque',
    description: 'Consultez les liens officiels des Bulletins Officiels du Maroc publiés par le Secrétariat Général du Gouvernement. Accès direct aux PDF officiels.',
    canonical:   '/fr/bulletins-officiels',
    type:        'website',
  })

  // Chargement du JSON statique
  useEffect(() => {
    setLoading(true)
    fetch('/data/bulletins-officiels.json')
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then(data => {
        setAllBOs(Array.isArray(data) ? data : [])
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  // Réinitialiser page quand les filtres changent
  useEffect(() => { setPage(1) }, [search, filterYear, filterLang, filterEd])

  // Filtrage
  const filtered = useMemo(() => {
    return allBOs.filter(bo => {
      if (filterYear && String(bo.year) !== filterYear) return false
      if (filterLang && bo.language !== filterLang) return false
      if (filterEd   && bo.edition !== filterEd)    return false
      if (search) {
        const q = search.toLowerCase()
        if (!String(bo.number).includes(q) &&
            !(bo.title || '').toLowerCase().includes(q)) return false
      }
      return true
    })
  }, [allBOs, search, filterYear, filterLang, filterEd])

  // Options de filtres dynamiques
  const years = useMemo(() =>
    [...new Set(allBOs.map(b => b.year).filter(Boolean))].sort((a, b) => b - a),
    [allBOs]
  )

  // Pagination
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)
  const paginated  = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const hasFilters = search || filterYear || filterLang || filterEd
  const clearFilters = () => {
    setSearch(''); setFilterYear(''); setFilterLang(''); setFilterEd('')
  }

  // JSON-LD
  const breadcrumbs = [
    { name: 'Accueil',             url: '/' },
    { name: 'Bulletins Officiels', url: '/fr/bulletins-officiels' },
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
            <span className="text-white/80">Bulletins Officiels</span>
          </div>

          <div className="flex items-start gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center flex-shrink-0">
              <Newspaper size={22} className="text-gold" />
            </div>
            <div>
              <h1 className="font-playfair font-bold text-3xl mb-1">
                Bulletins Officiels du Maroc
              </h1>
              <p className="text-white/60 text-sm leading-relaxed max-w-xl">
                Journal officiel du Royaume — publiés par le Secrétariat Général du Gouvernement.
                Les PDF sont hébergés sur le site officiel{' '}
                <a href="https://www.sgg.gov.ma" target="_blank" rel="noopener noreferrer"
                   className="text-gold hover:underline">sgg.gov.ma</a>.
              </p>
              {allBOs.length > 0 && (
                <p className="text-gold text-sm mt-2">{allBOs.length} bulletins référencés</p>
              )}
            </div>
          </div>

          {/* Barre de recherche + filtres */}
          <div className="flex flex-wrap gap-2 items-center">
            {/* Recherche numéro */}
            <div className="relative">
              <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Numéro, ex: 7432…"
                className="pl-8 pr-3 py-2 bg-white/10 border border-white/20 rounded-xl text-sm text-white placeholder-white/40 focus:outline-none focus:border-gold w-44"
              />
            </div>

            {/* Filtre année */}
            <select
              value={filterYear}
              onChange={e => setFilterYear(e.target.value)}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-sm text-white focus:outline-none focus:border-gold"
            >
              <option value="">Toutes les années</option>
              {years.map(y => <option key={y} value={y}>{y}</option>)}
            </select>

            {/* Filtre langue */}
            <select
              value={filterLang}
              onChange={e => setFilterLang(e.target.value)}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-sm text-white focus:outline-none focus:border-gold"
            >
              <option value="">FR + AR</option>
              <option value="fr">Français</option>
              <option value="ar">Arabe</option>
            </select>

            {/* Filtre édition */}
            <select
              value={filterEd}
              onChange={e => setFilterEd(e.target.value)}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-xl text-sm text-white focus:outline-none focus:border-gold"
            >
              <option value="">Toutes éditions</option>
              <option value="traduction_officielle">Traduction officielle</option>
              <option value="edition_generale">Édition générale (AR)</option>
            </select>

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
              <div key={i} className="bg-white rounded-xl border border-gray-100 p-5 h-40 animate-pulse">
                <div className="h-3 bg-gray-100 rounded w-1/3 mb-3" />
                <div className="h-7 bg-gray-100 rounded w-1/2 mb-4" />
                <div className="h-3 bg-gray-100 rounded w-2/3" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <Newspaper size={40} className="text-gray-200 mx-auto mb-4" />
            <p className="text-navy-500 text-sm mb-2">Erreur de chargement</p>
            <p className="text-navy-400 text-xs">
              Lance <code className="bg-gray-100 px-1.5 py-0.5 rounded text-navy-600">
                python pipeline/build_bo_links.py
              </code> pour générer le fichier.
            </p>
          </div>
        ) : allBOs.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-gray-100">
            <Newspaper size={40} className="text-gray-200 mx-auto mb-4" />
            <p className="text-navy-600 font-medium text-sm mb-2">Aucun bulletin disponible</p>
            <p className="text-navy-400 text-xs mb-4 max-w-sm mx-auto">
              Le fichier de bulletins est vide. Génère-le avec le script Python :
            </p>
            <code className="bg-gray-100 text-navy-700 px-4 py-2 rounded-lg text-xs">
              python pipeline/build_bo_links.py
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
                {filtered.length} bulletin{filtered.length > 1 ? 's' : ''}
                {hasFilters ? ' (filtré)' : ''}
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {paginated.map((bo, i) => <BOCard key={`${bo.number}-${bo.language}-${i}`} bo={bo} />)}
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
              <p className="text-xs font-semibold text-navy mb-1">À propos des Bulletins Officiels</p>
              <p className="text-xs text-navy-500 leading-relaxed">
                Le Bulletin Officiel du Royaume du Maroc est publié par le{' '}
                <strong>Secrétariat Général du Gouvernement (SGG)</strong>.
                Il contient l'ensemble des textes législatifs et réglementaires officiellement promulgués.
                Les liens de cette page redirigent vers les documents PDF hébergés sur{' '}
                <a href="https://www.sgg.gov.ma" target="_blank" rel="noopener noreferrer"
                   className="text-gold hover:underline font-medium">sgg.gov.ma</a>.
              </p>
            </div>
          </div>
        </div>

        {/* ── Maillage interne ── */}
        <div className="mt-6 pt-6 border-t border-gray-100 flex flex-wrap gap-3">
          <Link to="/fr/veille-juridique"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors">
            <Bell size={12} className="text-gold" /> Veille juridique
          </Link>
          <Link to="/base"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors">
            <FileText size={12} className="text-gold" /> Base de données
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
