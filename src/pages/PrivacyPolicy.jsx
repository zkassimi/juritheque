import { Link } from 'react-router-dom'
import { Shield, ArrowLeft, Eye, Database, Cookie, Mail, Lock, UserCheck, Globe, AlertCircle } from 'lucide-react'
import { useSEO } from '../hooks/useSEO'

function Section({ icon: Icon, title, children }) {
  return (
    <section className="bg-white rounded-2xl border border-gray-100 p-6">
      <h2 className="font-playfair font-bold text-navy text-xl mb-4 flex items-center gap-2">
        <Icon size={18} className="text-gold flex-shrink-0" />
        {title}
      </h2>
      <div className="text-sm text-navy-700 space-y-3 leading-relaxed">
        {children}
      </div>
    </section>
  )
}

export default function PrivacyPolicy() {
  useSEO({
    title:       'Politique de confidentialité — JuriThèque',
    description: 'Politique de confidentialité de JuriThèque : collecte des données, cookies, droits des utilisateurs, conformité loi 09-08 et RGPD.',
    canonical:   '/politique-confidentialite',
    type:        'website',
    noindex:     false,
  })

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">

      {/* ── En-tête ─────────────────────────────────────────────────────── */}
      <div className="bg-navy text-white py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6">
          <Link to="/" className="flex items-center gap-1.5 text-white/60 text-xs mb-4 hover:text-gold transition-colors">
            <ArrowLeft size={12} /> Retour à l'accueil
          </Link>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-gold/20 rounded-xl flex items-center justify-center">
              <Shield size={20} className="text-gold" />
            </div>
            <h1 className="font-playfair font-bold text-3xl">Politique de confidentialité</h1>
          </div>
          <p className="text-white/60 text-sm">Dernière mise à jour : juin 2026</p>
        </div>
      </div>

      {/* ── Contenu ─────────────────────────────────────────────────────── */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12 space-y-6">

        {/* Intro */}
        <div className="bg-gold/5 border border-gold/20 rounded-2xl p-5 flex gap-3">
          <AlertCircle size={18} className="text-gold flex-shrink-0 mt-0.5" />
          <p className="text-sm text-navy-700 leading-relaxed">
            JuriThèque (<strong>juritheque.com</strong>) s'engage à protéger la vie privée de ses utilisateurs.
            Cette politique explique quelles données nous collectons, comment nous les utilisons et quels
            sont vos droits, conformément à la <strong>loi marocaine 09-08</strong> relative à la protection
            des personnes physiques à l'égard du traitement des données à caractère personnel, et au
            <strong> Règlement Général sur la Protection des Données (RGPD)</strong> européen.
          </p>
        </div>

        {/* 1. Responsable du traitement */}
        <Section icon={UserCheck} title="1. Responsable du traitement">
          <p><strong>Nom du site :</strong> JuriThèque — مكتبة القانون</p>
          <p><strong>URL :</strong> <a href="https://juritheque.com" className="text-gold hover:underline">https://juritheque.com</a></p>
          <p><strong>Contact :</strong> <a href="mailto:contact@juritheque.com" className="text-gold hover:underline">contact@juritheque.com</a></p>
          <p><strong>Pays :</strong> Maroc 🇲🇦</p>
        </Section>

        {/* 2. Données collectées */}
        <Section icon={Database} title="2. Données collectées">
          <p className="font-semibold text-navy">2.1 Données collectées automatiquement</p>
          <p>Lorsque vous visitez JuriThèque, nous collectons automatiquement certaines informations techniques :</p>
          <ul className="list-disc list-inside space-y-1 pl-2">
            <li>Adresse IP (anonymisée)</li>
            <li>Type de navigateur et système d'exploitation</li>
            <li>Pages visitées et durée de visite</li>
            <li>Source de trafic (moteur de recherche, lien direct, etc.)</li>
            <li>Date et heure de la visite</li>
          </ul>

          <p className="font-semibold text-navy mt-4">2.2 Données fournies volontairement</p>
          <p>Si vous créez un compte ou nous contactez, nous collectons :</p>
          <ul className="list-disc list-inside space-y-1 pl-2">
            <li>Adresse e-mail</li>
            <li>Nom d'affichage (facultatif)</li>
            <li>Contenu de vos messages (formulaire de contact)</li>
            <li>Préférences de langue (français / arabe)</li>
          </ul>

          <p className="font-semibold text-navy mt-4">2.3 Ce que nous ne collectons PAS</p>
          <ul className="list-disc list-inside space-y-1 pl-2">
            <li>Numéros de carte bancaire ou données financières</li>
            <li>Données biométriques</li>
            <li>Données de localisation précise</li>
            <li>Données sensibles (santé, opinions politiques, religion)</li>
          </ul>
        </Section>

        {/* 3. Finalités */}
        <Section icon={Eye} title="3. Finalités du traitement">
          <p>Vos données sont utilisées uniquement aux fins suivantes :</p>
          <div className="space-y-2 mt-2">
            {[
              ['Fonctionnement du site', 'Authentification, accès aux fonctionnalités, sauvegarde de vos préférences'],
              ['Amélioration du service', 'Analyse des pages les plus consultées pour améliorer le contenu'],
              ['Communication', 'Réponse à vos messages de contact'],
              ['Sécurité', 'Détection et prévention des abus, protection contre les attaques'],
              ['Publicité contextuelle', 'Affichage d\'annonces via Google AdSense (voir section Publicité ci-dessous)'],
            ].map(([titre, desc]) => (
              <div key={titre} className="flex gap-3 p-3 bg-gray-50 rounded-xl">
                <span className="text-gold mt-0.5 flex-shrink-0">▸</span>
                <div>
                  <p className="font-medium text-navy">{titre}</p>
                  <p className="text-navy-500 text-xs mt-0.5">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </Section>

        {/* 4. Cookies */}
        <Section icon={Cookie} title="4. Cookies et technologies similaires">
          <p>JuriThèque utilise des cookies pour améliorer votre expérience. Voici les types de cookies utilisés :</p>

          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr className="bg-navy text-white">
                  <th className="p-2 text-left rounded-tl-lg">Type</th>
                  <th className="p-2 text-left">Nom</th>
                  <th className="p-2 text-left">Durée</th>
                  <th className="p-2 text-left rounded-tr-lg">Finalité</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                <tr className="bg-white">
                  <td className="p-2 font-medium">Essentiels</td>
                  <td className="p-2 text-navy-500">supabase-auth, lang-pref</td>
                  <td className="p-2 text-navy-500">Session / 1 an</td>
                  <td className="p-2 text-navy-500">Authentification et langue</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="p-2 font-medium">Analytiques</td>
                  <td className="p-2 text-navy-500">_ga, _gid</td>
                  <td className="p-2 text-navy-500">2 ans / 24h</td>
                  <td className="p-2 text-navy-500">Google Analytics (anonymisé)</td>
                </tr>
                <tr className="bg-white">
                  <td className="p-2 font-medium">Publicitaires</td>
                  <td className="p-2 text-navy-500">__gads, ANID</td>
                  <td className="p-2 text-navy-500">Jusqu'à 13 mois</td>
                  <td className="p-2 text-navy-500">Google AdSense</td>
                </tr>
              </tbody>
            </table>
          </div>

          <p className="mt-3">
            Vous pouvez refuser les cookies non essentiels via les paramètres de votre navigateur ou
            via notre bandeau de consentement. Le refus des cookies analytiques et publicitaires
            n'affecte pas l'accès au contenu du site.
          </p>
        </Section>

        {/* 5. Publicité */}
        <Section icon={Globe} title="5. Publicité — Google AdSense">
          <p>
            JuriThèque affiche des annonces publicitaires via <strong>Google AdSense</strong> (Google LLC,
            1600 Amphitheatre Parkway, Mountain View, CA 94043, USA).
          </p>
          <p className="mt-2">
            Google AdSense peut utiliser des cookies et technologies similaires pour afficher des
            annonces personnalisées basées sur vos visites passées sur ce site et d'autres sites web.
            Google utilise le cookie <em>DoubleClick</em> pour afficher des annonces pertinentes.
          </p>
          <p className="mt-2 font-semibold text-navy">Comment désactiver la publicité personnalisée :</p>
          <ul className="list-disc list-inside space-y-1 pl-2 mt-1">
            <li>
              Visitez{' '}
              <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener noreferrer" className="text-gold hover:underline">
                google.com/settings/ads
              </a>{' '}
              pour gérer vos préférences publicitaires Google
            </li>
            <li>
              Installez le{' '}
              <a href="https://www.google.com/ads/preferences/plugin/" target="_blank" rel="noopener noreferrer" className="text-gold hover:underline">
                module de désactivation de Google Analytics
              </a>
            </li>
            <li>Utilisez le mode de navigation privée de votre navigateur</li>
          </ul>
          <p className="mt-3">
            Pour en savoir plus :{' '}
            <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" className="text-gold hover:underline">
              Politique de confidentialité Google
            </a>
          </p>
        </Section>

        {/* 6. Partage des données */}
        <Section icon={Lock} title="6. Partage des données avec des tiers">
          <p>JuriThèque ne vend jamais vos données personnelles. Nous partageons uniquement les données nécessaires avec :</p>
          <div className="space-y-2 mt-2">
            {[
              ['Supabase', 'Hébergement de la base de données et authentification (serveurs UE)', 'supabase.com'],
              ['Hostinger', 'Hébergement du site web (Chypre)', 'hostinger.com'],
              ['Google Analytics', 'Mesure d\'audience anonymisée', 'analytics.google.com'],
              ['Google AdSense', 'Affichage d\'annonces publicitaires', 'adsense.google.com'],
              ['Anthropic (Claude)', 'Traitement des questions via l\'assistant IA (aucun stockage permanent)', 'anthropic.com'],
            ].map(([nom, desc, url]) => (
              <div key={nom} className="flex items-start gap-3 p-3 bg-gray-50 rounded-xl">
                <span className="text-gold mt-0.5 flex-shrink-0">▸</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-navy">{nom}</p>
                    <a href={`https://${url}`} target="_blank" rel="noopener noreferrer"
                      className="text-[10px] text-gold hover:underline">{url}</a>
                  </div>
                  <p className="text-navy-500 text-xs mt-0.5">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </Section>

        {/* 7. Droits des utilisateurs */}
        <Section icon={UserCheck} title="7. Vos droits">
          <p>
            Conformément à la <strong>loi marocaine 09-08</strong> et au <strong>RGPD</strong>,
            vous disposez des droits suivants sur vos données personnelles :
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
            {[
              ['Droit d\'accès', 'Obtenir une copie de vos données personnelles détenues par JuriThèque'],
              ['Droit de rectification', 'Corriger des données inexactes ou incomplètes'],
              ['Droit à l\'effacement', 'Demander la suppression de votre compte et de vos données'],
              ['Droit d\'opposition', 'Vous opposer au traitement de vos données à des fins publicitaires'],
              ['Droit à la portabilité', 'Recevoir vos données dans un format structuré et lisible'],
              ['Droit de retrait', 'Retirer votre consentement à tout moment sans affecter les traitements passés'],
            ].map(([titre, desc]) => (
              <div key={titre} className="p-3 border border-gray-100 rounded-xl bg-white">
                <p className="font-semibold text-navy text-xs mb-1">{titre}</p>
                <p className="text-navy-500 text-xs leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
          <p className="mt-4">
            Pour exercer ces droits, contactez-nous à :{' '}
            <a href="mailto:contact@juritheque.com" className="text-gold hover:underline font-medium">
              contact@juritheque.com
            </a>
          </p>
        </Section>

        {/* 8. Sécurité */}
        <Section icon={Lock} title="8. Sécurité des données">
          <p>
            JuriThèque met en œuvre des mesures techniques et organisationnelles adaptées pour protéger
            vos données contre tout accès non autorisé, perte ou divulgation :
          </p>
          <ul className="list-disc list-inside space-y-1 pl-2 mt-2">
            <li>Connexion chiffrée HTTPS/TLS sur l'ensemble du site</li>
            <li>Authentification sécurisée via Supabase Auth (JWT)</li>
            <li>Contrôle d'accès par rôles (RLS — Row Level Security) sur la base de données</li>
            <li>Mots de passe hashés — jamais stockés en clair</li>
            <li>Accès restreint aux données sensibles aux seuls administrateurs</li>
          </ul>
        </Section>

        {/* 9. Conservation */}
        <Section icon={Database} title="9. Durée de conservation">
          <div className="overflow-x-auto">
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr className="bg-navy text-white">
                  <th className="p-2 text-left rounded-tl-lg">Type de données</th>
                  <th className="p-2 text-left rounded-tr-lg">Durée de conservation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {[
                  ['Données de compte (email, nom)', '3 ans après dernière connexion, ou jusqu\'à suppression du compte'],
                  ['Logs de navigation', '13 mois maximum (Google Analytics)'],
                  ['Messages de contact', '2 ans'],
                  ['Cookies essentiels', 'Durée de la session ou 1 an'],
                  ['Cookies publicitaires', 'Jusqu\'à 13 mois (Google AdSense)'],
                ].map(([type, duree], i) => (
                  <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="p-2 font-medium">{type}</td>
                    <td className="p-2 text-navy-500">{duree}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>

        {/* 10. Contact */}
        <Section icon={Mail} title="10. Contact et réclamations">
          <p>
            Pour toute question relative à cette politique de confidentialité ou pour exercer vos droits :
          </p>
          <div className="mt-3 p-4 bg-navy/5 rounded-xl">
            <p className="font-semibold text-navy">JuriThèque — Délégué à la Protection des Données</p>
            <p className="text-navy-600 mt-1">
              Email :{' '}
              <a href="mailto:contact@juritheque.com" className="text-gold hover:underline">
                contact@juritheque.com
              </a>
            </p>
            <p className="text-navy-600 mt-1">Délai de réponse : 30 jours maximum</p>
          </div>
          <p className="mt-3 text-navy-500">
            Si vous estimez que vos droits ne sont pas respectés, vous pouvez déposer une réclamation
            auprès de la <strong>Commission Nationale de contrôle de la protection des Données à
            caractère Personnel (CNDP)</strong> au Maroc :{' '}
            <a href="https://www.cndp.ma" target="_blank" rel="noopener noreferrer" className="text-gold hover:underline">
              www.cndp.ma
            </a>
          </p>
        </Section>

        {/* Liens */}
        <div className="flex flex-wrap items-center gap-4 pt-2 text-sm">
          <Link to="/mentions-legales" className="text-gold hover:underline flex items-center gap-1.5">
            <Shield size={13} /> Mentions légales
          </Link>
          <Link to="/contact" className="text-gold hover:underline flex items-center gap-1.5">
            <Mail size={13} /> Nous contacter
          </Link>
          <Link to="/" className="text-navy-500 hover:text-gold transition-colors flex items-center gap-1.5">
            <ArrowLeft size={13} /> Retour à l'accueil
          </Link>
        </div>

      </div>
    </div>
  )
}
