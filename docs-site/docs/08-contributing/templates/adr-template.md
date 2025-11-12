---
id: adr-template
title: Architecture Decision Record (ADR) Template
description: Template for documenting important architectural decisions
sidebar_label: ADR Template
sidebar_position: 4
tags:
  - template
  - adr
  - architecture
---

# ADR-[NUMBER]: [Short Title]

**Date**: YYYY-MM-DD

**Status**: [Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

**Deciders**: [List of people involved in the decision]

**Technical Story**: [Link to related ticket/issue if applicable]

## Context and Problem Statement

Describe the context and problem statement that requires an architectural decision.

What is the issue we're trying to solve? Include any relevant background information, constraints, or requirements.

**Key Questions:**
- What problem are we trying to solve?
- What are the current pain points?
- What are the business/technical requirements?

## Decision Drivers

List the factors that influence the decision:

* **Driver 1**: Explanation (e.g., Performance requirements)
* **Driver 2**: Explanation (e.g., Team expertise)
* **Driver 3**: Explanation (e.g., Budget constraints)
* **Driver 4**: Explanation (e.g., Scalability needs)
* **Driver 5**: Explanation (e.g., Maintainability)

## Considered Options

List all options that were considered for solving the problem:

1. **Option 1**: [Name of option]
2. **Option 2**: [Name of option]
3. **Option 3**: [Name of option]

## Decision Outcome

**Chosen Option**: "[Option Name]"

Explanation of why this option was chosen.

### Positive Consequences

Benefits of this decision:

* **Pro 1**: Positive outcome or advantage
* **Pro 2**: Another benefit
* **Pro 3**: Third advantage

### Negative Consequences

Drawbacks or trade-offs accepted:

* **Con 1**: Negative aspect or limitation
* **Con 2**: Trade-off we're accepting
* **Con 3**: Risk or concern

## Detailed Analysis

### Option 1: [Option Name]

**Description**: Detailed description of this option.

**Pros:**
- ✅ Advantage 1
- ✅ Advantage 2
- ✅ Advantage 3

**Cons:**
- ❌ Disadvantage 1
- ❌ Disadvantage 2
- ❌ Disadvantage 3

**Technical Details:**
```
// Code example or technical specification
```

**Estimated Cost**: [Time/money/complexity]

**Risk Level**: [Low | Medium | High]

### Option 2: [Option Name]

**Description**: Detailed description of second option.

**Pros:**
- ✅ Advantage 1
- ✅ Advantage 2

**Cons:**
- ❌ Disadvantage 1
- ❌ Disadvantage 2

**Technical Details:**
```
// Code example or technical specification
```

**Estimated Cost**: [Time/money/complexity]

**Risk Level**: [Low | Medium | High]

### Option 3: [Option Name]

Similar structure for third option.

## Comparison Matrix

| Criteria | Option 1 | Option 2 | Option 3 | Weight |
|----------|----------|----------|----------|--------|
| Performance | 8/10 | 6/10 | 9/10 | High |
| Maintainability | 7/10 | 9/10 | 5/10 | High |
| Cost | 6/10 | 8/10 | 4/10 | Medium |
| Learning Curve | 8/10 | 9/10 | 3/10 | Medium |
| Scalability | 9/10 | 7/10 | 8/10 | High |
| **Total Weighted** | **X.X** | **X.X** | **X.X** | |

## Implementation Plan

### Phase 1: Preparation (Week 1-2)

1. **Task 1**: Description
   - Sub-task
   - Estimated time: X days
   - Owner: [Name]

2. **Task 2**: Description
   - Sub-task
   - Estimated time: X days
   - Owner: [Name]

### Phase 2: Implementation (Week 3-4)

1. **Task 3**: Description
2. **Task 4**: Description

### Phase 3: Testing & Rollout (Week 5)

1. **Task 5**: Description
2. **Task 6**: Description

**Total Estimated Time**: X weeks

**Resource Requirements**:
- X developers
- Y budget
- Z infrastructure

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| Risk 1 description | Low/Med/High | Low/Med/High | How we'll address it |
| Risk 2 description | Low/Med/High | Low/Med/High | How we'll address it |
| Risk 3 description | Low/Med/High | Low/Med/High | How we'll address it |

## Monitoring and Success Metrics

How we'll measure if this decision was successful:

**Key Metrics:**
- **Metric 1**: Target value and measurement method
- **Metric 2**: Target value and measurement method
- **Metric 3**: Target value and measurement method

**Review Schedule**: [When we'll review this decision]

## Rollback Plan

If this decision proves to be incorrect:

1. **Trigger Conditions**: What would indicate we need to rollback
   - Condition 1
   - Condition 2

2. **Rollback Steps**:
   - Step 1
   - Step 2
   - Step 3

3. **Fallback Option**: [Alternative approach if rollback is needed]

## References

* [Link to design document](./design-doc.md)
* [Related ADR-XXX](./adr-xxx.md)
* [External resource](https://example.com)
* [Research paper](https://example.com/paper.pdf)
* [Benchmark results](./benchmarks/results.md)

## Notes

Additional context, learnings, or observations:

- **Note 1**: Important observation
- **Note 2**: Lesson learned
- **Note 3**: Future consideration

## Changelog

| Date | Author | Change |
|------|--------|--------|
| YYYY-MM-DD | [Name] | Initial draft |
| YYYY-MM-DD | [Name] | Updated based on review feedback |
| YYYY-MM-DD | [Name] | Decision accepted |

---

**ADR Number**: [XXX]
**Created**: [Date]
**Last Modified**: [Date]
**Status**: [Current Status]
