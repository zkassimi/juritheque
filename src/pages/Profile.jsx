import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Heart, Clock, Bell, Trash2, LogOut, User, BookOpen } from 'lucide-react'
import { useLang } from '../contexts/LangContext'
import { useAuth } from '../contexts/AuthContext'
import { lawPath } from '../lib/lawUtils'
import LawCard from '../components/LawCard'
import TypeBadge from '../components/ui/TypeBadge'

export default function Profile() {
  const { t, lang } = useLang()
  const { user, logout, favorites, history } = useAuth()
  const navigate = useNavigate()
  const [tab, setTab] = useState('favorites')

  if (!user) {
    navigate('/connexion')
    return null
  }

  const TABS = [
    { key: 'favorites',     icon: Heart,    label: t('profile.favorites') },
    { key: 'history',       icon: Clock,    label: t('profile.history') },
    { key: 'notifications', icon: Bell,     label: t('profile.notifications') },
  ]

  return (
    <div className="min-h-screen bg-[#f8fafc] pt-16">
      {/* Header */}
      <div className="bg-navy text-white py-10">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="flex items-start gap-4 flex-wrap">
            <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gold rounded-2xl flex items-center justify-center text-navy text-xl sm:text-2xl font-bold flex-shrink-0">
              {user.name[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="font-playfair font-bold text-xl sm:text-2xl truncate">{user.name}</h1>
              <p className="text-white/60 text-xs sm:text-sm truncate">{user.profession}{user.profession && ' · '}{user.email}</p>
              {user.role !== 'user' && (
                <span className="inline-block mt-1 px-2 py-0.5 bg-gold/20 text-gold text-xs rounded font-medium capitalize">
                  {user.role}
                </span>
              )}
            </div>
            <button
              onClick={() => { logout(); navigate('/') }}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white/10 text-white/80 hover:bg-red-500/20 hover:text-red-300 text-sm transition-colors flex-shrink-0"
            >
              <LogOut size={14} /><span className="hidden sm:inline">{t('nav.logout')}</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-6 overflow-x-auto">
          {TABS.map(({ key, icon: Icon, label }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`flex items-center gap-2 px-4 sm:px-5 py-3 text-sm font-medium border-b-2 transition-all -mb-px whitespace-nowrap ${
                tab === key ? 'border-gold text-gold' : 'border-transparent text-navy-600 hover:text-navy'
              }`}
            >
              <Icon size={14} />{label}
              {key === 'favorites' && favorites.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 bg-gold/20 text-gold text-[10px] rounded-full">{favorites.length}</span>
              )}
            </button>
          ))}
        </div>

        {/* Favorites */}
        {tab === 'favorites' && (
          favorites.length === 0 ? (
            <div className="text-center py-20">
              <Heart size={40} className="text-gray-200 mx-auto mb-3" />
              <p className="text-navy-500">{t('profile.no_favorites')}</p>
              <Link to="/base" className="mt-4 inline-flex text-sm text-gold hover:underline">
                {t('nav.database')} →
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {favorites.map(law => <LawCard key={law.id} law={law} />)}
            </div>
          )
        )}

        {/* History */}
        {tab === 'history' && (
          history.length === 0 ? (
            <div className="text-center py-20">
              <Clock size={40} className="text-gray-200 mx-auto mb-3" />
              <p className="text-navy-500">{t('profile.no_history')}</p>
            </div>
          ) : (
            <div className="space-y-2">
              {history.map(law => (
                <Link
                  key={law.id + law.visitedAt}
                  to={lawPath(law)}
                  className="flex items-center gap-4 p-4 bg-white rounded-xl border border-gray-100 hover:border-gold/40 hover:shadow-md transition-all"
                >
                  <BookOpen size={16} className="text-gold flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-medium text-navy truncate ${lang === 'ar' ? 'font-arabic' : ''}`}>
                      {lang === 'ar' ? law.title_ar : law.title_fr}
                    </p>
                    <p className="text-xs text-navy-500">{law.number}</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <TypeBadge type={law.type} />
                    <span className="text-[10px] text-navy-400">{new Date(law.visitedAt).toLocaleDateString()}</span>
                  </div>
                </Link>
              ))}
            </div>
          )
        )}

        {/* Notifications */}
        {tab === 'notifications' && (
          <div className="text-center py-20">
            <Bell size={40} className="text-gray-200 mx-auto mb-3" />
            <p className="text-navy-500">{t('profile.no_notif')}</p>
          </div>
        )}
      </div>
    </div>
  )
}
