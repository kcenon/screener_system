---
id: changelog-template
title: Changelog Template
description: Template for maintaining project changelog
sidebar_label: Changelog Template
sidebar_position: 5
tags:
  - template
  - changelog
  - releases
---

# Changelog Template

Use this template to maintain a changelog file following [Keep a Changelog](https://keepachangelog.com/) principles.

---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features that have been added but not yet released
- Use bullet points for each change
- Link to relevant PR or issue: [#123](https://github.com/org/repo/pull/123)

### Changed
- Changes in existing functionality
- Breaking changes should be clearly marked with **BREAKING**

### Deprecated
- Features that will be removed in upcoming releases
- Include migration guide if applicable

### Removed
- Features that have been removed
- Include date when deprecation was announced

### Fixed
- Bug fixes
- Include issue number: Fixes [#456](https://github.com/org/repo/issues/456)

### Security
- Security vulnerability fixes
- Use CVE numbers when applicable

## [1.0.0] - 2025-11-13

### Added
- Initial release of Stock Screening Platform
- User authentication with JWT tokens ([#10](https://github.com/org/repo/pull/10))
- Stock screening with 200+ indicators ([#15](https://github.com/org/repo/pull/15))
- Real-time price updates via WebSocket ([#20](https://github.com/org/repo/pull/20))
- Portfolio tracking and performance analytics ([#25](https://github.com/org/repo/pull/25))
- Price alert notifications ([#30](https://github.com/org/repo/pull/30))
- REST API with OpenAPI documentation ([#35](https://github.com/org/repo/pull/35))
- Docker Compose development environment ([#40](https://github.com/org/repo/pull/40))
- CI/CD pipeline with GitHub Actions ([#45](https://github.com/org/repo/pull/45))
- Comprehensive test suite (80% coverage) ([#50](https://github.com/org/repo/pull/50))

### Changed
- Migrated from SQLite to PostgreSQL with TimescaleDB ([#55](https://github.com/org/repo/pull/55))
- Updated React to version 18 ([#60](https://github.com/org/repo/pull/60))
- Improved screening query performance by 45% ([#65](https://github.com/org/repo/pull/65))

### Fixed
- Fixed SQL injection vulnerability in screening API ([#70](https://github.com/org/repo/issues/70))
- Resolved memory leak in WebSocket connections ([#75](https://github.com/org/repo/issues/75))
- Corrected calculation error in RSI indicator ([#80](https://github.com/org/repo/issues/80))

### Security
- Updated dependencies to address vulnerabilities:
  - `fastapi` 0.100.0 → 0.104.1 (CVE-2023-XXXXX)
  - `react` 18.2.0 → 18.2.1

## [0.9.0] - 2025-10-15 (Beta Release)

### Added
- Beta launch with core screening functionality
- 50 technical indicators available
- Basic user authentication
- Stock detail pages with charts

### Fixed
- Resolved login session timeout issues ([#40](https://github.com/org/repo/issues/40))
- Fixed chart rendering on mobile devices ([#42](https://github.com/org/repo/issues/42))

## [0.5.0] - 2025-09-01 (Alpha Release)

### Added
- Alpha release for internal testing
- Basic stock listing and search
- 20 fundamental indicators
- Simple filtering interface

### Known Issues
- Performance degrades with >1000 stocks
- WebSocket connections occasionally drop
- Mobile layout needs improvement

## [0.1.0] - 2025-08-01 (Internal Preview)

### Added
- Initial project setup
- Database schema design
- Basic API structure
- Frontend prototype

---

## Version Format

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

## Change Categories

Use these categories in order:

1. **Added**: New features
2. **Changed**: Changes in existing functionality
3. **Deprecated**: Soon-to-be removed features
4. **Removed**: Removed features
5. **Fixed**: Bug fixes
6. **Security**: Vulnerability fixes

## Writing Guidelines

### Good Examples

✅ **Specific and actionable:**
```markdown
### Added
- Added pagination to stock listing API with `limit` and `offset` parameters ([#123](link))
```

✅ **User-focused:**
```markdown
### Fixed
- Fixed issue where portfolio performance chart showed incorrect data for multi-year holdings ([#456](link))
```

✅ **Breaking changes clearly marked:**
```markdown
### Changed
- **BREAKING**: Renamed `/api/stocks/search` endpoint to `/api/v2/stocks` for consistency ([#789](link))
  - Migration: Update all API calls to use new endpoint
  - Old endpoint will be removed in v2.0.0
```

### Bad Examples

❌ **Too vague:**
```markdown
### Changed
- Updated some dependencies
- Improved performance
```

❌ **Technical jargon without context:**
```markdown
### Fixed
- Refactored AbstractFactoryBuilder to use Strategy pattern
```

❌ **No references:**
```markdown
### Added
- New feature
```

## Linking

Always link to:
- **Pull Requests**: For implementations
- **Issues**: For bug fixes
- **Documentation**: For major features
- **Migration Guides**: For breaking changes

Format: `([#123](https://github.com/org/repo/pull/123))`

## Release Process

1. **Update Unreleased Section**: As changes merge
2. **Create Release**: When ready to release
   - Move "Unreleased" items to new version section
   - Add release date
   - Create git tag
3. **Publish**: Release notes and artifacts
4. **Announce**: Team communication

## Template for New Version

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Feature description ([#PR](link))

### Changed
- Change description ([#PR](link))

### Deprecated
- Deprecation description with migration path

### Removed
- Removal description

### Fixed
- Bug fix description ([#Issue](link))

### Security
- Security fix description (CVE-YYYY-XXXXX)
```

## Breaking Changes

Always include migration guide for breaking changes:

```markdown
### Changed
- **BREAKING**: Authentication now requires API key in header instead of query parameter ([#100](link))

  **Migration Guide:**
  ```diff
  - GET /api/stocks?api_key=xxx
  + GET /api/stocks
  + Header: X-API-Key: xxx
  ```

  **Timeline:**
  - v1.5.0: Both methods supported (current)
  - v2.0.0: Query parameter method removed (2026-01-01)
```

## See Also

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Last Updated:** [Date]
**Maintained By:** Release Team
