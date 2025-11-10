# [SECURITY-001] Resolve Dependabot Security Vulnerabilities

## Metadata
- **Status**: TODO
- **Priority**: High
- **Assignee**: TBD
- **Estimated Time**: 12 hours
- **Sprint**: Sprint 2 (Week 3-4)
- **Tags**: #security #dependencies #vulnerabilities #maintenance
- **Created**: 2025-11-10
- **Severity**: 1 Critical, 10 High, 11 Medium, 4 Low (26 total open alerts)

## Description
Address 26 open security vulnerabilities detected by GitHub Dependabot across backend dependencies. This includes critical authentication vulnerabilities and multiple high-severity issues in core dependencies (Apache Airflow, aiohttp, gunicorn, python-jose).

**Security Dashboard**: https://github.com/kcenon/screener_system/security/dependabot

## Vulnerability Summary

### 🔴 Critical (1)
**Immediate action required**

| Package | Alert # | Severity | Issue | Vulnerable Version | Fixed Version |
|---------|---------|----------|-------|-------------------|---------------|
| python-jose | #11 | **CRITICAL** | Algorithm confusion with OpenSSH ECDSA keys | < 3.4.0 | ≥ 3.4.0 |

**Impact**: JWT authentication bypass, potential authentication system compromise.

---

### 🟠 High (10)
**Urgent - Address within sprint**

| Package | Alert # | Issue | Vulnerable Version | Fixed Version |
|---------|---------|-------|-------------------|---------------|
| apache-airflow | #27 | Bypass permission verification to read code | < 2.8.1rc1 | ≥ 2.8.1rc1 |
| apache-airflow | #26 | Pickle deserialization vulnerability in XComs | < 2.8.1rc1 | ≥ 2.8.1rc1 |
| apache-airflow | #25 | Execution with Unnecessary Privileges | < 2.10.1 | ≥ 2.10.1 |
| apache-airflow | #23 | DAG Author Code Execution in scheduler | 2.4.0 - 2.9.3 | ≥ 2.9.3 |
| gunicorn | #14 | HTTP Request/Response Smuggling | < 22.0.0 | ≥ 22.0.0 |
| gunicorn | #5 | Request smuggling leading to endpoint bypass | < 22.0.0 | ≥ 22.0.0 |
| python-multipart | #9 | DoS via deformation multipart/form-data boundary | < 0.0.18 | ≥ 0.0.18 |
| python-multipart | #3 | Content-Type Header ReDoS | ≤ 0.0.6 | > 0.0.6 |
| aiohttp | #7 | DoS when parsing malformed POST requests | < 3.9.4 | ≥ 3.9.4 |
| aiohttp | #2 | Directory traversal vulnerability | 1.0.5 - 3.9.2 | ≥ 3.9.2 |

**Impact**: Remote code execution, privilege escalation, DoS attacks, authentication bypass.

---

### 🟡 Medium (11)

| Package | Alert # | Issue | Vulnerable Version | Fixed Version |
|---------|---------|-------|-------------------|---------------|
| apache-airflow | #24 | Cross-site Scripting Vulnerability | < 2.10.0 | ≥ 2.10.0 |
| apache-airflow | #22 | Potential XSS Vulnerability | < 2.9.3 | ≥ 2.9.3 |
| apache-airflow | #19 | Sensitive config displayed (non-sensitive-only) | 2.7.0 - 2.9.0 | ≥ 2.9.0 |
| apache-airflow | #18 | Ignored Airflow Permission | 2.8.0 - 2.8.3rc1 | ≥ 2.8.3rc1 |
| apache-airflow | #17 | Incorrect Default Permissions in audit logs | < 2.8.2 | ≥ 2.8.2 |
| apache-airflow | #16 | DAG Code and Import Error Permissions Ignored | ≤ 2.8.1 | > 2.8.1 |
| python-jose | #10 | Denial of service via compressed JWE content | < 3.4.0 | ≥ 3.4.0 |
| aiohttp | #8 | Request smuggling (incorrect chunk parsing) | ≤ 3.10.10 | > 3.10.10 |
| aiohttp | #6 | XSS on index pages for static file handling | < 3.9.4 | ≥ 3.9.4 |
| aiohttp | #1 | HTTP parser overly lenient about separators | < 3.9.2 | ≥ 3.9.2 |
| black | #4 | Regular Expression DoS (ReDoS) | < 24.3.0 | ≥ 24.3.0 |

**Impact**: XSS attacks, information disclosure, permission bypass, DoS.

---

### 🟢 Low (4)

| Package | Alert # | Issue | Vulnerable Version | Fixed Version |
|---------|---------|-------|-------------------|---------------|
| apache-airflow | #28 | Insertion of Sensitive Information Into Sent Data | < 2.10.3 | ≥ 2.10.3 |
| apache-airflow | #21 | Missing Cache-Control header for dynamic content | < 2.9.2 | ≥ 2.9.2 |
| aiohttp | #13 | HTTP Request/Response Smuggling (chunked trailer) | < 3.12.14 | ≥ 3.12.14 |
| sentry-sdk | #12 | Environment variables exposed to subprocesses | < 1.45.1 | ≥ 1.45.1 |

**Impact**: Information leakage, security header weaknesses.

---

## Subtasks

### Phase 1: Critical & High Priority (Immediate)
- [ ] **Critical: python-jose upgrade**
  - [ ] Update python-jose from current to ≥ 3.4.0
  - [ ] Test JWT authentication thoroughly
  - [ ] Verify ECDSA key handling
  - [ ] Run security regression tests

- [ ] **High: Apache Airflow upgrade**
  - [ ] Check current Airflow version (likely 2.8.0)
  - [ ] Plan upgrade to Airflow 2.10.3 (latest stable)
  - [ ] Review breaking changes (2.8 → 2.10)
  - [ ] Update DAG code if needed
  - [ ] Test all existing DAGs
  - [ ] Verify XCom functionality
  - [ ] Test permission system

- [ ] **High: gunicorn upgrade**
  - [ ] Update gunicorn from current to ≥ 22.0.0
  - [ ] Test backend API under load
  - [ ] Verify request/response handling

- [ ] **High: python-multipart upgrade**
  - [ ] Update to ≥ 0.0.18
  - [ ] Test file upload functionality
  - [ ] Verify multipart/form-data parsing

- [ ] **High: aiohttp upgrade**
  - [ ] Update to ≥ 3.12.14 (latest)
  - [ ] Test async HTTP operations
  - [ ] Verify WebSocket functionality (if used)

### Phase 2: Medium Priority (This Sprint)
- [ ] **Medium: Remaining Apache Airflow issues**
  - [ ] Verify all medium-severity issues resolved with 2.10.3 upgrade

- [ ] **Medium: black upgrade**
  - [ ] Update black to ≥ 24.3.0
  - [ ] Run code formatting
  - [ ] Commit any formatting changes

- [ ] **Medium: Remaining aiohttp issues**
  - [ ] Verify all issues resolved with latest version

### Phase 3: Low Priority (Sprint 3)
- [ ] **Low: sentry-sdk upgrade**
  - [ ] Update to ≥ 1.45.1
  - [ ] Test error reporting

- [ ] **Low: Verify all low-severity issues**
  - [ ] Confirm all alerts resolved

### Phase 4: Verification & Testing
- [ ] **Dependency Testing**
  - [ ] Run full test suite (pytest)
  - [ ] Run integration tests
  - [ ] Test all affected features:
    - [ ] JWT authentication (python-jose)
    - [ ] Airflow DAGs (apache-airflow)
    - [ ] API endpoints (gunicorn, aiohttp)
    - [ ] File uploads (python-multipart)
    - [ ] Error tracking (sentry-sdk)

- [ ] **Security Verification**
  - [ ] Re-scan with Dependabot
  - [ ] Verify all 26 alerts resolved
  - [ ] Run security audit: `pip audit`
  - [ ] Check for new vulnerabilities

- [ ] **Documentation**
  - [ ] Update requirements.txt
  - [ ] Document upgrade notes
  - [ ] Update CHANGELOG.md

## Acceptance Criteria
- [ ] **All 26 Dependabot alerts resolved**
  - [ ] 1 Critical alert fixed
  - [ ] 10 High alerts fixed
  - [ ] 11 Medium alerts fixed
  - [ ] 4 Low alerts fixed

- [ ] **Zero regressions**
  - [ ] All existing tests passing
  - [ ] No functionality broken
  - [ ] Performance maintained or improved

- [ ] **Dependencies updated**
  - [ ] requirements.txt updated
  - [ ] package-lock.json updated (if frontend affected)
  - [ ] All dependency conflicts resolved

- [ ] **Documentation complete**
  - [ ] Upgrade notes documented
  - [ ] Breaking changes documented
  - [ ] Security improvements noted

## Dependencies
- **Depends on**: None (independent security work)
- **Blocks**: Production deployment, security audit
- **Related**: All BE and DP tickets (affects all backend code)

## References
- **GitHub Security Dashboard**: https://github.com/kcenon/screener_system/security/dependabot
- **Dependabot Docs**: https://docs.github.com/en/code-security/dependabot
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/

### Package-Specific References
- **python-jose**: https://github.com/mpdavis/python-jose/security/advisories
- **Apache Airflow**: https://airflow.apache.org/docs/apache-airflow/stable/security/index.html
- **gunicorn**: https://docs.gunicorn.org/en/stable/news.html
- **aiohttp**: https://docs.aiohttp.org/en/stable/security.html

## Progress
- **0%** - Not started

## Notes

### Upgrade Strategy
1. **Create separate branch**: `feature/SECURITY-001-dependency-upgrades`
2. **Upgrade in phases**: Critical → High → Medium → Low
3. **Test after each phase**: Don't batch all upgrades
4. **Commit per package**: Easier to rollback if issues arise

### Risk Assessment
- **python-jose (Critical)**: Low risk - straightforward upgrade, well-tested
- **Apache Airflow (High)**: Medium risk - major version jump (2.8 → 2.10)
  - Requires DAG review
  - May have breaking changes
  - Test thoroughly
- **gunicorn (High)**: Low risk - production-stable upgrade
- **aiohttp (High)**: Low risk - async code already tested
- **python-multipart (High)**: Low risk - used in FastAPI, well-tested

### Rollback Plan
If any upgrade causes issues:
1. Revert specific commit
2. Pin problematic package to working version
3. Create issue ticket for deeper investigation
4. Proceed with other upgrades

### Testing Requirements
- **Unit tests**: All existing tests must pass
- **Integration tests**: API endpoints functional
- **Performance tests**: No performance regression
- **Security tests**:
  - JWT authentication working
  - Permission system functional
  - File uploads secure

### Estimated Time Breakdown
- **Phase 1 (Critical/High)**: 6 hours
  - python-jose: 1h
  - Apache Airflow: 3h (includes testing)
  - gunicorn: 0.5h
  - python-multipart: 0.5h
  - aiohttp: 1h
- **Phase 2 (Medium)**: 3 hours
- **Phase 3 (Low)**: 1 hour
- **Phase 4 (Testing)**: 2 hours
- **Total**: 12 hours

### Post-Upgrade Actions
- [ ] Enable Dependabot auto-updates for security patches
- [ ] Set up automated security scanning in CI/CD
- [ ] Schedule quarterly dependency review
- [ ] Document dependency upgrade process

## Security Impact Assessment

### Before Upgrade
- ⚠️ **Authentication vulnerability** (python-jose)
- ⚠️ **Remote code execution risk** (Apache Airflow)
- ⚠️ **Request smuggling risk** (gunicorn)
- ⚠️ **DoS vulnerability** (aiohttp, python-multipart)

### After Upgrade
- ✅ **Secure authentication** (python-jose 3.4.0+)
- ✅ **Protected DAG execution** (Airflow 2.10.3+)
- ✅ **Secure request handling** (gunicorn 22.0.0+)
- ✅ **DoS protection** (latest aiohttp, python-multipart)

---

**⚠️ IMPORTANT**: This ticket should be prioritized alongside feature development. Security vulnerabilities, especially Critical and High severity, should not wait until all features are complete.

**Recommended Action**: Start Phase 1 (Critical/High) immediately, complete within current sprint.
