import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Mail, Lock, User, Briefcase, Eye, EyeOff, Scale, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { useLang } from '../contexts/LangContext'
import { useAuth } from '../contexts/AuthContext'
import { PROFESSIONS } from '../data/mockData'

export default function Auth() {
  const { t } = useLang()
  const { user, login, register, loginWithGoogle, resetPassword } = useAuth()
  const navigate = useNavigate()
  const [tab, setTab]           = useState('login')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading]             = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)
  const [error, setError]                 = useState('')
  const [success, setSuccess]             = useState('')
  const [forgotMode, setForgotMode]       = useState(false)
  const [forgotEmail, setForgotEmail]     = useState('')
  const [form, setForm] = useState({ name: '', email: '', password: '', profession: '' })

  useEffect(() => { if (user) navigate('/') }, [user])

  const set = (k, v) => { setForm(f => ({ ...f, [k]: v })); setError('') }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      if (tab === 'login') {
        await login(form.email, form.password)
        // onAuthStateChange will update user → useEffect redirects to /
      } else {
        await register({
          name: form.name,
          email: form.email,
          password: form.password,       // ← was missing before!
          profession: form.profession,
        })
        setSuccess('Compte créé ! Vérifiez votre email pour confirmer votre inscription.')
      }
    } catch (err) {
      // Translate common Supabase error messages to French
      const msg = err?.message || ''
      if (msg.includes('Invalid login credentials'))
        setError('Email ou mot de passe incorrect.')
      else if (msg.includes('Email not confirmed'))
        setError('Veuillez confirmer votre email avant de vous connecter.')
      else if (msg.includes('User already registered'))
        setError('Un compte existe déjà avec cet email.')
      else if (msg.includes('Password should be at least'))
        setError('Le mot de passe doit contenir au moins 6 caractères.')
      else if (msg.includes('Unable to validate email'))
        setError('Adresse email invalide.')
      else
        setError(msg || 'Une erreur est survenue. Réessayez.')
    } finally {
      setLoading(false)
    }
  }

  const benefits = [
    'Accès à 7 400+ textes juridiques',
    'Assistant IA juridique inclus',
    'Sauvegardez vos favoris',
    'Alertes sur vos domaines',
  ]

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-2 bg-white rounded-3xl shadow-2xl overflow-hidden">

        {/* Left panel */}
        <div className="bg-navy p-10 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 w-48 h-48 rounded-full bg-gold/10 blur-3xl" />
          <div className="absolute bottom-0 left-0 w-32 h-32 rounded-full bg-blue-500/10 blur-3xl" />

          <div className="relative z-10">
            <Link to="/" className="flex items-center gap-2 mb-10">
              <div className="w-9 h-9 bg-gold rounded-lg flex items-center justify-center">
                <Scale size={18} className="text-navy" />
              </div>
              <div>
                <span className="font-playfair font-bold text-white text-xl">JuriThèque</span>
                <span className="block text-[10px] text-gold font-arabic leading-none">مكتبة القانون</span>
              </div>
            </Link>

            <h2 className="font-playfair font-bold text-white text-3xl mb-3">
              {t('auth.free_access')}
            </h2>
            <p className="text-white/60 text-sm mb-8">{t('auth.tagline')}</p>

            <div className="space-y-3">
              {benefits.map((b, i) => (
                <div key={i} className="flex items-center gap-2.5 text-sm text-white/80">
                  <CheckCircle2 size={16} className="text-gold flex-shrink-0" />
                  {b}
                </div>
              ))}
            </div>
          </div>

          <div className="relative z-10 mt-10">
            <div className="gold-line mb-4" />
            <p className="text-white/40 text-xs">
              Créez votre compte gratuitement pour accéder à toutes les fonctionnalités.
            </p>
          </div>
        </div>

        {/* Right panel */}
        <div className="p-8 sm:p-10 flex flex-col justify-center">
          <div className="max-w-sm mx-auto w-full">
            {/* Tabs */}
            <div className="flex bg-gray-100 rounded-xl p-1 mb-6">
              {['login', 'register'].map(tab_ => (
                <button
                  key={tab_}
                  onClick={() => { setTab(tab_); setError(''); setSuccess('') }}
                  className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    tab === tab_ ? 'bg-white text-navy shadow-sm' : 'text-navy-600 hover:text-navy'
                  }`}
                >
                  {t(`auth.${tab_}`)}
                </button>
              ))}
            </div>

            {/* Success message */}
            {success && (
              <div className="flex items-start gap-2.5 p-3.5 bg-green-50 border border-green-200 rounded-xl mb-4">
                <CheckCircle2 size={16} className="text-green-600 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-green-700">{success}</p>
              </div>
            )}

            {/* Error message */}
            {error && (
              <div className="flex items-start gap-2.5 p-3.5 bg-red-50 border border-red-200 rounded-xl mb-4">
                <AlertCircle size={16} className="text-red-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {tab === 'register' && (
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">{t('auth.name')}</label>
                  <div className="relative">
                    <User size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      value={form.name}
                      onChange={e => set('name', e.target.value)}
                      required
                      placeholder="Votre nom complet"
                      className="w-full pl-9 pr-4 py-3 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-navy-700 mb-1">{t('auth.email')}</label>
                <div className="relative">
                  <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    type="email"
                    value={form.email}
                    onChange={e => set('email', e.target.value)}
                    required
                    placeholder="votre@email.com"
                    className="w-full pl-9 pr-4 py-3 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20"
                  />
                </div>
              </div>

              {tab === 'register' && (
                <div>
                  <label className="block text-xs font-medium text-navy-700 mb-1">{t('auth.profession')}</label>
                  <div className="relative">
                    <Briefcase size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <select
                      value={form.profession}
                      onChange={e => set('profession', e.target.value)}
                      required
                      className="w-full pl-9 pr-4 py-3 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold appearance-none bg-white"
                    >
                      <option value="" disabled>Sélectionner...</option>
                      {PROFESSIONS.map(p => <option key={p}>{p}</option>)}
                    </select>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-navy-700 mb-1">{t('auth.password')}</label>
                <div className="relative">
                  <Lock size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    type={showPass ? 'text' : 'password'}
                    value={form.password}
                    onChange={e => set('password', e.target.value)}
                    required
                    minLength={6}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-10 py-3 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20"
                  />
                  <button type="button" onClick={() => setShowPass(v => !v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-navy">
                    {showPass ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
                {tab === 'register' && (
                  <p className="text-[11px] text-gray-400 mt-1">Minimum 6 caractères</p>
                )}
                {tab === 'login' && (
                  <button
                    type="button"
                    onClick={() => { setForgotMode(true); setError(''); setSuccess('') }}
                    className="text-[11px] text-gold hover:underline mt-1 block text-right w-full"
                  >
                    Mot de passe oublié ?
                  </button>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-navy text-white rounded-xl text-sm font-bold tracking-wide hover:bg-gold hover:text-navy transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                    </svg>
                    {t('common.loading')}
                  </span>
                ) : t(`auth.submit_${tab}`)}
              </button>
            </form>

            {/* Divider */}
            <div className="relative my-5">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-100" /></div>
              <div className="relative text-center"><span className="bg-white px-3 text-xs text-gray-400">ou</span></div>
            </div>

            {/* Google OAuth */}
            <button
              type="button"
              disabled={googleLoading}
              onClick={async () => {
                setGoogleLoading(true)
                setError('')
                try {
                  await loginWithGoogle()
                } catch {
                  setError('Connexion Google impossible. Vérifiez la configuration Supabase.')
                  setGoogleLoading(false)
                }
              }}
              className="w-full py-3 border border-gray-200 rounded-xl text-sm text-navy-700 hover:bg-gray-50 flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {googleLoading ? (
                <Loader2 size={16} className="animate-spin text-navy" />
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
              )}
              {googleLoading ? 'Redirection vers Google...' : 'Continuer avec Google'}
            </button>

            <p className="text-center text-xs text-navy-500 mt-5">
              {t(tab === 'login' ? 'auth.no_account' : 'auth.has_account')}{' '}
              <button
                onClick={() => { setTab(tab === 'login' ? 'register' : 'login'); setError(''); setSuccess('') }}
                className="text-gold font-semibold hover:underline"
              >
                {t(tab === 'login' ? 'auth.register' : 'auth.login')}
              </button>
            </p>
          </div>
        </div>
      </div>

      {/* ── Forgot Password Modal ── */}
      {forgotMode && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-8">
            <h3 className="font-playfair font-bold text-navy text-xl mb-2">Mot de passe oublié</h3>
            <p className="text-sm text-navy-600 mb-5">
              Entrez votre email et nous vous enverrons un lien pour réinitialiser votre mot de passe.
            </p>

            {success ? (
              <div className="flex items-start gap-2.5 p-3.5 bg-green-50 border border-green-200 rounded-xl mb-4">
                <CheckCircle2 size={16} className="text-green-600 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-green-700">{success}</p>
              </div>
            ) : (
              <>
                {error && (
                  <div className="flex items-start gap-2.5 p-3.5 bg-red-50 border border-red-200 rounded-xl mb-4">
                    <AlertCircle size={16} className="text-red-500 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}
                <div className="relative mb-4">
                  <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    type="email"
                    value={forgotEmail}
                    onChange={e => setForgotEmail(e.target.value)}
                    placeholder="votre@email.com"
                    className="w-full pl-9 pr-4 py-3 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20"
                  />
                </div>
                <button
                  disabled={loading || !forgotEmail}
                  onClick={async () => {
                    setLoading(true); setError('')
                    try {
                      await resetPassword(forgotEmail)
                      setSuccess('Email envoyé ! Vérifiez votre boîte mail pour le lien de réinitialisation.')
                    } catch (err) {
                      setError(err?.message || "Erreur lors de l'envoi.")
                    } finally { setLoading(false) }
                  }}
                  className="w-full py-3 bg-navy text-white rounded-xl text-sm font-bold hover:bg-gold hover:text-navy transition-all disabled:opacity-50"
                >
                  {loading ? <Loader2 size={16} className="animate-spin mx-auto" /> : 'Envoyer le lien'}
                </button>
              </>
            )}

            <button
              onClick={() => { setForgotMode(false); setError(''); setSuccess(''); setForgotEmail('') }}
              className="mt-4 w-full py-2 text-sm text-navy-500 hover:text-navy transition-colors"
            >
              ← Retour à la connexion
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
