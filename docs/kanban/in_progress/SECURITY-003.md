# SECURITY-003: Implement SBOM (Software Bill of Materials) Generation

**Status**: IN_PROGRESS
**Priority**: P1 (High - Security & Compliance)
**Type**: Security Enhancement
**Assignee**: Development Team
**Created**: 2025-11-27
**Estimated Time**: 6-8 hours
**Sprint**: Post-MVP Enhancement

---

## Summary

Implement automated Software Bill of Materials (SBOM) generation for supply chain security and regulatory compliance. Generate SBOM in CycloneDX format for all components (Frontend, Backend, Data Pipeline, Docker images).

---

## Background

### Why SBOM?

1. **Regulatory Compliance**
   - US Executive Order 14028 (May 2021) mandates SBOM for federal software
   - EU Cyber Resilience Act requires SBOM for products sold in EU
   - PCI DSS 4.0 recommends software inventory management

2. **Supply Chain Security**
   - Log4Shell (CVE-2021-44228) demonstrated need for dependency visibility
   - Enables rapid vulnerability impact assessment
   - Provides full dependency chain transparency

3. **Customer Requirements**
   - Enterprise customers increasingly require SBOM delivery
   - Security audits expect software component documentation

### Current State

| Component | Vulnerability Scan | SBOM Generation |
|-----------|-------------------|-----------------|
| Frontend (npm) | ✅ npm audit | ❌ Not implemented |
| Backend (Python) | ✅ pip-audit | ❌ Not implemented |
| Data Pipeline | ✅ pip-audit | ❌ Not implemented |
| Docker Images | ❌ None | ❌ Not implemented |

---

## Technical Details

### SBOM Standard Selection

**Selected**: CycloneDX v1.5

| Standard | Pros | Cons |
|----------|------|------|
| **CycloneDX** | Lightweight, CI/CD focused, better tooling | Less adoption in government |
| SPDX | ISO standard, government preferred | More complex, larger files |

**Rationale**: CycloneDX offers better integration with modern CI/CD pipelines and has excellent tooling support for our tech stack.

### Tools Selection

| Component | Tool | Output |
|-----------|------|--------|
| Frontend (npm) | `@cyclonedx/cyclonedx-npm` | `sbom-frontend.json` |
| Backend (Python) | `cyclonedx-py` | `sbom-backend.json` |
| Data Pipeline | `cyclonedx-py` | `sbom-datapipeline.json` |
| Docker Images | `syft` (Anchore) | `sbom-docker-*.json` |
| Merged SBOM | `cyclonedx-cli` | `sbom-complete.json` |

---

## Implementation

### Subtasks

#### 1. Tool Installation and Configuration (1h)
- [ ] Add `@cyclonedx/cyclonedx-npm` to frontend devDependencies
- [ ] Add `cyclonedx-bom` to backend dev requirements
- [ ] Add `cyclonedx-bom` to data_pipeline dev requirements
- [ ] Install `syft` for Docker image scanning
- [ ] Create SBOM output directory structure

#### 2. Local SBOM Generation Scripts (2h)
- [ ] Create `scripts/generate-sbom.sh` master script
- [ ] Create frontend SBOM generation script
- [ ] Create backend SBOM generation script
- [ ] Create data pipeline SBOM generation script
- [ ] Create Docker image SBOM generation script
- [ ] Create SBOM merge script for complete inventory

#### 3. CI/CD Integration (2h)
- [ ] Create `.github/workflows/sbom.yml` workflow
- [ ] Generate SBOM on every release tag
- [ ] Attach SBOM artifacts to GitHub releases
- [ ] Upload SBOM to artifact storage
- [ ] Add SBOM generation to security workflow

#### 4. Vulnerability Integration (1h)
- [ ] Configure `grype` for SBOM-based vulnerability scanning
- [ ] Add vulnerability scan step after SBOM generation
- [ ] Create alerts for new vulnerabilities in SBOM

#### 5. Documentation (1h)
- [ ] Document SBOM generation process
- [ ] Add SBOM section to SECURITY_AUDIT.md
- [ ] Create SBOM FAQ for customers
- [ ] Update CI/CD documentation

#### 6. Testing and Validation (1h)
- [ ] Verify SBOM format compliance
- [ ] Validate SBOM completeness
- [ ] Test CI/CD workflow
- [ ] Verify GitHub release attachment

---

## Files to Create/Modify

### New Files
```
scripts/
├── generate-sbom.sh           # Master SBOM generation script
├── sbom/
│   ├── generate-frontend.sh   # Frontend SBOM script
│   ├── generate-backend.sh    # Backend SBOM script
│   ├── generate-pipeline.sh   # Data pipeline SBOM script
│   ├── generate-docker.sh     # Docker image SBOM script
│   └── merge-sbom.sh          # SBOM merge script

.github/workflows/
└── sbom.yml                   # SBOM generation workflow

docs/
└── SBOM.md                    # SBOM documentation
```

### Modified Files
```
frontend/package.json          # Add cyclonedx-npm devDependency
backend/requirements-dev.txt   # Add cyclonedx-bom
data_pipeline/requirements-dev.txt  # Add cyclonedx-bom
.github/workflows/cd.yml       # Add SBOM to release workflow
docs/SECURITY_AUDIT.md         # Add SBOM section
```

---

## CI/CD Workflow Design

```yaml
# .github/workflows/sbom.yml
name: Generate SBOM

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  generate-sbom:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Generate Frontend SBOM
        run: npx @cyclonedx/cyclonedx-npm --output-file sbom-frontend.json
        working-directory: frontend

      - name: Generate Backend SBOM
        run: cyclonedx-py -r requirements.txt -o sbom-backend.json
        working-directory: backend

      - name: Generate Docker SBOM
        uses: anchore/sbom-action@v0
        with:
          image: ${{ env.DOCKER_IMAGE }}
          format: cyclonedx-json
          output-file: sbom-docker.json

      - name: Merge SBOMs
        run: cyclonedx merge --input-files sbom-*.json --output-file sbom-complete.json

      - name: Upload SBOM to Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            sbom-complete.json
            sbom-frontend.json
            sbom-backend.json
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] SBOM generated for all components (frontend, backend, data pipeline)
- [ ] SBOM includes all direct and transitive dependencies
- [ ] SBOM follows CycloneDX v1.5 specification
- [ ] SBOM attached to every GitHub release
- [ ] Manual SBOM generation available via script

### Quality Requirements
- [ ] SBOM passes CycloneDX schema validation
- [ ] SBOM generation completes in < 5 minutes
- [ ] No sensitive data (secrets, internal paths) in SBOM
- [ ] SBOM includes component licenses
- [ ] SBOM includes component hashes (SHA-256)

### Documentation Requirements
- [ ] SBOM generation process documented
- [ ] CI/CD workflow documented
- [ ] Customer FAQ available

---

## Verification Plan

### 1. Schema Validation
```bash
# Validate CycloneDX format
cyclonedx validate --input-file sbom-complete.json
```

### 2. Completeness Check
```bash
# Count components vs known dependencies
npm ls --all --json | jq '.dependencies | length'
cat sbom-frontend.json | jq '.components | length'
```

### 3. Vulnerability Scan
```bash
# Scan SBOM for vulnerabilities
grype sbom:sbom-complete.json
```

### 4. CI/CD Test
- [ ] Trigger workflow manually
- [ ] Verify artifact upload
- [ ] Check release attachment

---

## Dependencies

### Blocking
- None (independent feature)

### Blocked By
- None

---

## Risk Assessment

### Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Tool incompatibility | Low | Medium | Test tools locally first |
| CI/CD timeout | Low | Low | Optimize parallel execution |
| Large SBOM file size | Medium | Low | Use minified JSON format |

### Security Considerations
- SBOM may expose internal dependency structure
- Ensure no secrets included in SBOM
- Consider private vs public SBOM distribution

---

## References

- [CycloneDX Specification](https://cyclonedx.org/specification/overview/)
- [NTIA SBOM Minimum Elements](https://www.ntia.gov/page/software-bill-materials)
- [US Executive Order 14028](https://www.whitehouse.gov/briefing-room/presidential-actions/2021/05/12/executive-order-on-improving-the-nations-cybersecurity/)
- [OWASP SBOM Guide](https://owasp.org/www-project-dependency-track/)
- [Anchore Syft](https://github.com/anchore/syft)
- [CycloneDX Python Tool](https://github.com/CycloneDX/cyclonedx-python)

---

## Success Metrics

| Metric | Target |
|--------|--------|
| SBOM Coverage | 100% of components |
| Generation Time | < 5 minutes |
| Schema Compliance | 100% valid |
| Release Attachment | Every release |

---

**Estimated Effort**: 6-8 hours
**Priority Justification**: Supply chain security is critical for enterprise adoption and regulatory compliance
**Branch**: `feature/security-003-sbom`
**PR Target**: `main`
