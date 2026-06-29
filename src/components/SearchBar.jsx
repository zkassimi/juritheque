import { useState, useRef, useEffect } from 'react'
import { Search, X, ArrowRight, Scale, PlayCircle, BookOpen, Loader2 } from 'lucide-react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useLang } from '../contexts/LangContext'
import { supabase } from '../lib/supabase'
import { lawPath } from '../lib/lawUtils'
import { SEO_INTENT_PAGES } from '../data/seoIntentPages'
import { expandQuery } from '../data/searchSynonyms'

// ── Debounce hook ────────────────────────────────────────────────────────────
function useDebounce(value, delay) {
  const [dv, setDv] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDv(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return dv
}

// ── Component ────────────────────────────────────────────────────────────────
export default function SearchBar({ size = 'md', onSearch, compact = false, className = '' }) {
  const { t, lang } = useLang()
  const navigate    = useNavigate()
  const location    = useLocation()

  const [query,   setQuery]   = useState('')
  const [results, setResults] = useState({ laws: [], videos: [], guides: [] })
  const [loading, setLoading] = useState(false)
  const [focused, setFocused] = useState(false)
  const inputRef  = useRef(null)
  const wrapperRef= useRef(null)

  const dq = useDebounce(query, 280)   // debounced query

  // ── Close dropdown on route change (fix mobile sticky) ──────────────────
  useEffect(() => {
    setFocused(false)
    setQuery('')
    setResults({ laws: [], videos: [], guides: [] })
  }, [location.pathname])

  // ── Close on outside click / touch ──────────────────────────────────────
  useEffect(() => {
    const close = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setFocused(false)
      }
    }
    document.addEventListener('mousedown', close)
    document.addEventListener('touchstart', close, { passive: true })
    return () => {
      document.removeEventListener('mousedown', close)
      document.removeEventListener('touchstart', close)
    }
  }, [])

  // ── Multi-source search ──────────────────────────────────────────────────
  useEffect(() => {
    if (dq.length < 2) {
      setResults({ laws: [], videos: [], guides: [] })
      return
    }

    const isArabic = /[؀-ۿ]/.test(dq)
    const ql = dq.toLowerCase()
    const expanded = expandQuery(dq)
    const expandedLower = expanded.map(s => s.toLowerCase())

    // 1. Guides — local (instant) avec synonymes
    const guides = SEO_INTENT_PAGES.filter(g => {
      const h1 = g.h1.toLowerCase()
      const title = g.title.toLowerCase()
      const cat = (g.category || '').toLowerCase()
      const kws = (g.keywords || []).map(k => k.toLowerCase())
      const h1ar = (g.h1_ar || '').toLowerCase()
      return expandedLower.some(term =>
        h1.includes(term) || title.includes(term) || cat.includes(term) ||
        kws.some(k => k.includes(term)) || h1ar.includes(term)
      )
    }).slice(0, 3)

    setLoading(true)

    // 2. Laws — Supabase avec expansion synonymes (moudawana → famille, أسرة, etc.)
    const terms = dq.trim().split(/\s+/).filter(t => t.length >= 1)
    let lawQ = supabase.from('laws')
      .select('id,title_fr,title_ar,number,type,canonical_slug,status,domain_id')
      .eq('is_publicly_indexable', true)
      .limit(5)

    if (expanded.length > 1) {
      // Synonymes précis trouvés (numéros de loi, titres arabes exacts)
      // Stratégie : (termes originaux en AND) OR (synonymes spécifiques)
      // PostgREST : and(a,b),c = (a AND b) OR c
      const synParts = expanded.slice(1).map(s => {
        const t = s.trim()
        return isArabic
          ? `title_ar.ilike.%${t}%,number.ilike.%${t}%`
          : `title_fr.ilike.%${t}%,title_ar.ilike.%${t}%,number.ilike.%${t}%`
      }).join(',')

      if (terms.length <= 1) {
        // Terme unique : OR simple entre original + synonymes
        const termParts = isArabic
          ? `title_ar.ilike.%${dq}%,number.ilike.%${dq}%`
          : `title_fr.ilike.%${dq}%,title_ar.ilike.%${dq}%,number.ilike.%${dq}%`
        lawQ = lawQ.or(`${termParts},${synParts}`)
      } else {
        // Multi-termes : and(term1,term2) OR synonymes
        // → trouve "Code de la Famille" via AND, et via l'arabe/numéro
        const andTerms = terms.map(t => `title_fr.ilike.%${t}%`).join(',')
        lawQ = lawQ.or(`and(${andTerms}),${synParts}`)
      }
    } else {
      // Pas de synonymes : cherche terme par terme (AND) — comportement normal
      for (const term of terms) {
        lawQ = isArabic
          ? lawQ.or(`title_ar.ilike.%${term}%,number.ilike.%${term}%`)
          : lawQ.or(`title_fr.ilike.%${term}%,number.ilike.%${term}%,title_ar.ilike.%${term}%`)
      }
    }

    // 3. Videos — Supabase
    const vidQ = isArabic
      ? supabase.from('videos')
          .select('id,title_fr,title_ar,youtube_id,level,domain_id')
          .or(`title_ar.ilike.%${dq}%,title_fr.ilike.%${dq}%`)
          .limit(3)
      : supabase.from('videos')
          .select('id,title_fr,title_ar,youtube_id,level,domain_id')
          .ilike('title_fr', `%${dq}%`)
          .limit(3)

    Promise.all([lawQ, vidQ])
      .then(([{ data: laws }, { data: videos }]) => {
        setResults({
          laws:   laws   || [],
          videos: videos || [],
          guides,
        })
      })
      .catch(() => {
        // Fallback : show guides only on error
        setResults({ laws: [], videos: [], guides })
      })
      .finally(() => setLoading(false))

  }, [dq])

  // ── Handlers ─────────────────────────────────────────────────────────────
  const close = () => {
    setFocused(false)
    setQuery('')
    setResults({ laws: [], videos: [], guides: [] })
  }

  const handleSubmit = (e) => {
    e?.preventDefault()
    if (!query.trim()) return
    if (onSearch) onSearch(query)
    else navigate(`/base?q=${encodeURIComponent(query)}`)
    close()
  }

  const handleLaw   = (law)   => { navigate(lawPath(law));                   close() }
  const handleVideo = (video) => { navigate(`/videos`);                      close() }
  const handleGuide = (guide) => { navigate(`/${lang}/guides/${guide.slug}`); close() }

  const total  = results.laws.length + results.videos.length + results.guides.length
  const isOpen = focused && dq.length >= 2

  // ── Size classes ─────────────────────────────────────────────────────────
  const sizes = {
    sm: 'h-10 text-sm',
    md: 'h-12 text-sm',
    lg: 'h-14 text-[15px]',
  }

  return (
    <div ref={wrapperRef} className={`relative ${className}`}>
      {/* ── Input form ─────────────────────────────────────────────────── */}
      <form onSubmit={handleSubmit} className="relative">
        {/* Left icon */}
        {loading
          ? <Loader2 size={size === 'lg' ? 17 : 14} className="absolute left-4 top-1/2 -translate-y-1/2 text-gold animate-spin pointer-events-none" />
          : <Search  size={size === 'lg' ? 17 : 14} className="absolute left-4 top-1/2 -translate-y-1/2 text-navy-500 pointer-events-none" />
        }

        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onFocus={() => setFocused(true)}
          placeholder={t('hero.search_placeholder')}
          autoComplete="off"
          spellCheck={false}
          className={`
            w-full ${sizes[size]} pl-10 ${compact ? 'pr-12' : 'pr-16 sm:pr-28'}
            bg-white rounded-xl border border-gray-200
            text-navy placeholder-navy-400
            focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20
            transition-all shadow-sm
          `}
        />

        {/* Clear button */}
        {query && (
          <button
            type="button"
            onClick={() => { setQuery(''); setResults({ laws: [], videos: [], guides: [] }); inputRef.current?.focus() }}
            className={`absolute ${compact ? 'right-[44px]' : 'right-[52px] sm:right-[76px]'} top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-navy transition-colors`}
            aria-label="Effacer"
          >
            <X size={13} />
          </button>
        )}

        {/* Submit button — icon-only en mode compact/sidebar ou mobile, texte+icône sinon */}
        <button
          type="submit"
          className={`absolute right-2 top-1/2 -translate-y-1/2 bg-navy text-white text-xs font-semibold rounded-lg hover:bg-gold hover:text-navy transition-colors flex items-center gap-1 whitespace-nowrap ${compact ? 'p-2' : 'px-3 py-1.5 sm:px-3.5'}`}
          aria-label={t('common.search')}
        >
          {compact ? (
            <Search size={14} />
          ) : (
            <>
              <Search size={14} className="sm:hidden" />
              <span className="hidden sm:inline">{t('common.search')}</span>
              <ArrowRight size={11} className="hidden sm:inline" />
            </>
          )}
        </button>
      </form>

      {/* ── Dropdown ───────────────────────────────────────────────────── */}
      {isOpen && (
        <div
          className="absolute top-full left-0 right-0 mt-1.5 bg-white rounded-xl shadow-2xl border border-gray-100 overflow-hidden"
          style={{ zIndex: 90, maxHeight: '72vh', overflowY: 'auto' }}
        >

          {/* Loading state */}
          {loading && total === 0 && (
            <div className="flex items-center gap-2 px-4 py-3 text-xs text-navy-500">
              <Loader2 size={12} className="animate-spin text-gold" />
              {t('search.loading')}
            </div>
          )}

          {/* Empty state */}
          {!loading && total === 0 && (
            <div className="px-4 py-5 text-center">
              <p className="text-sm text-navy-500 mb-1">{t('search.no_results_for')} <strong className="text-navy">« {query} »</strong></p>
              <button
                onClick={handleSubmit}
                className="text-xs text-gold font-medium hover:underline"
              >
                {t('search.advanced')}
              </button>
            </div>
          )}

          {/* ── Section : Textes juridiques ───────────────────────────── */}
          {results.laws.length > 0 && (
            <div>
              <SectionHeader icon={<Scale size={11} />} label={t('search.section_laws')} count={results.laws.length} />
              {results.laws.map(law => (
                <button
                  key={law.id}
                  onClick={() => handleLaw(law)}
                  className="w-full flex items-start gap-3 px-4 py-2.5 hover:bg-gold/5 text-start border-b border-gray-50 last:border-0 transition-colors group"
                >
                  <span className="mt-2 w-1.5 h-1.5 rounded-full bg-gold/60 flex-shrink-0 group-hover:bg-gold transition-colors" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-navy font-medium leading-snug line-clamp-1">
                      {(() => {
                        if (lang === 'ar' && law.title_ar) return law.title_ar
                        const t = law.title_fr || ''
                        // Si le titre commence par minuscule (ex: "relatif à..."), préfixer avec type + numéro
                        if (t && t.charAt(0) === t.charAt(0).toLowerCase() && t.charAt(0) !== t.charAt(0).toUpperCase()) {
                          const prefix = [law.type, law.number ? `n° ${law.number}` : ''].filter(Boolean).join(' ')
                          return prefix ? `${prefix} ${t}` : t
                        }
                        return t
                      })()}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-navy-500">{law.number}</span>
                      <span className="text-navy-300">·</span>
                      <span className="text-xs text-gold/80">{law.type}</span>
                    </div>
                  </div>
                  {law.status === 'En vigueur' && (
                    <span className="flex-shrink-0 self-center text-[9px] bg-emerald-50 text-emerald-700 border border-emerald-200 rounded px-1.5 py-0.5 font-semibold">
                      {t('search.status_active')}
                    </span>
                  )}
                  {law.status === 'Abrogé' && (
                    <span className="flex-shrink-0 self-center text-[9px] bg-red-50 text-red-600 border border-red-200 rounded px-1.5 py-0.5 font-semibold">
                      {t('search.status_repealed')}
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}

          {/* ── Section : Guides thématiques ──────────────────────────── */}
          {results.guides.length > 0 && (
            <div>
              <SectionHeader icon={<BookOpen size={11} />} label={t('search.section_guides')} count={results.guides.length} />
              {results.guides.map(guide => (
                <button
                  key={guide.slug}
                  onClick={() => handleGuide(guide)}
                  className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-gold/5 text-start border-b border-gray-50 last:border-0 transition-colors"
                >
                  <BookOpen size={14} className="text-gold/50 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-navy font-medium line-clamp-1">{(lang === 'ar' && guide.h1_ar) ? guide.h1_ar : guide.h1}</p>
                    <p className="text-xs text-navy-500 capitalize">{guide.category}</p>
                  </div>
                  <ArrowRight size={12} className="text-gray-300 flex-shrink-0" />
                </button>
              ))}
            </div>
          )}

          {/* ── Section : Vidéos ──────────────────────────────────────── */}
          {results.videos.length > 0 && (
            <div>
              <SectionHeader icon={<PlayCircle size={11} />} label={t('search.section_videos')} count={results.videos.length} />
              {results.videos.map(video => (
                <button
                  key={video.id}
                  onClick={() => handleVideo(video)}
                  className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-gold/5 text-start border-b border-gray-50 last:border-0 transition-colors"
                >
                  {/* Thumbnail */}
                  <div className="w-10 h-7 rounded bg-navy/10 flex-shrink-0 overflow-hidden">
                    <img
                      src={`https://img.youtube.com/vi/${video.youtube_id}/default.jpg`}
                      alt=""
                      className="w-full h-full object-cover"
                      onError={e => { e.currentTarget.style.display = 'none' }}
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-navy font-medium line-clamp-1">
                      {lang === 'ar' && video.title_ar ? video.title_ar : video.title_fr}
                    </p>
                    <p className="text-xs text-navy-500">{video.level || 'Vidéo'}</p>
                  </div>
                  <PlayCircle size={12} className="text-gold/50 flex-shrink-0" />
                </button>
              ))}
            </div>
          )}

          {/* ── Footer : voir tous les résultats ──────────────────────── */}
          {total > 0 && (
            <div className="px-4 py-2.5 bg-gray-50 border-t border-gray-100">
              <button
                onClick={handleSubmit}
                className="text-xs text-gold font-semibold hover:underline flex items-center gap-1"
              >
                {t('search.all_results')} « {query} » <ArrowRight size={11} />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── Helper : section header ──────────────────────────────────────────────────
function SectionHeader({ icon, label, count }) {
  return (
    <div className="flex items-center justify-between px-4 py-1.5 bg-gray-50 border-y border-gray-100 first:border-t-0">
      <div className="flex items-center gap-1.5">
        <span className="text-gold">{icon}</span>
        <span className="text-[10px] font-semibold uppercase tracking-wider text-navy-500">{label}</span>
      </div>
      <span className="text-[10px] text-navy-400 bg-gray-100 rounded-full px-1.5 py-0.5">{count}</span>
    </div>
  )
}
