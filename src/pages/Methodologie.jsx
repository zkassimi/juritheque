import { Link } from 'react-router-dom'
import { ChevronRight, BookOpen, Database, AlertTriangle, Mail, CheckCircle } from 'lucide-react'
import { useSEO } from '../hooks/useSEO'

const SOURCES = [
  { name: 'SGG — Secrétariat Général du Gouvernement',  url: 'https://www.sgg.gov.ma',          desc: 'Textes consolidés, lois organiques, décrets réglementaires' },
  { name: 'Adala — Ministère de la Justice',            url: 'https://adala.justice.gov.ma',    desc: 'Base de données officielle du Ministère de la Justice' },
  { name: 'BKAM — Bank Al-Maghrib',                     url: 'https://www.bkam.ma',             desc: 'Réglementation bancaire et financière' },
  { name: 'ANRT — Agence Nationale de Réglementation des Télécommunications', url: 'https://www.anrt.ma', desc: 'Textes relatifs au numérique et aux télécommunications' },
  { name: 'MMSP — Ministère de la Modernisation',       url: 'https://www.mmsp.gov.ma',         desc: 'Fonction publique et administration' },
  { name: 'MEM — Ministère de l\'Énergie et des Mines', url: 'https://www.mem.gov.ma',          desc: 'Énergie, mines et développement durable' },
  { name: 'Chambre des Représentants',                  url: 'https://www.chambredesrepresentants.ma', desc: 'Lois votées et textes parlementaires' },
  { name: 'Ministère de l\'Économie et des Finances',   url: 'https://www.finances.gov.ma',     desc: 'Lois de finances, fiscalité, budget' },
  { name: 'Ministère de l\'Environnement',              url: 'https://www.environnement.gov.ma', desc: 'Environnement et développement durable' },
  { name: 'ISM — Institut Supérieur de la Magistrature', url: 'https://www.ism.ma',             desc: 'Textes de référence pour la formation judiciaire' },
  { name: 'WIPO Lex & UNODC',                          url: 'https://wipolex.wipo.int',         desc: 'Propriété intellectuelle et droit international' },
]

export default function Methodologie() {
  useSEO({
    title: 'Méthodologie — Comment JuriThèque collecte les textes juridiques',
    description: 'Découvrez comment JuriThèque sélectionne, organise et présente les textes juridiques marocains. Sources officielles, processus de sélection, limites et avertissement.',
    canonical: '/methodologie',
    type: 'website',
  })

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      {/* En-tête */}
      <div className="bg-navy text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12 md:py-16">
          <nav className="flex items-center gap-2 text-white/50 text-xs mb-6">
            <Link to="/" className="hover:text-gold transition-colors">Accueil</Link>
            <ChevronRight size={12} />
            <span className="text-white/80">Méthodologie</span>
          </nav>
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-gold/20 flex items-center justify-center flex-shrink-0 mt-1">
              <BookOpen size={22} className="text-gold" />
            </div>
            <div>
              <h1 className="font-playfair font-bold text-3xl md:text-4xl mb-3">
                Méthodologie
              </h1>
              <p className="text-white/60 text-sm md:text-base leading-relaxed max-w-2xl">
                Comment JuriThèque sélectionne, organise et présente les textes juridiques marocains.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Corps */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12 space-y-10">

        {/* Notre démarche */}
        <section className="bg-white rounded-2xl border border-gray-100 p-8">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-xl bg-gold/10 flex items-center justify-center">
              <Database size={18} className="text-gold" />
            </div>
            <h2 className="font-playfair font-bold text-navy text-xl">Notre démarche</h2>
          </div>
          <p className="text-navy-700 text-sm leading-relaxed mb-4">
            JuriThèque a pour mission de centraliser les textes juridiques marocains officiels et de les rendre accessibles à tous — étudiants en droit, juristes, fonctionnaires, entrepreneurs et citoyens — dans un format clair, bilingue (français et arabe) et gratuit.
          </p>
          <p className="text-navy-700 text-sm leading-relaxed">
            Nous collectons les textes directement depuis les portails officiels des institutions marocaines compétentes. Chaque texte est associé à sa source d'origine afin de garantir la traçabilité et permettre la vérification indépendante.
          </p>
        </section>

        {/* Sources utilisées */}
        <section className="bg-white rounded-2xl border border-gray-100 p-8">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-xl bg-blue-50 flex items-center justify-center">
              <CheckCircle size={18} className="text-blue-600" />
            </div>
            <h2 className="font-playfair font-bold text-navy text-xl">Sources officielles utilisées</h2>
          </div>
          <p className="text-navy-500 text-sm mb-6">
            JuriThèque s'appuie exclusivement sur <strong className="text-navy">{SOURCES.length} sources gouvernementales et institutionnelles publiques</strong>. Aucune source non officielle n'est intégrée.
          </p>
          <div className="space-y-3">
            {SOURCES.map((src, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-[#f8fafc] border border-gray-100">
                <span className="w-5 h-5 rounded-full bg-gold/20 text-gold text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <div>
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-semibold text-navy hover:text-gold transition-colors"
                  >
                    {src.name}
                  </a>
                  <p className="text-xs text-navy-400 mt-0.5">{src.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Synthèses */}
        <section className="bg-white rounded-2xl border border-gray-100 p-8">
          <h2 className="font-playfair font-bold text-navy text-xl mb-4">Synthèses et résumés</h2>
          <p className="text-navy-700 text-sm leading-relaxed mb-3">
            Pour faciliter la lecture et la compréhension, certains textes sont accompagnés d'une synthèse en français et/ou en arabe. Ces synthèses sont fournies à titre indicatif pour aider à comprendre l'objet du texte.
          </p>
          <p className="text-navy-700 text-sm leading-relaxed">
            <strong className="text-navy">Seul le texte officiel fait référence juridique.</strong> En cas de divergence entre une synthèse et le texte original, c'est toujours le texte officiel publié par l'institution compétente qui prévaut. Nous vous invitons à consulter systématiquement la source officielle pour toute démarche juridique.
          </p>
        </section>

        {/* Limites */}
        <section className="bg-white rounded-2xl border border-gray-100 p-8">
          <h2 className="font-playfair font-bold text-navy text-xl mb-4">Limites de la plateforme</h2>
          <ul className="space-y-3 text-sm text-navy-700">
            {[
              "La base de données est en cours d'enrichissement continu. Tous les textes juridiques marocains n'y figurent pas encore.",
              "Certains textes peuvent être incomplets, notamment lorsque le document source n'est pas disponible en format numérique exploitable.",
              "Les modifications et abrogations intervenues après la dernière mise à jour d'un texte peuvent ne pas être encore reflétées.",
              "JuriThèque ne couvre pas actuellement la jurisprudence (décisions de justice) ni les circulaires internes non publiées.",
            ].map((item, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-gold flex-shrink-0 mt-1.5" />
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* Avertissement juridique */}
        <section className="bg-amber-50 border border-amber-200 rounded-2xl p-8">
          <div className="flex items-start gap-3 mb-4">
            <AlertTriangle size={20} className="text-amber-600 flex-shrink-0 mt-0.5" />
            <h2 className="font-playfair font-bold text-navy text-xl">Avertissement important</h2>
          </div>
          <p className="text-amber-900 text-sm leading-relaxed mb-3">
            JuriThèque est un <strong>outil documentaire de référence</strong> et ne constitue pas un conseil juridique professionnel. Les informations présentées ne sauraient remplacer l'avis d'un avocat, notaire ou juriste qualifié.
          </p>
          <p className="text-amber-900 text-sm leading-relaxed">
            Pour toute démarche juridique engageant vos droits ou obligations, nous vous recommandons de consulter un professionnel du droit ou de vous référer directement aux textes officiels publiés au Bulletin Officiel du Royaume du Maroc.
          </p>
        </section>

        {/* Signaler une erreur */}
        <section className="bg-white rounded-2xl border border-gray-100 p-8">
          <div className="flex items-center gap-3 mb-4">
            <Mail size={18} className="text-navy-400" />
            <h2 className="font-playfair font-bold text-navy text-xl">Signaler une erreur</h2>
          </div>
          <p className="text-navy-700 text-sm leading-relaxed mb-5">
            Vous avez constaté une erreur, une information manquante ou un texte inexact ? Votre signalement nous aide à améliorer la qualité de la plateforme.
          </p>
          <Link
            to="/contact"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-navy text-white rounded-xl text-sm font-semibold hover:bg-gold hover:text-navy transition-colors"
          >
            <Mail size={14} />
            Contacter l'équipe JuriThèque
          </Link>
        </section>

      </div>
    </div>
  )
}
