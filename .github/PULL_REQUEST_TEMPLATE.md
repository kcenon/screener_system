# Pull Request

## Summary

Brief description of what this PR does and why.

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] CI/CD changes
- [ ] Dependency updates

## Related Issues

- Fixes #(issue number)
- Related to #(issue number)
- Closes #(issue number)

## Changes Made

Describe the changes in detail:

### Backend Changes
- Change 1
- Change 2

### Frontend Changes
- Change 1
- Change 2

### Database Changes
- [ ] Migration required
- [ ] Schema changes
- [ ] Data migration script included

### Infrastructure Changes
- [ ] Docker configuration
- [ ] CI/CD pipeline
- [ ] Environment variables

## Testing

### Test Coverage
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated
- [ ] Manual testing completed

### Test Results
```
# Paste test output or describe manual testing performed
```

### Test Environment
- OS: [e.g., macOS 13, Ubuntu 22.04]
- Browser: [e.g., Chrome 119, Firefox 120]
- Node version: [e.g., 18.17.0]
- Python version: [e.g., 3.9.16]

## Documentation

- [ ] Code comments added/updated
- [ ] API documentation updated
- [ ] User guide updated
- [ ] README updated
- [ ] Changelog updated
- [ ] Migration guide created (if breaking change)

### Documentation Checklist
- [ ] All new functions/classes have docstrings
- [ ] Complex logic has inline comments
- [ ] Public APIs are documented
- [ ] Examples provided where applicable

## Code Quality

- [ ] Code follows project style guidelines
- [ ] Linting passes (`npm run lint` / `ruff check .`)
- [ ] Type checking passes (`mypy`)
- [ ] No console.log or debug statements left
- [ ] No commented-out code
- [ ] Error handling implemented
- [ ] Security best practices followed

## Performance

- [ ] No N+1 query problems
- [ ] Database queries optimized
- [ ] Caching implemented where appropriate
- [ ] Bundle size impact assessed (frontend)
- [ ] Memory leaks checked

### Performance Metrics
```
# Add before/after metrics if applicable
# Example:
# - API response time: 450ms → 220ms (-51%)
# - Bundle size: 2.1MB → 1.8MB (-14%)
```

## Security

- [ ] Input validation implemented
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified
- [ ] Authentication/authorization checked
- [ ] Sensitive data not logged
- [ ] Dependencies scanned for vulnerabilities
- [ ] No hardcoded secrets

## Breaking Changes

:::warning
List any breaking changes and migration steps required
:::

- **Breaking Change 1**: Description
  - Migration: Steps to migrate
- **Breaking Change 2**: Description
  - Migration: Steps to migrate

## Deployment Notes

Special deployment considerations:

- [ ] Database migration required
- [ ] Environment variables need updating
- [ ] Cache clearing required
- [ ] Service restart required
- [ ] Backward compatible with current production

### Deployment Steps
1. Step 1
2. Step 2
3. Step 3

## Screenshots

Add screenshots for UI changes:

### Before
[Screenshot or N/A]

### After
[Screenshot or N/A]

## Checklist

- [ ] My code follows the project's coding standards
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Additional Context

Add any other context about the PR here.

## Reviewer Notes

Special areas to focus on during review:

- Area 1 that needs careful review
- Area 2 with potential concerns
- Area 3 with complex logic

---

**PR Author**: @username
**Reviewers**: @reviewer1, @reviewer2
**Estimated Review Time**: [X hours]
