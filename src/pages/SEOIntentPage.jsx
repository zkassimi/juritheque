import { useEffect, useState, useRef, useCallback } from 'react'
import { useParams, Link, useLocation } from 'react-router-dom'
import {
  ChevronRight, Bot, Search, BookOpen, ArrowRight,
  ChevronDown, ChevronUp, FileText, Bell, PlayCircle, Flag, AlertTriangle, Calendar
} from 'lucide-react'
import ReportModal from '../components/ReportModal'
import { useLang } from '../contexts/LangContext'
import { useSEO } from '../hooks/useSEO'
import JsonLD, { breadcrumbSchema } from '../components/JsonLD'
import { getIntentBySlug, getRelatedGuides } from '../data/seoIntentPages'
import { lawPath, lawCanonical } from '../lib/lawUtils'
import { getRelatedLawsForIntent } from '../lib/seoIntentApi'
import TypeBadge from '../components/ui/TypeBadge'
import StatusBadge from '../components/ui/StatusBadge'
import VideoModal from '../components/VideoModal'

const BASE_URL = 'https://juritheque.com'

// ── FAQ item accordéon ────────────────────────────────────────────────────────
function FAQItem({ question, answer }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-gray-100 rounded-xl overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-5 py-4 text-left bg-white hover:bg-gray-50 transition-colors"
        onClick={() => setOpen(v => !v)}
        aria-expanded={open}
      >
        <span className="text-sm font-medium text-navy pr-4">{question}</span>
        {open
          ? <ChevronUp  size={16} className="text-gold flex-shrink-0" />
          : <ChevronDown size={16} className="text-gold flex-shrink-0" />
        }
      </button>
      {open && (
        <div className="px-5 pb-4 pt-1 bg-gray-50/80">
          <p className="text-sm text-navy-600 leading-relaxed">{answer}</p>
        </div>
      )}
    </div>
  )
}

// ── Carte loi pour les guides ─────────────────────────────────────────────────
function IntentLawCard({ law }) {
  return (
    <Link
      to={lawPath(law)}
      className="group flex items-start gap-3 bg-white rounded-xl border border-gray-100 p-3 hover:border-gold hover:shadow-sm transition-all"
    >
      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-center gap-1.5 mb-1">
          <TypeBadge   type={law.type} />
          <StatusBadge status={law.status} />
        </div>
        <h3 className="text-xs font-semibold text-navy group-hover:text-gold transition-colors leading-snug line-clamp-2">
          {law.title_fr || law.title_ar || `Texte n°${law.id}`}
        </h3>
        {law.number && (
          <p className="text-[11px] text-navy-400 mt-0.5">
            {law.number}{law.date ? ` · ${law.date}` : ''}{law.public_article_count > 0 ? ` · ${law.public_article_count} articles` : ''}
          </p>
        )}
      </div>
      <ArrowRight size={13} className={`text-gold flex-shrink-0 mt-1 opacity-0 group-hover:opacity-100 transition-opacity`} />
    </Link>
  )
}

// ── Skeleton chargement ───────────────────────────────────────────────────────
function LawSkeleton() {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4 animate-pulse">
      <div className="flex gap-2 mb-3">
        <div className="h-5 w-16 bg-gray-100 rounded-full" />
        <div className="h-5 w-20 bg-gray-100 rounded-full" />
      </div>
      <div className="h-4 bg-gray-100 rounded w-4/5 mb-2" />
      <div className="h-3 bg-gray-100 rounded w-2/5 mb-3" />
      <div className="h-3 bg-gray-100 rounded w-full mb-1" />
      <div className="h-3 bg-gray-100 rounded w-3/4" />
    </div>
  )
}

// ── Mini carte vidéo pour les guides ─────────────────────────────────────────
function GuideVideoCard({ video, onClick }) {
  const thumb = video.thumbnail || `https://img.youtube.com/vi/${video.youtube_id}/mqdefault.jpg`
  return (
    <button
      onClick={() => onClick(video)}
      className="group w-full text-left bg-white rounded-xl border border-gray-100 overflow-hidden hover:shadow-md hover:border-gold/40 transition-all"
    >
      {/* Thumbnail */}
      <div className="relative aspect-video overflow-hidden bg-navy">
        <img
          src={thumb}
          alt={video.title_fr}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="w-10 h-10 rounded-full bg-gold flex items-center justify-center">
            <PlayCircle size={20} className="text-navy" />
          </div>
        </div>
        {video.duration && (
          <span className="absolute bottom-2 right-2 text-[10px] bg-black/70 text-white px-1.5 py-0.5 rounded font-mono">
            {video.duration}
          </span>
        )}
      </div>
      {/* Info */}
      <div className="p-3">
        <p className="text-sm font-semibold text-navy group-hover:text-gold transition-colors line-clamp-2 leading-snug">
          {video.title_fr}
        </p>
        {video.author && (
          <p className="text-[11px] text-navy-400 mt-1">{video.author}</p>
        )}
      </div>
    </button>
  )
}

// ── Helpers TOC ───────────────────────────────────────────────────────────────
function slugify(str) {
  return str
    .toLowerCase()
    .replace(/[^\w؀-ۿ\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .slice(0, 60)
}

// ── Sections + TOC sticky ─────────────────────────────────────────────────────
function SectionsWithTOC({ sections, isAr }) {
  const [activeId, setActiveId] = useState(null)
  const [tocOpen, setTocOpen] = useState(false)
  const observerRef = useRef(null)

  const ids = sections.map((s) => slugify(s.h2))

  const observe = useCallback(() => {
    if (observerRef.current) observerRef.current.disconnect()
    observerRef.current = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting)
        if (visible.length > 0) setActiveId(visible[0].target.id)
      },
      { rootMargin: '-20% 0px -60% 0px', threshold: 0 }
    )
    ids.forEach((id) => {
      const el = document.getElementById(id)
      if (el) observerRef.current.observe(el)
    })
  }, [ids.join(',')])

  useEffect(() => {
    observe()
    return () => observerRef.current?.disconnect()
  }, [observe])

  if (sections.length === 0) return null

  const hasTOC = sections.length >= 2

  const TocList = () => (
    <ul className="space-y-1" dir={isAr ? 'rtl' : 'ltr'}>
      {sections.map((sec, i) => {
        const id = ids[i]
        const active = activeId === id
        return (
          <li key={id}>
            <a
              href={`#${id}`}
              onClick={(e) => { e.preventDefault(); document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }); setTocOpen(false) }}
              className={`block text-xs leading-snug py-1 px-2 rounded transition-colors ${
                active
                  ? 'bg-gold/15 text-gold font-semibold'
                  : 'text-navy/60 hover:text-navy hover:bg-gray-100'
              }`}
            >
              {sec.h2}
            </a>
          </li>
        )
      })}
    </ul>
  )

  return (
    <div className={hasTOC ? 'lg:grid lg:grid-cols-[1fr_220px] lg:gap-6 lg:items-start' : ''}>
      {/* ── Contenu sections ── */}
      <section className="space-y-6 min-w-0">
        {/* TOC mobile collapsible */}
        {hasTOC && (
          <div className="lg:hidden bg-white border border-gray-100 rounded-2xl overflow-hidden">
            <button
              onClick={() => setTocOpen((o) => !o)}
              className="w-full flex items-center justify-between px-4 py-3 text-sm font-semibold text-navy"
              aria-expanded={tocOpen}
            >
              <span>{isAr ? 'محتوى الدليل' : 'Sommaire'}</span>
              {tocOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
            {tocOpen && (
              <div className="px-4 pb-3 border-t border-gray-100">
                <TocList />
              </div>
            )}
          </div>
        )}

        {sections.map((sec, i) => (
          <div key={i} id={ids[i]} className="bg-white rounded-2xl border border-gray-100 p-6 scroll-mt-20">
            <h2 className={`font-semibold text-navy text-lg mb-3 flex items-center gap-2 ${isAr ? 'font-arabic' : 'font-playfair'}`}>
              {sec.icon && <span className="text-gold">{sec.icon}</span>}
              {sec.h2}
            </h2>
            {Array.isArray(sec.content)
              ? sec.content.map((para, j) => (
                  <p key={j} className="text-sm text-navy-700 leading-relaxed mb-3 last:mb-0">{para}</p>
                ))
              : <p className="text-sm text-navy-700 leading-relaxed">{sec.content}</p>
            }
            {sec.bullets?.length > 0 && (
              <ul className="mt-3 space-y-1.5">
                {sec.bullets.map((b, k) => (
                  <li key={k} dir={isAr ? 'rtl' : undefined} className={`flex items-start gap-2 text-sm text-navy-700`}>
                    <span className="text-gold mt-0.5 flex-shrink-0">{isAr ? '◂' : '▸'}</span>
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </section>

      {/* ── TOC desktop sticky ── */}
      {hasTOC && (
        <aside className="hidden lg:block">
          <div className="sticky top-24 bg-white border border-gray-100 rounded-2xl p-4">
            <p className={`text-xs font-semibold text-navy/50 uppercase tracking-wider mb-3 ${isAr ? 'text-right font-arabic' : ''}`}>
              {isAr ? 'محتوى الدليل' : 'Sommaire'}
            </p>
            <TocList />
          </div>
        </aside>
      )}
    </div>
  )
}

// ── Page principale ───────────────────────────────────────────────────────────
export default function SEOIntentPage() {
  const { slug } = useParams()
  const { pathname } = useLocation()
  const { lang, setLang } = useLang()
  const [laws,       setLaws]       = useState([])
  const [loading,    setLoading]    = useState(true)
  const [videos,     setVideos]     = useState([])
  const [activeVideo,setActiveVideo] = useState(null)
  const [reportOpen, setReportOpen] = useState(false)

  // Sync lang context with URL prefix (/ar/ → arabe, /fr/ → français)
  useEffect(() => {
    if (pathname.startsWith('/ar/')) setLang('ar')
    else setLang('fr')
  }, [pathname]) // eslint-disable-line react-hooks/exhaustive-deps

  const intent = getIntentBySlug(slug)

  // Sélection du contenu selon la langue
  const pageH1    = lang === 'ar' && intent?.h1_ar    ? intent.h1_ar    : intent?.h1
  const pageIntro = lang === 'ar' && intent?.intro_ar ? intent.intro_ar : intent?.intro
  const pageTitle = lang === 'ar' && intent?.title_ar ? intent.title_ar : intent?.title
  const pageMeta  = lang === 'ar' && intent?.metaDescription_ar ? intent.metaDescription_ar : intent?.metaDescription
  const pageKw    = lang === 'ar' && intent?.keywords_ar?.length ? intent.keywords_ar : intent?.keywords
  const pageFaq   = lang === 'ar' && intent?.faq_ar?.length ? intent.faq_ar : intent?.faq

  useSEO({
    title:       pageTitle || 'Guide juridique — JuriThèque',
    description: pageMeta  || 'Consultez les textes juridiques marocains sur JuriThèque.',
    canonical:   intent ? `/${lang === 'ar' ? 'ar' : 'fr'}/guides/${intent.slug}` : '/fr/guides',
    type:        'article',
    lang,
    hreflang: intent ? [
      { lang: 'fr', url: `${BASE_URL}/fr/guides/${intent.slug}` },
      { lang: 'ar', url: `${BASE_URL}/ar/guides/${intent.slug}` },
      { lang: 'x-default', url: `${BASE_URL}/fr/guides/${intent.slug}` },
    ] : undefined,
  })

  useEffect(() => {
    if (!intent) { setLoading(false); return }
    setLoading(true)
    getRelatedLawsForIntent(intent)
      .then(data => { setLaws(data || []); setLoading(false) })
      .catch(()  => { setLaws([]);        setLoading(false) })

    // ── Fetch vidéos liées ──────────────────────────────────────────────────
    import('../lib/supabase').then(({ supabase }) => {
      const featuredIds = intent.featuredVideoIds || []

      if (featuredIds.length > 0) {
        // Vidéos spécifiquement choisies pour ce guide (par youtube_id)
        supabase
          .from('videos')
          .select('*')
          .in('youtube_id', featuredIds)
          .then(({ data }) => { if (data?.length) setVideos(data) })
          .catch(() => {})
      } else if (intent.legalDomain) {
        // Fallback : vidéos du même domaine, max 3, triées par vues
        supabase
          .from('videos')
          .select('*')
          .eq('domain_id', intent.legalDomain)
          .order('views', { ascending: false })
          .limit(3)
          .then(({ data }) => { if (data?.length) setVideos(data) })
          .catch(() => {})
      }
    })
  }, [slug]) // eslint-disable-line react-hooks/exhaustive-deps

  const relatedGuides = getRelatedGuides(intent, 4)

  // ── 404 guide ──────────────────────────────────────────────────────────────
  if (!loading && !intent) return (
    <div className="min-h-screen flex items-center justify-center pt-16">
      <div className="text-center">
        <FileText size={48} className="text-gray-300 mx-auto mb-4" />
        <h2 className="font-playfair text-xl text-navy mb-2">Guide introuvable</h2>
        <Link to="/fr/guides" className="text-sm text-gold hover:underline">← Tous les guides</Link>
      </div>
    </div>
  )

  if (!intent) return null

  // ── JSON-LD ─────────────────────────────────────────────────────────────────
  const isAr = lang === 'ar'
  const guideUrl = `${BASE_URL}/${isAr ? 'ar' : 'fr'}/guides/${intent.slug}`

  const breadcrumbs = [
    { name: isAr ? 'الرئيسية' : 'Accueil',              url: '/' },
    { name: isAr ? 'الأدلة القانونية' : 'Guides juridiques', url: `/${isAr ? 'ar' : 'fr'}/guides` },
    { name: pageH1,                                       url: guideUrl },
  ]

  const jsonLdData = [
    // WebPage
    {
      '@context':   'https://schema.org',
      '@type':      'WebPage',
      name:         pageTitle,
      description:  pageMeta,
      url:          guideUrl,
      inLanguage:   isAr ? 'ar' : 'fr',
      isPartOf:     { '@type': 'WebSite', name: 'JuriThèque', url: BASE_URL },
    },
    // BreadcrumbList
    breadcrumbSchema(breadcrumbs),
    // Article
    {
      '@context':        'https://schema.org',
      '@type':           'Article',
      headline:          pageH1,
      description:       pageMeta,
      inLanguage:        isAr ? 'ar' : 'fr',
      url:               guideUrl,
      dateModified:      intent.lastUpdated ? `${intent.lastUpdated}-01` : undefined,
      publisher: {
        '@type': 'Organization',
        name:    'JuriThèque',
        url:     BASE_URL,
        logo:    { '@type': 'ImageObject', url: `${BASE_URL}/og-image.png` },
      },
      mainEntityOfPage:  { '@type': 'WebPage', '@id': guideUrl },
    },
    // FAQPage
    pageFaq?.length > 0 && {
      '@context':   'https://schema.org',
      '@type':      'FAQPage',
      mainEntity:   pageFaq.map(f => ({
        '@type':         'Question',
        name:            f.question,
        acceptedAnswer:  { '@type': 'Answer', text: f.answer },
      })),
    },
    // ItemList (textes liés)
    laws.length > 0 && {
      '@context':        'https://schema.org',
      '@type':           'ItemList',
      name:              `Textes juridiques liés : ${intent.h1}`,
      numberOfItems:     laws.length,
      itemListElement:   laws.map((l, i) => ({
        '@type':    'ListItem',
        position:   i + 1,
        url:        lawCanonical(l, BASE_URL),
        name:       l.title_fr || l.title_ar || `Texte n°${l.id}`,
      })),
    },
  ].filter(Boolean)

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      <JsonLD data={jsonLdData} />

      {/* ── En-tête ──────────────────────────────────────────────────────── */}
      <div className="bg-navy text-white py-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6">
          {/* Fil d'Ariane */}
          <nav className="flex items-center gap-1.5 text-xs text-white/50 mb-5" aria-label="Fil d'Ariane">
            <Link to="/" className="hover:text-gold transition-colors">{isAr ? 'الرئيسية' : 'Accueil'}</Link>
            <ChevronRight size={10} className={isAr ? 'rotate-180' : ''} />
            <Link to={`/${isAr ? 'ar' : 'fr'}/guides`} className="hover:text-gold transition-colors">{isAr ? 'الأدلة' : 'Guides'}</Link>
            <ChevronRight size={10} className={isAr ? 'rotate-180' : ''} />
            <span className="text-white/80 truncate">{pageH1}</span>
          </nav>

          <h1 className={`font-bold text-2xl sm:text-3xl mb-2 ${isAr ? 'font-arabic' : 'font-playfair'}`} dir={isAr ? 'rtl' : 'ltr'}>{pageH1}</h1>
          {(isAr ? intent.badge_ar : intent.badge) && (
            <span className={`inline-block mb-3 px-3 py-1 text-xs font-medium rounded-full bg-amber-400/20 text-amber-200 border border-amber-400/30 ${isAr ? 'font-arabic' : ''}`}>
              {isAr ? intent.badge_ar : intent.badge}
            </span>
          )}
          {intent.lastUpdated && (
            <p className="flex items-center gap-1.5 text-xs text-white/45 mb-3">
              <Calendar size={11} />
              {isAr ? `آخر تحديث: ${intent.lastUpdated} · المصادر الرسمية المغربية` : `Mis à jour : ${intent.lastUpdated} · Textes officiels marocains`}
            </p>
          )}
          <p className={`text-white/70 text-sm leading-relaxed max-w-2xl ${isAr ? 'font-arabic' : ''}`} dir={isAr ? 'rtl' : 'ltr'}>{pageIntro}</p>

          {/* Mots-clés */}
          {pageKw?.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-4">
              {pageKw.map(kw => (
                <span
                  key={kw}
                  className={`text-xs bg-white/10 text-white/70 px-2.5 py-1 rounded-full border border-white/10 ${isAr ? 'font-arabic' : ''}`}
                >
                  {kw}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Contenu principal ────────────────────────────────────────────── */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-8">

        {/* ── Vue d'ensemble (intro dans zone blanche) ──────────────────── */}
        {pageIntro && (
          <section className="bg-white rounded-2xl border border-gray-100 p-6">
            <h2 className={`font-semibold text-navy text-base mb-3 flex items-center gap-2 ${isAr ? 'font-arabic' : 'font-playfair'}`}>
              <BookOpen size={15} className="text-gold flex-shrink-0" />
              {isAr ? 'نظرة عامة' : 'Vue d\'ensemble'}
            </h2>
            <p className={`text-sm text-navy-700 leading-relaxed ${isAr ? 'font-arabic' : ''}`} dir={isAr ? 'rtl' : 'ltr'}>
              {pageIntro}
            </p>
            {/* Fiabilité */}
            <div className="mt-4 pt-4 border-t border-gray-50 flex flex-wrap items-center gap-3 text-xs text-navy-400">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block" />
                {isAr ? 'مصادر رسمية مغربية' : 'Sources officielles marocaines'}
              </span>
              {intent.lastUpdated && (
                <span className="flex items-center gap-1">
                  <Calendar size={11} />
                  {isAr ? `تحديث: ${intent.lastUpdated}` : `Mis à jour : ${intent.lastUpdated}`}
                </span>
              )}
            </div>
          </section>
        )}

        {/* ── Cartes statistiques clés ──────────────────────────────────── */}
        {(() => {
          const stats = isAr ? intent?.stats_ar : intent?.stats
          if (!stats?.length) return null
          return (
            <div className={`grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3`} dir={isAr ? 'rtl' : 'ltr'}>
              {stats.map((s, i) => (
                <div key={i} className="bg-white border border-gray-100 rounded-xl p-3 text-center shadow-sm">
                  <div className={`text-base font-bold text-navy leading-tight ${isAr ? 'font-arabic' : ''}`}>{s.value}</div>
                  <div className={`text-[11px] text-gray-500 mt-1 leading-tight ${isAr ? 'font-arabic' : ''}`}>{s.label}</div>
                  {s.badge && (
                    <span className={`mt-1.5 inline-block px-2 py-0.5 text-[10px] bg-amber-50 text-amber-700 border border-amber-200 rounded-full ${isAr ? 'font-arabic' : ''}`}>
                      {s.badge}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )
        })()}

        {/* ── Sections éditoriales + TOC sticky ─────────────────────────── */}
        <SectionsWithTOC
          sections={(isAr && intent?.sections_ar?.length) ? intent.sections_ar : (intent?.sections || [])}
          isAr={isAr}
        />

        {/* ── Textes juridiques liés ─────────────────────────────────────── */}
        <section dir={isAr ? 'rtl' : 'ltr'}>
          <div className="flex items-center justify-between mb-4">
            <h2 className={`font-semibold text-navy text-xl ${isAr ? 'font-arabic' : 'font-playfair'}`}>
              {isAr ? 'النصوص القانونية المتاحة' : 'Textes juridiques disponibles'}
              {!loading && laws.length > 0 && (
                <span className="mx-2 text-sm font-normal text-navy-400">({laws.length})</span>
              )}
            </h2>
            <Link
              to={`/base?domain=${intent.legalDomain}`}
              className="flex items-center gap-1 text-xs text-gold hover:underline whitespace-nowrap"
            >
              {isAr ? 'عرض الكل' : 'Voir tous'} <ArrowRight size={11} className={isAr ? 'rotate-180' : ''} />
            </Link>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[...Array(4)].map((_, i) => <LawSkeleton key={i} />)}
            </div>
          ) : laws.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-100 p-8 text-center">
              <FileText size={32} className="text-gray-200 mx-auto mb-3" />
              <p className="text-sm text-navy-500 mb-2">{isAr ? 'لا توجد نصوص لهذا الموضوع.' : 'Aucun texte trouvé pour ce thème.'}</p>
              <Link to="/base" className="text-xs text-gold hover:underline">
                {isAr ? '← البحث في القاعدة' : 'Rechercher dans la base →'}
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {laws.map(law => <IntentLawCard key={law.id} law={law} />)}
            </div>
          )}
        </section>

        {/* ── FAQ ───────────────────────────────────────────────────────── */}
        {pageFaq?.length > 0 && (
          <section dir={isAr ? 'rtl' : 'ltr'}>
            <h2 className={`font-semibold text-navy text-xl mb-4 ${isAr ? 'font-arabic' : 'font-playfair'}`}>
              {isAr ? 'أسئلة شائعة' : 'Questions fréquentes'}
            </h2>
            <div className="space-y-2">
              {pageFaq.map((f, i) => (
                <FAQItem key={i} question={f.question} answer={f.answer} />
              ))}
            </div>
          </section>
        )}

        {/* ── Disclaimer projet de texte (si défini) ──────────────────── */}
        {(isAr ? intent?.disclaimer_ar : intent?.disclaimer) && (
          <div className={`bg-amber-50 border-2 border-amber-300 rounded-xl p-5 flex items-start gap-3 ${isAr ? 'flex-row-reverse' : ''}`} dir={isAr ? 'rtl' : 'ltr'}>
            <AlertTriangle size={18} className="text-amber-600 flex-shrink-0 mt-0.5" />
            <p className={`text-sm text-amber-900 leading-relaxed ${isAr ? 'font-arabic text-right' : ''}`}>
              {isAr ? intent.disclaimer_ar : intent.disclaimer}
            </p>
          </div>
        )}

        {/* ── Note méthodologique ─────────────────────────────────────── */}
        {(isAr ? intent?.methodology_note_ar : intent?.methodology_note) && (
          <p className={`text-xs text-gray-400 italic leading-relaxed ${isAr ? 'font-arabic text-right' : ''}`} dir={isAr ? 'rtl' : 'ltr'}>
            {isAr ? intent.methodology_note_ar : intent.methodology_note}
          </p>
        )}

        {/* ── Avertissement juridique générique ───────────────────────── */}
        <div className={`bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3 ${isAr ? 'flex-row-reverse' : ''}`} dir={isAr ? 'rtl' : 'ltr'}>
          <AlertTriangle size={15} className="text-amber-600 flex-shrink-0 mt-0.5" />
          <p className={`text-xs text-amber-800 leading-relaxed ${isAr ? 'font-arabic text-right' : ''}`}>
            {isAr ? (
              <><strong>تنبيه:</strong> هذا الدليل مقدَّم لأغراض إعلامية فقط ولا يشكل استشارة قانونية مهنية. لأي إجراء يمسّ حقوقك أو التزاماتك، استشر محاميًا أو موثقًا أو حقوقيًا مؤهلًا، وارجع إلى النصوص الرسمية.</>
            ) : (
              <><strong>Avertissement :</strong> Ce guide est fourni à titre informatif uniquement. Il ne constitue pas un conseil juridique professionnel. Pour toute démarche engageant vos droits ou obligations, consultez un avocat, notaire ou juriste qualifié, et référez-vous aux textes officiels.</>
            )}
          </p>
        </div>

        {/* ── Vidéos pédagogiques (section conditionnelle) ──────────────── */}
        {videos.length > 0 && (
          <section dir={isAr ? 'rtl' : 'ltr'}>
            <div className="flex items-center justify-between mb-4">
              <h2 className={`font-semibold text-navy text-xl flex items-center gap-2 ${isAr ? 'font-arabic flex-row-reverse' : 'font-playfair'}`}>
                <PlayCircle size={18} className="text-gold" />
                {isAr ? 'فيديوهات تعليمية' : 'Vidéos pédagogiques'}
              </h2>
              <Link
                to="/videos"
                className="flex items-center gap-1 text-xs text-gold hover:underline whitespace-nowrap"
              >
                {isAr ? 'عرض الكل' : 'Voir toutes'} <ArrowRight size={11} className={isAr ? 'rotate-180' : ''} />
              </Link>
            </div>
            <div className={`grid gap-4 ${videos.length === 1 ? 'grid-cols-1 max-w-xs' : videos.length === 2 ? 'grid-cols-1 sm:grid-cols-2' : 'grid-cols-1 sm:grid-cols-3'}`}>
              {videos.map(video => (
                <GuideVideoCard key={video.id} video={video} onClick={setActiveVideo} />
              ))}
            </div>
          </section>
        )}

        {/* ── CTA double ──────────────────────────────────────────────────── */}
        <section className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Link
            to="/assistant"
            className="flex items-center gap-3 p-5 bg-navy text-white rounded-2xl hover:bg-gold hover:text-navy transition-colors group"
          >
            <Bot size={22} className="flex-shrink-0 group-hover:scale-110 transition-transform" />
            <div className={isAr ? 'font-arabic text-right' : ''}>
              <p className="font-semibold text-sm">{isAr ? 'اطرح سؤالاً على الذكاء الاصطناعي' : 'Poser une question à l\'IA'}</p>
              <p className="text-xs opacity-70 mt-0.5">{isAr ? 'يجيب المساعد بالفرنسية والعربية' : 'L\'assistant répond en français et arabe'}</p>
            </div>
          </Link>
          <Link
            to={`/base?domain=${intent.legalDomain}`}
            className="flex items-center gap-3 p-5 bg-white border border-gray-200 rounded-2xl hover:border-gold transition-colors group"
          >
            <Search size={22} className="flex-shrink-0 text-gold" />
            <div className={isAr ? 'font-arabic text-right' : ''}>
              <p className="font-semibold text-sm text-navy">{isAr ? 'استكشف قاعدة البيانات' : 'Explorer la base de données'}</p>
              <p className="text-xs text-navy-500 mt-0.5">{isAr ? 'التصفية حسب المجال والنوع والتاريخ' : 'Filtrer par domaine, type et date'}</p>
            </div>
          </Link>
        </section>

        {/* ── Guides proches ──────────────────────────────────────────────── */}
        {relatedGuides.length > 0 && (
          <section dir={isAr ? 'rtl' : 'ltr'}>
            <h2 className={`font-semibold text-navy text-xl mb-4 ${isAr ? 'font-arabic' : 'font-playfair'}`}>{isAr ? 'أدلة ذات صلة' : 'Guides proches'}</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {relatedGuides.map(guide => (
                <Link
                  key={guide.slug}
                  to={`/${isAr ? 'ar' : 'fr'}/guides/${guide.slug}`}
                  className="flex items-start gap-3 p-4 bg-white rounded-xl border border-gray-100 hover:border-gold hover:shadow-sm transition-all group"
                >
                  <BookOpen size={16} className="text-gold flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-medium text-navy group-hover:text-gold transition-colors truncate ${isAr ? 'font-arabic' : ''}`}>
                      {isAr && guide.h1_ar ? guide.h1_ar : guide.h1}
                    </p>
                    <p className={`text-xs text-navy-400 mt-0.5 line-clamp-2 ${isAr ? 'font-arabic' : ''}`}>{isAr && guide.metaDescription_ar ? guide.metaDescription_ar : guide.metaDescription}</p>
                  </div>
                  <ChevronRight size={14} className={`text-gray-300 group-hover:text-gold flex-shrink-0 mt-0.5 transition-colors ${isAr ? 'rotate-180' : ''}`} />
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* ── Liens secondaires ───────────────────────────────────────────── */}
        {intent.legalDomain && (
          <div className={`flex flex-wrap items-center justify-center gap-5 pt-2 pb-4 text-sm text-navy-500 ${isAr ? 'font-arabic' : ''}`} dir={isAr ? 'rtl' : 'ltr'}>
            <Link
              to={`/domaine/${intent.legalDomain}`}
              className="inline-flex items-center gap-1.5 hover:text-gold transition-colors"
            >
              <ArrowRight size={13} className={isAr ? 'rotate-180' : ''} />
              {isAr ? 'كل نصوص هذا المجال' : 'Tous les textes du domaine'}
            </Link>
            <Link
              to={`/${isAr ? 'ar' : 'fr'}/veille-juridique?domain=${intent.legalDomain}`}
              className="inline-flex items-center gap-1.5 hover:text-gold transition-colors"
            >
              <Bell size={13} />
              {isAr ? 'اليقظة القانونية ذات الصلة' : 'Veille juridique liée'}
            </Link>
            <Link
              to={`/${isAr ? 'ar' : 'fr'}/guides`}
              className="inline-flex items-center gap-1.5 hover:text-gold transition-colors"
            >
              <BookOpen size={13} />
              {isAr ? 'كل الأدلة' : 'Tous les guides'}
            </Link>
          </div>
        )}

        {/* ── Signaler une erreur dans ce guide ────────────────────── */}
        <div className="flex items-center justify-center pt-2 pb-2">
          <button
            onClick={() => setReportOpen(true)}
            className="inline-flex items-center gap-1.5 text-xs text-navy-400 hover:text-orange-500 transition-colors px-3 py-1.5 rounded-lg hover:bg-orange-50 border border-transparent hover:border-orange-200"
          >
            <Flag size={12} />
            Signaler une erreur dans ce guide
          </button>
        </div>

      </div>

      {/* Lecteur vidéo modal */}
      {activeVideo && <VideoModal video={activeVideo} onClose={() => setActiveVideo(null)} />}

      {/* Modal signalement */}
      <ReportModal
        isOpen={reportOpen}
        onClose={() => setReportOpen(false)}
        contentType="guide"
        subject={intent?.h1 || intent?.title || 'Guide thématique'}
        subjectUrl={typeof window !== 'undefined' ? window.location.href : ''}
        guideSlug={slug}
      />
    </div>
  )
}
