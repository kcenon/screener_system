# [BUGFIX-003] Fix updated_at Column in calculated_indicators Table

## Metadata
- **Status**: DONE
- **Priority**: High
- **Assignee**: AI Assistant
- **Estimated Time**: 2 hours
- **Actual Time**: 1.5 hours
- **Sprint**: Sprint 3
- **Tags**: #bugfix #database #schema #backend
- **Created**: 2025-11-10
- **Completed**: 2025-11-10

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
- [x] Check database migration file for calculated_indicators table
- [x] Add `updated_at` column to migration if missing
- [x] Create new migration to add updated_at column
- [x] Test migration on development database
- [x] Verify all stock/screening endpoints work
- [x] Update any queries that reference this column

## Acceptance Criteria
- [x] `updated_at` column exists in calculated_indicators table
- [x] Column has DEFAULT CURRENT_TIMESTAMP
- [x] UPDATE trigger sets updated_at automatically
- [x] Stock listing endpoint returns data without errors
- [x] Screening endpoint works correctly
- [x] No SQL errors in application logs

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
- **100%** - Complete

## Implementation Details

### Changes Made
1. **Migration File Created**: `database/migrations/06_add_calculated_indicators_updated_at.sql`
   - Added `updated_at TIMESTAMP DEFAULT NOW()` column
   - Created trigger `update_calculated_indicators_updated_at`

2. **Database Updated**:
   ```sql
   ALTER TABLE calculated_indicators ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
   CREATE TRIGGER update_calculated_indicators_updated_at
       BEFORE UPDATE ON calculated_indicators
       FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
   ```

3. **Verification**:
   - ✅ Column exists: `\d calculated_indicators` shows both `created_at` and `updated_at`
   - ✅ Trigger created: `update_calculated_indicators_updated_at` in information_schema.triggers
   - ✅ `/v1/stocks` endpoint: Returns 200 OK (no UndefinedColumnError)
   - ✅ `/v1/screen` endpoint: Returns 200 OK (no UndefinedColumnError)

### Resolution
The schema inconsistency has been resolved. The `calculated_indicators` table now has both `created_at` and `updated_at` columns, matching the SQLAlchemy model's `TimestampMixin` expectations.

## Notes
- This was a schema inconsistency issue
- Root cause: Missing column in `01_create_tables.sql`
- All other tables already had both timestamp columns
- Migration pattern follows existing conventions (users, stocks, portfolios, etc.)
