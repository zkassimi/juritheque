import { useLang } from '../../contexts/LangContext'

const CONFIG = {
  'En vigueur': { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500', key: 'status.active' },
  'Abrogé':     { bg: 'bg-red-50',     text: 'text-red-700',     dot: 'bg-red-500',     key: 'status.repealed' },
  'Modifié':    { bg: 'bg-amber-50',   text: 'text-amber-700',   dot: 'bg-amber-500',   key: 'status.modified' },
}

export default function StatusBadge({ status, size = 'sm' }) {
  const { t } = useLang()
  const cfg = CONFIG[status] ?? CONFIG['En vigueur']
  const px = size === 'lg' ? 'px-3 py-1 text-sm' : 'px-2 py-0.5 text-xs'

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-medium ${cfg.bg} ${cfg.text} ${px}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {t(cfg.key)}
    </span>
  )
}
