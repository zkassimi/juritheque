import { Link } from 'react-router-dom'
import { Calendar, Tag, Heart, ArrowRight } from 'lucide-react'
import { useLang } from '../contexts/LangContext'
import { useAuth } from '../contexts/AuthContext'
import { LAW_TYPES } from '../data/mockData'
import StatusBadge from './ui/StatusBadge'
import TypeBadge from './ui/TypeBadge'
import { lawPath } from '../lib/lawUtils'

// Filtre les numéros de loi propres — rejette les slugs/filenames
const isCleanNumber = (n) => {
  if (!n || typeof n !== 'string') return false
  if (n.startsWith('adala-')) return false
  if (n.includes('_') || n.includes('.consolide') || n.includes('.pdf')) return false
  if (n.length > 20) return false
  if (/^[a-z]{3,}(-[a-z]{2,}){2,}/.test(n)) return false // slug style
  return true
}

// Domain accent colors — matches DomainCard palette
const DOMAIN_COLORS = {
  civil:            '#3b82f6',
  penal:            '#ef4444',
  commercial:       '#f59e0b',
  administratif:    '#8b5cf6',
  travail:          '#10b981',
  fiscal:           '#f97316',
  international:    '#06b6d4',
  numerique:        '#6366f1',
  constitutionnel:  '#ec4899',
  bancaire:         '#0ea5e9',
  finances_publiques:'#84cc16',
  transport:        '#9333ea',
  environnement:    '#16a34a',
  sante:            '#e11d48',
  energie:          '#f59e0b',
  collectivites:    '#0369a1',
}

// Detect garbled title: replacement chars, Arabic Presentation Forms (FB50-FEFF), OCR noise
const isGarbled = (str) => {
  if (!str) return true
  const clean = str.replace(/\s/g, '')
  if (clean.length === 0) return true
  let bad = 0
  for (const c of clean) {
    const cp = c.codePointAt(0)
    // replacement char, control chars, Arabic Presentation Forms (legacy visual encoding)
    if (cp === 0xFFFD || cp < 0x0020 || (cp >= 0xFB50 && cp <= 0xFEFF)) bad++
  }
  return bad / clean.length > 0.25
}

export default function LawCard({ law, view = 'grid' }) {
  const { lang, t, isRTL } = useLang()
  const { user, toggleFavorite, isFavorite } = useAuth()

  // Border: prefer domain color, fall back to type color
  const borderColor = DOMAIN_COLORS[law.domain_id] ?? LAW_TYPES[law.type]?.color ?? '#64748b'
  const domainLabel = law.domain_id ? law.domain_id.charAt(0).toUpperCase() + law.domain_id.slice(1) : ''

  // Smart title: handle missing/generic title_fr (= just the type name) → fallback to title_ar
  const titleFrOk = law.title_fr?.trim() &&
    !/^\d+$/.test(law.title_fr.trim()) &&
    law.title_fr.trim().toLowerCase() !== (law.type || '').toLowerCase()

  const titleArOk = law.title_ar && !isGarbled(law.title_ar)

  let rawTitle
  if (lang === 'ar' && titleArOk) {
    rawTitle = law.title_ar
  } else if (titleFrOk) {
    rawTitle = law.title_fr
  } else if (titleArOk) {
    rawTitle = law.title_ar  // fallback AR quand title_fr absent ou générique
  } else {
    rawTitle = law.title_fr
  }

  const title = (rawTitle && rawTitle.trim() && !/^\d+$/.test(rawTitle.trim()))
    ? rawTitle
    : law.number ? `Texte N° ${law.number}` : 'Texte juridique'

  const excerpt = (lang === 'ar' && law.excerpt_ar) ? law.excerpt_ar : law.excerpt_fr
  const fav = user && isFavorite(law.id)

  const handleFav = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (user) toggleFavorite(law)
  }

  if (view === 'list') {
    return (
      <Link
        to={lawPath(law, lang)}
        className="group flex items-start gap-4 bg-white rounded-xl border border-gray-100 px-5 py-4 hover:shadow-md hover:border-gold/30 transition-all duration-200"
        style={{ borderLeft: `4px solid ${borderColor}` }}
      >
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <TypeBadge type={law.type} />
            <StatusBadge status={law.status} />
            {isCleanNumber(law.number) && (
              <span className="text-xs text-navy-500">{law.number}</span>
            )}
          </div>
          <h3 className={`font-semibold text-navy text-sm leading-snug group-hover:text-gold transition-colors line-clamp-1 ${lang === 'ar' ? 'font-arabic' : 'font-playfair'}`}>
            {title}
          </h3>
          <p className="text-navy-600 text-xs mt-1 line-clamp-1">{excerpt}</p>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0 text-xs text-navy-500">
          {domainLabel && <span className="hidden md:block">{domainLabel}</span>}
          <span className="flex items-center gap-1"><Calendar size={11} />{law.date ? law.date.slice(0, 4) : '—'}</span>
          {user && (
            <button onClick={handleFav} className={`p-2 rounded-lg transition-colors ${fav ? 'text-gold' : 'text-gray-300 hover:text-gold'}`}>
              <Heart size={14} fill={fav ? 'currentColor' : 'none'} />
            </button>
          )}
        </div>
      </Link>
    )
  }

  return (
    <Link
      to={lawPath(law, lang)}
      className="group bg-white rounded-xl border border-gray-100 p-5 hover:shadow-lg hover:border-gold/30 transition-all duration-200 flex flex-col overflow-hidden"
      style={{ borderLeft: `4px solid ${borderColor}` }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="flex flex-wrap gap-1.5 min-w-0">
          <TypeBadge type={law.type} />
          <StatusBadge status={law.status} />
        </div>
        {user && (
          <button onClick={handleFav} className={`flex-shrink-0 p-1.5 rounded-lg transition-colors ${fav ? 'text-gold' : 'text-gray-300 hover:text-gold'}`}>
            <Heart size={15} fill={fav ? 'currentColor' : 'none'} />
          </button>
        )}
      </div>

      {/* Number */}
      {isCleanNumber(law.number) && (
        <p className="text-xs text-navy-500 mb-1.5 truncate">{law.number}</p>
      )}

      {/* Title */}
      <h3 className={`font-semibold text-navy text-sm leading-snug group-hover:text-gold transition-colors mb-2 line-clamp-2 break-words ${lang === 'ar' ? 'font-arabic text-base' : 'font-playfair'}`}>
        {title}
      </h3>

      {/* Excerpt */}
      <p className={`text-navy-600 text-xs leading-relaxed line-clamp-2 flex-1 ${lang === 'ar' ? 'font-arabic' : ''}`}>
        {excerpt}
      </p>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-gray-50 flex items-center justify-between">
        <div className="flex items-center gap-3 text-xs text-navy-500">
          <span className="flex items-center gap-1"><Calendar size={11} />{law.date ?? '—'}</span>
          {law.bo_number && (
            <span className="text-[10px] bg-gray-50 text-navy-500 px-1.5 py-0.5 rounded font-medium">
              BO {law.bo_number}
            </span>
          )}
        </div>
        <span className="text-gold text-xs font-medium flex items-center gap-0.5 group-hover:gap-1.5 transition-all">
          {t('common.read_more')} <ArrowRight size={11} />
        </span>
      </div>

      {/* Tags */}
      {law.tags?.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {law.tags.slice(0, 3).map(tag => (
            <span key={tag} className="flex items-center gap-0.5 text-[10px] text-navy-500 bg-gray-50 px-1.5 py-0.5 rounded">
              <Tag size={9} />{tag}
            </span>
          ))}
        </div>
      )}
    </Link>
  )
}
