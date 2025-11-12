# Documentation Migration Plan

## Overview

This document outlines the plan to migrate existing documentation from `docs/` to the unified Docusaurus documentation site at `docs-site/docs/`.

**Created**: 2025-11-13
**Ticket**: DOC-004
**Estimated Effort**: 6 hours

## Current State Analysis

### Documentation Inventory

**Total Files**: 97 markdown files in docs/
**Total Size**: ~500KB of documentation

#### Large Documents (Require Splitting)

| File | Lines | Size | Target Location |
|------|-------|------|-----------------|
| SDS.md | 4,702 | 147KB | `specifications/` (split into sections) |
| PRD.md | 2,521 | 98KB | `specifications/` (split into sections) |
| SRS.md | 1,732 | 69KB | `specifications/` (split into sections) |

#### Medium Documents

| File | Lines | Size | Target Location |
|------|-------|------|-----------------|
| PROJECT_SCHEDULE.md | 1,190 | 42KB | `project/schedule.md` |
| VERIFICATION_REPORT.md | 1,132 | 37KB | `operations/verification.md` |
| VALIDATION_REPORT.md | 1,126 | 43KB | `operations/validation.md` |
| TESTING.md | 1,108 | 23KB | `guides/developer/testing.md` |

#### Guide Documents

| File | Lines | Size | Target Location |
|------|-------|------|-----------------|
| WEBSOCKET_API.md | 590 | 12KB | `api/websocket-api.md` |
| DEPLOYMENT_GUIDE.md | 444 | 11KB | `guides/deployment/overview.md` |
| PERFORMANCE_BASELINE.md | 443 | 12KB | `operations/performance.md` |
| CI_CD_SETUP.md | 356 | 11KB | `guides/deployment/cicd.md` |
| DATA_LOADING.md | 372 | 8KB | `guides/developer/data-loading.md` |
| SECURITY_AUDIT.md | 342 | 9KB | `operations/security.md` |
| AIRFLOW_VALIDATION.md | 403 | 11KB | `operations/airflow-validation.md` |
| CICD_VALIDATION.md | 386 | 11KB | `operations/cicd-validation.md` |

#### Special Folders

| Folder | Files | Purpose | Target |
|--------|-------|---------|--------|
| docs/api/ | 1 | API documentation | `api/` |
| docs/data_pipeline/ | 2 | Pipeline verification docs | `operations/data-pipeline/` |
| docs/database/ | 2 | DB verification docs | `operations/database/` |
| docs/contributing/ | 1 | TSDoc templates | `contributing/` |
| docs/reviews/ | 12 | Code review documents | Keep in docs/reviews/ (not migrated) |
| docs/kanban/ | 66 | Ticket management | Keep in docs/kanban/ (not migrated) |

### Current docs-site Structure

```
docs-site/docs/
├── getting-started/
│   └── index.md (placeholder)
├── api/
│   ├── intro.md (placeholder)
│   ├── python.mdx (backend API - auto-generated)
│   ├── backend/
│   │   └── intro.md (placeholder)
│   └── frontend/ (full TypeDoc - auto-generated)
├── guides/
│   └── intro.md (placeholder)
├── architecture/
│   └── overview.md (placeholder)
├── contributing/
│   └── intro.md (placeholder)
└── tutorial-basics/ (Docusaurus default - to be removed)
```

## Target Structure

```
docs-site/docs/
├── 01-getting-started/
│   ├── index.md                          # Quick start guide
│   ├── installation.md                   # Local setup
│   ├── architecture-overview.md          # High-level architecture
│   └── project-structure.md              # Codebase tour
│
├── 02-guides/
│   ├── user/
│   │   ├── screening.md                  # How to use screener
│   │   ├── stock-detail.md               # Stock detail features
│   │   └── watchlist.md                  # Watchlist features
│   ├── developer/
│   │   ├── local-development.md          # Dev environment setup
│   │   ├── testing.md                    # FROM: TESTING.md
│   │   ├── data-loading.md               # FROM: DATA_LOADING.md
│   │   ├── debugging.md                  # Debugging tips
│   │   └── contributing.md               # Contribution guidelines
│   └── deployment/
│       ├── overview.md                   # FROM: DEPLOYMENT_GUIDE.md
│       ├── docker.md                     # Docker deployment
│       ├── kubernetes.md                 # K8s deployment
│       └── cicd.md                       # FROM: CI_CD_SETUP.md
│
├── 03-api-reference/
│   ├── intro.md                          # API overview
│   ├── rest-api.md                       # REST API guide
│   ├── websocket-api.md                  # FROM: WEBSOCKET_API.md
│   ├── rate-limiting.md                  # FROM: docs/api/RATE_LIMITING.md
│   ├── backend/
│   │   └── (Sphinx auto-generated)
│   └── frontend/
│       └── (TypeDoc auto-generated)
│
├── 04-architecture/
│   ├── overview.md                       # System architecture
│   ├── backend.md                        # FROM: SDS.md (Backend section)
│   ├── frontend.md                       # FROM: SDS.md (Frontend section)
│   ├── database.md                       # FROM: SDS.md (Database section)
│   ├── data-pipeline.md                  # FROM: SDS.md (Pipeline section)
│   ├── security.md                       # FROM: SDS.md (Security section)
│   └── performance.md                    # FROM: SDS.md (Performance section)
│
├── 05-specifications/
│   ├── prd/
│   │   ├── index.md                      # FROM: PRD.md (intro)
│   │   ├── product-vision.md             # FROM: PRD.md (Vision)
│   │   ├── features.md                   # FROM: PRD.md (Features)
│   │   ├── user-stories.md               # FROM: PRD.md (User Stories)
│   │   └── requirements.md               # FROM: PRD.md (Requirements)
│   ├── srs/
│   │   ├── index.md                      # FROM: SRS.md (intro)
│   │   ├── functional.md                 # FROM: SRS.md (Functional)
│   │   └── non-functional.md             # FROM: SRS.md (Non-Functional)
│   └── sds/
│       ├── index.md                      # FROM: SDS.md (intro)
│       ├── system-architecture.md        # FROM: SDS.md (Architecture)
│       ├── data-design.md                # FROM: SDS.md (Data Design)
│       └── api-design.md                 # FROM: SDS.md (API Design)
│
├── 06-operations/
│   ├── monitoring.md                     # Monitoring guide
│   ├── performance.md                    # FROM: PERFORMANCE_BASELINE.md
│   ├── security.md                       # FROM: SECURITY_AUDIT.md
│   ├── troubleshooting.md                # Common issues
│   ├── verification.md                   # FROM: VERIFICATION_REPORT.md
│   ├── validation.md                     # FROM: VALIDATION_REPORT.md
│   ├── airflow-validation.md             # FROM: AIRFLOW_VALIDATION.md
│   ├── cicd-validation.md                # FROM: CICD_VALIDATION.md
│   ├── database/
│   │   ├── indexes-views.md              # FROM: docs/database/INDEXES_VIEWS_VERIFICATION.md
│   │   └── functions-triggers.md         # FROM: docs/database/FUNCTIONS_TRIGGERS_VERIFICATION.md
│   └── data-pipeline/
│       ├── kis-integration.md            # FROM: docs/data_pipeline/DAG_KIS_INTEGRATION.md
│       └── daily-price-dag.md            # FROM: docs/data_pipeline/DAILY_PRICE_DAG_VERIFICATION.md
│
├── 07-project/
│   ├── schedule.md                       # FROM: PROJECT_SCHEDULE.md
│   ├── roadmap.md                        # Future plans
│   └── changelog.md                      # Release notes
│
└── 08-contributing/
    ├── index.md                          # Contribution overview
    ├── code-style.md                     # Code style guide
    ├── documentation-style.md            # Doc style guide (DOC-005)
    ├── pr-process.md                     # PR guidelines
    └── tsdoc-templates.md                # FROM: docs/contributing/TSDOC_TEMPLATES.md
```

## Migration Strategy

### Phase 1: Content Audit (Completed)
✅ Cataloged all existing documentation
✅ Identified document sizes and target locations
✅ Mapped old docs to new structure

### Phase 2: Directory Structure Setup (1 hour)
- [ ] Create numbered directory structure (01- through 08-)
- [ ] Create subdirectories for each section
- [ ] Update `sidebars.ts` with new structure
- [ ] Create placeholder index files

### Phase 3: Small Documents Migration (1.5 hours)
Migrate guides and operational docs (< 600 lines):
- [ ] WEBSOCKET_API.md → api/websocket-api.md
- [ ] DATA_LOADING.md → guides/developer/data-loading.md
- [ ] DEPLOYMENT_GUIDE.md → guides/deployment/overview.md
- [ ] CI_CD_SETUP.md → guides/deployment/cicd.md
- [ ] SECURITY_AUDIT.md → operations/security.md
- [ ] PERFORMANCE_BASELINE.md → operations/performance.md
- [ ] docs/api/RATE_LIMITING.md → api/rate-limiting.md
- [ ] docs/contributing/TSDOC_TEMPLATES.md → contributing/tsdoc-templates.md

### Phase 4: Medium Documents Migration (1 hour)
Migrate reports and testing docs:
- [ ] TESTING.md → guides/developer/testing.md
- [ ] VERIFICATION_REPORT.md → operations/verification.md
- [ ] VALIDATION_REPORT.md → operations/validation.md
- [ ] PROJECT_SCHEDULE.md → project/schedule.md
- [ ] AIRFLOW_VALIDATION.md → operations/airflow-validation.md
- [ ] CICD_VALIDATION.md → operations/cicd-validation.md

### Phase 5: Large Documents Splitting (2 hours)
Split and migrate large specifications:
- [ ] PRD.md → specifications/prd/ (4 files)
- [ ] SRS.md → specifications/srs/ (3 files)
- [ ] SDS.md → specifications/sds/ (4 files) + architecture/ (6 files)

### Phase 6: Enhancement & Testing (0.5 hours)
- [ ] Add frontmatter to all migrated docs
- [ ] Update internal links
- [ ] Add admonitions (tips, warnings, notes)
- [ ] Test documentation site build
- [ ] Verify search indexing
- [ ] Test mobile responsiveness
- [ ] Check all internal links
- [ ] Verify images display correctly

## Frontmatter Template

```yaml
---
id: document-id
title: Document Title
description: Brief description for SEO and search
sidebar_label: Short Label
sidebar_position: 1
tags:
  - category
  - topic
last_updated: 2025-11-13
---
```

## Link Migration Rules

### Old Format → New Format

```diff
- [See SDS](SDS.md)
+ [See SDS](../../specifications/sds/index.md)

- [Database Schema](../database/README.md)
+ [Database Schema](../../architecture/database.md)

- [WebSocket API](WEBSOCKET_API.md)
+ [WebSocket API](../../api/websocket-api.md)
```

## Documents NOT Being Migrated

The following will remain in `docs/` directory:
- ✅ **docs/reviews/**: Code review documents (project artifacts)
- ✅ **docs/kanban/**: Ticket management (project management)
- ✅ **docs/SECURITY_NOTES.md**: Internal security notes
- ✅ **docs/SECURITY_UPDATES.md**: Security patch log
- ✅ **docs/TICKET_*.md**: Ticket audit reports

## Deprecation Strategy

After migration:
1. Add deprecation notice to old docs in `docs/`:
   ```markdown
   > ⚠️ **DEPRECATED**: This document has been migrated to the [unified documentation site](https://docs.screener.kr).
   > Please visit [new location](https://docs.screener.kr/path/to/doc) for the latest version.
   ```

2. Update main README.md to point to docs site
3. Keep old docs for 1 sprint (reference purposes)
4. Remove deprecated docs in Sprint 5

## Testing Checklist

- [ ] All documents build without errors
- [ ] No broken internal links
- [ ] No broken external links
- [ ] Images display correctly
- [ ] Code blocks have syntax highlighting
- [ ] Search finds all migrated content
- [ ] Mobile view renders properly
- [ ] Sidebar navigation is logical
- [ ] Breadcrumbs work correctly
- [ ] "Edit this page" links work

## Success Criteria

✅ All 30+ documents migrated to docs-site
✅ Large docs (PRD, SRS, SDS) split into logical sections
✅ Zero broken links
✅ Documentation site builds successfully
✅ Search indexes all content
✅ Mobile-responsive design verified
✅ Sidebar navigation is intuitive and numbered
✅ Old docs marked as deprecated with redirects

## Timeline

| Phase | Duration | Completion |
|-------|----------|------------|
| Phase 1: Audit | 1h | ✅ Complete |
| Phase 2: Structure Setup | 1h | Pending |
| Phase 3: Small Docs | 1.5h | Pending |
| Phase 4: Medium Docs | 1h | Pending |
| Phase 5: Large Docs | 2h | Pending |
| Phase 6: Enhancement | 0.5h | Pending |
| **Total** | **7h** | **In Progress** |

## Notes

- API Reference (backend/frontend) are auto-generated and remain untouched
- Tutorial-basics/ and tutorial-extras/ will be removed (Docusaurus defaults)
- All new docs use MDX format for enhanced features
- Version badges will be added to specifications
- PDF export capability will be configured for specifications
