import { useTranslation } from 'react-i18next'
import { Globe } from 'lucide-react'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import {
  SUPPORTED_LANGUAGES,
  LANGUAGE_NAMES,
  LANGUAGE_FLAGS,
  type SupportedLanguage,
} from '@/i18n'

/**
 * Language switcher component for changing the application language.
 * Uses a dropdown menu to select between supported languages.
 */
export function LanguageSwitcher() {
  const { i18n, t } = useTranslation()

  const currentLanguage = i18n.language as SupportedLanguage

  const handleLanguageChange = (language: SupportedLanguage) => {
    i18n.changeLanguage(language)
  }

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          className="flex items-center gap-1.5 px-2 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          aria-label={t('language.select')}
        >
          <Globe size={18} />
          <span className="hidden sm:inline">
            {LANGUAGE_FLAGS[currentLanguage]} {LANGUAGE_NAMES[currentLanguage]}
          </span>
          <span className="sm:hidden">{LANGUAGE_FLAGS[currentLanguage]}</span>
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="min-w-[140px] bg-white dark:bg-gray-800 rounded-md shadow-lg p-1 border border-gray-200 dark:border-gray-700 z-50"
          sideOffset={5}
          align="end"
        >
          <DropdownMenu.Label className="px-2 py-1.5 text-xs font-medium text-gray-500 dark:text-gray-400">
            {t('language.title')}
          </DropdownMenu.Label>

          {SUPPORTED_LANGUAGES.map((lang) => (
            <DropdownMenu.Item
              key={lang}
              onClick={() => handleLanguageChange(lang)}
              className={`flex items-center gap-2 px-2 py-2 text-sm rounded-md cursor-pointer outline-none transition-colors
                ${
                  currentLanguage === lang
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }
              `}
            >
              <span className="text-base">{LANGUAGE_FLAGS[lang]}</span>
              <span>{LANGUAGE_NAMES[lang]}</span>
              {currentLanguage === lang && (
                <span className="ml-auto text-blue-600 dark:text-blue-400">✓</span>
              )}
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}

export default LanguageSwitcher
