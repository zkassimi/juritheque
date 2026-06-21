import { Link } from 'react-router-dom'
import { Scale, ArrowLeft, Shield, FileText, Globe, Mail } from 'lucide-react'
import { useSEO } from '../hooks/useSEO'

export default function Legal() {
  useSEO({
    title: 'Mentions légales — JuriThèque',
    description: 'Mentions légales de JuriThèque : éditeur, hébergeur, propriété intellectuelle, données personnelles et protection des données (loi marocaine 09-08).',
    canonical: '/mentions-legales',
    type: 'website',
    noindex: false,
  })

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      {/* Header */}
      <div className="bg-navy text-white py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6">
          <Link to="/" className="flex items-center gap-1.5 text-white/60 text-xs mb-4 hover:text-gold transition-colors">
            <ArrowLeft size={12} /> Retour à l'accueil
          </Link>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-gold/20 rounded-xl flex items-center justify-center">
              <Shield size={20} className="text-gold" />
            </div>
            <h1 className="font-playfair font-bold text-3xl">Mentions Légales</h1>
          </div>
          <p className="text-white/60 text-sm">Dernière mise à jour : mai 2026</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12">
        <div className="space-y-8">

          {/* Éditeur */}
          <section className="bg-white rounded-2xl border border-gray-100 p-6">
            <h2 className="font-playfair font-bold text-navy text-xl mb-4 flex items-center gap-2">
              <Scale size={18} className="text-gold" /> Éditeur du site
            </h2>
            <div className="text-sm text-navy-700 space-y-2 leading-relaxed">
              <p><strong>Nom :</strong> JuriThèque — مكتبة القانون</p>
              <p><strong>Description :</strong> Plateforme bilingue de documentation juridique marocaine (français / arabe)</p>
              <p><strong>Email :</strong> <a href="mailto:contact@juritheque.com" className="text-gold hover:underline">contact@juritheque.com</a></p>
              <p><strong>Pays :</strong> Maroc 🇲🇦</p>
            </div>
          </section>

          {/* Hébergement */}
          <section className="bg-white rounded-2xl border border-gray-100 p-6">
            <h2 className="font-playfair font-bold text-navy text-xl mb-4 flex items-center gap-2">
              <Globe size={18} className="text-gold" /> Hébergement
            </h2>
            <div className="text-sm text-navy-700 space-y-2 leading-relaxed">
              <p><strong>Hébergeur :</strong> Hostinger International Ltd</p>
              <p><strong>Adresse :</strong> 61 Lordou Vironos Street, 6023 Larnaca, Chypre</p>
              <p><strong>Site web :</strong> <a href="https://www.hostinger.com" target="_blank" rel="noopener noreferrer" className="text-gold hover:underline">www.hostinger.com</a></p>
              <p><strong>Base de données :</strong> Supabase (Supabase Inc., San Francisco, CA, USA)</p>
            </div>
          </section>

          {/* Propriété intellectuelle */}
          <section className="bg-white rounded-2xl border border-gray-100 p-6">
            <h2 className="font-playfair font-bold text-navy text-xl mb-4 flex items-center gap-2">
              <FileText size={18} className="text-gold" /> Propriété intellectuelle
            </h2>
            <div className="text-sm text-navy-700 space-y-3 leading-relaxed">
              <p>
                Les textes juridiques publiés sur JuriThèque sont des textes officiels de la législation marocaine
                (Dahirs, Lois, Décrets, Arrêtés) qui sont dans le domaine public. JuriThèque se limite à leur
                collecte, structuration et mise en accessibilité bilingue.
              </p>
              <p>
                Le design, le code source, les interfaces et les fonctionnalités du site JuriThèque sont la propriété
                exclusive de leurs créateurs. Toute reproduction est interdite sans autorisation préalable.
              </p>
            </div>
          </section>

          {/* Données personnelles */}
          <section className="bg-white rounded-2xl border border-gray-100 p-6">
            <h2 className="font-playfair font-bold text-navy text-xl mb-4 flex items-center gap-2">
              <Shield size={18} className="text-gold" /> Données personnelles & RGPD
            </h2>
            <div className="text-sm text-navy-700 space-y-3 leading-relaxed">
              <p>
                JuriThèque collecte uniquement les données nécessaires au fonctionnement du service : email,
                nom et profession lors de l'inscription. Ces données sont stockées de manière sécurisée
                sur Supabase et ne sont jamais vendues ou partagées avec des tiers.
              </p>
              <p>
                Conformément à la loi marocaine 09-08 relative à la protection des personnes physiques à
                l'égard du traitement des données à caractère personnel, vous disposez d'un droit d'accès,
                de rectification et de suppression de vos données.
              </p>
              <p>
                Pour exercer ces droits, contactez-nous à :{' '}
                <a href="mailto:contact@juritheque.com" className="text-gold hover:underline">contact@juritheque.com</a>
              </p>
            </div>
          </section>

          {/* Responsabilité */}
          <section className="bg-white rounded-2xl border border-gray-100 p-6">
            <h2 className="font-playfair font-bold text-navy text-xl mb-4">Limitation de responsabilité</h2>
            <div className="text-sm text-navy-700 space-y-3 leading-relaxed">
              <p>
                Les informations publiées sur JuriThèque sont fournies à titre informatif uniquement.
                Malgré le soin apporté à la mise à jour des textes juridiques, JuriThèque ne garantit pas
                l'exactitude, la complétude ou l'actualité des informations.
              </p>
              <p className="font-medium text-navy bg-gold/5 border border-gold/20 rounded-lg px-4 py-3">
                ⚠️ Les textes publiés ne constituent pas un avis juridique. Pour tout conseil juridique,
                consultez un avocat ou un conseiller juridique qualifié.
              </p>
            </div>
          </section>

        </div>
      </div>
    </div>
  )
}
