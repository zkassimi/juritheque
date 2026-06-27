import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Scale, Menu, X, ChevronDown, User, LogOut, Settings, BookOpen, Bell, Newspaper } from 'lucide-react'
import { useLang } from '../contexts/LangContext'
import { useAuth } from '../contexts/AuthContext'
import { SEO_INTENT_PAGES } from '../data/seoIntentPages'

const GUIDE_COUNT = SEO_INTENT_PAGES.length

export default function Navbar() {
  const { t, lang, toggleLang, isRTL } = useLang()
  const { user, logout, isAdmin, isEditor } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [open, setOpen]           = useState(false)
  const [scrolled, setScrolled]   = useState(false)
  const [dropOpen, setDropOpen]   = useState(false)
  const [resOpen, setResOpen]     = useState(false)
  const resRef = useRef(null)

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handler)
    return () => window.removeEventListener('scroll', handler)
  }, [])

  useEffect(() => { setOpen(false); setResOpen(false) }, [location.pathname])

  // Ferme le dropdown Ressources si clic en dehors
  useEffect(() => {
    const handler = (e) => { if (resRef.current && !resRef.current.contains(e.target)) setResOpen(false) }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const navLinks = [
    { to: '/',          label: t('nav.home') },
    { to: '/base',      label: t('nav.database') },
    { to: '/domaines',  label: t('nav.domains') },
    { to: '/videos',    label: t('nav.videos') },
    { to: '/assistant', label: t('nav.assistant') },
  ]

  const ressources = [
    { to: '/fr/guides',              icon: BookOpen,  label: t('nav.thematic_guides'), desc: t('nav.thematic_guides_desc').replace('%n', GUIDE_COUNT) },
    { to: '/glossaire',              icon: BookOpen,  label: t('nav.glossary'),         desc: t('nav.glossary_desc') },
    { to: '/fr/veille-juridique',    icon: Bell,      label: t('nav.legal_watch'),      desc: t('nav.legal_watch_desc') },
    { to: '/fr/bulletins-officiels', icon: Newspaper, label: t('nav.bulletins'),        desc: t('nav.bulletins_desc') },
  ]

  const isActive = (to) =>
    to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)

  const isRessourcesActive = ressources.some(r => location.pathname.startsWith(r.to))

  // Only use transparent/hero style on the home page
  const isHome = location.pathname === '/'
  const isTransparent = isHome && !scrolled

  const handleLogout = () => { logout(); setDropOpen(false); navigate('/') }

  return (
    <header
      className={`fixed top-0 inset-x-0 z-[200] transition-all duration-300 ${
        !isTransparent ? 'bg-white/95 backdrop-blur-md shadow-sm border-b border-gray-100' : 'bg-transparent'
      }`}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 flex-shrink-0 group">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors duration-200 ${
            isTransparent ? 'bg-white/20 group-hover:bg-gold' : 'bg-navy group-hover:bg-gold'
          }`}>
            <Scale size={16} className={`transition-colors duration-200 ${
              isTransparent ? 'text-gold group-hover:text-navy' : 'text-gold group-hover:text-navy'
            }`} />
          </div>
          <div className="hidden sm:block leading-tight">
            <span className={`font-playfair font-bold text-lg tracking-tight transition-colors duration-300 ${
              isTransparent ? 'text-white' : 'text-navy'
            }`}>JuriThèque</span>
            <span className="block text-[10px] text-gold font-arabic leading-none">مكتبة القانون</span>
          </div>
        </Link>

        {/* Desktop nav */}
        <div className="hidden lg:flex items-center gap-1">
          {navLinks.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors duration-150 ${
                isActive(link.to)
                  ? 'text-gold bg-gold/10'
                  : !isTransparent ? 'text-navy-700 hover:text-navy hover:bg-gray-50' : 'text-white/80 hover:text-white hover:bg-white/10'
              }`}
            >
              {link.label}
            </Link>
          ))}

          {/* Dropdown Ressources */}
          <div className="relative" ref={resRef}>
            <button
              onClick={() => setResOpen(v => !v)}
              className={`flex items-center gap-1 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors duration-150 ${
                isRessourcesActive
                  ? 'text-gold bg-gold/10'
                  : !isTransparent ? 'text-navy-700 hover:text-navy hover:bg-gray-50' : 'text-white/80 hover:text-white hover:bg-white/10'
              }`}
            >
              {t('nav.resources')}
              <ChevronDown size={13} className={`transition-transform duration-200 ${resOpen ? 'rotate-180' : ''}`} />
            </button>

            {resOpen && (
              <div className="absolute top-full mt-2 left-0 w-56 bg-white rounded-2xl shadow-xl border border-gray-100 py-2 z-[300]">
                {ressources.map(({ to, icon: Icon, label, desc }) => (
                  <Link
                    key={to}
                    to={to}
                    className={`flex items-start gap-3 px-4 py-3 hover:bg-gray-50 transition-colors group ${
                      location.pathname.startsWith(to) ? 'bg-gold/5' : ''
                    }`}
                  >
                    <div className="w-8 h-8 rounded-lg bg-gold/10 flex items-center justify-center flex-shrink-0 group-hover:bg-gold/20 transition-colors mt-0.5">
                      <Icon size={14} className="text-gold" />
                    </div>
                    <div>
                      <p className={`text-sm font-semibold leading-tight ${location.pathname.startsWith(to) ? 'text-gold' : 'text-navy'}`}>
                        {label}
                      </p>
                      <p className="text-xs text-navy-400 mt-0.5">{desc}</p>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          {/* Lang toggle */}
          <button
            onClick={() => {
              const newLang = lang === 'fr' ? 'ar' : 'fr'
              const arFrMatch = location.pathname.match(/^\/(fr|ar)\/loi\/(.+)$/)
              const legacyMatch = location.pathname.match(/^\/loi\/(.+)$/)
              const guideMatch = location.pathname.match(/^\/(fr|ar)\/guides\/(.+)$/)
              if (arFrMatch) { navigate(`/${newLang}/loi/${arFrMatch[2]}`); return }
              if (legacyMatch) { navigate(`/${newLang}/loi/${legacyMatch[1]}`); return }
              if (guideMatch) { navigate(`/${newLang}/guides/${guideMatch[2]}`); return }
              toggleLang()
            }}
            className={`px-3 py-2 rounded-lg text-xs font-semibold border transition-all duration-150 ${
              !isTransparent
                ? 'border-navy/20 text-navy hover:border-gold hover:text-gold'
                : 'border-white/30 text-white hover:border-gold hover:text-gold'
            }`}
          >
            {lang === 'fr' ? 'عربي' : 'FR'}
          </button>

          {/* Auth */}
          {user ? (
            <div className="relative">
              <button
                onClick={() => setDropOpen(v => !v)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  !isTransparent ? 'text-navy hover:bg-gray-100' : 'text-white hover:bg-white/10'
                }`}
              >
                <div className="w-7 h-7 rounded-full bg-gold flex items-center justify-center text-navy font-bold text-xs">
                  {user.name[0].toUpperCase()}
                </div>
                <span className="hidden sm:block max-w-[100px] truncate">{user.name}</span>
                <ChevronDown size={14} className={`transition-transform ${dropOpen ? 'rotate-180' : ''}`} />
              </button>
              {dropOpen && (
                <div className="absolute end-0 mt-1 w-48 bg-white rounded-xl shadow-xl border border-gray-100 py-1 z-[300]">
                  <Link to="/profil"   onClick={() => setDropOpen(false)} className="flex items-center gap-2.5 px-4 py-2.5 text-sm text-navy-700 hover:bg-gray-50 hover:text-navy">
                    <User size={14} /> {t('nav.profile')}
                  </Link>
                  {isEditor && (
                    <Link to="/admin" onClick={() => setDropOpen(false)} className="flex items-center gap-2.5 px-4 py-2.5 text-sm text-navy-700 hover:bg-gray-50 hover:text-navy">
                      <Settings size={14} /> {isAdmin ? t('nav.admin') : t('nav.editor')}
                    </Link>
                  )}
                  <hr className="my-1 border-gray-100" />
                  <button onClick={handleLogout} className="flex items-center gap-2.5 w-full px-4 py-2.5 text-sm text-red-600 hover:bg-red-50">
                    <LogOut size={14} /> {t('nav.logout')}
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link
              to="/connexion"
              className="px-4 py-2 rounded-lg text-sm font-semibold bg-gold text-navy hover:bg-gold-dark transition-colors duration-150"
            >
              {t('nav.login')}
            </Link>
          )}

          {/* Mobile burger */}
          <button
            onClick={() => setOpen(v => !v)}
            className={`lg:hidden p-3 rounded-lg transition-colors ${
              !isTransparent ? 'text-navy hover:bg-gray-100' : 'text-white hover:bg-white/10'
            }`}
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </nav>

      {/* Mobile menu */}
      {open && (
        <div className="lg:hidden bg-white border-t border-gray-100 shadow-lg">
          <div className="px-4 py-3 space-y-1">
            {navLinks.map(link => (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-2 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive(link.to) ? 'text-gold bg-gold/10' : 'text-navy-700 hover:bg-gray-50'
                }`}
              >
                <BookOpen size={14} className="text-gold" />
                {link.label}
              </Link>
            ))}

            {/* Séparateur Ressources */}
            <div className="pt-2 pb-1 px-4">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-navy-400">{t('nav.resources')}</p>
            </div>
            {ressources.map(({ to, icon: Icon, label }) => (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-2 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  location.pathname.startsWith(to) ? 'text-gold bg-gold/10' : 'text-navy-700 hover:bg-gray-50'
                }`}
              >
                <Icon size={14} className="text-gold" />
                {label}
              </Link>
            ))}

            {/* Toggle langue mobile */}
            <div className="pt-3 border-t border-gray-100 mt-1">
              <button
                onClick={() => {
                  const newLang = lang === 'fr' ? 'ar' : 'fr'
                  const arFrMatch = location.pathname.match(/^\/(fr|ar)\/loi\/(.+)$/)
                  const legacyMatch = location.pathname.match(/^\/loi\/(.+)$/)
                  const guideMatch = location.pathname.match(/^\/(fr|ar)\/guides\/(.+)$/)
                  if (arFrMatch) { navigate(`/${newLang}/loi/${arFrMatch[2]}`); setOpen(false); return }
                  if (legacyMatch) { navigate(`/${newLang}/loi/${legacyMatch[1]}`); setOpen(false); return }
                  if (guideMatch) { navigate(`/${newLang}/guides/${guideMatch[2]}`); setOpen(false); return }
                  toggleLang(); setOpen(false)
                }}
                className="w-full flex items-center justify-between px-4 py-3 rounded-lg text-sm font-medium text-navy-700 hover:bg-gray-50 transition-colors"
              >
                <span>{lang === 'fr' ? 'Basculer en arabe' : 'التبديل إلى الفرنسية'}</span>
                <span className="text-base font-semibold text-gold">{lang === 'fr' ? 'عربي' : 'FR'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
