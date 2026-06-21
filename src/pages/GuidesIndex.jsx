import { Link } from 'react-router-dom'
import { BookOpen, ChevronRight, ArrowRight, Bot, Search, Bell } from 'lucide-react'
import { useSEO } from '../hooks/useSEO'
import JsonLD, { breadcrumbSchema } from '../components/JsonLD'
import { getIntentsByCategory } from '../data/seoIntentPages'

const BASE_URL = 'https://juritheque.com'

const CATEGORY_META = {
  mre:           { label: '🌍 Marocains Résidant à l\'Étranger', badge: 'bg-indigo-50 text-indigo-700 border-indigo-200',   dot: 'bg-indigo-400' },
  investissement: { label: '💼 Investissement au Maroc',          badge: 'bg-gold/10 text-amber-800 border-amber-200',       dot: 'bg-amber-400' },
  travail:       { label: 'Droit du Travail',                    badge: 'bg-blue-50 text-blue-700 border-blue-200',         dot: 'bg-blue-400' },
  commercial:    { label: 'Droit Commercial',                    badge: 'bg-amber-50 text-amber-700 border-amber-200',      dot: 'bg-amber-400' },
  famille:       { label: 'Droit de la Famille',                 badge: 'bg-pink-50 text-pink-700 border-pink-200',         dot: 'bg-pink-400' },
  civil:         { label: 'Droit Civil',                         badge: 'bg-emerald-50 text-emerald-700 border-emerald-200', dot: 'bg-emerald-400' },
  penal:         { label: 'Droit Pénal',                         badge: 'bg-red-50 text-red-700 border-red-200',            dot: 'bg-red-400' },
  administratif: { label: 'Droit Administratif',                 badge: 'bg-violet-50 text-violet-700 border-violet-200',   dot: 'bg-violet-400' },
  collectivites: { label: 'Collectivités Territoriales',         badge: 'bg-purple-50 text-purple-700 border-purple-200',   dot: 'bg-purple-400' },
  societe:       { label: '⚡ Droit & Société',                  badge: 'bg-teal-50 text-teal-700 border-teal-200',         dot: 'bg-teal-400' },
}

export default function GuidesIndex() {
  useSEO({
    title:       'Guides juridiques marocains — JuriThèque',
    description: 'Guides pratiques sur le droit marocain : droits des MRE, investir au Maroc, héritage, immobilier, droit du travail, droit commercial. Avec les textes officiels liés.',
    canonical:   '/fr/guides',
    type:        'website',
  })

  const grouped = getIntentsByCategory()

  const breadcrumbs = [
    { name: 'Accueil',           url: '/' },
    { name: 'Guides juridiques', url: '/fr/guides' },
  ]

  // JSON-LD — CollectionPage + BreadcrumbList
  const jsonLdData = [
    {
      '@context':   'https://schema.org',
      '@type':      'CollectionPage',
      name:         'Guides juridiques marocains — JuriThèque',
      description:  'Guides thématiques sur le droit marocain basés sur les textes officiels.',
      url:          `${BASE_URL}/fr/guides`,
      inLanguage:   'fr',
      isPartOf:     { '@type': 'WebSite', name: 'JuriThèque', url: BASE_URL },
    },
    breadcrumbSchema(breadcrumbs),
  ]

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      <JsonLD data={jsonLdData} />

      {/* ── En-tête ───────────────────────────────────────────────────── */}
      <div className="bg-navy text-white py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <nav className="flex items-center gap-1.5 text-xs text-white/50 mb-4" aria-label="Fil d'Ariane">
            <Link to="/" className="hover:text-gold transition-colors">Accueil</Link>
            <ChevronRight size={10} />
            <span className="text-white/80">Guides juridiques</span>
          </nav>
          <p className="text-gold text-xs font-semibold uppercase tracking-widest mb-3">
            Guides thématiques
          </p>
          <h1 className="font-playfair font-bold text-3xl sm:text-4xl mb-3">
            Guides juridiques marocains
          </h1>
          <p className="text-white/60 text-sm max-w-xl leading-relaxed">
            Des guides thématiques basés uniquement sur les textes officiels disponibles dans JuriThèque.
            Chaque guide oriente vers les lois, codes et décrets pertinents.
          </p>
        </div>
      </div>

      {/* ── Contenu ───────────────────────────────────────────────────── */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10 space-y-10">

        {Object.entries(grouped).map(([cat, pages]) => {
          const meta = CATEGORY_META[cat] || { label: cat, badge: 'bg-gray-50 text-gray-700 border-gray-200', dot: 'bg-gray-400' }
          return (
            <section key={cat}>
              {/* En-tête catégorie */}
              <div className="flex items-center gap-3 mb-5">
                <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full border ${meta.badge}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${meta.dot}`} />
                  {meta.label}
                </span>
                <div className="h-px flex-1 bg-gray-200" />
                <span className="text-xs text-navy-400">{pages.length} guide{pages.length > 1 ? 's' : ''}</span>
              </div>

              {/* Grille des guides */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {pages.map(guide => (
                  <Link
                    key={guide.slug}
                    to={`/fr/guides/${guide.slug}`}
                    className="group flex flex-col bg-white rounded-2xl border border-gray-100 p-5 hover:border-gold hover:shadow-md transition-all"
                  >
                    {/* Icône + titre */}
                    <div className="flex items-start gap-3 mb-3">
                      <div className="w-9 h-9 rounded-xl bg-gold/10 flex items-center justify-center flex-shrink-0 group-hover:bg-gold/20 transition-colors">
                        <BookOpen size={15} className="text-gold" />
                      </div>
                      <h2 className="font-semibold text-navy text-sm leading-snug group-hover:text-gold transition-colors">
                        {guide.h1}
                      </h2>
                    </div>

                    {/* Description */}
                    <p className="text-xs text-navy-500 leading-relaxed flex-1 line-clamp-3 mb-3">
                      {guide.metaDescription}
                    </p>

                    {/* Mots-clés (3 max) */}
                    {guide.keywords?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {guide.keywords.slice(0, 3).map(kw => (
                          <span key={kw} className="text-[10px] bg-gray-50 text-navy-500 px-2 py-0.5 rounded-full border border-gray-100">
                            {kw}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* CTA */}
                    <div className="flex items-center gap-1 text-xs text-gold font-semibold group-hover:gap-2 transition-all">
                      Voir le guide <ChevronRight size={12} />
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          )
        })}

        {/* ── Bloc CTA final ─────────────────────────────────────────── */}
        <div className="bg-navy rounded-2xl p-6 sm:p-10 text-center text-white">
          <h3 className="font-playfair font-bold text-xl sm:text-2xl mb-2">
            Vous ne trouvez pas ce que vous cherchez ?
          </h3>
          <p className="text-white/60 text-sm mb-6 max-w-md mx-auto">
            Explorez la base complète ou posez directement votre question à l'assistant IA juridique.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link
              to="/base"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-navy rounded-xl text-sm font-semibold hover:bg-gold transition-colors"
            >
              <Search size={14} /> Explorer la base
            </Link>
            <Link
              to="/assistant"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-gold text-navy rounded-xl text-sm font-semibold hover:bg-gold/80 transition-colors"
            >
              <Bot size={14} /> Poser une question à l'IA
            </Link>
          </div>
        </div>

        {/* ── Liens secondaires ─────────────────────────────────────── */}
        <div className="flex flex-wrap items-center justify-center gap-6 pb-4 text-sm text-navy-500">
          <Link
            to="/fr/veille-juridique"
            className="inline-flex items-center gap-2 hover:text-gold transition-colors"
          >
            <Bell size={14} />
            Veille juridique — nouveaux textes
          </Link>
          <Link
            to="/domaines"
            className="inline-flex items-center gap-2 hover:text-gold transition-colors"
          >
            <ArrowRight size={14} />
            Explorer par domaine juridique
          </Link>
        </div>
      </div>
    </div>
  )
}
