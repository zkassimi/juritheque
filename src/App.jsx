import { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { SpeedInsights } from '@vercel/speed-insights/react'
import { useLang } from './contexts/LangContext'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import ScrollToTop from './components/ScrollToTop'
import FeedbackButton from './components/FeedbackButton'

// ── Pages chargées immédiatement (above the fold critique) ───────────────────
import Home from './pages/Home'
// SEOIntentPage importé en eager (évite le problème MIME type sur Hostinger)
import SEOIntentPage from './pages/SEOIntentPage'

// ── Pages chargées à la demande (lazy) ───────────────────────────────────────
const Database          = lazy(() => import('./pages/Database'))
const LawDetail         = lazy(() => import('./pages/LawDetail'))
const Domains           = lazy(() => import('./pages/Domains'))
const DomainView        = lazy(() => import('./pages/DomainView'))
const Videos            = lazy(() => import('./pages/Videos'))
const Assistant         = lazy(() => import('./pages/Assistant'))
const Auth              = lazy(() => import('./pages/Auth'))
const Profile           = lazy(() => import('./pages/Profile'))
const Admin             = lazy(() => import('./pages/Admin'))
const Legal             = lazy(() => import('./pages/Legal'))
const PrivacyPolicy     = lazy(() => import('./pages/PrivacyPolicy'))
const Contact           = lazy(() => import('./pages/Contact'))
const GuidesIndex       = lazy(() => import('./pages/GuidesIndex'))
const LegalWatch        = lazy(() => import('./pages/LegalWatch'))
const Bulletins         = lazy(() => import('./pages/Bulletins'))
const BulletinsOfficiels = lazy(() => import('./pages/BulletinsOfficiels'))
const Glossaire          = lazy(() => import('./pages/Glossaire'))
const Methodologie       = lazy(() => import('./pages/Methodologie'))
const APropos            = lazy(() => import('./pages/APropos'))

// ── Fallback de chargement ────────────────────────────────────────────────────
function PageLoader() {
  return (
    <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center pt-16">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin" />
        <p className="text-xs text-navy-400">Chargement…</p>
      </div>
    </div>
  )
}

export default function App() {
  const { isRTL } = useLang()

  return (
    <div dir={isRTL ? 'rtl' : 'ltr'} className={isRTL ? 'font-arabic' : 'font-sans'}>
      <ScrollToTop />
      <Navbar />
      <main>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/"                              element={<Home />} />
            <Route path="/base"                          element={<Database />} />
            <Route path="/loi/:slug"                     element={<LawDetail />} />
            <Route path="/fr/loi/:slug"                  element={<LawDetail />} />
            <Route path="/ar/loi/:slug"                  element={<LawDetail />} />
            <Route path="/domaines"                      element={<Domains />} />
            <Route path="/domaine/:slug"                 element={<DomainView />} />
            <Route path="/videos"                        element={<Videos />} />
            <Route path="/assistant"                     element={<Assistant />} />
            <Route path="/connexion"                     element={<Auth />} />
            <Route path="/profil"                        element={<Profile />} />
            <Route path="/admin"                         element={<Admin />} />
            <Route path="/methodologie"                  element={<Methodologie />} />
            <Route path="/a-propos"                      element={<APropos />} />
            <Route path="/mentions-legales"              element={<Legal />} />
            <Route path="/politique-confidentialite"     element={<PrivacyPolicy />} />
            <Route path="/contact"                       element={<Contact />} />
            <Route path="/fr/guides"                     element={<GuidesIndex />} />
            <Route path="/fr/guides/:slug"               element={<SEOIntentPage />} />
            <Route path="/ar/guides/:slug"               element={<SEOIntentPage />} />
            <Route path="/fr/veille-juridique"           element={<LegalWatch />} />
            <Route path="/bulletins"                     element={<Bulletins />} />
            <Route path="/fr/bulletins-officiels"        element={<BulletinsOfficiels />} />
            <Route path="/glossaire"                     element={<Glossaire />} />
            {/* Redirige l'ancienne page séparée vers la base unifiée */}
            <Route path="/fr/lois-complementaires"       element={<Navigate to="/base?source=Adala" replace />} />
          </Routes>
        </Suspense>
      </main>
      <Footer />
      <FeedbackButton />
      <SpeedInsights />
    </div>
  )
}
