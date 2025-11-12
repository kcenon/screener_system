# CI/CD Documentation Deployment Setup

This document describes the automated documentation build and deployment pipeline for the Stock Screening Platform.

## Overview

The documentation system automatically builds and deploys to GitHub Pages whenever changes are pushed to the `main` branch. The pipeline includes:

1. **Sphinx Documentation** - Python API documentation from backend
2. **TypeDoc Documentation** - TypeScript API documentation from frontend
3. **Docusaurus Site** - Main documentation platform
4. **GitHub Pages** - Hosting at https://docs.screener.kr

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Push (main)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions Workflow                         │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ Build Sphinx   │  │ Build TypeDoc  │  │ Build        │  │
│  │ (Python API)   │  │ (Frontend API) │  │ Docusaurus   │  │
│  └───────┬────────┘  └───────┬────────┘  └──────┬───────┘  │
│          │                   │                   │          │
│          └───────────────────┴───────────────────┘          │
│                              │                              │
│                              ▼                              │
│                  ┌───────────────────────┐                  │
│                  │ Deploy to GitHub Pages│                  │
│                  └───────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │  https://docs.screener.kr │
                  └───────────────────────┘
```

## Workflow Configuration

### File Location
`.github/workflows/docs.yml`

### Trigger Events
- **Push to main branch** with changes to:
  - `docs/**`
  - `frontend/src/**`
  - `backend/app/**`
  - `docs-site/**`
  - `.github/workflows/docs.yml`
- **Manual trigger** via GitHub Actions UI

### Build Steps

#### 1. Sphinx Documentation (Python API)
```bash
cd docs/api/python
sphinx-build -b html -W --keep-going . _build/html
```

**Output**: `docs-site/build/api/backend/`

#### 2. TypeDoc Documentation (Frontend API)
```bash
cd frontend
npm run docs:generate
```

**Output**: `docs-site/docs/api/frontend/` (configured in `frontend/typedoc.json`)

#### 3. Docusaurus Build
```bash
cd docs-site
npm run build
```

**Output**: `docs-site/build/`

#### 4. GitHub Pages Deployment
Uses `actions/deploy-pages@v4` to deploy `docs-site/build/` to GitHub Pages.

## Performance Optimizations

### Dependency Caching
The workflow caches dependencies to speed up builds:

```yaml
- Node.js packages: docs-site/package-lock.json, frontend/package-lock.json
- Python packages: requirements-docs.txt
```

**Expected Savings**: 30-60 seconds per build

### Build Parallelization
Where possible, independent steps run in parallel through GitHub Actions' natural workflow execution.

### Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Total build time | < 3 minutes | TBD |
| Sphinx build | < 30 seconds | TBD |
| TypeDoc build | < 20 seconds | TBD |
| Docusaurus build | < 90 seconds | TBD |
| Deployment time | < 30 seconds | TBD |

## GitHub Pages Configuration

### Repository Settings Required

1. **Enable GitHub Pages**
   - Go to: `Settings → Pages`
   - Source: `GitHub Actions`
   - Custom domain: `docs.screener.kr`
   - Enforce HTTPS: ✓

2. **Workflow Permissions**
   - Go to: `Settings → Actions → General → Workflow permissions`
   - Select: `Read and write permissions`
   - Enable: `Allow GitHub Actions to create and approve pull requests`

3. **Environments**
   - Automatically created: `github-pages`
   - Protection rules can be added if needed

### DNS Configuration

At your domain provider, add a CNAME record:

```
Type: CNAME
Name: docs
Value: kcenon.github.io
TTL: 3600
```

**Note**: DNS propagation may take up to 24 hours.

### SSL Certificate

GitHub automatically provisions an SSL certificate for custom domains. This typically takes 24-48 hours after DNS configuration.

## Verification

### Check Workflow Status

```bash
# List recent workflow runs
gh run list --workflow=docs.yml

# View specific run details
gh run view <run-id> --log

# Watch a running workflow
gh run watch
```

### Test Deployment

```bash
# Check if site is accessible
curl -I https://docs.screener.kr

# Verify SSL certificate
curl -vI https://docs.screener.kr 2>&1 | grep "SSL certificate"

# Check GitHub Pages status
gh api repos/kcenon/screener_system/pages
```

### Manual Trigger

```bash
# Trigger workflow manually
gh workflow run docs.yml

# Or via GitHub UI:
# Actions → Deploy Documentation to GitHub Pages → Run workflow
```

## Troubleshooting

### Build Failures

#### Sphinx Build Fails
**Symptom**: Import errors, module not found

**Solutions**:
1. Verify Python dependencies in `requirements-docs.txt`
2. Check that backend modules are importable
3. Review Sphinx configuration in `docs/api/python/conf.py`

```bash
# Test locally
cd docs/api/python
sphinx-build -b html . _build/html
```

#### TypeDoc Build Fails
**Symptom**: TypeScript compilation errors

**Solutions**:
1. Check TypeScript compilation: `cd frontend && npx tsc --noEmit`
2. Verify `frontend/typedoc.json` configuration
3. Check for TypeScript errors in source files

```bash
# Test locally
cd frontend
npm run docs:generate
```

#### Docusaurus Build Fails
**Symptom**: MDX syntax errors, broken links

**Solutions**:
1. Check for MDX syntax errors: `cd docs-site && npm run build -- --debug`
2. Review broken links in output
3. Known issue: TypeDoc MDX compatibility (see DOC-008)

```bash
# Test locally
cd docs-site
npm run build
```

### Deployment Failures

#### Permission Denied
**Symptom**: `Error: Resource not accessible by integration`

**Solution**: Check workflow permissions in repository settings:
- Settings → Actions → General → Workflow permissions
- Enable "Read and write permissions"

#### Custom Domain Not Working
**Symptom**: Site loads at `kcenon.github.io/screener_system` but not `docs.screener.kr`

**Solutions**:
1. Verify CNAME file exists: `docs-site/static/CNAME`
2. Check DNS configuration: `dig docs.screener.kr`
3. Wait for DNS propagation (up to 24 hours)
4. Verify custom domain in GitHub Pages settings

#### SSL Certificate Issues
**Symptom**: SSL certificate not valid or not found

**Solutions**:
1. Wait 24-48 hours for GitHub to provision certificate
2. Ensure "Enforce HTTPS" is enabled in Pages settings
3. Check that CNAME record is correctly configured

### Performance Issues

#### Slow Builds
**Solutions**:
1. Check that caching is working (look for cache hit/miss in logs)
2. Profile individual build steps to identify bottlenecks
3. Consider splitting documentation into multiple workflows if needed

## Monitoring

### Build Status Badge

Add to `README.md`:

```markdown
[![Documentation](https://img.shields.io/badge/docs-live-success)](https://docs.screener.kr)
[![Deploy Docs](https://github.com/kcenon/screener_system/actions/workflows/docs.yml/badge.svg)](https://github.com/kcenon/screener_system/actions/workflows/docs.yml)
```

### Notifications

GitHub Actions automatically sends notifications for workflow failures to:
- Workflow author
- Commit author
- Repository watchers (if configured)

Configure additional notifications in repository settings:
- Settings → Notifications → Actions

### Deployment History

View deployment history:
- Repository → Environments → github-pages
- Shows all deployments with timestamps and commit links

## Cost

| Component | Cost | Notes |
|-----------|------|-------|
| GitHub Actions | $0 | 2,000 minutes/month free for public repos |
| GitHub Pages | $0 | Unlimited bandwidth for public repos |
| Storage | $0 | Unlimited for documentation sites |
| SSL Certificate | $0 | Auto-managed by GitHub |
| **Total** | **$0/month** | Completely free for open source |

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Docusaurus Deployment Guide](https://docusaurus.io/docs/deployment#deploying-to-github-pages)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [TypeDoc Documentation](https://typedoc.org/)

## Known Issues

### TypeDoc MDX Compatibility (DOC-008)
TypeDoc-generated Markdown contains comparison operators (`<=`, `>=`) that conflict with Docusaurus MDX parser.

**Status**: Tracked in ticket DOC-008
**Workaround**: Documentation is accessible but Docusaurus build may fail
**Resolution**: Planned for DOC-008 implementation

## Maintenance

### Regular Tasks
- Review build times monthly and optimize if needed
- Update workflow versions quarterly
- Monitor GitHub Actions minutes usage
- Test manual deployment rollback procedure

### Updating Workflow
1. Make changes to `.github/workflows/docs.yml`
2. Test on feature branch first
3. Review workflow run logs
4. Merge to main only after successful test

### Emergency Rollback
If a deployment breaks the documentation site:

```bash
# Revert to previous deployment
gh workflow run docs.yml --ref <previous-commit-sha>

# Or manually trigger workflow from previous commit via GitHub UI
```

## Support

For issues with documentation deployment:
1. Check workflow logs: `gh run list --workflow=docs.yml`
2. Review troubleshooting section above
3. Create issue with `documentation` and `ci/cd` labels
4. Contact repository maintainers

---

**Last Updated**: 2025-11-12
**Workflow Version**: 1.0.0
**Status**: Active
