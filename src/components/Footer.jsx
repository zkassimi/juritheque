import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Scale, Mail, Twitter, Linkedin, Github, ArrowRight, BookOpen, Bell, Newspaper, Loader2, Library } from 'lucide-react'
import { useLang } from '../contexts/LangContext'
import { subscribeEmail } from '../lib/api'

export default function Footer() {
  const { t, isRTL } = useLang()
  const [email,      setEmail]      = useState('')
  const [subStatus,  setSubStatus]  = useState('idle') // idle | loading | success | error | duplicate

  const handleSubscribe = async (e) => {
    e.preventDefault()
    if (!email || subStatus === 'loading') return
    setSubStatus('loading')
    try {
      await subscribeEmail(email, 'footer', 'fr')
      setSubStatus('success')
      setEmail('')
    } catch (err) {
      // Code 23505 = unique violation (email already exists)
      if (err?.code === '23505' || err?.message?.includes('unique')) {
        setSubStatus('duplicate')
      } else {
        setSubStatus('error')
      }
    }
  }

  const colPlateforme = [
    { to: '/base',      label: t('nav.database') },
    { to: '/domaines',  label: t('nav.domains') },
    { to: '/videos',    label: t('nav.videos') },
    { to: '/assistant', label: t('nav.assistant') },
  ]

  const colRessources = [
    { to: '/fr/guides',              icon: BookOpen,  label: 'Guides thématiques' },
    { to: '/glossaire',              icon: Library,   label: 'Glossaire juridique' },
    { to: '/fr/veille-juridique',    icon: Bell,      label: 'Veille juridique' },
    { to: '/fr/bulletins-officiels', icon: Newspaper, label: 'Bulletins Officiels' },
  ]

  const colInfo = [
    { to: '/a-propos',                  label: 'À propos' },
    { to: '/methodologie',              label: 'Méthodologie' },
    { to: '/mentions-legales',          label: t('footer.legal') },
    { to: '/politique-confidentialite', label: 'Confidentialité' },
    { to: '/contact',                   label: t('footer.contact') },
  ]

  return (
    <footer className="bg-navy text-white">
      {/* Newsletter banner */}
      <div className="border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <h3 className="font-playfair text-xl font-semibold mb-1">{t('home.newsletter_title')}</h3>
              <p className="text-white/60 text-sm">{t('home.newsletter_sub')}</p>
            </div>
            <form onSubmit={handleSubscribe} className="flex gap-2 w-full sm:min-w-[300px] sm:w-auto">
              {subStatus === 'success' ? (
                <p className="text-gold text-sm font-medium flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-gold animate-pulse" />
                  Abonnement confirmé ! Bienvenue 🎉
                </p>
              ) : subStatus === 'duplicate' ? (
                <p className="text-white/70 text-sm flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-white/40" />
                  Vous êtes déjà abonné à cette adresse.
                </p>
              ) : (
                <>
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    placeholder={t('home.newsletter_placeholder')}
                    required
                    className="flex-1 px-4 py-2.5 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40 text-sm focus:outline-none focus:border-gold"
                  />
                  <button
                    type="submit"
                    disabled={subStatus === 'loading'}
                    className="px-4 py-2.5 bg-gold text-navy rounded-lg text-sm font-semibold hover:bg-gold-light transition-colors flex items-center gap-1.5 disabled:opacity-70"
                  >
                    {subStatus === 'loading'
                      ? <Loader2 size={14} className="animate-spin" />
                      : <>{t('home.subscribe')} <ArrowRight size={14} /></>
                    }
                  </button>
                </>
              )}
            </form>
          </div>
        </div>
      </div>

      {/* Main footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10">
          {/* Brand */}
          <div className="sm:col-span-2 lg:col-span-1">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-9 h-9 bg-gold rounded-lg flex items-center justify-center">
                <Scale size={18} className="text-navy" />
              </div>
              <div>
                <span className="font-playfair font-bold text-xl">JuriThèque</span>
                <span className="block text-xs text-gold font-arabic leading-none">مكتبة القانون</span>
              </div>
            </div>
            <p className="text-white/50 text-sm leading-relaxed">{t('footer.tagline')}</p>
            <div className="flex gap-3 mt-5">
              {[Twitter, Linkedin, Github].map((Icon, i) => (
                <button key={i} className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center text-white/60 hover:text-gold hover:bg-white/20 transition-colors">
                  <Icon size={15} />
                </button>
              ))}
            </div>
          </div>

          {/* Plateforme col */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-widest text-gold mb-4">Plateforme</h4>
            <ul className="space-y-2.5">
              {colPlateforme.map(item => (
                <li key={item.to}>
                  <Link to={item.to} className="text-white/60 text-sm hover:text-gold transition-colors">{item.label}</Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Ressources col */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-widest text-gold mb-4">Ressources</h4>
            <ul className="space-y-2.5">
              {colRessources.map(({ to, icon: Icon, label }) => (
                <li key={to}>
                  <Link to={to} className="flex items-center gap-1.5 text-white/60 text-sm hover:text-gold transition-colors">
                    <Icon size={12} className="flex-shrink-0 opacity-60" />{label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Info col */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-widest text-gold mb-4">{t('footer.col3')}</h4>
            <ul className="space-y-2.5">
              {colInfo.map((item, i) => (
                <li key={i}>
                  <Link to={item.to} className="text-white/60 text-sm hover:text-gold transition-colors">{item.label}</Link>
                </li>
              ))}
              <li>
                <a href="mailto:contact@juritheque.com" className="flex items-center gap-1.5 text-white/60 text-sm hover:text-gold transition-colors">
                  <Mail size={12} /> contact@juritheque.com
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Gold divider */}
        <div className="gold-line my-8" />

        <div className="flex flex-col sm:flex-row justify-between items-center gap-3 text-white/40 text-xs">
          <span>© 2026 JuriThèque — {t('footer.rights')}</span>
          <span className="font-arabic text-sm">{isRTL ? 'جميع الحقوق محفوظة · JuriThèque' : 'JuriThèque · مكتبة القانون'}</span>
        </div>
      </div>
    </footer>
  )
}
