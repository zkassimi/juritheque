import { Play, Clock, Eye, Star } from 'lucide-react'
import { useLang } from '../contexts/LangContext'
import { DOMAINS } from '../data/mockData'

const LEVEL_COLORS = {
  'Débutant':      { bg: 'bg-emerald-50', text: 'text-emerald-700' },
  'Intermédiaire': { bg: 'bg-blue-50',    text: 'text-blue-700' },
  'Expert':        { bg: 'bg-purple-50',  text: 'text-purple-700' },
}

export default function VideoCard({ video, onClick }) {
  const { lang, t } = useLang()
  // Normalize: Supabase uses youtube_id + domain_id; mockData uses youtubeId + domain
  const ytId   = video.youtube_id  ?? video.youtubeId
  const domId  = video.domain_id   ?? video.domain
  const domain = DOMAINS.find(d => d.id === domId)
  const lvl    = LEVEL_COLORS[video.level] ?? LEVEL_COLORS['Débutant']
  const title  = lang === 'ar' && video.title_ar ? video.title_ar : video.title_fr
  const thumb  = video.thumbnail || `https://img.youtube.com/vi/${ytId}/mqdefault.jpg`

  return (
    <div
      onClick={() => onClick(video)}
      className="group bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-xl hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
    >
      {/* Thumbnail */}
      <div className="relative aspect-video bg-navy-800 overflow-hidden">
        <img
          src={thumb}
          alt={title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          onError={e => { e.target.src = `https://img.youtube.com/vi/${ytId}/mqdefault.jpg` }}
        />
        <div className="absolute inset-0 bg-navy/40 group-hover:bg-navy/20 transition-colors duration-200" />
        {/* Play button */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center border border-white/30 group-hover:scale-110 group-hover:bg-gold/80 transition-all duration-200">
            <Play size={18} className="text-white fill-white ml-0.5" />
          </div>
        </div>
        {/* Duration badge */}
        <span className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-0.5 rounded flex items-center gap-1">
          <Clock size={10} />{video.duration}
        </span>
        {/* Level badge */}
        <span className={`absolute top-2 left-2 text-xs px-2 py-0.5 rounded-full font-medium ${lvl.bg} ${lvl.text}`}>
          {video.level}
        </span>
      </div>

      {/* Content */}
      <div className="p-4">
        {domain && (
          <span className="text-[11px] font-semibold text-gold uppercase tracking-wide">
            {lang === 'ar' ? domain.ar : domain.fr}
          </span>
        )}
        <h3 className={`font-semibold text-navy text-sm leading-snug mt-1 mb-2 line-clamp-2 group-hover:text-gold transition-colors ${lang === 'ar' ? 'font-arabic' : ''}`}>
          {title}
        </h3>
        <div className="flex items-center justify-between text-xs text-navy-500">
          <span className="truncate max-w-[140px]">{t('videos.author')} {video.author}</span>
          <span className="flex items-center gap-1 flex-shrink-0">
            <Eye size={11} />{video.views.toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  )
}
