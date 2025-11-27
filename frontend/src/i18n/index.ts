import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

// Import translation files
import koCommon from './locales/ko/common.json'
import koScreener from './locales/ko/screener.json'
import koStock from './locales/ko/stock.json'
import koAuth from './locales/ko/auth.json'
import koPortfolio from './locales/ko/portfolio.json'

import enCommon from './locales/en/common.json'
import enScreener from './locales/en/screener.json'
import enStock from './locales/en/stock.json'
import enAuth from './locales/en/auth.json'
import enPortfolio from './locales/en/portfolio.json'

// Define supported languages
export const SUPPORTED_LANGUAGES = ['ko', 'en'] as const
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number]

// Language display names
export const LANGUAGE_NAMES: Record<SupportedLanguage, string> = {
  ko: '한국어',
  en: 'English',
}

// Language flags for UI
export const LANGUAGE_FLAGS: Record<SupportedLanguage, string> = {
  ko: '🇰🇷',
  en: '🇺🇸',
}

// Resources object for i18next
const resources = {
  ko: {
    common: koCommon,
    screener: koScreener,
    stock: koStock,
    auth: koAuth,
    portfolio: koPortfolio,
  },
  en: {
    common: enCommon,
    screener: enScreener,
    stock: enStock,
    auth: enAuth,
    portfolio: enPortfolio,
  },
}

// Initialize i18next
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'ko',
    supportedLngs: SUPPORTED_LANGUAGES,
    defaultNS: 'common',
    ns: ['common', 'screener', 'stock', 'auth', 'portfolio'],

    // Language detection options
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18n-language',
    },

    interpolation: {
      escapeValue: false, // React already escapes values
    },

    // React-specific options
    react: {
      useSuspense: false, // Disable suspense for SSR compatibility
    },
  })

export default i18n
