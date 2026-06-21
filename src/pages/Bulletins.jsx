import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ExternalLink, Calendar, ChevronLeft, ChevronRight, Search, Newspaper } from 'lucide-react'
import { supabase } from '../lib/supabase'
import { useSEO } from '../hooks/useSEO'
import { SkeletonGrid } from '../components/ui/SkeletonLoader'

const PAGE_SIZE = 24

export default function Bulletins() {
  const [bulletins, setBulletins] = useState([])
  const [total, setTotal]         = useState(0)
  const [page, setPage]           = useState(1)
  const [loading, setLoading]     = useState(true)
  const [search, setSearch]       = useState('')
  const [searchInput, setSearchInput] = useState('')

  useSEO({
    title: 'Bulletins Officiels du Maroc — JuriThèque',
    description: 'Accédez aux Bulletins Officiels du Royaume du Maroc publiés par le Secrétariat Général du Gouvernement (SGG). Liste complète avec liens officiels.',
    canonical: '/bulletins',
    type: 'website',
  })

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    const from = (page - 1) * PAGE_SIZE
    let query = supabase
      .from('bulletins_officiels')
      .select('*', { count: 'exact' })
      .order('date', { ascending: false, nullsFirst: false })
      .range(from, from + PAGE_SIZE - 1)

    if (search) {
      query = query.or(`number.ilike.%${search}%,title.ilike.%${search}%,description.ilike.%${search}%`)
    }

    query.then(({ data, count, error }) => {
      if (cancelled) return
      if (!error) {
        setBulletins(data || [])
        setTotal(count || 0)
      }
      setLoading(false)
    })

    return () => { cancelled = true }
  }, [page, search])

  useEffect(() => { setPage(1) }, [search])

  const handleSearch = (e) => {
    e.preventDefault()
    setSearch(searchInput.trim())
  }

  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">

      {/* Header */}
      <div className="bg-navy text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center gap-3 mb-4">
            <Link to="/" className="text-white/50 text-xs hover:text-gold transition-colors">Accueil</Link>
            <span className="text-white/30 text-xs">/</span>
            <span className="text-white/80 text-xs">Bulletins Officiels</span>
          </div>
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center flex-shrink-0">
              <Newspaper size={22} className="text-gold" />
            </div>
            <div>
              <h1 className="font-playfair font-bold text-3xl mb-1">Bulletins Officiels</h1>
              <p className="text-white/60 text-sm">
                Journal officiel du Royaume du Maroc — publiés par le SGG
              </p>
              {total > 0 && (
                <p className="text-gold text-sm mt-2">{total} bulletins référencés</p>
              )}
            </div>
          </div>

          {/* Search */}
          <form onSubmit={handleSearch} className="mt-6 max-w-lg flex gap-2">
            <div className="flex-1 relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
              <input
                type="text"
                value={searchInput}
                onChange={e => setSearchInput(e.target.value)}
                placeholder="Numéro de BO, ex: 7432…"
                className="w-full pl-9 pr-4 py-2.5 bg-white/10 border border-white/20 rounded-xl text-sm text-white placeholder-white/40 focus:outline-none focus:border-gold"
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2.5 bg-gold text-navy rounded-xl text-sm font-semibold hover:bg-gold/90 transition-colors"
            >
              Chercher
            </button>
            {search && (
              <button
                type="button"
                onClick={() => { setSearch(''); setSearchInput('') }}
                className="px-3 py-2.5 bg-white/10 border border-white/20 text-white/70 rounded-xl text-xs hover:bg-white/20 transition-colors"
              >
                ✕
              </button>
            )}
          </form>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">

        {loading ? (
          <SkeletonGrid count={12} />
        ) : bulletins.length === 0 ? (
          <div className="text-center py-20">
            <Newspaper size={40} className="text-gray-200 mx-auto mb-4" />
            <p className="text-navy-500 text-sm">
              {search
                ? `Aucun bulletin trouvé pour "${search}".`
                : 'Aucun bulletin disponible pour le moment.'}
            </p>
            {!search && (
              <p className="text-navy-400 text-xs mt-2">
                Lance <code className="bg-gray-100 px-1 rounded">python pipeline/scrape_bulletins.py</code> pour importer les BOs.
              </p>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {bulletins.map(bo => (
              <a
                key={bo.id}
                href={bo.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group bg-white rounded-xl border border-gray-100 p-5 hover:shadow-md hover:border-gold/40 transition-all duration-200 flex flex-col gap-3"
              >
                {/* Numéro */}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-widest text-gold mb-0.5">BO</p>
                    <p className="font-playfair font-bold text-navy text-2xl leading-none">
                      n°&nbsp;{bo.number}
                    </p>
                  </div>
                  <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center flex-shrink-0 group-hover:bg-gold/10 group-hover:border-gold/30 transition-colors">
                    <ExternalLink size={13} className="text-blue-400 group-hover:text-gold transition-colors" />
                  </div>
                </div>

                {/* Date */}
                {bo.date && (
                  <p className="flex items-center gap-1.5 text-xs text-navy-500">
                    <Calendar size={11} />
                    {new Date(bo.date).toLocaleDateString('fr-MA', {
                      day: 'numeric', month: 'long', year: 'numeric'
                    })}
                  </p>
                )}

                {/* Description */}
                {bo.description && (
                  <p className="text-xs text-navy-500 line-clamp-2 flex-1 leading-relaxed">
                    {bo.description}
                  </p>
                )}

                {/* Footer */}
                <div className="pt-2 border-t border-gray-50 flex items-center justify-between">
                  <span className="text-[10px] text-navy-400 uppercase tracking-wide">SGG.gov.ma</span>
                  <span className="text-xs text-gold font-medium flex items-center gap-0.5 group-hover:gap-1.5 transition-all">
                    Voir <ExternalLink size={10} />
                  </span>
                </div>
              </a>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && !loading && (
          <div className="flex items-center justify-center gap-2 mt-10 flex-wrap">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 rounded-lg border border-gray-200 bg-white text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronLeft size={16} />
            </button>
            {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
              const p = page <= 4 ? i + 1 : page - 3 + i
              if (p < 1 || p > totalPages) return null
              return (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${p === page ? 'bg-navy text-white' : 'bg-white border border-gray-200 text-navy-600 hover:border-gold'}`}
                >
                  {p}
                </button>
              )
            })}
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-2 rounded-lg border border-gray-200 bg-white text-navy-600 hover:border-gold disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        )}

        {/* Info encart */}
        <div className="mt-10 p-5 bg-white rounded-2xl border border-gray-100">
          <p className="text-xs text-navy-500 leading-relaxed">
            <span className="font-semibold text-navy">À propos des Bulletins Officiels —</span>{' '}
            Les Bulletins Officiels du Royaume du Maroc sont publiés par le Secrétariat Général du Gouvernement (SGG).
            Ils contiennent l'ensemble des textes législatifs et réglementaires officiellement promulgués.
            Les liens ci-dessus redirigent vers les documents officiels hébergés sur{' '}
            <a href="https://www.sgg.gov.ma" target="_blank" rel="noopener noreferrer" className="text-gold hover:underline">sgg.gov.ma</a>.
          </p>
        </div>
      </div>
    </div>
  )
}
