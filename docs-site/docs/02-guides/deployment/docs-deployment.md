---
id: docs-deployment
title: Documentation Deployment Guide
description: Complete guide for deploying the documentation site to GitHub Pages with automatic CI/CD
sidebar_label: Docs Deployment
sidebar_position: 1
tags:
  - deployment
  - github-pages
  - docusaurus
  - ci-cd
last_updated: 2025-11-13
---

# Documentation Deployment Guide

This guide covers the deployment of the Stock Screening Platform documentation site to GitHub Pages.

## Overview

The documentation site is automatically built and deployed to GitHub Pages at **https://docs.screener.kr** whenever changes are pushed to the `main` branch.

:::info Automated Deployment
The entire deployment process is automated through GitHub Actions. You typically don't need to deploy manually unless troubleshooting issues.
:::

### Architecture

```
GitHub Repository (main branch)
    ↓ (push trigger)
GitHub Actions Workflow (.github/workflows/docs.yml)
    ↓ (build process)
Build Documentation
    ├─ Sphinx (Python API docs) → docs-site/build/api/backend/
    ├─ TypeDoc (TypeScript API docs) → docs-site/docs/api/frontend/
    └─ Docusaurus (main site) → docs-site/build/
    ↓ (deploy)
GitHub Pages (gh-pages branch)
    ↓ (serve via CDN)
https://docs.screener.kr
```

## Deployment Configuration

### 1. GitHub Pages Settings

#### Enable GitHub Pages

1. Navigate to repository **Settings** → **Pages**
2. Configure the following:
   - **Source**: Deploy from a branch
   - **Branch**: `gh-pages`
   - **Folder**: `/` (root)
   - **Enforce HTTPS**: ✅ Enabled

:::warning HTTPS Required
Always enforce HTTPS to ensure secure access to documentation and prevent man-in-the-middle attacks.
:::

#### Custom Domain Setup

1. In GitHub Pages settings, add custom domain: `docs.screener.kr`
2. Wait for DNS check to complete (may take up to 24 hours)
3. Enable "Enforce HTTPS" after DNS propagation

### 2. DNS Configuration

Configure DNS records at your domain provider (Cloudflare, Route53, etc.):

```
Type: CNAME
Name: docs
Value: kcenon.github.io
TTL: 3600 (1 hour)
Proxy: Disabled (DNS only)
```

:::tip DNS Propagation
DNS changes can take up to 24 hours to propagate globally. Use `dig` or online tools to check propagation status.
:::

#### Verification

```bash
# Check DNS propagation
dig docs.screener.kr

# Expected output:
# docs.screener.kr.    3600    IN    CNAME    kcenon.github.io.
# kcenon.github.io.    3600    IN    A        185.199.108.153
```

### 3. Repository Configuration Files

#### CNAME File
Location: `docs-site/static/CNAME`

```
docs.screener.kr
```

This file is automatically copied to the build output by Docusaurus and tells GitHub Pages which custom domain to use.

#### Docusaurus Configuration
Location: `docs-site/docusaurus.config.ts`

```typescript
const config: Config = {
  title: 'Stock Screening Platform',
  url: 'https://docs.screener.kr',
  baseUrl: '/',

  // GitHub Pages deployment config
  organizationName: 'kcenon',
  projectName: 'screener_system',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  // ...
};
```

## Automatic Deployment Workflow

The `.github/workflows/docs.yml` workflow handles automatic deployment.

### Trigger Conditions

Deployment occurs when:
- Changes are pushed to the `main` branch
- Changes affect documentation-related paths:
  - `docs/**`
  - `frontend/src/**` (for TypeDoc)
  - `backend/app/**` (for Sphinx)
  - `docs-site/**`
  - `.github/workflows/docs.yml`

:::tip Selective Deployment
The workflow only runs when documentation-related files change, saving build minutes and reducing unnecessary deployments.
:::

### Workflow Steps

1. **Checkout repository** - Fetch source code
2. **Set up Node.js** (v20) - For Docusaurus and TypeDoc
3. **Set up Python** (v3.11) - For Sphinx
4. **Install Python dependencies** - Install Sphinx and extensions
5. **Build Sphinx documentation** - Generate Python API docs
6. **Install frontend dependencies** - Install TypeDoc
7. **Generate TypeDoc documentation** - Generate TypeScript API docs
8. **Install docs-site dependencies** - Install Docusaurus
9. **Build Docusaurus site** - Generate static site
10. **Setup Pages** - Configure GitHub Pages environment
11. **Upload artifact** - Upload build output
12. **Deploy to GitHub Pages** - Deploy to gh-pages branch

### Build Time

Expected build time: **2-4 minutes**

## Manual Deployment

### Local Build and Test

```bash
# Build all documentation locally
cd docs-site

# Install dependencies
npm install

# Build Sphinx docs
cd ../docs/api/python
sphinx-build -b html . _build/html
cp -r _build/html/* ../../../docs-site/build/api/backend/

# Build TypeDoc docs
cd ../../../frontend
npm install
npm run docs:generate

# Build Docusaurus site
cd ../docs-site
npm run build

# Test locally
npm run serve
# Opens http://localhost:3000
```

:::info Local Testing
Always test documentation builds locally before pushing to ensure all links work and formatting is correct.
:::

### Manual GitHub Pages Deployment

If automatic deployment fails, you can deploy manually:

```bash
# Deploy using Docusaurus CLI
cd docs-site
GIT_USER=kcenon npm run deploy

# Or using GitHub CLI
gh workflow run docs.yml
```

## Monitoring & Maintenance

### Deployment Status

Check deployment status:
- **GitHub Actions**: https://github.com/kcenon/screener_system/actions/workflows/docs.yml
- **Deployments**: https://github.com/kcenon/screener_system/deployments
- **GitHub Pages Status**: https://github.com/kcenon/screener_system/settings/pages

### Health Checks

```bash
# Check site availability
curl -I https://docs.screener.kr
# Expected: HTTP/2 200

# Verify SSL certificate
curl -vI https://docs.screener.kr 2>&1 | grep -i "SSL certificate"
# Expected: OK

# Test page load speed
lighthouse https://docs.screener.kr --only-categories=performance
# Target: > 90 score
```

:::tip Performance Monitoring
Use Lighthouse CI in your workflow to automatically test performance on every deployment.
:::

### Uptime Monitoring

**Recommended Tool**: UptimeRobot (free tier)

Setup:
1. Create monitor at https://uptimerobot.com
2. Add HTTP(s) monitor for `https://docs.screener.kr`
3. Set check interval: 5 minutes
4. Configure alert email

### Analytics

**Recommended Tool**: Plausible Analytics (privacy-friendly)

Setup:
1. Sign up at https://plausible.io
2. Add site: `docs.screener.kr`
3. Add tracking script to `docs-site/docusaurus.config.ts`:

```typescript
themeConfig: {
  headTags: [
    {
      tagName: 'script',
      attributes: {
        defer: true,
        'data-domain': 'docs.screener.kr',
        src: 'https://plausible.io/js/script.js',
      },
    },
  ],
  // ...
}
```

## Troubleshooting

### Common Issues

#### Issue: 404 errors after deployment
**Symptoms**: Site shows 404 or pages not found

**Solutions**:
1. Check `baseUrl` in `docusaurus.config.ts` matches deployment path (`/` for custom domain)
2. Verify CNAME file exists in build output: `docs-site/build/CNAME`
3. Check GitHub Pages settings shows correct custom domain
4. Wait 5-10 minutes for cache to clear

```bash
# Verify build output
ls docs-site/build/CNAME
cat docs-site/build/CNAME
# Should show: docs.screener.kr
```

#### Issue: SSL certificate not working
**Symptoms**: Browser shows "Not Secure" or SSL error

**Solutions**:
1. Wait 24 hours for DNS propagation
2. Check "Enforce HTTPS" is enabled in GitHub Pages settings
3. Clear browser cache
4. Verify DNS record is correct:
   ```bash
   dig docs.screener.kr
   # Should show CNAME pointing to kcenon.github.io
   ```

:::warning DNS Propagation Time
SSL certificate generation by GitHub Pages can only happen after DNS propagation completes, which may take up to 24 hours.
:::

#### Issue: Deployment fails with permission error
**Symptoms**: Workflow shows "Permission denied" error

**Solutions**:
1. Check workflow has `contents: write` and `pages: write` permissions in `.github/workflows/docs.yml`
2. Verify repository Settings → Actions → General → Workflow permissions is set to "Read and write permissions"
3. Check GitHub Pages is enabled in repository settings

#### Issue: Custom domain not working
**Symptoms**: Site accessible via `kcenon.github.io/screener_system` but not `docs.screener.kr`

**Solutions**:
1. Verify DNS CNAME record points to `kcenon.github.io` (not `kcenon.github.io/screener_system`)
2. Check DNS propagation: `dig docs.screener.kr`
3. Ensure CNAME file contains only `docs.screener.kr` (no protocol, no trailing slash)
4. Wait 24 hours for full DNS propagation

#### Issue: Build fails with "Module not found"
**Symptoms**: Workflow fails during Sphinx, TypeDoc, or Docusaurus build

**Solutions**:
1. **Sphinx errors**: Check Python dependencies in `requirements-docs.txt`
2. **TypeDoc errors**: Verify TypeScript compilation: `cd frontend && npm run build`
3. **Docusaurus errors**: Check for MDX syntax errors in `.md` files

```bash
# Test builds locally
cd docs/api/python && sphinx-build -b html . _build/html
cd frontend && npm run docs:generate
cd docs-site && npm run build
```

#### Issue: Old content still showing after deployment
**Symptoms**: Changes don't appear on live site

**Solutions**:
1. Wait 5-10 minutes for GitHub Pages CDN cache to clear
2. Hard refresh browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
3. Check deployment completed successfully in Actions tab
4. Verify changes are in `gh-pages` branch

:::tip Cache Busting
If users report seeing old content, advise them to hard refresh their browser or clear cache.
:::

## Performance Optimization

### Target Metrics
- **Page Load Time**: < 1 second (Lighthouse score > 90)
- **First Contentful Paint**: < 1.5 seconds
- **Time to Interactive**: < 2.5 seconds

### Optimization Techniques

1. **Image Optimization**
   - Use WebP format for images
   - Compress images before adding to `static/img/`
   - Use responsive images with `srcset`

2. **Code Splitting**
   - Docusaurus automatically code-splits by route
   - Keep page components lean

3. **CDN Benefits**
   - GitHub Pages serves via global CDN
   - Automatic HTTPS with HTTP/2
   - Gzip compression enabled

## Cost Analysis

| Service | Cost | Notes |
|---------|------|-------|
| **GitHub Pages** | $0 | Free for public repositories, unlimited bandwidth |
| **SSL Certificate** | $0 | Included with GitHub Pages (Let's Encrypt) |
| **CDN Bandwidth** | $0 | Unlimited via GitHub's global CDN |
| **Domain (docs.screener.kr)** | $12/year | Subdomain of main domain |
| **UptimeRobot** | $0 | Free tier: 50 monitors, 5-min intervals |
| **Plausible Analytics** | $0-9/month | Optional: 10k events free, $9/mo for 100k |
| **Total** | **$12-120/year** | Minimal infrastructure cost |

:::tip Cost-Effective Hosting
GitHub Pages provides enterprise-grade hosting at zero cost, making it ideal for documentation sites.
:::

## Security Considerations

### HTTPS Enforcement
- All traffic redirected to HTTPS
- TLS 1.3 support
- HTTP Strict Transport Security (HSTS) enabled

### Access Control
- Documentation is public (as intended)
- Edit access controlled via GitHub repository permissions
- Deployment requires write access to repository

### Dependency Security
- Dependabot enabled for npm and pip dependencies
- Regular security audits via `npm audit` and `safety check`
- GitHub Security Advisories monitored

## Backup and Recovery

### Content Backup
- All documentation source files in Git repository
- GitHub provides redundant storage
- gh-pages branch contains deployed builds

### Recovery Procedures

**Scenario 1: Accidental deletion of gh-pages branch**
```bash
# Trigger rebuild
gh workflow run docs.yml

# Or manually
cd docs-site
GIT_USER=kcenon npm run deploy
```

**Scenario 2: DNS issues**
```bash
# Temporarily use GitHub Pages URL
https://kcenon.github.io/screener_system/

# Fix DNS records
# Update CNAME in domain provider
```

**Scenario 3: Build failure**
```bash
# Revert to last working commit
git revert HEAD
git push origin main

# Fix issue in new PR
```

## Continuous Improvement

### Regular Maintenance Tasks

**Weekly**:
- Monitor deployment success rate
- Review uptime reports
- Check for broken links

**Monthly**:
- Update dependencies: `npm update`
- Review analytics data
- Optimize slow-loading pages

**Quarterly**:
- Performance audit with Lighthouse
- Review and update documentation
- Check for Docusaurus updates

### Feedback Collection

Enable documentation feedback:
1. Add feedback form to footer
2. Monitor GitHub Issues for documentation bugs
3. Track analytics for popular pages

## Additional Resources

### Documentation
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Docusaurus Deployment Guide](https://docusaurus.io/docs/deployment#deploying-to-github-pages)
- [Custom Domain Configuration](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)

### Tools
- [GitHub CLI](https://cli.github.com/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [UptimeRobot](https://uptimerobot.com/)
- [Plausible Analytics](https://plausible.io/)

### Support
- **GitHub Issues**: https://github.com/kcenon/screener_system/issues
- **Docusaurus Discord**: https://discord.gg/docusaurus

---

*Last Updated: 2025-11-13*
*Version: 1.1.0*
