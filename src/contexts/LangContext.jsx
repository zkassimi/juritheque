import { createContext, useContext, useState, useCallback } from 'react'
import { translations } from '../data/translations'

const LangContext = createContext(null)
const LS_KEY = 'jt_lang'

export function LangProvider({ children }) {
  const [lang, setLangState] = useState(() => {
    const saved = localStorage.getItem(LS_KEY)
    return saved === 'ar' ? 'ar' : 'fr'
  })

  const setLang = useCallback((l) => {
    setLangState(l)
    localStorage.setItem(LS_KEY, l)
  }, [])

  const t = useCallback((key) => {
    return translations[lang]?.[key] ?? translations['fr']?.[key] ?? key
  }, [lang])

  const toggleLang = useCallback(() => {
    setLang(lang === 'fr' ? 'ar' : 'fr')
  }, [lang, setLang])

  const isRTL = lang === 'ar'

  return (
    <LangContext.Provider value={{ lang, setLang, toggleLang, t, isRTL }}>
      {children}
    </LangContext.Provider>
  )
}

export function useLang() {
  const ctx = useContext(LangContext)
  if (!ctx) throw new Error('useLang must be used inside LangProvider')
  return ctx
}
