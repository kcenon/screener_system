# [BUGFIX-003] Fix updated_at Column in calculated_indicators Table

## Metadata
- **Status**: TODO
- **Priority**: High
- **Assignee**: AI Assistant
- **Estimated Time**: 2 hours
- **Sprint**: Sprint 3
- **Tags**: #bugfix #database #schema #backend
- **Created**: 2025-11-10

## Description
The `calculated_indicators` table is missing the `updated_at` column, causing SQL errors when querying stock data. The model expects this column but the database schema doesn't include it.

## Error Details
```
asyncpg.exceptions.UndefinedColumnError: column calculated_indicators.updated_at does not exist
HINT: Perhaps you meant to reference the column "calculated_indicators.created_at".
```

## Root Cause
Database migration file creates `calculated_indicators` table with only `created_at` column, but the SQLAlchemy model (`app/db/models/calculated_indicator.py`) includes both `created_at` and `updated_at`.

## Subtasks
- [ ] Check database migration file for calculated_indicators table
- [ ] Add `updated_at` column to migration if missing
- [ ] Create new migration to add updated_at column
- [ ] Test migration on development database
- [ ] Verify all stock/screening endpoints work
- [ ] Update any queries that reference this column

## Acceptance Criteria
- [ ] `updated_at` column exists in calculated_indicators table
- [ ] Column has DEFAULT CURRENT_TIMESTAMP
- [ ] UPDATE trigger sets updated_at automatically
- [ ] Stock listing endpoint returns data without errors
- [ ] Screening endpoint works correctly
- [ ] No SQL errors in application logs

## Dependencies
- **Depends on**: DB-002 (schema migrations)
- **Blocks**: FE-003 (integration testing)

## Testing Plan
```bash
# Test migration
docker exec screener_postgres psql -U screener_user -d screener_db -c "\d calculated_indicators"

# Test endpoints
curl http://localhost:8000/v1/stocks?limit=10
curl -X POST http://localhost:8000/v1/screen -H "Content-Type: application/json" \
  -d '{"filters":{"market":"ALL"},"page":1,"per_page":10}'
```

## References
- **Error Log**: Backend logs showing UndefinedColumnError
- **Model**: `backend/app/db/models/calculated_indicator.py`
- **Migration**: `backend/database/migrations/`

## Progress
- **0%** - Not started

## Notes
- This is a schema inconsistency issue
- Similar pattern should be verified for all tables
- Consider adding schema validation tests
