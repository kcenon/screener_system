import { useTranslation } from 'react-i18next'
import { Globe } from 'lucide-react'

const languages = [
  { code: 'ko', name: '한국어', flag: '🇰🇷' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
]

interface LanguageSwitcherProps {
  variant?: 'default' | 'compact'
  className?: string
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
  variant = 'default',
  className = '',
}) => {
  const { i18n } = useTranslation()

  const handleLanguageChange = (langCode: string) => {
    i18n.changeLanguage(langCode)
  }

  if (variant === 'compact') {
    return (
      <button
        onClick={() => {
          const currentIndex = languages.findIndex((l) => l.code === i18n.language)
          const nextIndex = (currentIndex + 1) % languages.length
          handleLanguageChange(languages[nextIndex].code)
        }}
        className={`flex items-center gap-1 px-2 py-1 text-sm rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${className}`}
        title="Switch language"
      >
        <Globe className="w-4 h-4" />
        <span>{languages.find((l) => l.code === i18n.language)?.flag}</span>
      </button>
    )
  }

  return (
    <select
      value={i18n.language}
      onChange={(e) => handleLanguageChange(e.target.value)}
      className={`px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
    >
      {languages.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.flag} {lang.name}
        </option>
      ))}
    </select>
  )
}

export default LanguageSwitcher
