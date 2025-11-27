# TECH-DEBT-009: Migrate ESLint to v9 Flat Config Format

## Metadata
- **Status**: DONE
- **Priority**: Medium
- **Assignee**: Claude
- **Estimated Time**: 2-3 hours
- **Actual Time**: 2.5 hours
- **Sprint**: Phase 5 (Quality)
- **Tags**: frontend, tooling, eslint, configuration
- **Completed**: 2025-11-27

## Description

ESLint v9.39.1 requires a new flat configuration format (`eslint.config.js`) instead of the legacy `.eslintrc.*` files. The current configuration is outdated and causes ESLint to fail with configuration errors.

**Current Error:**
```
ESLint couldn't find an eslint.config.(js|mjs|cjs) file.
From ESLint v9.0.0, the default configuration file is now eslint.config.js.
```

## Subtasks

- [x] Review current `.eslintrc.*` configuration
- [x] Create new `eslint.config.js` using flat config format
- [x] Migrate all rules and plugins to new format
- [x] Update `.eslintignore` patterns to `ignores` property
- [x] Configure TypeScript-ESLint for flat config
- [x] Configure React and React Hooks plugins
- [x] Test linting on all source files
- [x] Remove legacy `.eslintrc.*` and `.eslintignore` files
- [x] Update `package.json` lint script if needed
- [x] Verify CI/CD pipeline passes

## Acceptance Criteria

1. ✅ `npm run lint` executes without configuration errors
2. ✅ All existing lint rules are preserved
3. ✅ TypeScript files are properly linted
4. ✅ React/JSX files are properly linted
5. ✅ No regressions in code quality checks
6. ✅ CI/CD pipeline passes lint checks

## Implementation Details

### Changes Made

1. **Created `eslint.config.js`** with flat config format:
   - Used `typescript-eslint` package for TypeScript support
   - Configured React and React Hooks plugins
   - Set up proper ignores for dist, node_modules, config files
   - Preserved all existing rules

2. **Installed new dependencies**:
   - `@eslint/js` - ESLint recommended rules for flat config
   - `globals` - Global variable definitions
   - `typescript-eslint` - TypeScript-ESLint flat config support

3. **Removed legacy files**:
   - `.eslintrc.json`
   - `.eslintignore`

4. **Updated `package.json`**:
   - Changed lint script from `eslint . --ext js,jsx,ts,tsx` to `eslint .`
   - Added `lint:fix` script

5. **Disabled new React Hooks v7.0.0 experimental rules**:
   - `react-hooks/purity`
   - `react-hooks/set-state-in-effect`
   - `react-hooks/static-components`
   - `react-hooks/react-compiler`
   - `react-hooks/incompatible-library`

6. **Fixed React Hooks rules-of-hooks violations**:
   - DashboardPage.tsx - moved useEffect before conditional return
   - PortfolioDetailPage.tsx - moved useEffect before conditional return
   - PortfolioListPage.tsx - moved useEffect before conditional return

### Final Results

- **Lint**: 0 errors, 104 warnings
- **TypeScript**: No errors
- **Tests**: 577 passed (30 files)

## Dependencies
- None (standalone task)

## Blocks
- None

## Progress
- [x] 100% - Complete

## Notes
- New react-hooks v7.0.0 includes experimental React Compiler rules that were disabled for compatibility
- Fixed 3 actual rules-of-hooks violations (useEffect after conditional return)
- Added `varsIgnorePattern: '^_'` to no-unused-vars rule for consistent underscore prefix pattern
