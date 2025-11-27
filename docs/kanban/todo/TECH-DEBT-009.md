# TECH-DEBT-009: Migrate ESLint to v9 Flat Config Format

## Metadata
- **Status**: TODO
- **Priority**: Medium
- **Assignee**: TBD
- **Estimated Time**: 2-3 hours
- **Sprint**: Phase 5 (Quality)
- **Tags**: frontend, tooling, eslint, configuration

## Description

ESLint v9.39.1 requires a new flat configuration format (`eslint.config.js`) instead of the legacy `.eslintrc.*` files. The current configuration is outdated and causes ESLint to fail with configuration errors.

**Current Error:**
```
ESLint couldn't find an eslint.config.(js|mjs|cjs) file.
From ESLint v9.0.0, the default configuration file is now eslint.config.js.
```

## Subtasks

- [ ] Review current `.eslintrc.*` configuration
- [ ] Create new `eslint.config.js` using flat config format
- [ ] Migrate all rules and plugins to new format
- [ ] Update `.eslintignore` patterns to `ignores` property
- [ ] Configure TypeScript-ESLint for flat config
- [ ] Configure React and React Hooks plugins
- [ ] Test linting on all source files
- [ ] Remove legacy `.eslintrc.*` and `.eslintignore` files
- [ ] Update `package.json` lint script if needed
- [ ] Verify CI/CD pipeline passes

## Acceptance Criteria

1. `npm run lint` executes without configuration errors
2. All existing lint rules are preserved
3. TypeScript files are properly linted
4. React/JSX files are properly linted
5. No regressions in code quality checks
6. CI/CD pipeline passes lint checks

## Technical Details

### Migration Steps

1. **Install @eslint/js**:
   ```bash
   npm install @eslint/js --save-dev
   ```

2. **Create eslint.config.js**:
   ```javascript
   import js from '@eslint/js';
   import typescript from '@typescript-eslint/eslint-plugin';
   import tsParser from '@typescript-eslint/parser';
   import react from 'eslint-plugin-react';
   import reactHooks from 'eslint-plugin-react-hooks';

   export default [
     js.configs.recommended,
     {
       files: ['**/*.{ts,tsx}'],
       languageOptions: {
         parser: tsParser,
         parserOptions: {
           ecmaVersion: 'latest',
           sourceType: 'module',
         },
       },
       plugins: {
         '@typescript-eslint': typescript,
         'react': react,
         'react-hooks': reactHooks,
       },
       rules: {
         // Migrate existing rules here
       },
     },
     {
       ignores: ['dist/**', 'node_modules/**', '*.config.js'],
     },
   ];
   ```

### Reference
- [ESLint v9 Migration Guide](https://eslint.org/docs/latest/use/configure/migration-guide)
- [TypeScript ESLint Flat Config](https://typescript-eslint.io/getting-started)

## Dependencies
- None (standalone task)

## Blocks
- None

## Progress
- [ ] 0% - Not started

## Notes
- This is a tooling improvement that does not affect runtime behavior
- Consider also updating to latest ESLint plugin versions during migration
- Test thoroughly as rule behavior may differ slightly in new format
