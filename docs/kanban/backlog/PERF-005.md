# PERF-005: Query Optimization Audit

## Metadata

| Field | Value |
|-------|-------|
| **ID** | PERF-005 |
| **Title** | Conduct Query Optimization Audit |
| **Type** | Technical Debt |
| **Status** | BACKLOG |
| **Priority** | P2 (Medium) |
| **Estimate** | 8 hours |
| **Sprint** | Sprint 7 |
| **Epic** | Performance & Scalability |
| **Assignee** | TBD |
| **Created** | 2025-11-29 |

## Description

슬로우 쿼리 분석 및 최적화

## Acceptance Criteria

- [ ] pg_stat_statements 분석
- [ ] 슬로우 쿼리 식별 (> 100ms)
- [ ] 실행 계획 분석 (EXPLAIN ANALYZE)
- [ ] 인덱스 추가/수정
- [ ] 쿼리 리팩토링
- [ ] 최적화 결과 문서화

## References

- [IMPROVEMENT_TICKETS.md](../../IMPROVEMENT_TICKETS.md) - Epic 9: Performance & Scalability
