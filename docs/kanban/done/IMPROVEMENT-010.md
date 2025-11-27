# [IMPROVEMENT-010] Internationalization (i18n) - Multi-Language Support

## Metadata
- **Status**: TODO
- **Priority**: Medium
- **Assignee**: Frontend Team
- **Estimated Time**: 10-12 hours
- **Actual Time**: TBD
- **Sprint**: Phase 4 Enhancement
- **Tags**: #frontend #i18n #localization #multi-language #react-i18next
- **Dependencies**: FE-001 ✅
- **Blocks**: None
- **Related**: README.md Future Enhancements (Internationalization)
- **PR**: TBD

## Description
Implement comprehensive internationalization (i18n) support using react-i18next to enable multi-language access to the platform. This enables the Stock Screener system to reach a broader audience by supporting both Korean (default) and English languages, with infrastructure for future language additions.

## Problem Statement
Current limitations:
- ❌ **Korean Only**: All UI text is hardcoded in Korean
- ❌ **No Language Switching**: Users cannot change language preferences
- ❌ **Hardcoded Strings**: Text scattered throughout components
- ❌ **No Date/Number Formatting**: Numbers and dates not localized
- ❌ **Limited Market Reach**: Cannot serve international users

**Impact**: Missing ~40% potential user base who prefer English interface

## Proposed Solution

### 1. i18n Infrastructure Setup (2 hours)
**Configuration**: `frontend/src/i18n/index.ts`

**Features**:
- react-i18next as core library
- Namespace-based translation organization
- Language detection from browser/localStorage
- Lazy loading of language bundles
- Fallback language handling

**Implementation**:
```typescript
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import Backend from 'i18next-http-backend'

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'ko',
    supportedLngs: ['ko', 'en'],
    defaultNS: 'common',
    ns: ['common', 'screener', 'stock', 'auth', 'portfolio'],
    interpolation: { escapeValue: false },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  })

export default i18n
```

### 2. Translation File Structure (3 hours)
**Directory Structure**:
```
frontend/src/
├── i18n/
│   ├── index.ts              # i18n configuration
│   └── locales/
│       ├── ko/
│       │   ├── common.json   # Common UI strings
│       │   ├── screener.json # Screener page strings
│       │   ├── stock.json    # Stock detail strings
│       │   ├── auth.json     # Authentication strings
│       │   └── portfolio.json # Portfolio strings
│       └── en/
│           ├── common.json
│           ├── screener.json
│           ├── stock.json
│           ├── auth.json
│           └── portfolio.json
```

**Example Translation Files**:
```json
// ko/common.json
{
  "nav": {
    "home": "홈",
    "screener": "스크리너",
    "portfolio": "포트폴리오",
    "watchlist": "관심종목",
    "login": "로그인",
    "signup": "회원가입",
    "logout": "로그아웃"
  },
  "actions": {
    "save": "저장",
    "cancel": "취소",
    "delete": "삭제",
    "edit": "수정",
    "search": "검색",
    "filter": "필터",
    "export": "내보내기",
    "refresh": "새로고침"
  },
  "status": {
    "loading": "로딩 중...",
    "error": "오류가 발생했습니다",
    "noData": "데이터가 없습니다",
    "success": "성공"
  }
}

// en/common.json
{
  "nav": {
    "home": "Home",
    "screener": "Screener",
    "portfolio": "Portfolio",
    "watchlist": "Watchlist",
    "login": "Login",
    "signup": "Sign Up",
    "logout": "Logout"
  },
  "actions": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "search": "Search",
    "filter": "Filter",
    "export": "Export",
    "refresh": "Refresh"
  },
  "status": {
    "loading": "Loading...",
    "error": "An error occurred",
    "noData": "No data available",
    "success": "Success"
  }
}
```

### 3. Language Switcher Component (2 hours)
**Component**: `frontend/src/components/common/LanguageSwitcher.tsx`

**Features**:
- Dropdown or toggle for language selection
- Current language indicator
- Persists preference to localStorage
- Accessible with keyboard navigation

**Implementation**:
```tsx
import { useTranslation } from 'react-i18next'

const LANGUAGES = [
  { code: 'ko', name: '한국어', flag: '🇰🇷' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
]

export function LanguageSwitcher() {
  const { i18n } = useTranslation()

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng)
  }

  return (
    <select
      value={i18n.language}
      onChange={(e) => changeLanguage(e.target.value)}
      className="language-select"
    >
      {LANGUAGES.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.flag} {lang.name}
        </option>
      ))}
    </select>
  )
}
```

### 4. Locale-aware Formatting (2 hours)
**Utilities**: `frontend/src/utils/formatters.ts`

**Features**:
- Number formatting (1,234.56 vs 1.234,56)
- Currency formatting (₩ vs $)
- Date formatting (YYYY년 MM월 DD일 vs MM/DD/YYYY)
- Percentage formatting

**Implementation**:
```typescript
import { useTranslation } from 'react-i18next'

export function useFormatters() {
  const { i18n } = useTranslation()
  const locale = i18n.language === 'ko' ? 'ko-KR' : 'en-US'

  return {
    formatNumber: (value: number) =>
      new Intl.NumberFormat(locale).format(value),

    formatCurrency: (value: number, currency = 'KRW') =>
      new Intl.NumberFormat(locale, {
        style: 'currency',
        currency
      }).format(value),

    formatDate: (date: Date) =>
      new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }).format(date),

    formatPercent: (value: number) =>
      new Intl.NumberFormat(locale, {
        style: 'percent',
        minimumFractionDigits: 2,
      }).format(value / 100),
  }
}
```

### 5. Component Integration (3 hours)
**Key Pages to Translate**:
- Navbar component
- Screener page (filters, results table headers)
- Stock detail page (tabs, sections)
- Authentication pages (login, signup forms)
- Portfolio page (holdings, transactions)

## Subtasks

### Phase A: Infrastructure Setup (2 hours)
- [ ] Install react-i18next and dependencies
- [ ] Create i18n configuration file
- [ ] Set up language detection
- [ ] Create translation file structure
- [ ] Add i18n provider to App

### Phase B: Translation Files (3 hours)
- [ ] Create Korean translation files (common, screener, stock, auth, portfolio)
- [ ] Create English translation files
- [ ] Review and verify translation accuracy
- [ ] Add type definitions for translation keys

### Phase C: Language Switcher (2 hours)
- [ ] Create LanguageSwitcher component
- [ ] Add to Navbar
- [ ] Style for desktop and mobile
- [ ] Test language switching
- [ ] Verify localStorage persistence

### Phase D: Formatters (2 hours)
- [ ] Create useFormatters hook
- [ ] Implement number formatting
- [ ] Implement currency formatting
- [ ] Implement date formatting
- [ ] Implement percentage formatting
- [ ] Update components to use formatters

### Phase E: Component Integration (3 hours)
- [ ] Translate Navbar
- [ ] Translate ScreenerPage
- [ ] Translate StockDetailPage
- [ ] Translate AuthPages (Login, Signup)
- [ ] Translate common components (buttons, modals, etc.)

### Phase F: Testing & Verification (2 hours)
- [ ] Unit tests for i18n hooks
- [ ] Integration tests for language switching
- [ ] Visual verification in both languages
- [ ] Build verification
- [ ] Documentation

## Acceptance Criteria

- [ ] **Language Support**
  - [ ] Korean is default language
  - [ ] English fully translated
  - [ ] Language persists across sessions
  - [ ] All user-facing text translated

- [ ] **Language Switcher**
  - [ ] Visible in Navbar
  - [ ] Switches language immediately
  - [ ] Shows current language
  - [ ] Accessible via keyboard

- [ ] **Formatting**
  - [ ] Numbers formatted per locale
  - [ ] Dates formatted per locale
  - [ ] Currency formatted per locale
  - [ ] Percentages formatted per locale

- [ ] **Performance**
  - [ ] Lazy loading of language bundles
  - [ ] No flicker on initial load
  - [ ] Bundle size increase < 20KB

- [ ] **Testing**
  - [ ] All unit tests pass
  - [ ] Language switching tested
  - [ ] Formatters tested

## Dependencies
- 📦 `react-i18next` ^14.0.0
- 📦 `i18next` ^23.0.0
- 📦 `i18next-browser-languagedetector` ^7.0.0
- 📦 `i18next-http-backend` ^2.0.0 (optional, for lazy loading)

## Technical Considerations

### Translation Key Convention
- Use dot notation: `namespace.section.key`
- Example: `screener.filters.marketCap`
- Keep keys lowercase with camelCase

### Handling Dynamic Values
```tsx
// With variables
t('stock.priceChange', { value: 5.2, direction: 'up' })
// Translation: "주가가 {{direction}} {{value}}% 변동했습니다"
```

### Pluralization
```tsx
// With count
t('portfolio.holdings', { count: stocks.length })
// ko: "{{count}}개 종목 보유"
// en: "{{count}} stock(s) held"
```

## Testing Strategy

### Unit Tests
- i18n initialization
- Translation key existence
- Formatter functions
- Language switching

### Integration Tests
- Language persistence
- Component rendering in both languages
- Formatter integration

### Manual Tests
- Visual verification of all pages
- Check for untranslated strings
- Verify text overflow handling

## Progress
**Current Status**: 0% (Not Started)

## Notes
- Start with common namespace to cover shared UI elements
- Consider adding more languages in future (Japanese, Chinese)
- Some financial terms may not have direct translations - use glossary
- Stock names remain in original language (Korean company names)

## References
- [react-i18next Documentation](https://react.i18next.com/)
- [i18next Documentation](https://www.i18next.com/)
- [Intl API](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl)
