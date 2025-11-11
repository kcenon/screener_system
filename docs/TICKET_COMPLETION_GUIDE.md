# Ticket Completion Guide

## Purpose

This guide ensures that tickets are properly documented and validated before being marked as DONE. Following these guidelines prevents documentation gaps and maintains project quality.

## Definition of Done

A ticket can only be moved to `docs/kanban/done/` when ALL of the following are complete:

### 1. Implementation Complete
- [ ] All subtasks checked off
- [ ] Code written and committed
- [ ] Tests written and passing
- [ ] Code reviewed and approved

### 2. Documentation Updated
- [ ] **Status** field set to `DONE`
- [ ] **Progress** set to `100%`
- [ ] **Completed** date added (YYYY-MM-DD format)
- [ ] **Actual Time** recorded (vs estimated)
- [ ] All acceptance criteria checkboxes verified

### 3. Validation Evidence
- [ ] Each acceptance criterion has supporting evidence:
  - Screenshot (for UI changes)
  - Test output (for backend/logic)
  - Metrics (for performance)
  - Manual testing notes
- [ ] Evidence documented in ticket or linked PR

### 4. PR Requirements
- [ ] PR created and merged
- [ ] PR number referenced in ticket
- [ ] All CI/CD checks passed
- [ ] Code review completed

## Ticket Update Checklist

Use this checklist when marking a ticket as DONE:

```markdown
## Pre-Completion Checklist
- [ ] All subtasks implemented and checked
- [ ] Tests written (unit, integration as needed)
- [ ] Code reviewed by peer
- [ ] PR merged to main branch

## Documentation Update Checklist
- [ ] Status changed from IN_PROGRESS to DONE
- [ ] Progress changed from X% to 100%
- [ ] Completed date added: YYYY-MM-DD
- [ ] Actual time recorded: X hours
- [ ] PR reference added: #123

## Acceptance Criteria Validation
For EACH acceptance criterion:
- [ ] Criterion tested manually or automatically
- [ ] Evidence documented (screenshot/test/metric)
- [ ] Checkbox marked [x]
- [ ] Any unmet criteria explained with reason

## Final Review
- [ ] All checkboxes in ticket are complete
- [ ] No TODO or placeholder text remains
- [ ] Implementation Summary written (if complex)
- [ ] Ticket moved to docs/kanban/done/
```

## Example: Proper Ticket Completion

### Before (Incomplete)
```markdown
## Acceptance Criteria
- [ ] Feature works correctly
- [ ] Tests passing
- [ ] Documentation updated

**Progress**: 95%
**Status**: IN_PROGRESS
```

### After (Complete)
```markdown
## Acceptance Criteria
- [x] Feature works correctly
  - ✅ Tested with manual test cases (see evidence below)
  - ✅ Edge cases validated (null inputs, boundary values)
- [x] Tests passing
  - ✅ 15 unit tests added (tests/test_feature.py)
  - ✅ 3 integration tests added (tests/integration/test_feature_api.py)
  - ✅ All 96 tests passing in CI (see PR #123)
- [x] Documentation updated
  - ✅ README.md updated with usage examples
  - ✅ API docs regenerated (see docs/api/feature.md)

**Progress**: 100%
**Status**: DONE
**Completed**: 2025-11-11
**Actual Time**: 6 hours (estimated: 8 hours)

### Testing Evidence
![Feature Screenshot](../images/feature-screenshot.png)

### Performance Metrics
- Response time: 45ms (p95)
- Memory usage: +2MB (acceptable)
- Test coverage: 95% for new code

### PR Reference
- **PR #123**: https://github.com/org/repo/pull/123
- **Commits**: 3 commits, 15 files changed
- **Review**: Approved by @reviewer
```

## Common Mistakes to Avoid

### ❌ DON'T: Move ticket to done/ with unchecked criteria
```markdown
## Acceptance Criteria
- [ ] Feature implemented  <-- Still unchecked!
- [ ] Tests written        <-- Still unchecked!

**Status**: DONE  <-- Wrong!
```

### ✅ DO: Check all criteria with evidence
```markdown
## Acceptance Criteria
- [x] Feature implemented (see commit abc123)
- [x] Tests written (12 tests in test_feature.py, all passing)

**Status**: DONE  <-- Correct!
```

### ❌ DON'T: Leave progress at 0% in done folder
```markdown
**Progress**: 0%  <-- Wrong!
**Status**: DONE
```

### ✅ DO: Update progress to 100%
```markdown
**Progress**: 100%  <-- Correct!
**Status**: DONE
**Completed**: 2025-11-11
```

### ❌ DON'T: Claim completion without evidence
```markdown
- [x] Performance improved

<-- No metrics or evidence provided!
```

### ✅ DO: Provide measurable evidence
```markdown
- [x] Performance improved
  - Before: 450ms avg response time
  - After: 220ms avg response time (51% improvement)
  - Method: Replaced double query with window function
  - Evidence: Load test results in PR #24
```

## Validation Evidence Types

### For Backend Changes
- **Test Output**: Pytest results, coverage reports
- **Performance**: Benchmark results, profiling data
- **API**: Swagger docs, request/response examples
- **Database**: Migration success, query performance

### For Frontend Changes
- **Screenshots**: Before/after UI changes
- **Responsiveness**: Mobile/tablet/desktop views
- **Interaction**: Video of user flow working
- **Accessibility**: WAVE report, keyboard navigation test

### For Infrastructure Changes
- **Deployment**: Successful deployment logs
- **Monitoring**: Grafana dashboard showing metrics
- **Logs**: Sample logs showing feature working
- **Performance**: Load test results

## Ticket Review Process

### Self-Review (Before Moving to Review)
1. Read ticket from top to bottom
2. Verify every checkbox can be checked honestly
3. Add evidence for each acceptance criterion
4. Update metadata (status, progress, dates)
5. Write implementation summary if complex

### Peer Review (In Review Phase)
1. Verify PR is merged and CI passed
2. Check that all acceptance criteria are validated
3. Ensure evidence supports claimed completion
4. Confirm no placeholders or TODOs remain
5. Move to done/ only if everything is validated

### Quality Audit (Periodic)
1. Run scan script to find documentation gaps
2. Review tickets with unchecked criteria
3. Verify actual implementation matches ticket
4. Update tickets with missing validation
5. Improve process based on findings

## Automated Checks

Run this script before moving ticket to done/:

```bash
#!/bin/bash
# check_ticket_completion.sh

TICKET_FILE=$1

echo "Checking ticket: $TICKET_FILE"

# Check status is DONE
if ! grep -q "Status.*DONE" "$TICKET_FILE"; then
    echo "❌ Status is not DONE"
    exit 1
fi

# Check progress is 100%
if ! grep -q "100%" "$TICKET_FILE"; then
    echo "❌ Progress is not 100%"
    exit 1
fi

# Check completed date exists
if ! grep -q "Completed.*202[0-9]" "$TICKET_FILE"; then
    echo "❌ No completion date found"
    exit 1
fi

# Count unchecked items
unchecked=$(grep -c "- \[ \]" "$TICKET_FILE")
if [ "$unchecked" -gt 5 ]; then
    echo "⚠️  Warning: $unchecked unchecked items remain"
    echo "   (Acceptable if explained, but review carefully)"
fi

echo "✅ Ticket validation passed"
```

## Process Improvement

### Short-term
1. Use this checklist for all new tickets
2. Review existing tickets in done/ folder
3. Update any tickets with documentation gaps
4. Add PR template requiring ticket validation

### Long-term
1. Implement automated ticket validation in CI
2. Create bot to check ticket status in PRs
3. Generate completion reports for sprints
4. Track documentation quality metrics

## Questions?

If unclear whether a ticket meets definition of done:
1. Ask in code review: "Is this evidence sufficient?"
2. Reference this guide in discussions
3. When in doubt, ask for peer validation
4. Better to over-document than under-document

---

**Remember**: The ticket is your project's permanent record. Future you (and your team) will thank you for thorough documentation!

**Last Updated**: 2025-11-11
**Related**: BUGFIX-006, docs/TICKET_AUDIT_REPORT.md
