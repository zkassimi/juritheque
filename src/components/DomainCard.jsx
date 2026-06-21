import { Link } from 'react-router-dom'
import { Scale, Gavel, Briefcase, Building2, Users, Receipt, Globe, Monitor, Landmark, CreditCard, BarChart2, Truck, Leaf, Heart, Zap, MapPin, ArrowRight } from 'lucide-react'
import { useLang } from '../contexts/LangContext'

const ICONS = { Scale, Gavel, Briefcase, Building2, Users, Receipt, Globe, Monitor, Landmark, CreditCard, BarChart2, Truck, Leaf, Heart, Zap, MapPin }

const DOMAIN_STYLES = {
  civil:              { color: '#2563eb', light: '#eff6ff', border: '#bfdbfe' },
  penal:              { color: '#7c3aed', light: '#f5f3ff', border: '#ddd6fe' },
  commercial:         { color: '#059669', light: '#ecfdf5', border: '#a7f3d0' },
  administratif:      { color: '#d97706', light: '#fffbeb', border: '#fde68a' },
  travail:            { color: '#0d9488', light: '#f0fdfa', border: '#99f6e4' },
  fiscal:             { color: '#ca8a04', light: '#fefce8', border: '#fef08a' },
  international:      { color: '#0891b2', light: '#ecfeff', border: '#a5f3fc' },
  numerique:          { color: '#4f46e5', light: '#eef2ff', border: '#c7d2fe' },
  constitutionnel:    { color: '#dc2626', light: '#fef2f2', border: '#fecaca' },
  bancaire:           { color: '#0369a1', light: '#f0f9ff', border: '#bae6fd' },
  finances_publiques: { color: '#15803d', light: '#f0fdf4', border: '#bbf7d0' },
  // Nouveaux domaines
  transport:          { color: '#9333ea', light: '#faf5ff', border: '#e9d5ff' },
  environnement:      { color: '#16a34a', light: '#f0fdf4', border: '#86efac' },
  sante:              { color: '#e11d48', light: '#fff1f2', border: '#fecdd3' },
  energie:            { color: '#f59e0b', light: '#fffbeb', border: '#fcd34d' },
  collectivites:      { color: '#0369a1', light: '#f0f9ff', border: '#bae6fd' },
}

const DEFAULT_STYLE = { color: '#64748b', light: '#f8fafc', border: '#e2e8f0' }

export default function DomainCard({ domain }) {
  const { t } = useLang()
  const Icon = ICONS[domain.icon] ?? Scale
  const s = DOMAIN_STYLES[domain.id] ?? DEFAULT_STYLE

  return (
    <Link
      to={`/domaine/${domain.id}`}
      className="group block bg-white rounded-2xl border border-gray-100 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200"
      style={{ borderTop: `3px solid ${s.color}` }}
    >
      <div className="p-6">

        {/* Icon — fully controlled by inline styles, no Tailwind size classes */}
        <div style={{
          width: 48,
          height: 48,
          minWidth: 48,
          minHeight: 48,
          borderRadius: 12,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: 16,
          background: s.light,
          border: `1px solid ${s.border}`,
          flexShrink: 0,
        }}>
          <Icon size={22} style={{ color: s.color }} />
        </div>

        {/* Names */}
        <h3 className="font-playfair font-semibold text-navy text-base mb-0.5 group-hover:text-gold transition-colors">
          {domain.fr}
        </h3>
        <p className="font-arabic text-navy-600 text-sm mb-3">{domain.ar}</p>

        {/* Sub-domains */}
        <div className="flex flex-wrap gap-1 mb-4">
          {domain.sub.slice(0, 3).map(s2 => (
            <span key={s2} className="text-[10px] bg-gray-50 text-navy-600 px-2 py-0.5 rounded border border-gray-200">
              {s2}
            </span>
          ))}
          {domain.sub.length > 3 && (
            <span className="text-[10px] text-navy-400 self-center">+{domain.sub.length - 3}</span>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <span className="text-xs text-navy-500">
            <strong style={{ color: s.color }}>{domain.count}</strong>
            {' '}{t('domains.laws')}
          </span>
          <span
            className="text-xs font-medium flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
            style={{ color: s.color }}
          >
            {t('domains.browse')} <ArrowRight size={11} />
          </span>
        </div>

      </div>
    </Link>
  )
}
