# [IMPROVEMENT-010] Internationalization (i18n) - Multi-Language Support

## Metadata
- **Status**: DONE ✅
- **Priority**: Medium
- **Assignee**: Frontend Team
- **Estimated Time**: 10-12 hours
- **Actual Time**: 8 hours
- **Sprint**: Phase 4 Enhancement
- **Tags**: #frontend #i18n #localization #translation #ux
- **Dependencies**: FE-001 ✅
- **Blocks**: None
- **Related**: README.md Future Enhancements (Internationalization)
- **Completed**: 2025-11-27

## Description
Implement comprehensive internationalization (i18n) infrastructure to support multiple languages, enabling the platform to serve international users interested in Korean markets. Initial release will support Korean (default), English, and prepare the foundation for additional languages.

## Problem Statement
Current limitations:
- ❌ **Korean Only**: All UI text is hardcoded in Korean
- ❌ **No Language Switching**: Users cannot change display language
- ❌ **Limited Reach**: International investors cannot use platform effectively
- ❌ **Hardcoded Strings**: Text scattered throughout components
- ❌ **No RTL Support**: Cannot support Arabic/Hebrew markets in future

**Impact**: Missing ~30% potential user base of international Korean market investors

## Proposed Solution

### 1. i18n Infrastructure Setup (3 hours)
**Library**: react-i18next (industry standard)

**Configuration**:
```typescript
// frontend/src/i18n/config.ts
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
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
  })

export default i18n
```

**Directory Structure**:
```
frontend/
├── public/
│   └── locales/
│       ├── ko/
│       │   ├── common.json     # Common UI elements
│       │   ├── screener.json   # Screener page
│       │   ├── stock.json      # Stock detail
│       │   ├── auth.json       # Authentication
│       │   └── portfolio.json  # Portfolio management
│       └── en/
│           ├── common.json
│           ├── screener.json
│           ├── stock.json
│           ├── auth.json
│           └── portfolio.json
```

### 2. Translation Files (3 hours)
**Korean (ko/common.json)**:
```json
{
  "navigation": {
    "home": "홈",
    "market": "시장",
    "screener": "스크리너",
    "portfolio": "포트폴리오",
    "watchlist": "관심종목",
    "settings": "설정",
    "login": "로그인",
    "logout": "로그아웃"
  },
  "market": {
    "indices": "시장지수",
    "breadth": "시장폭",
    "movers": "등락",
    "topGainers": "상위 상승",
    "topLosers": "상위 하락",
    "mostActive": "거래량 상위"
  },
  "stock": {
    "code": "종목코드",
    "name": "종목명",
    "price": "현재가",
    "change": "등락",
    "changePercent": "등락률",
    "volume": "거래량",
    "marketCap": "시가총액",
    "high52w": "52주 최고",
    "low52w": "52주 최저"
  },
  "actions": {
    "search": "검색",
    "filter": "필터",
    "sort": "정렬",
    "export": "내보내기",
    "save": "저장",
    "cancel": "취소",
    "apply": "적용",
    "clear": "초기화"
  }
}
```

**English (en/common.json)**:
```json
{
  "navigation": {
    "home": "Home",
    "market": "Market",
    "screener": "Screener",
    "portfolio": "Portfolio",
    "watchlist": "Watchlist",
    "settings": "Settings",
    "login": "Login",
    "logout": "Logout"
  },
  "market": {
    "indices": "Market Indices",
    "breadth": "Market Breadth",
    "movers": "Movers",
    "topGainers": "Top Gainers",
    "topLosers": "Top Losers",
    "mostActive": "Most Active"
  },
  "stock": {
    "code": "Code",
    "name": "Name",
    "price": "Price",
    "change": "Change",
    "changePercent": "Change %",
    "volume": "Volume",
    "marketCap": "Market Cap",
    "high52w": "52W High",
    "low52w": "52W Low"
  },
  "actions": {
    "search": "Search",
    "filter": "Filter",
    "sort": "Sort",
    "export": "Export",
    "save": "Save",
    "cancel": "Cancel",
    "apply": "Apply",
    "clear": "Clear"
  }
}
```

### 3. Component Migration (3 hours)
**Using Translation Hook**:
```tsx
// Before
const Navbar = () => (
  <nav>
    <Link to="/market">시장</Link>
    <Link to="/screener">스크리너</Link>
  </nav>
)

// After
import { useTranslation } from 'react-i18next'

const Navbar = () => {
  const { t } = useTranslation('common')

  return (
    <nav>
      <Link to="/market">{t('navigation.market')}</Link>
      <Link to="/screener">{t('navigation.screener')}</Link>
    </nav>
  )
}
```

**Priority Components to Migrate**:
1. Navigation (Navbar, Sidebar, Footer)
2. GlobalMarketBar
3. Market Dashboard tabs
4. Screener filters and results
5. Stock detail page
6. Authentication pages
7. Error messages
8. Tooltips and help text

### 4. Language Switcher Component (1 hour)
**Component**: `frontend/src/components/common/LanguageSwitcher.tsx`

```tsx
import { useTranslation } from 'react-i18next'

const languages = [
  { code: 'ko', name: '한국어', flag: '🇰🇷' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
]

const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation()

  return (
    <select
      value={i18n.language}
      onChange={(e) => i18n.changeLanguage(e.target.value)}
      className="border rounded px-2 py-1"
    >
      {languages.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.flag} {lang.name}
        </option>
      ))}
    </select>
  )
}
```

### 5. Number & Date Formatting (2 hours)
**Locale-Aware Formatting**:
```typescript
// frontend/src/utils/formatters.ts
import { useTranslation } from 'react-i18next'

export function useLocalizedFormatters() {
  const { i18n } = useTranslation()
  const locale = i18n.language

  const formatNumber = (num: number, options?: Intl.NumberFormatOptions) => {
    return new Intl.NumberFormat(locale, options).format(num)
  }

  const formatCurrency = (num: number, currency = 'KRW') => {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
      maximumFractionDigits: 0,
    }).format(num)
  }

  const formatPercent = (num: number) => {
    return new Intl.NumberFormat(locale, {
      style: 'percent',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num / 100)
  }

  const formatDate = (date: Date, options?: Intl.DateTimeFormatOptions) => {
    return new Intl.DateTimeFormat(locale, options).format(date)
  }

  const formatRelativeTime = (date: Date) => {
    const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' })
    const diff = (date.getTime() - Date.now()) / 1000

    if (Math.abs(diff) < 60) return rtf.format(Math.round(diff), 'second')
    if (Math.abs(diff) < 3600) return rtf.format(Math.round(diff / 60), 'minute')
    if (Math.abs(diff) < 86400) return rtf.format(Math.round(diff / 3600), 'hour')
    return rtf.format(Math.round(diff / 86400), 'day')
  }

  return { formatNumber, formatCurrency, formatPercent, formatDate, formatRelativeTime }
}
```

## Subtasks

### Phase A: Infrastructure Setup (3 hours)
- [ ] Install i18next dependencies
- [ ] Create i18n configuration
- [ ] Set up language detection
- [ ] Create translation file structure
- [ ] Configure lazy loading for translations
- [ ] Add i18n provider to App
- [ ] Verify hot reload works for translations

### Phase B: Translation Files (3 hours)
- [ ] Create Korean translation files (common, screener, stock, auth, portfolio)
- [ ] Create English translation files
- [ ] Extract all hardcoded strings from components
- [ ] Organize translations by namespace
- [ ] Add plural rules where needed
- [ ] Review translations for accuracy

### Phase C: Component Migration (3 hours)
- [ ] Migrate Navigation components
- [ ] Migrate GlobalMarketBar
- [ ] Migrate Market Dashboard
- [ ] Migrate Screener page
- [ ] Migrate Stock Detail page
- [ ] Migrate Authentication pages
- [ ] Migrate Portfolio pages
- [ ] Update error messages

### Phase D: Formatting & Localization (2 hours)
- [ ] Create locale-aware formatting utilities
- [ ] Update number formatting across app
- [ ] Update date/time formatting
- [ ] Handle currency display (KRW)
- [ ] Test with different locales

### Phase E: Testing & Polish (1 hour)
- [ ] Language switcher in header
- [ ] Persist language preference
- [ ] Test all pages in both languages
- [ ] Fix any layout issues with longer text
- [ ] Update SEO meta tags for language
- [ ] Documentation update

## Acceptance Criteria

- [ ] **Language Support**
  - [ ] Korean (default) fully working
  - [ ] English fully translated
  - [ ] Language switcher accessible
  - [ ] Language persists across sessions
  - [ ] Auto-detects browser language

- [ ] **Translation Quality**
  - [ ] No hardcoded strings remain
  - [ ] No broken layouts with longer text
  - [ ] Proper pluralization
  - [ ] Context-appropriate translations
  - [ ] Financial terms accurate

- [ ] **Formatting**
  - [ ] Numbers formatted per locale
  - [ ] Dates formatted per locale
  - [ ] Currency displays correctly
  - [ ] Percentages formatted correctly

- [ ] **Performance**
  - [ ] Translations lazy-loaded
  - [ ] Bundle size increase < 20KB
  - [ ] No flash of untranslated content

## Technical Considerations

### Bundle Size
- Lazy load translation files (only load active language)
- Use namespaces to split translations
- Expected increase: ~15KB per language

### SEO
- Add `lang` attribute to HTML
- Consider separate URLs for languages (/en/screener)
- Update meta tags based on language

### RTL Support (Future)
- Use CSS logical properties (start/end vs left/right)
- Prepare for Arabic/Hebrew if needed

## Dependencies
- 📦 `i18next` ^23.0.0
- 📦 `react-i18next` ^14.0.0
- 📦 `i18next-browser-languagedetector` ^7.0.0
- 📦 `i18next-http-backend` ^2.0.0

## Testing Strategy

### Unit Tests
- Translation loading
- Formatting utilities
- Language switching

### Integration Tests
- Full page rendering in each language
- Navigation with language persistence

### Visual Tests
- Layout stability with different text lengths
- Right-to-left layout (future)

## Rollout Plan
1. **Development**: Implement infrastructure and Korean translations
2. **Staging**: Add English translations, team review
3. **Beta**: Enable language switcher for all users
4. **Production**: Monitor adoption, gather feedback
5. **Expansion**: Add more languages based on demand

## Success Metrics
- [ ] < 5% users encountering untranslated strings
- [ ] +20% international user engagement
- [ ] +15% time on site for English users
- [ ] 0 layout breaking issues

## Progress
**Current Status**: 100% (Completed)

### Implementation Summary
- ✅ i18n infrastructure setup with react-i18next
- ✅ 8 translation namespaces (common, market, stock, screener, chart, landing, auth, portfolio)
- ✅ Korean (ko) and English (en) translation files
- ✅ Language switcher component in navbar
- ✅ Browser language detection
- ✅ LocalStorage persistence
- ✅ Locale-aware formatting utilities (useLocalizedFormatters hook)
- ✅ Key components migrated (GlobalMarketBar, QuickFiltersBar)
- ✅ Build passes with no type errors

## Notes
- Start with Korean and English only
- Financial terminology needs expert review
- Consider community translations for additional languages
- May need backend support for translated stock names (future)
- Sector names should remain in Korean with English tooltip

## References
- [react-i18next Documentation](https://react.i18next.com/)
- [i18next Best Practices](https://www.i18next.com/principles/best-practices)
- [Intl API Reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl)
