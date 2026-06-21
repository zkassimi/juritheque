import { useState, useEffect } from 'react'
import { Play, AlertCircle } from 'lucide-react'
import { useLang } from '../contexts/LangContext'
import { VIDEOS as MOCK_VIDEOS, DOMAINS as DOMAINS_FALLBACK } from '../data/mockData'
import { supabase } from '../lib/supabase'
import { fetchDomains } from '../lib/api'
import VideoCard from '../components/VideoCard'
import VideoModal from '../components/VideoModal'
import { useSEO } from '../hooks/useSEO'

const LEVELS = ['Débutant', 'Intermédiaire', 'Expert']

export default function Videos() {
  const { t, lang } = useLang()

  useSEO({
    title: 'Vidéos juridiques — Cours et explications de droit marocain',
    description: 'Vidéos pédagogiques sur le droit marocain en darija et français : procédures, contrats, droits des MRE, code du travail. Accessibles à tous, du débutant au juriste.',
    canonical: '/videos',
    type: 'website',
  })

  const [activeVideo, setActiveVideo] = useState(null)
  const [levelFilter,  setLevelFilter]  = useState('')
  const [domainFilter, setDomainFilter] = useState('')
  const [videos, setVideos]   = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(false)
  const [domains, setDomains] = useState([])

  // Charger les vidéos depuis Supabase, fallback mock
  useEffect(() => {
    supabase
      .from('videos')
      .select('*')
      .order('created_at', { ascending: false })
      .then(({ data, error: err }) => {
        if (!err && data && data.length > 0) {
          setVideos(data)
        } else if (!err && data && data.length === 0) {
          // Table vide mais pas d'erreur : afficher état vide (pas de fallback mock)
          setVideos([])
        } else {
          // Erreur réseau → fallback mock
          setVideos(MOCK_VIDEOS)
          setError(false) // mock data disponible, pas une vraie erreur
        }
      })
      .catch(() => { setVideos(MOCK_VIDEOS); setError(false) })
      .finally(() => setLoading(false))
  }, [])

  // Charger les domaines depuis Supabase pour le filtre
  useEffect(() => {
    fetchDomains()
      .then(data => setDomains(data.length ? data : DOMAINS_FALLBACK))
      .catch(() => setDomains(DOMAINS_FALLBACK))
  }, [])

  const filtered = videos.filter(v => {
    const domId = v.domain_id ?? v.domain
    if (levelFilter  && v.level  !== levelFilter)  return false
    if (domainFilter && domId    !== domainFilter)  return false
    return true
  })

  const featured = videos[0] ?? null

  if (loading) return (
    <div className="min-h-screen bg-[#f8fafc] pt-16 flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <div className="w-10 h-10 border-2 border-gold border-t-transparent rounded-full animate-spin" />
        <p className="text-navy-400 text-sm">Chargement des vidéos…</p>
      </div>
    </div>
  )

  if (error) return (
    <div className="min-h-screen bg-[#f8fafc] pt-16 flex items-center justify-center">
      <div className="text-center">
        <AlertCircle size={40} className="text-red-400 mx-auto mb-3" />
        <p className="text-navy-600 text-sm">Impossible de charger les vidéos.</p>
        <button onClick={() => window.location.reload()} className="mt-3 text-xs text-gold hover:underline">Réessayer</button>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      {/* Hero — featured video */}
      {featured && (
        <div className="bg-navy relative overflow-hidden">
          <div className="absolute inset-0 opacity-20">
            <img
              src={featured.thumbnail || `https://img.youtube.com/vi/${featured.youtube_id ?? featured.youtubeId}/maxresdefault.jpg`}
              alt=""
              className="w-full h-full object-cover"
            />
          </div>
          <div className="absolute inset-0 bg-gradient-to-t from-navy via-navy/80 to-navy/40" />

          <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-16">
            <p className="text-gold text-xs font-semibold uppercase tracking-widest mb-3">{t('videos.featured')}</p>
            <h1 className="font-playfair font-bold text-white text-3xl sm:text-4xl max-w-2xl mb-4">
              {lang === 'ar' && featured.title_ar ? featured.title_ar : featured.title_fr}
            </h1>
            <p className="text-white/60 text-sm mb-6">
              {featured.author}
              {featured.duration && <> · {featured.duration}</>}
              {featured.views > 0 && <> · {featured.views.toLocaleString()} {t('videos.views')}</>}
            </p>
            <button
              onClick={() => setActiveVideo(featured)}
              className="flex items-center gap-2.5 px-6 py-3 bg-gold text-navy rounded-xl font-semibold text-sm hover:bg-gold-light transition-colors"
            >
              <Play size={16} fill="currentColor" /> Regarder
            </button>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 mb-8">
          <h2 className="font-playfair font-semibold text-navy text-xl me-4">{t('videos.title')}</h2>
          {/* Level filter */}
          <div className="flex bg-white rounded-xl border border-gray-200 overflow-hidden">
            <button
              onClick={() => setLevelFilter('')}
              className={`px-3 py-2 text-xs font-medium transition-colors ${!levelFilter ? 'bg-navy text-white' : 'text-navy-600 hover:text-navy'}`}
            >
              {t('videos.all_levels')}
            </button>
            {LEVELS.map(l => (
              <button
                key={l}
                onClick={() => setLevelFilter(levelFilter === l ? '' : l)}
                className={`px-3 py-2 text-xs font-medium border-l border-gray-200 transition-colors ${levelFilter === l ? 'bg-navy text-white' : 'text-navy-600 hover:text-navy'}`}
              >
                {l}
              </button>
            ))}
          </div>
          {/* Domain filter */}
          <select
            value={domainFilter}
            onChange={e => setDomainFilter(e.target.value)}
            className="px-3 py-2 text-xs border border-gray-200 rounded-xl bg-white text-navy-700 focus:outline-none focus:border-gold"
          >
            <option value="">{t('videos.all_domains')}</option>
            {domains.map(d => (
              <option key={d.id} value={d.id}>
                {lang === 'ar' ? (d.ar || d.name_ar || d.fr || d.name_fr) : (d.fr || d.name_fr || d.ar || d.name_ar)}
              </option>
            ))}
          </select>
        </div>

        {/* Grid */}
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <Play size={40} className="text-gray-200 mx-auto mb-4" />
            <p className="text-navy-600 font-medium mb-1">{t('db.empty_title')}</p>
            <p className="text-navy-400 text-sm">
              {domainFilter || levelFilter
                ? 'Aucune vidéo pour ces filtres — essayez d\'en modifier un.'
                : 'Aucune vidéo disponible pour le moment.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((video, i) => (
              <div key={video.id} className="animate-fade-in" style={{ animationDelay: `${i * 60}ms` }}>
                <VideoCard video={video} onClick={setActiveVideo} />
              </div>
            ))}
          </div>
        )}
      </div>

      {activeVideo && <VideoModal video={activeVideo} onClose={() => setActiveVideo(null)} />}
    </div>
  )
}
