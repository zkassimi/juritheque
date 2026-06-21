import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { supabase } from '../lib/supabase'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]           = useState(null)
  const [profile, setProfile]     = useState(null)
  const [favorites, setFavorites] = useState([])
  const [history, setHistory]     = useState([])
  const [loading, setLoading]     = useState(true)

  /* ── Load session on mount ── */
  useEffect(() => {
    let cancelled = false
    // Safety timeout — never block UI more than 3s
    const timeout = setTimeout(() => { if (!cancelled) setLoading(false) }, 3000)

    supabase.auth.getSession()
      .then(({ data: { session } }) => {
        if (cancelled) return
        setUser(session?.user ?? null)
        if (session?.user) fetchProfile(session.user.id)
      })
      .catch(() => {})
      .finally(() => { if (!cancelled) { setLoading(false); clearTimeout(timeout) } })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
      if (session?.user) fetchProfile(session.user.id)
      else { setProfile(null); setFavorites([]) }
    })

    return () => { cancelled = true; clearTimeout(timeout); subscription.unsubscribe() }
  }, [])

  const fetchProfile = async (uid) => {
    try {
      const { data } = await supabase.from('profiles').select('*').eq('id', uid).single()
      if (data) { setProfile(data); fetchFavorites(uid) }
    } catch {}
  }

  const fetchFavorites = async (uid) => {
    try {
      const { data } = await supabase.from('favorites').select('law_id, laws(*)').eq('user_id', uid)
      if (data) setFavorites(data.map(f => f.laws).filter(Boolean))
    } catch {}
  }

  /* ── Auth actions ── */
  const login = useCallback(async (email, password) => {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
    return true
  }, [])

  const register = useCallback(async ({ name, email, password, profession }) => {
    const { error } = await supabase.auth.signUp({
      email, password,
      options: { data: { name, profession } },
    })
    if (error) throw error
    return true
  }, [])

  const loginWithGoogle = useCallback(async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: 'https://juritheque.com',
      },
    })
    if (error) throw error
  }, [])

  const resetPassword = useCallback(async (email) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: 'https://juritheque.com/reset-password',
    })
    if (error) throw error
  }, [])

  const logout = useCallback(async () => {
    await supabase.auth.signOut()
    setUser(null); setProfile(null); setFavorites([]); setHistory([])
  }, [])

  /* ── Favorites ── */
  const toggleFavorite = useCallback(async (law) => {
    if (!user) return
    const exists = favorites.some(f => f.id === law.id)
    if (exists) {
      await supabase.from('favorites').delete().eq('user_id', user.id).eq('law_id', law.id)
      setFavorites(prev => prev.filter(f => f.id !== law.id))
    } else {
      await supabase.from('favorites').insert({ user_id: user.id, law_id: law.id })
      setFavorites(prev => [law, ...prev])
    }
  }, [user, favorites])

  const isFavorite = useCallback((id) => favorites.some(f => f.id === id), [favorites])

  const addToHistory = useCallback((law) => {
    setHistory(prev => {
      const filtered = prev.filter(h => h.id !== law.id)
      return [{ ...law, visitedAt: new Date().toISOString() }, ...filtered].slice(0, 20)
    })
  }, [])

  const displayUser = profile || (user ? {
    id: user.id,
    name: user.user_metadata?.name || user.email?.split('@')[0],
    email: user.email,
    profession: user.user_metadata?.profession || '',
    role: 'user',
  } : null)

  const isAdmin  = displayUser?.role === 'admin'
  const isEditor = ['editor','admin'].includes(displayUser?.role)

  return (
    <AuthContext.Provider value={{
      user: displayUser, supabaseUser: user, loading,
      login, register, loginWithGoogle, logout, resetPassword,
      favorites, toggleFavorite, isFavorite,
      history, addToHistory,
      isAdmin, isEditor,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
