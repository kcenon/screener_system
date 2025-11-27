# Security Audit Report - November 11, 2025

## Executive Summary

Security audit performed on stock screening platform dependencies to identify and resolve known vulnerabilities.

**Audit Date**: 2025-11-11
**Audit Scope**: Frontend (Node.js/npm) and Backend (Python) dependencies
**Total Vulnerabilities Found**: 24 (6 frontend, 18 backend)
**Total Vulnerabilities Fixed**: 23 (6 frontend, 17 backend)
**Status**: ✅ **Complete**

---

## Frontend Dependencies (Node.js/npm)

### Audit Results

```bash
$ npm audit
```

**Summary**:
- **Total**: 6 moderate severity vulnerabilities
- **Critical**: 0
- **High**: 0
- **Moderate**: 6
- **Low**: 0

### Vulnerabilities Detail

#### 1. esbuild <=0.24.2 (GHSA-67mh-4wv8-2f99)
- **Severity**: Moderate
- **Package**: esbuild
- **Current Version**: 0.21.5 (transitive dependency via vite)
- **Vulnerable Range**: <=0.24.2
- **CVE**: GHSA-67mh-4wv8-2f99
- **Description**: esbuild enables any website to send any requests to the development server and read the response
- **Impact**: Development environment only
- **Fix**: Update vite to 7.2.2+ (which includes esbuild >0.24.2)

#### 2-6. Transitive Dependencies (vite, vite-node, vitest, @vitest/coverage-v8, @vitest/ui)
- **Severity**: Moderate (all depend on vulnerable esbuild)
- **Current Versions**:
  - vite: 5.4.21
  - vitest: 1.6.1
  - @vitest/coverage-v8: 1.6.1
  - @vitest/ui: 1.6.1
- **Latest Versions**:
  - vite: 7.2.2
  - vitest: 4.0.8
  - @vitest/coverage-v8: 4.0.8
  - @vitest/ui: 4.0.8
- **Fix**: Major version upgrade (breaking changes expected)

### Dependency Tree

```
vite@5.4.21
└── esbuild@0.21.5 (VULNERABLE)

vitest@1.6.1
├── vite-node@1.6.1
│   └── vite@5.4.21
│       └── esbuild@0.21.5 (VULNERABLE)
└── vite@5.4.21 (deduped)

@vitest/coverage-v8@1.6.1
└── vitest@1.6.1 (depends on vulnerable vite)

@vitest/ui@1.6.1
└── vitest@1.6.1 (depends on vulnerable vite)
```

---

## Backend Dependencies (Python)

### Audit Status

**Tool**: safety / pip-audit
**Status**: Unable to run automated scan (PATH issues in Docker container)
**Manual Review**: Pending

### Known Package Versions

```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1
aiohttp==3.9.1
python-jose==3.3.0
bcrypt==4.1.2
celery==5.4.0
pandas==2.1.3
numpy==1.26.2
httpx==0.25.2
sentry-sdk==1.38.0
pytest==7.4.3
```

**Action Required**: Set up automated Python security scanning in CI/CD pipeline

---

## Remediation Plan

### Phase 1: Frontend Security Updates (IMMEDIATE)

#### Step 1.1: Update Build Tools
```bash
npm install vite@latest @vitejs/plugin-react@latest
npm install -D vitest@latest @vitest/coverage-v8@latest @vitest/ui@latest
```

#### Step 1.2: Verify Build
```bash
npm run build
npm run test
```

#### Step 1.3: Test Application
- Verify development server starts
- Verify production build succeeds
- Verify all unit tests pass
- Verify UI functionality intact

#### Expected Breaking Changes
1. **Vite 5→7**:
   - Config API changes
   - Plugin compatibility
   - Build output structure
2. **Vitest 1→4**:
   - Test configuration updates
   - Coverage reporter changes
   - Assertions API changes

### Phase 2: Backend Security Setup (NEXT)

#### Step 2.1: Add Python Security Scanner
```dockerfile
# Add to backend/Dockerfile
RUN pip install safety pip-audit
```

#### Step 2.2: Run Security Audit
```bash
docker exec screener_backend pip-audit
docker exec screener_backend safety check
```

#### Step 2.3: Update Vulnerable Packages
- Review audit results
- Update packages to safe versions
- Test application functionality

### Phase 3: Automated Security Scanning (ONGOING)

#### Step 3.1: Enable Dependabot
Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

#### Step 3.2: Add Security Scanning to CI/CD
Update `.github/workflows/security.yml`:
```yaml
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  npm-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: npm audit
        run: |
          cd frontend
          npm audit --audit-level=moderate

  python-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install security tools
        run: |
          pip install safety pip-audit
      - name: Run pip-audit
        run: |
          cd backend
          pip-audit -r requirements.txt
```

---

## Risk Assessment

### Current Risk Level: **MODERATE**

**Factors**:
1. ✅ **Production Impact**: NONE (esbuild vulnerability only affects dev environment)
2. ⚠️ **Developer Risk**: MODERATE (potential for dev machine compromise)
3. ⚠️ **CI/CD Risk**: MODERATE (build servers could be targeted)
4. ✅ **Data Risk**: NONE (no data-layer vulnerabilities found)

### Deployment Recommendation

**Current State**: ✅ **SAFE TO DEPLOY**
- Production builds do not include esbuild or development server
- Vulnerabilities are dev-dependency only
- No runtime security issues detected

**Post-Update State**: ⚡ **IMPROVED SECURITY POSTURE**
- All known vulnerabilities resolved
- Automated scanning prevents future issues
- Reduced attack surface

---

## Timeline

| Phase | Task | Estimated Time | Status |
|-------|------|----------------|--------|
| 1.1 | Frontend dependency updates | 30 min | ✅ Complete |
| 1.2 | Frontend testing | 30 min | ✅ Complete |
| 1.3 | Frontend verification | 15 min | ✅ Complete |
| 2.1 | Backend security scanner setup | 15 min | ✅ Complete |
| 2.2 | Backend security audit | 15 min | ✅ Complete |
| 2.3 | Backend updates | 1 hour | ✅ Complete |
| 3.1 | Dependabot configuration | 15 min | ✅ Complete |
| 3.2 | CI/CD security workflow | 30 min | ✅ Complete |
| **Total** | **End-to-end security hardening** | **3 hours** | **100%** ✅ |

---

## References

- **esbuild Advisory**: https://github.com/advisories/GHSA-67mh-4wv8-2f99
- **Vite Security**: https://vitejs.dev/guide/migration
- **npm audit docs**: https://docs.npmjs.com/cli/v8/commands/npm-audit
- **OWASP Dependency Check**: https://owasp.org/www-project-dependency-check/
- **Python safety**: https://pypi.org/project/safety/
- **pip-audit**: https://pypi.org/project/pip-audit/

---

## Final Results Summary

### Frontend Updates ✅

| Package | Old Version | New Version | Vulnerabilities Fixed |
|---------|-------------|-------------|----------------------|
| vite | 5.4.21 | 7.2.2 | 6 (transitive via esbuild) |
| vitest | 1.6.1 | 4.0.8 | (dependency of vite) |
| @vitest/coverage-v8 | 1.6.1 | 4.0.8 | (dependency of vite) |
| @vitest/ui | 1.6.1 | 4.0.8 | (dependency of vite) |
| esbuild | 0.21.5 | 0.25.12 | GHSA-67mh-4wv8-2f99 |

**Test Results**: ✅ 139 tests passed, build successful

### Backend Updates ✅

| Package | Old Version | New Version | Vulnerabilities Fixed |
|---------|-------------|-------------|----------------------|
| aiohttp | 3.9.1 | 3.11.14 | 6 CVEs (directory traversal, XSS, DoS, request smuggling) |
| fastapi | 0.104.1 | 0.115.6 | PYSEC-2024-38 (ReDoS) |
| gunicorn | 21.2.0 | 22.0.0 | 2 (request smuggling) |
| python-jose | 3.3.0 | 3.4.0 | 2 (algorithm confusion, JWT bomb) |
| python-multipart | 0.0.6 | 0.0.20 | 2 (ReDoS) |
| sentry-sdk | 1.38.0 | 2.22.0 | GHSA-g92j-qhmh-64v2 (env exposure) |
| black | 23.12.0 | 24.10.0 | PYSEC-2024-48 (ReDoS) |
| starlette | 0.27.0 | 0.41.3 | 2 (DoS via form data) |

**Test Results**: ✅ 258 tests passed, 77% coverage maintained

### Automation Configured ✅

1. **Dependabot** (`.github/dependabot.yml`):
   - Weekly npm dependency updates (frontend)
   - Weekly pip dependency updates (backend, data pipeline)
   - Monthly GitHub Actions updates
   - Monthly Docker base image updates
   - Auto-grouping of minor/patch updates
   - Automatic PR creation with security labels

2. **Security Scanning** (`.github/workflows/security.yml`):
   - Runs on every push to main/develop
   - Runs on every pull request
   - Weekly scheduled scans (Mondays 9:00 AM KST)
   - Manual trigger available
   - Scans frontend (npm audit)
   - Scans backend (pip-audit)
   - Scans data pipeline (pip-audit)
   - Secret scanning with Gitleaks
   - Fails CI if high/critical vulnerabilities found
   - Generates security summary in GitHub Actions

### Known Issues Remaining

**ecdsa 0.19.1 - Minerva Timing Attack**:
- Severity: Moderate
- Status: No fix available (maintainers consider out of scope)
- Risk: LOW-MODERATE (side-channel attack requires precise timing)
- Mitigation: Documented in `SECURITY_NOTES.md`
- Action: Monitor for python-jose updates that might switch crypto library

---

## Software Bill of Materials (SBOM)

### Overview

The Stock Screening Platform generates Software Bill of Materials (SBOM) in CycloneDX v1.5 format for supply chain security and regulatory compliance.

### SBOM Status

| Component | Status | Tool |
|-----------|--------|------|
| Frontend (npm) | ✅ Implemented | `@cyclonedx/cyclonedx-npm` |
| Backend (Python) | ✅ Implemented | `cyclonedx-bom` |
| Data Pipeline (Python) | ✅ Implemented | `cyclonedx-bom` |
| CI/CD Integration | ✅ Implemented | GitHub Actions |
| Vulnerability Scanning | ✅ Implemented | Grype |

### Generated SBOMs

- `sbom-frontend.json` - Frontend npm dependencies
- `sbom-backend.json` - Backend Python dependencies
- `sbom-datapipeline.json` - Data Pipeline Python dependencies
- `sbom-complete.json` - Merged SBOM with all components

### CI/CD Integration

SBOMs are automatically generated:
- **On Release**: Attached to GitHub releases as artifacts
- **Manual Trigger**: Via `gh workflow run sbom.yml`

### Local Generation

```bash
# Generate all SBOMs
./scripts/generate-sbom.sh

# Output directory: ./sbom/
```

### Vulnerability Scanning

SBOMs are scanned for vulnerabilities using Grype:

```bash
# Scan locally
grype sbom:sbom/sbom-complete.json
```

### Compliance

This SBOM implementation supports:
- US Executive Order 14028
- NTIA SBOM Minimum Elements
- EU Cyber Resilience Act
- PCI DSS 4.0

### Documentation

Full SBOM documentation available in [docs/SBOM.md](./SBOM.md)

---

**Report Generated**: 2025-11-11
**SBOM Implementation**: 2025-11-27
**Completion Date**: 2025-11-27
**Next Review**: 2026-02-11 (quarterly or when Dependabot alerts trigger)
**Auditor**: Development Team
**Status**: ✅ **All Critical and High Vulnerabilities Resolved**
