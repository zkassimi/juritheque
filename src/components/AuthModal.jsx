import { useState } from 'react'
import { X, Mail, Lock, User, Briefcase, Eye, EyeOff } from 'lucide-react'
import { useLang } from '../contexts/LangContext'
import { useAuth } from '../contexts/AuthContext'
import { PROFESSIONS } from '../data/mockData'

export default function AuthModal({ onClose, defaultTab = 'login' }) {
  const { t } = useLang()
  const { login, register } = useAuth()
  const [tab, setTab]           = useState(defaultTab)
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading]   = useState(false)
  const [form, setForm] = useState({ name: '', email: '', password: '', profession: '' })

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    await new Promise(r => setTimeout(r, 600))
    if (tab === 'login') login(form.email, form.password)
    else register({ name: form.name, email: form.email, profession: form.profession })
    setLoading(false)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="absolute inset-0 bg-navy/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative z-10 w-full max-w-sm bg-white rounded-2xl shadow-2xl overflow-hidden animate-fade-in">
        {/* Close */}
        <button onClick={onClose} className="absolute top-3 right-3 p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 z-10">
          <X size={16} />
        </button>

        {/* Top gold bar */}
        <div className="h-1 bg-gradient-to-r from-gold-dark via-gold to-gold-light" />

        <div className="p-6">
          {/* Logo */}
          <div className="text-center mb-6">
            <p className="font-playfair font-bold text-navy text-xl">JuriThèque</p>
            <p className="text-xs text-navy-500 mt-0.5">{t('auth.free_access')}</p>
          </div>

          {/* Tabs */}
          <div className="flex bg-gray-100 rounded-xl p-1 mb-5">
            {['login', 'register'].map(tab_ => (
              <button
                key={tab_}
                onClick={() => setTab(tab_)}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                  tab === tab_ ? 'bg-white text-navy shadow-sm' : 'text-navy-600 hover:text-navy'
                }`}
              >
                {t(`auth.${tab_}`)}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            {tab === 'register' && (
              <div className="relative">
                <User size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder={t('auth.name')}
                  value={form.name}
                  onChange={e => set('name', e.target.value)}
                  required
                  className="w-full pl-9 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20"
                />
              </div>
            )}

            <div className="relative">
              <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="email"
                placeholder={t('auth.email')}
                value={form.email}
                onChange={e => set('email', e.target.value)}
                required
                className="w-full pl-9 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20"
              />
            </div>

            {tab === 'register' && (
              <div className="relative">
                <Briefcase size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <select
                  value={form.profession}
                  onChange={e => set('profession', e.target.value)}
                  required
                  className="w-full pl-9 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold appearance-none bg-white"
                >
                  <option value="" disabled>{t('auth.profession')}</option>
                  {PROFESSIONS.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
            )}

            <div className="relative">
              <Lock size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type={showPass ? 'text' : 'password'}
                placeholder={t('auth.password')}
                value={form.password}
                onChange={e => set('password', e.target.value)}
                required
                className="w-full pl-9 pr-10 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/20"
              />
              <button type="button" onClick={() => setShowPass(v => !v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                {showPass ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-navy text-white rounded-xl text-sm font-semibold hover:bg-gold hover:text-navy transition-colors disabled:opacity-50"
            >
              {loading ? t('common.loading') : t(`auth.submit_${tab}`)}
            </button>
          </form>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-100" /></div>
            <div className="relative text-center"><span className="bg-white px-3 text-xs text-gray-400">ou</span></div>
          </div>

          <button className="w-full py-2.5 border border-gray-200 rounded-xl text-sm text-navy-700 hover:bg-gray-50 flex items-center justify-center gap-2 transition-colors">
            <svg width="16" height="16" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            {t('auth.google')}
          </button>

          <p className="text-center text-xs text-navy-500 mt-4">
            {t(tab === 'login' ? 'auth.no_account' : 'auth.has_account')}{' '}
            <button onClick={() => setTab(tab === 'login' ? 'register' : 'login')} className="text-gold font-medium hover:underline">
              {t(tab === 'login' ? 'auth.register' : 'auth.login')}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
