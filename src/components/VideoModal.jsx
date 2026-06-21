import { useEffect } from 'react'
import { X, ExternalLink } from 'lucide-react'
import { useLang } from '../contexts/LangContext'

export default function VideoModal({ video, onClose }) {
  const { lang } = useLang()

  useEffect(() => {
    const handler = (e) => e.key === 'Escape' && onClose()
    document.addEventListener('keydown', handler)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', handler)
      document.body.style.overflow = ''
    }
  }, [onClose])

  if (!video) return null
  const title = lang === 'ar' && video.title_ar ? video.title_ar : video.title_fr
  const ytId  = video.youtube_id ?? ytId

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <div className="absolute inset-0 bg-navy/80 backdrop-blur-sm" onClick={onClose} />
      <div className="relative z-10 w-full max-w-4xl bg-white rounded-2xl overflow-hidden shadow-2xl animate-slide-up">
        {/* Header */}
        <div className="flex items-start justify-between p-4 border-b border-gray-100">
          <h3 className={`font-semibold text-navy text-sm leading-snug pr-4 ${lang === 'ar' ? 'font-arabic' : 'font-playfair'}`}>
            {title}
          </h3>
          <button onClick={onClose} className="flex-shrink-0 p-1.5 rounded-lg hover:bg-gray-100 text-navy-600 transition-colors">
            <X size={18} />
          </button>
        </div>
        {/* Video embed */}
        <div className="aspect-video bg-black">
          <iframe
            src={`https://www.youtube.com/embed/${ytId}?autoplay=1&rel=0`}
            title={title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="w-full h-full"
          />
        </div>
        {/* Footer */}
        <div className="flex items-center justify-between px-4 py-3 bg-gray-50">
          <div className="text-xs text-navy-600">
            <span className="font-medium">{video.author}</span>
            <span className="mx-2 text-gray-300">·</span>
            <span>{video.duration}</span>
            <span className="mx-2 text-gray-300">·</span>
            <span>{video.views.toLocaleString()} vues</span>
          </div>
          <a
            href={`https://youtube.com/watch?v=${ytId}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-gold hover:text-gold-dark"
          >
            YouTube <ExternalLink size={11} />
          </a>
        </div>
      </div>
    </div>
  )
}
