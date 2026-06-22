import { useState, useEffect } from 'react'
import { useLang } from '../contexts/LangContext'
import { fetchDomains } from '../lib/api'
import DomainCard from '../components/DomainCard'
import { DOMAINS as DOMAINS_FALLBACK } from '../data/mockData'
import { useSEO } from '../hooks/useSEO'

export default function Domains() {
  const { t } = useLang()
  const [domains, setDomains] = useState([])
  const [loading, setLoading] = useState(true)

  useSEO({
    title: 'Domaines du droit marocain — 15 spécialités juridiques',
    description: 'Explorez les textes juridiques marocains par domaine : droit civil, pénal, commercial, administratif, fiscal, du travail, international, numérique, constitutionnel, bancaire, finances publiques, transport, environnement, santé et énergie.',
    canonical: '/domaines',
    type: 'website',
  })

  useEffect(() => {
    fetchDomains()
      .then(data => setDomains(data.length ? data : DOMAINS_FALLBACK))
      .catch(() => setDomains(DOMAINS_FALLBACK))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      <div className="bg-navy text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <p className="text-gold text-xs font-semibold uppercase tracking-widest mb-2">Droit marocain</p>
          <h1 className="font-playfair font-bold text-3xl sm:text-4xl">{t('domains.title')}</h1>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Array.from({ length: 9 }).map((_, i) => (
              <div key={i} className="h-36 bg-white rounded-xl border border-gray-100 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {domains.map((domain, i) => (
              <div key={domain.id} className="animate-fade-in" style={{ animationDelay: `${i * 70}ms` }}>
                <DomainCard domain={domain} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
