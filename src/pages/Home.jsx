import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen, Bot, PlayCircle, TrendingUp, FileSearch, Bell, Newspaper } from 'lucide-react'
import { SEO_INTENT_PAGES } from '../data/seoIntentPages'
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
    // Réinitialiser à chaque changement de target (ex: quand Supabase répond)
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

export default function Home() {
  const { t, lang } = useLang()

  useSEO({
    title: 'La référence juridique marocaine — Lois, Décrets, Dahirs',
    description: 'JuriThèque — 7 400+ textes juridiques marocains bilingues (français/arabe) : lois, dahirs, décrets, codes. Gratuit. Pour MRE, investisseurs, étudiants et juristes au Maroc.',
    canonical: '/',
    type: 'website',
  })

  const [activeVideo, setActiveVideo]   = useState(null)
  const [recentLaws, setRecentLaws]     = useState([])
  const [domains, setDomains]           = useState(DOMAINS_FALLBACK)
  const [stats, setStats]               = useState(STATS_FALLBACK)
  const [featuredVideos, setFeaturedVideos] = useState(VIDEOS_FALLBACK.slice(0, 3))

  useEffect(() => {
    fetchRecentLaws(6).then(setRecentLaws).catch(() => {})

    fetchDomains()
      .then(data => { if (data.length) setDomains(data) })
      .catch(() => {})

    fetchStats()
      .then(({ lawsCount, domainsCount }) => {
        setStats(prev => prev.map(s => {
          if (s.key === 'texts'   && lawsCount    > 0) return { ...s, value: lawsCount }
          if (s.key === 'domains' && domainsCount > 0) return { ...s, value: domainsCount }
          return s
        }))
      })
      .catch(() => {})

    // Charger les vraies vidéos depuis Supabase
    import('../lib/supabase').then(({ supabase }) => {
      supabase
        .from('videos')
        .select('*')
        .order('views', { ascending: false })
        .limit(3)
        .then(({ data }) => {
          if (data && data.length > 0) setFeaturedVideos(data)
        })
        .catch(() => {})
    })
  }, [])

  return (
    <div className="min-h-screen">
      <JsonLD data={[websiteSchema(), organizationSchema()]} />

      {/* ═══ HERO ═══ */}
      <section className="hero-bg noise-overlay min-h-[88vh] flex items-center relative pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 lg:py-14 w-full">
          <div className="max-w-2xl mx-auto text-center">
            {/* Eyebrow */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/10 border border-white/20 text-gold text-xs font-medium mb-5 animate-fade-in">
              <span className="w-1.5 h-1.5 rounded-full bg-gold animate-pulse" />
              {t('hero.eyebrow')}
            </div>

            {/* Headline */}
            <h1 className="font-playfair font-bold text-white text-4xl sm:text-5xl lg:text-5xl xl:text-6xl leading-tight mb-2 animate-fade-in animate-stagger-1">
              {t('hero.title')}
            </h1>
            <p className="font-arabic text-white/60 text-lg sm:text-xl mb-5 animate-fade-in animate-stagger-2">
              {t('hero.title_ar')}
            </p>

            {/* Gold divider */}
            <div className="gold-line w-24 mx-auto mb-5" />

            <p className="text-white/70 text-sm sm:text-base leading-relaxed mb-6 max-w-lg mx-auto animate-fade-in animate-stagger-2">
              {t('hero.subtitle')}
            </p>

            {/* Search */}
            <div className="animate-fade-in animate-stagger-3 relative z-20">
              <SearchBar size="lg" className="max-w-xl mx-auto shadow-2xl" />
            </div>

            {/* CTA cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-xl mx-auto mt-5 animate-fade-in animate-stagger-4 relative z-10">
              {[
                { to: '/base',      icon: BookOpen,   label: t('hero.cta_browse'), bg: 'bg-white/10 hover:bg-white/20' },
                { to: '/assistant', icon: Bot,        label: t('hero.cta_ai'),     bg: 'bg-gold/80 hover:bg-gold' },
                { to: '/videos',    icon: PlayCircle, label: t('hero.cta_videos'), bg: 'bg-white/10 hover:bg-white/20' },
              ].map(({ to, icon: Icon, label, bg }) => (
                <Link
                  key={to}
                  to={to}
                  className={`flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-white text-sm font-medium ${bg} border border-white/20 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg`}
                >
                  <Icon size={16} />{label}
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom fade — pointer-events-none pour ne pas bloquer les boutons */}
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

      {/* ═══ DOMAINS ═══ */}
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
            {domains.map(domain => (
              <DomainCard key={domain.id} domain={domain} />
            ))}
          </div>
        </div>
      </section>

      {/* ═══ EXPLORER PAR BESOIN ═══ */}
      <section className="py-14 bg-white border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-gold mb-1">
                <FileSearch size={11} className="inline mr-1" />Guides &amp; Veille
              </p>
              <h2 className="font-playfair font-bold text-navy text-2xl sm:text-3xl">Explorer par besoin juridique</h2>
            </div>
            <Link to="/fr/guides" className="hidden sm:flex items-center gap-1.5 text-sm text-gold font-medium hover:gap-2.5 transition-all">
              Tous les guides <ArrowRight size={14} />
            </Link>
          </div>
          <div className="flex flex-wrap gap-2">
            {/* Veille juridique — mise en avant */}
            <Link
              to="/fr/veille-juridique"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-navy border border-navy rounded-xl text-xs font-semibold text-white hover:bg-gold hover:border-gold hover:text-navy transition-colors"
            >
              <Bell size={12} className="flex-shrink-0" />
              Veille juridique
            </Link>
            {/* Bulletins Officiels */}
            <Link
              to="/fr/bulletins-officiels"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-navy/80 border border-navy/60 rounded-xl text-xs font-semibold text-white hover:bg-gold hover:border-gold hover:text-navy transition-colors"
            >
              <Newspaper size={12} className="flex-shrink-0" />
              Bulletins Officiels
            </Link>
            {/* 8 guides prioritaires selon les intentions de recherche principales */}
            {[
              'code-du-travail-maroc',
              'sarl-maroc',
              'divorce-maroc',
              'bail-commercial-maroc',
              'licenciement-maroc',
              'recouvrement-maroc',
              'cheque-sans-provision-maroc',
              'collectivites-territoriales-maroc',
            ].map(slug => {
              const guide = SEO_INTENT_PAGES.find(g => g.slug === slug)
              if (!guide) return null
              return (
                <Link
                  key={guide.slug}
                  to={`/fr/guides/${guide.slug}`}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#f8fafc] border border-gray-200 rounded-xl text-xs font-medium text-navy-700 hover:border-gold hover:text-gold transition-colors"
                >
                  <BookOpen size={12} className="text-gold flex-shrink-0" />
                  {guide.h1}
                </Link>
              )
            })}
            <Link
              to="/fr/guides"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-gold/10 border border-gold/30 rounded-xl text-xs font-semibold text-gold hover:bg-gold hover:text-navy transition-colors"
            >
              + {SEO_INTENT_PAGES.length - 8} autres <ArrowRight size={11} />
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ RECENT TEXTS ═══ */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between mb-8">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-gold mb-1">
                <TrendingUp size={11} className="inline mr-1" />Récent
              </p>
              <h2 className="font-playfair font-bold text-navy text-2xl sm:text-3xl">{t('home.recent_title')}</h2>
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
          <div className="mt-6 text-center">
            <Link
              to="/base"
              className="inline-flex items-center gap-2 px-6 py-3 bg-navy text-white rounded-xl text-sm font-semibold hover:bg-gold hover:text-navy transition-colors"
            >
              {t('db.title')} <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ VIDEOS ═══ */}
      <section className="py-16 bg-navy relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-64 h-64 rounded-full bg-gold/5 blur-3xl" />
        <div className="absolute bottom-0 left-0 w-48 h-48 rounded-full bg-blue-500/5 blur-3xl" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 relative z-10">
          <div className="flex items-center justify-between mb-8">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-gold mb-1">Vidéos</p>
              <h2 className="font-playfair font-bold text-white text-2xl sm:text-3xl">{t('home.videos_title')}</h2>
            </div>
            <Link to="/videos" className="hidden sm:flex items-center gap-1.5 text-sm text-gold font-medium hover:gap-2.5 transition-all">
              {t('common.view_all')} <ArrowRight size={14} />
            </Link>
          </div>
          <p className="text-sm text-white/60 mb-6 max-w-2xl">
            Sélection de vidéos pédagogiques pour comprendre les principales notions du droit marocain.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {featuredVideos.map(video => (
              <VideoCard key={video.id} video={video} onClick={setActiveVideo} />
            ))}
          </div>
        </div>
      </section>

      {activeVideo && <VideoModal video={activeVideo} onClose={() => setActiveVideo(null)} />}
    </div>
  )
}
