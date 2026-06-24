import { useState, useMemo, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Search, BookOpen, ChevronRight, X } from 'lucide-react'
import { useSEO } from '../hooks/useSEO'
import { useLang } from '../contexts/LangContext'
import { GLOSSAIRE, getGlossaireByLetter, getAvailableLetters, searchGlossaire } from '../data/glossaire'

// ── Correspondance domaine → page ────────────────────────────────────────────
const DOMAIN_LINKS = {
  civil:           '/domaine/civil',
  penal:           '/domaine/penal',
  commercial:      '/domaine/commercial',
  administratif:   '/domaine/administratif',
  travail:         '/domaine/travail',
  fiscal:          '/domaine/fiscal',
  constitutionnel: '/domaine/constitutionnel',
  numerique:       '/domaine/numerique',
  bancaire:        '/domaine/bancaire',
  international:   '/domaine/international',
}

const DOMAIN_LABELS_FR = {
  civil:           'Droit civil',
  penal:           'Droit pénal',
  commercial:      'Droit commercial',
  administratif:   'Droit administratif',
  travail:         'Droit du travail',
  fiscal:          'Droit fiscal',
  constitutionnel: 'Droit constitutionnel',
  numerique:       'Droit numérique',
  bancaire:        'Droit bancaire',
  international:   'Droit international',
}

const DOMAIN_LABELS_AR = {
  civil:           'القانون المدني',
  penal:           'القانون الجنائي',
  commercial:      'القانون التجاري',
  administratif:   'القانون الإداري',
  travail:         'قانون الشغل',
  fiscal:          'القانون الضريبي',
  constitutionnel: 'القانون الدستوري',
  numerique:       'القانون الرقمي',
  bancaire:        'القانون البنكي',
  international:   'القانون الدولي',
}

const DOMAIN_COLORS = {
  civil:           'bg-blue-50 text-blue-700 border-blue-200',
  penal:           'bg-red-50 text-red-700 border-red-200',
  commercial:      'bg-amber-50 text-amber-700 border-amber-200',
  administratif:   'bg-purple-50 text-purple-700 border-purple-200',
  travail:         'bg-green-50 text-green-700 border-green-200',
  fiscal:          'bg-orange-50 text-orange-700 border-orange-200',
  constitutionnel: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  numerique:       'bg-cyan-50 text-cyan-700 border-cyan-200',
  bancaire:        'bg-teal-50 text-teal-700 border-teal-200',
  international:   'bg-sky-50 text-sky-700 border-sky-200',
}

// ── Composant termes ──────────────────────────────────────────────────────────
function TermCard({ entry, highlight = '' }) {
  const { lang } = useLang()
  const DOMAIN_LABELS = lang === 'ar' ? DOMAIN_LABELS_AR : DOMAIN_LABELS_FR
  const domainLabel = entry.domain ? DOMAIN_LABELS[entry.domain] : null
  const domainColor = entry.domain ? DOMAIN_COLORS[entry.domain] : ''
  const domainLink  = entry.domain ? DOMAIN_LINKS[entry.domain] : null

  const highlightText = (text) => {
    if (!highlight || highlight.length < 2) return text
    const parts = text.split(new RegExp(`(${highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'))
    return parts.map((part, i) =>
      part.toLowerCase() === highlight.toLowerCase()
        ? <mark key={i} className="bg-gold/20 text-navy rounded px-0.5">{part}</mark>
        : part
    )
  }

  return (
    <div id={`term-${entry.term.toLowerCase().replace(/[^a-z0-9]/g, '-')}`}
         className="bg-white rounded-xl border border-gray-100 p-5 hover:border-gold/40 hover:shadow-sm transition-all group">
      <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
        <div className="min-w-0 flex-1">
          <h3 className="font-playfair font-semibold text-navy text-base group-hover:text-gold transition-colors break-words">
            {highlightText(entry.term)}
          </h3>
          <p className="text-xs font-arabic text-navy-400 mt-0.5 leading-relaxed" dir="rtl">
            {entry.ar}
          </p>
        </div>
        {domainLabel && (
          domainLink
            ? <Link to={domainLink}
                    className={`flex-shrink-0 text-xs px-2 py-0.5 rounded-full border font-medium hover:opacity-80 transition-opacity ${domainColor}`}>
                {domainLabel}
              </Link>
            : <span className={`flex-shrink-0 text-xs px-2 py-0.5 rounded-full border font-medium ${domainColor}`}>
                {domainLabel}
              </span>
        )}
      </div>
      <p className={`text-sm text-navy-600 leading-relaxed ${lang === 'ar' ? 'font-arabic' : ''}`}
         dir={lang === 'ar' ? 'rtl' : 'ltr'}>
        {lang === 'ar' && entry.definition_ar
          ? highlightText(entry.definition_ar)
          : highlightText(entry.definition)}
      </p>
    </div>
  )
}

// ── Page principale ───────────────────────────────────────────────────────────
export default function Glossaire() {
  const { lang, t } = useLang()

  useSEO({
    title: 'Glossaire juridique marocain — Définitions FR/AR | JuriThèque',
    description: `Glossaire de ${GLOSSAIRE.length}+ termes juridiques marocains bilingues (français/arabe). Définitions claires du droit civil, commercial, pénal, du travail et administratif au Maroc.`,
    canonical: 'https://juritheque.com/glossaire',
  })

  const [query, setQuery]           = useState('')
  const [activeLetter, setActiveLetter] = useState(null)
  const searchRef = useRef(null)

  const letters     = useMemo(() => getAvailableLetters(), [])
  const byLetter    = useMemo(() => getGlossaireByLetter(), [])
  const searchResults = useMemo(() => searchGlossaire(query), [query])
  const isSearching   = query.trim().length >= 2

  // Scroll vers une lettre
  const scrollToLetter = (letter) => {
    setActiveLetter(letter)
    const el = document.getElementById(`section-${letter}`)
    if (el) {
      const offset = 120
      window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - offset, behavior: 'smooth' })
    }
  }

  // Intersection observer pour la lettre active
  useEffect(() => {
    if (isSearching) return
    const sections = letters.map(l => document.getElementById(`section-${l}`)).filter(Boolean)
    const observer = new IntersectionObserver(
      entries => {
        for (const e of entries) {
          if (e.isIntersecting) {
            setActiveLetter(e.target.dataset.letter)
            break
          }
        }
      },
      { rootMargin: '-120px 0px -60% 0px' }
    )
    sections.forEach(s => observer.observe(s))
    return () => observer.disconnect()
  }, [letters, isSearching])

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      {/* ── En-tête ── */}
      <div className="bg-navy text-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-12 md:py-16">
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-white/50 text-xs mb-6">
            <Link to="/" className="hover:text-gold transition-colors">{t('glossary.home')}</Link>
            <ChevronRight size={12} />
            <span className="text-white/80">{t('glossary.breadcrumb')}</span>
          </nav>

          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-gold/20 flex items-center justify-center flex-shrink-0 mt-1">
              <BookOpen size={22} className="text-gold" />
            </div>
            <div>
              <h1 className="font-playfair font-bold text-3xl md:text-4xl mb-2">
                {t('glossary.title')}
              </h1>
              <p className="text-white/60 text-sm md:text-base leading-relaxed max-w-2xl">
                {t('glossary.desc').replace('{n}', GLOSSAIRE.length)}
              </p>
            </div>
          </div>

          {/* Barre de recherche */}
          <div className="mt-8 relative max-w-xl">
            <Search size={16} className={`absolute ${lang === 'ar' ? 'right-4' : 'left-4'} top-1/2 -translate-y-1/2 text-white/40`} />
            <input
              ref={searchRef}
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder={t('glossary.search_placeholder')}
              className={`w-full bg-white/10 border border-white/20 text-white placeholder-white/40 rounded-xl ${lang === 'ar' ? 'pr-10 pl-10' : 'pl-10 pr-10'} py-3 text-sm focus:outline-none focus:border-gold focus:bg-white/15 transition-all`}
              dir={lang === 'ar' ? 'rtl' : 'ltr'}
            />
            {query && (
              <button onClick={() => setQuery('')}
                      className={`absolute ${lang === 'ar' ? 'left-3' : 'right-3'} top-1/2 -translate-y-1/2 text-white/40 hover:text-white transition-colors`}>
                <X size={15} />
              </button>
            )}
          </div>

          {/* Stats */}
          <div className="flex flex-wrap gap-4 mt-6 text-xs text-white/50">
            <span>{GLOSSAIRE.length} {t('glossary.stat_terms')}</span>
            <span>·</span>
            <span>{letters.length} {t('glossary.stat_letters')}</span>
            <span>·</span>
            <span>{t('glossary.stat_bilingual')}</span>
            <span>·</span>
            <span>{t('glossary.stat_domains')}</span>
          </div>
        </div>
      </div>

      {/* ── Corps ── */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">

        {/* ── Mode recherche ── */}
        {isSearching ? (
          <div>
            <p className="text-sm text-navy-500 mb-4">
              {searchResults.length > 0
                ? <><strong className="text-navy">{searchResults.length}</strong> {t('glossary.results_for').replace('{q}', query)}</>
                : <>{t('glossary.no_results').replace('{q}', query)}</>
              }
            </p>
            <div className="space-y-3">
              {searchResults.map(entry => (
                <TermCard key={entry.term} entry={entry} highlight={query} />
              ))}
            </div>
          </div>
        ) : (
          <>
          {/* ── Navigation mobile horizontale (hors du flex row) ── */}
          <div className="lg:hidden mb-6 -mx-4 px-4 overflow-x-auto">
            <div className="flex gap-1.5 pb-2">
              {letters.map(letter => (
                <button
                  key={letter}
                  onClick={() => scrollToLetter(letter)}
                  className={`flex-shrink-0 w-8 h-8 text-xs font-bold rounded-lg transition-all ${
                    activeLetter === letter
                      ? 'bg-gold text-navy shadow-sm'
                      : 'bg-white text-navy-400 border border-gray-200 hover:border-gold hover:text-navy'
                  }`}
                >
                  {letter}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-8">
            {/* ── Navigation alphabétique desktop (sticky) ── */}
            <aside className="hidden lg:block flex-shrink-0 w-12">
              <div className="sticky top-24 space-y-0.5">
                {letters.map(letter => (
                  <button
                    key={letter}
                    onClick={() => scrollToLetter(letter)}
                    className={`w-full text-center text-xs font-semibold py-1 rounded transition-all ${
                      activeLetter === letter
                        ? 'bg-gold text-navy shadow-sm'
                        : 'text-navy-400 hover:text-navy hover:bg-gray-100'
                    }`}
                  >
                    {letter}
                  </button>
                ))}
              </div>
            </aside>

            {/* ── Sections alphabétiques ── */}
            <div className="flex-1 min-w-0 space-y-10">
              {letters.map(letter => (
                <section
                  key={letter}
                  id={`section-${letter}`}
                  data-letter={letter}
                >
                  {/* Lettre titre */}
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-navy rounded-xl flex items-center justify-center flex-shrink-0">
                      <span className="font-playfair font-bold text-gold text-lg">{letter}</span>
                    </div>
                    <div className="h-px bg-gray-200 flex-1" />
                    <span className="text-xs text-navy-400 flex-shrink-0">
                      {byLetter[letter]?.length} terme{byLetter[letter]?.length > 1 ? 's' : ''}
                    </span>
                  </div>

                  {/* Termes */}
                  <div className="space-y-3">
                    {byLetter[letter]?.map(entry => (
                      <TermCard key={entry.term} entry={entry} />
                    ))}
                  </div>
                </section>
              ))}

              {/* Footer glossaire */}
              <div className="border-t border-gray-200 pt-8 pb-4">
                <div className="bg-gold/5 border border-gold/20 rounded-xl p-5">
                  <h3 className="font-playfair font-semibold text-navy text-base mb-2">
                    {t('glossary.missing_title')}
                  </h3>
                  <p className="text-sm text-navy-500 leading-relaxed mb-3">
                    {t('glossary.missing_desc')}
                  </p>
                  <div className="flex flex-wrap gap-3">
                    <Link to="/base"
                          className="inline-flex items-center gap-1.5 text-xs font-semibold text-navy bg-gold px-3 py-1.5 rounded-lg hover:bg-gold-light transition-colors">
                      <Search size={12} /> {t('glossary.search_db')}
                    </Link>
                    <Link to="/contact"
                          className="inline-flex items-center gap-1.5 text-xs font-semibold text-navy-600 border border-navy-200 px-3 py-1.5 rounded-lg hover:border-gold hover:text-navy transition-colors">
                      {t('glossary.suggest_term')}
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
          </>
        )}
      </div>

      {/* ── JSON-LD ── */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'DefinedTermSet',
        name: 'Glossaire juridique marocain',
        description: `Glossaire de ${GLOSSAIRE.length} termes juridiques marocains bilingues français-arabe`,
        url: 'https://juritheque.com/glossaire',
        inLanguage: ['fr', 'ar'],
        hasDefinedTerm: GLOSSAIRE.slice(0, 10).map(e => ({
          '@type': 'DefinedTerm',
          name: e.term,
          description: e.definition,
          termCode: e.ar,
          inDefinedTermSet: 'https://juritheque.com/glossaire',
        })),
      })}} />
    </div>
  )
}
