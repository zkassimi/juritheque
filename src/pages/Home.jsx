import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen, Bot, PlayCircle, TrendingUp, FileSearch, Bell, Newspaper, Library, Database, Scale } from 'lucide-react'
import { SEO_INTENT_PAGES } from '../data/seoIntentPages'
import { GLOSSAIRE } from '../data/glossaire'
import { useLang } from '../contexts/LangContext'
import { DOMAINS as DOMAINS_FALLBACK, VIDEOS as VIDEOS_FALLBACK, STATS as STATS_FALLBACK } from '../data/mockData'
import { fetchRecentLaws, fetchDomains, fetchStats } from '../lib/api'
import { useSEO } from '../hooks/useSEO'
import JsonLD, { websiteSchema, organizationSchema } from '../components/JsonLD'
import SearchBar from '../components/SearchBar'
import DomainCard from '../components/DomainCard'
import LawCard from '../components/LawCard'
import VideoCard from '../components/VideoCard'
import VideoModal from '../components/VideoModal'

function AnimatedCounter({ target, duration = 1500 }) {
  const [count, setCount] = useState(0)
  const ref = useRef(null)
  const started = useRef(false)

  useEffect(() => {
    started.current = false
    setCount(0)
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true
        const start = Date.now()
        const tick = () => {
          const elapsed = Date.now() - start
          const progress = Math.min(elapsed / duration, 1)
          const eased = 1 - Math.pow(1 - progress, 3)
          setCount(Math.round(eased * target))
          if (progress < 1) requestAnimationFrame(tick)
        }
        requestAnimationFrame(tick)
      }
    }, { threshold: 0.1 })
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [target, duration])

  return <span ref={ref}>{count.toLocaleString()}</span>
}

const FEATURED_GUIDES = [
  'licenciement-maroc',
  'sarl-maroc',
  'divorce-maroc',
  'code-du-travail-maroc',
  'bail-commercial-maroc',
  'cheque-sans-provision-maroc',
  'recouvrement-maroc',
  'collectivites-territoriales-maroc',
]

export default function Home() {
  const { t, lang } = useLang()

  useSEO({
    title: 'La référence juridique marocaine — Lois, Décrets, Dahirs',
    description: 'JuriThèque — 7 400+ textes juridiques marocains bilingues (français/arabe) : lois, dahirs, décrets, codes. Gratuit. Pour MRE, investisseurs, étudiants et juristes au Maroc.',
    canonical: '/',
    type: 'website',
  })

  const [activeVideo, setActiveVideo]       = useState(null)
  const [recentLaws, setRecentLaws]         = useState([])
  const [domains, setDomains]               = useState(DOMAINS_FALLBACK)
  const [stats, setStats]                   = useState(STATS_FALLBACK)
  const [featuredVideos, setFeaturedVideos] = useState(VIDEOS_FALLBACK.slice(0, 3))

  useEffect(() => {
    fetchRecentLaws(6).then(setRecentLaws).catch(() => {})
    fetchDomains().then(data => { if (data.length) setDomains(data) }).catch(() => {})
    fetchStats()
      .then(({ lawsCount, domainsCount }) => {
        setStats(prev => prev.map(s => {
          if (s.key === 'texts'   && lawsCount    > 0) return { ...s, value: lawsCount }
          if (s.key === 'domains' && domainsCount > 0) return { ...s, value: domainsCount }
          return s
        }))
      })
      .catch(() => {})

    import('../lib/supabase').then(({ supabase }) => {
      supabase.from('videos').select('*').order('views', { ascending: false }).limit(3)
        .then(({ data }) => { if (data && data.length > 0) setFeaturedVideos(data) })
        .catch(() => {})
    })
  }, [])

  const glossaireSample = GLOSSAIRE.slice(0, 6)

  return (
    <div className="min-h-screen">
      <JsonLD data={[websiteSchema(), organizationSchema()]} />

      {/* ═══ HERO ═══ */}
      <section className="hero-bg noise-overlay min-h-[88vh] flex items-center relative pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 lg:py-14 w-full">
          <div className="max-w-2xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/10 border border-white/20 text-gold text-xs font-medium mb-5 animate-fade-in">
              <span className="w-1.5 h-1.5 rounded-full bg-gold animate-pulse" />
              {t('hero.eyebrow')}
            </div>
            <h1 className="font-playfair font-bold text-white text-4xl sm:text-5xl lg:text-5xl xl:text-6xl leading-tight mb-2 animate-fade-in animate-stagger-1">
              {t('hero.title')}
            </h1>
            <p className="font-arabic text-white/60 text-lg sm:text-xl mb-5 animate-fade-in animate-stagger-2">
              {t('hero.title_ar')}
            </p>
            <div className="gold-line w-24 mx-auto mb-5" />
            <p className="text-white/70 text-sm sm:text-base leading-relaxed mb-6 max-w-lg mx-auto animate-fade-in animate-stagger-2">
              {t('hero.subtitle')}
            </p>
            <div className="animate-fade-in animate-stagger-3 relative z-20">
              <SearchBar size="lg" className="max-w-xl mx-auto shadow-2xl" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-xl mx-auto mt-5 animate-fade-in animate-stagger-4 relative z-10">
              {[
                { to: '/base',      icon: BookOpen,   label: t('hero.cta_browse'), bg: 'bg-white/10 hover:bg-white/20' },
                { to: '/assistant', icon: Bot,        label: t('hero.cta_ai'),     bg: 'bg-gold/80 hover:bg-gold' },
                { to: '/videos',    icon: PlayCircle, label: t('hero.cta_videos'), bg: 'bg-white/10 hover:bg-white/20' },
              ].map(({ to, icon: Icon, label, bg }) => (
                <Link key={to} to={to}
                  className={`flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-white text-sm font-medium ${bg} border border-white/20 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg`}
                >
                  <Icon size={16} />{label}
                </Link>
              ))}
            </div>
          </div>
        </div>
        <div className="absolute bottom-0 inset-x-0 h-24 bg-gradient-to-t from-[#f8fafc] to-transparent pointer-events-none" />
      </section>

      {/* ═══ STATS ═══ */}
      <section className="py-8 bg-white border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-0 divide-x divide-gray-100">
            {stats.map((stat, i) => (
              <div key={stat.key} className="text-center px-4 sm:px-8 py-4">
                <div className="font-playfair font-bold text-3xl sm:text-4xl text-navy mb-1">
                  <AnimatedCounter target={stat.value} duration={1200 + i * 200} />
                  <span className="text-gold">+</span>
                </div>
                <p className="text-xs sm:text-sm text-navy-600">
                  {lang === 'ar' ? stat.label_ar : stat.label_fr}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ DOMAINES ═══ */}
      <section className="py-16 bg-[#f8fafc]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between mb-8">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-gold mb-1">{t('nav.domains')}</p>
              <h2 className="font-playfair font-bold text-navy text-2xl sm:text-3xl">{t('home.domains_title')}</h2>
            </div>
            <Link to="/domaines" className="hidden sm:flex items-center gap-1.5 text-sm text-gold font-medium hover:gap-2.5 transition-all">
              {t('common.view_all')} <ArrowRight size={14} />
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {domains.slice(0, 8).map(domain => (
              <DomainCard key={domain.id} domain={domain} />
            ))}
          </div>
        </div>
      </section>

      {/* ═══ BASE DE DONNÉES ═══ */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between mb-8">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-gold mb-1">
                <Database size={11} className="inline mr-1" />{t('home.db_badge')}
              </p>
              <h2 className="font-playfair font-bold text-navy text-2xl sm:text-3xl">{t('home.recent_laws_title')}</h2>
            </div>
            <Link to="/base" className="hidden sm:flex items-center gap-1.5 text-sm text-gold font-medium hover:gap-2.5 transition-all">
              {t('common.view_all')} <ArrowRight size={14} />
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {recentLaws.map((law, i) => (
              <div key={law.id} className="animate-fade-in" style={{ animationDelay: `${i * 80}ms` }}>
                <LawCard law={law} />
              </div>
            ))}
          </div>
          <div className="mt-8 text-center">
            <Link to="/base"
              className="inline-flex items-center gap-2 px-6 py-3 bg-navy text-white rounded-xl text-sm font-semibold hover:bg-gold hover:text-navy transition-colors"
            >
              {t('home.view_database')} <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ GUIDES JURIDIQUES ═══ */}
      <section className="py-16 bg-[#f8fafc]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between mb-8">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-gold mb-1">
                <BookOpen size={11} className="inline mr-1" />{t('home.guides_badge')}
              </p>
              <h2 className="font-playfair font-bold text-navy text-2xl sm:text-3xl">{t('home.guides_explore')}</h2>
            </div>
            <Link to="/fr/guides" className="hidden sm:flex items-center gap-1.5 text-sm text-gold font-medium hover:gap-2.5 transition-all">
              {t('home.all_guides')} <ArrowRight size={14} />
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {FEATURED_GUIDES.map(slug => {
              const guide = SEO_INTENT_PAGES.find(g => g.slug === slug)
              if (!guide) return null
              return (
                <Link key={guide.slug} to={`/fr/guides/${guide.slug}`}
                  className="group flex items-start gap-3 p-4 bg-white rounded-xl border border-gray-100 hover:border-gold hover:shadow-md transition-all duration-200"
                >
                  <div className="w-8 h-8 rounded-lg bg-gold/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <BookOpen size={14} className="text-gold" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-navy group-hover:text-gold transition-colors leading-snug">
                      {(lang === 'ar' && guide.h1_ar) ? guide.h1_ar : guide.h1}
                    </p>
                    {guide.category && (
                      <p className="text-[10px] text-navy-400 mt-1 uppercase tracking-wide">{guide.category}</p>
                    )}
                  </div>
                </Link>
              )
            })}
          </div>
          <div className="mt-6 text-center">
            <Link to="/fr/guides"
              className="inline-flex items-center gap-2 px-5 py-2.5 border border-gold text-gold rounded-xl text-sm font-semibold hover:bg-gold hover:text-navy transition-colors"
            >
              {t('home.see_n_guides').replace('{n}', SEO_INTENT_PAGES.length)} <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ VEILLE & BULLETINS ═══ */}
      <section className="py-16 bg-white border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-widest text-gold mb-1">
              <TrendingUp size={11} className="inline mr-1" />{t('home.news_badge')}
            </p>
            <h2 className="font-playfair font-bold text-navy text-2xl sm:text-3xl">{t('home.newsletter_title')}</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Veille juridique */}
            <Link to="/fr/veille-juridique"
              className="group relative overflow-hidden rounded-2xl bg-navy p-8 hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
            >
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full bg-gold/10 blur-2xl" />
              <div className="relative z-10">
                <div className="w-12 h-12 rounded-xl bg-gold/20 flex items-center justify-center mb-5">
                  <Bell size={22} className="text-gold" />
                </div>
                <h3 className="font-playfair font-bold text-white text-xl mb-2">{t('home.watch_card_title')}</h3>
                <p className="text-white/60 text-sm mb-5 leading-relaxed">
                  {t('home.watch_card_desc')}
                </p>
                <span className="inline-flex items-center gap-2 text-gold text-sm font-semibold group-hover:gap-3 transition-all">
                  {t('home.watch_card_cta')} <ArrowRight size={14} />
                </span>
              </div>
            </Link>

            {/* Bulletins Officiels */}
            <Link to="/fr/bulletins-officiels"
              className="group relative overflow-hidden rounded-2xl bg-[#f8fafc] border border-gray-200 p-8 hover:border-gold hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
            >
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full bg-gold/5 blur-2xl" />
              <div className="relative z-10">
                <div className="w-12 h-12 rounded-xl bg-navy/10 flex items-center justify-center mb-5">
                  <Newspaper size={22} className="text-navy" />
                </div>
                <h3 className="font-playfair font-bold text-navy text-xl mb-2">{t('home.bo_card_title')}</h3>
                <p className="text-navy-500 text-sm mb-5 leading-relaxed">
                  {t('home.bo_card_desc')}
                </p>
                <span className="inline-flex items-center gap-2 text-gold text-sm font-semibold group-hover:gap-3 transition-all">
                  {t('home.bo_card_cta')} <ArrowRight size={14} />
                </span>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ GLOSSAIRE ═══ */}
      <section className="py-14 bg-[#f8fafc]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-gold mb-1">
                <Library size={11} className="inline mr-1" />{t('home.glossary_badge')}
              </p>
              <h2 className="font-playfair font-bold text-navy text-2xl sm:text-3xl">{t('home.glossary_title')}</h2>
            </div>
            <Link to="/glossaire" className="hidden sm:flex items-center gap-1.5 text-sm text-gold font-medium hover:gap-2.5 transition-all">
              {t('home.see_terms').replace('{n}', GLOSSAIRE.length)} <ArrowRight size={14} />
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {glossaireSample.map(entry => (
              <Link key={entry.term} to="/glossaire"
                className="group flex items-start gap-3 p-4 bg-white rounded-xl border border-gray-100 hover:border-gold hover:shadow-sm transition-all duration-200"
              >
                <div className="w-8 h-8 rounded-lg bg-navy/5 flex items-center justify-center flex-shrink-0 mt-0.5 font-playfair font-bold text-navy text-sm">
                  {entry.term[0]}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-navy group-hover:text-gold transition-colors truncate">{entry.term}</p>
                  {entry.term_ar && (
                    <p className="font-arabic text-xs text-navy-400 truncate">{entry.term_ar}</p>
                  )}
                  {entry.definition && (
                    <p className="text-[11px] text-navy-500 mt-1 line-clamp-2 leading-relaxed">{entry.definition}</p>
                  )}
                </div>
              </Link>
            ))}
          </div>
          <div className="mt-6 text-center">
            <Link to="/glossaire"
              className="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-200 text-navy rounded-xl text-sm font-semibold hover:border-gold hover:text-gold transition-colors"
            >
              <Library size={14} />{t('home.full_glossary')}
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ VIDÉOS ═══ */}
      <section className="py-16 bg-white border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-gold mb-1">
                <PlayCircle size={11} className="inline mr-1" />{t('home.videos_badge')}
              </p>
              <h2 className="font-playfair font-bold text-navy text-2xl sm:text-3xl">{t('home.videos_title')}</h2>
            </div>
            <Link to="/videos" className="hidden sm:flex items-center gap-1.5 text-sm text-gold font-medium hover:gap-2.5 transition-all">
              {t('common.view_all')} <ArrowRight size={14} />
            </Link>
          </div>
          <p className="text-sm text-navy-500 mb-7 max-w-2xl">
            {t('home.videos_desc')}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {featuredVideos.map(video => (
              <VideoCard key={video.id} video={video} onClick={setActiveVideo} />
            ))}
          </div>
          <div className="mt-8 text-center">
            <Link to="/videos"
              className="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-200 text-navy rounded-xl text-sm font-semibold hover:border-gold hover:text-gold transition-colors"
            >
              <PlayCircle size={14} />{t('home.all_videos')}
            </Link>
          </div>
        </div>
      </section>

      {activeVideo && <VideoModal video={activeVideo} onClose={() => setActiveVideo(null)} />}
    </div>
  )
}
