import { Link } from 'react-router-dom'
import { ChevronRight, Scale, BookOpen, Target, Users, Database, Globe, Mail, ArrowRight } from 'lucide-react'
import { useSEO } from '../hooks/useSEO'

const STATS = [
  { value: '7 400+', label: 'Textes juridiques référencés' },
  { value: '11',     label: 'Sources officielles' },
  { value: '16',     label: 'Domaines juridiques' },
  { value: '2',      label: 'Langues (français & arabe)' },
]

const VALUES = [
  {
    icon: Target,
    title: 'Accessibilité',
    desc: 'Rendre le droit marocain compréhensible par tous — étudiants, citoyens, juristes et fonctionnaires — sans barrière linguistique ni technique.',
  },
  {
    icon: Database,
    title: 'Fiabilité',
    desc: 'Chaque texte est collecté exclusivement depuis les portails officiels des institutions marocaines et associé à sa source d\'origine.',
  },
  {
    icon: Globe,
    title: 'Bilinguisme',
    desc: 'L\'interface et les textes sont disponibles en français et en arabe, avec prise en charge du mode RTL pour les usagers arabophones.',
  },
  {
    icon: BookOpen,
    title: 'Pédagogie',
    desc: 'Au-delà de la base documentaire, JuriThèque propose des guides thématiques et des synthèses pour faciliter la compréhension des textes.',
  },
]

export default function APropos() {
  useSEO({
    title: 'À propos — JuriThèque, plateforme de droit marocain',
    description: 'JuriThèque est une plateforme documentaire bilingue centralisant les textes juridiques marocains officiels. Découvrez notre mission, nos valeurs et nos sources.',
    canonical: '/a-propos',
    type: 'website',
  })

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">

      {/* ── En-tête ── */}
      <div className="bg-navy text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12 md:py-16">
          <nav className="flex items-center gap-2 text-white/50 text-xs mb-6">
            <Link to="/" className="hover:text-gold transition-colors">Accueil</Link>
            <ChevronRight size={12} />
            <span className="text-white/80">À propos</span>
          </nav>
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-gold/20 flex items-center justify-center flex-shrink-0 mt-1">
              <Scale size={22} className="text-gold" />
            </div>
            <div>
              <h1 className="font-playfair font-bold text-3xl md:text-4xl mb-3">
                À propos de JuriThèque
              </h1>
              <p className="text-white/60 text-sm md:text-base leading-relaxed max-w-2xl">
                Plateforme documentaire bilingue de référence pour le droit marocain — gratuite, indépendante et accessible à tous.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Corps ── */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12 space-y-10">

        {/* Notre mission */}
        <section className="bg-white rounded-2xl border border-gray-100 p-8">
          <h2 className="font-playfair font-bold text-navy text-xl mb-4">Notre mission</h2>
          <p className="text-navy-700 text-sm leading-relaxed mb-4">
            JuriThèque a été créée avec un constat simple : accéder aux textes juridiques marocains est difficile.
            Les sources officielles sont dispersées sur des dizaines de portails institutionnels, souvent peu indexés,
            rarement bilingues, et avec une expérience utilisateur éloignée des standards modernes.
          </p>
          <p className="text-navy-700 text-sm leading-relaxed mb-4">
            Notre réponse : centraliser, organiser et rendre accessibles les textes officiels marocains — lois, dahirs,
            décrets, arrêtés, codes — dans une interface fluide, bilingue français-arabe, gratuitement.
          </p>
          <p className="text-navy-700 text-sm leading-relaxed">
            JuriThèque s'adresse aux étudiants en droit, aux juristes, aux fonctionnaires, aux entrepreneurs,
            aux élus locaux et à tout citoyen souhaitant comprendre ses droits et obligations selon le droit marocain.
          </p>
        </section>

        {/* Chiffres clés */}
        <section>
          <h2 className="font-playfair font-bold text-navy text-xl mb-5">La plateforme en chiffres</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {STATS.map((s, i) => (
              <div key={i} className="bg-white rounded-2xl border border-gray-100 p-5 text-center">
                <p className="font-playfair font-bold text-navy text-2xl mb-1">{s.value}</p>
                <p className="text-xs text-navy-500 leading-snug">{s.label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Nos valeurs */}
        <section className="bg-white rounded-2xl border border-gray-100 p-8">
          <h2 className="font-playfair font-bold text-navy text-xl mb-6">Nos valeurs</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {VALUES.map((v, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="w-9 h-9 rounded-xl bg-gold/10 flex items-center justify-center flex-shrink-0">
                  <v.icon size={17} className="text-gold" />
                </div>
                <div>
                  <h3 className="font-semibold text-navy text-sm mb-1">{v.title}</h3>
                  <p className="text-xs text-navy-600 leading-relaxed">{v.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Pour qui */}
        <section className="bg-white rounded-2xl border border-gray-100 p-8">
          <h2 className="font-playfair font-bold text-navy text-xl mb-4">Pour qui ?</h2>
          <div className="flex flex-wrap gap-2.5">
            {[
              'Étudiants en droit', 'Avocats et notaires', 'Magistrats',
              'Fonctionnaires', 'Élus locaux', 'Entrepreneurs',
              'Chercheurs juridiques', 'Enseignants', 'Citoyens',
              'Marocains résidant à l\'étranger',
            ].map(audience => (
              <span
                key={audience}
                className="px-3 py-1.5 bg-[#f8fafc] border border-gray-200 rounded-full text-xs text-navy-700 font-medium"
              >
                {audience}
              </span>
            ))}
          </div>
        </section>

        {/* Liens utiles */}
        <section className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Link
            to="/methodologie"
            className="flex items-center justify-between gap-3 p-5 bg-navy text-white rounded-2xl hover:bg-gold hover:text-navy transition-colors group"
          >
            <div>
              <p className="font-semibold text-sm">Méthodologie</p>
              <p className="text-xs opacity-70 mt-0.5">Nos sources et notre démarche éditoriale</p>
            </div>
            <ArrowRight size={18} className="flex-shrink-0 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link
            to="/contact"
            className="flex items-center justify-between gap-3 p-5 bg-white border border-gray-200 rounded-2xl hover:border-gold transition-colors group"
          >
            <div>
              <p className="font-semibold text-sm text-navy">Nous contacter</p>
              <p className="text-xs text-navy-500 mt-0.5">Questions, partenariats, signalements</p>
            </div>
            <Mail size={18} className="flex-shrink-0 text-gold" />
          </Link>
        </section>

        {/* Avertissement */}
        <section className="bg-amber-50 border border-amber-200 rounded-2xl p-6">
          <p className="text-amber-900 text-sm leading-relaxed">
            <strong>Avertissement :</strong> JuriThèque est un outil documentaire de référence et ne constitue
            pas un conseil juridique professionnel. Pour toute démarche engageant vos droits ou obligations,
            nous vous recommandons de consulter un professionnel du droit qualifié.
          </p>
        </section>

      </div>
    </div>
  )
}
