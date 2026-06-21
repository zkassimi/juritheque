import { LAW_TYPES } from '../../data/mockData'
import { useLang } from '../../contexts/LangContext'

export default function TypeBadge({ type, size = 'sm' }) {
  const { lang } = useLang()
  const cfg = LAW_TYPES[type] ?? { color: '#64748b', bg: '#f8fafc', label_ar: type }
  const label = lang === 'ar' ? cfg.label_ar : type
  const px = size === 'lg' ? 'px-3 py-1 text-sm' : 'px-2 py-0.5 text-xs'

  return (
    <span
      className={`inline-flex items-center rounded font-semibold tracking-wide ${px}`}
      style={{ color: cfg.color, backgroundColor: cfg.bg, border: `1px solid ${cfg.color}30` }}
    >
      {label}
    </span>
  )
}
