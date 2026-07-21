import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { t as translate } from '../i18n'

const LanguageContext = createContext(null)

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || 'es'
  })

  useEffect(() => {
    localStorage.setItem('language', language)
    document.documentElement.lang = language === 'en' ? 'en' : 'es'
    document.title =
      language === 'en'
        ? 'Breast Cancer Detection'
        : 'Detección de Cáncer de Mama'
  }, [language])

  const t = useCallback(
    (key, params) => translate(language, key, params),
    [language]
  )

  const toggleLanguage = useCallback(() => {
    setLanguage((prev) => (prev === 'es' ? 'en' : 'es'))
  }, [])

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLanguage debe usarse dentro de LanguageProvider')
  return ctx
}

export default LanguageContext
