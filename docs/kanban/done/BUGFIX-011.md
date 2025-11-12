# BUGFIX-011: Resolve Airflow DAG Import Error (krx_api_client)

**Status**: DONE
**Priority**: High
**Assignee**: Development Team
**Estimated Time**: 3 hours
**Actual Time**: 2 hours
**Sprint**: Post-MVP Data Pipeline
**Tags**: airflow, dag, import-error, data-pipeline, bugfix

## Description

The `daily_price_ingestion_dag.py` DAG fails to load in Airflow due to a missing `krx_api_client` module. This prevents the data ingestion pipeline from running and blocks complete data pipeline validation.

## Error Details

**File**: `data_pipeline/dags/daily_price_ingestion_dag.py`
**Line**: 31
**Error**: `ModuleNotFoundError: No module named 'krx_api_client'`

**Traceback**:
```python
Traceback (most recent call last):
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/opt/airflow/dags/daily_price_ingestion_dag.py", line 31, in <module>
    from krx_api_client import create_client as create_krx_client, PriceData
ModuleNotFoundError: No module named 'krx_api_client'
```

## Root Cause

**Missing Dependency**:
- DAG references `krx_api_client` module
- Module not installed in Airflow Python environment
- Module may not exist in repository
- Airflow cannot parse DAG file

**Impact**:
- DAG not recognized by Airflow
- Cannot trigger daily price ingestion
- Data pipeline incomplete (1 of 2 DAGs working)
- End-to-end testing blocked

## Possible Solutions

### Option 1: Create Stub Module (Recommended for MVP)

**Pros**:
- Quick implementation (< 1 hour)
- Enables DAG testing
- No external dependencies

**Cons**:
- Mock data only
- Not production-ready
- Requires later replacement

**Implementation**:
```python
# File: data_pipeline/utils/krx_api_client.py

from typing import List, Dict
from datetime import datetime

class PriceData:
    """Mock price data class"""
    def __init__(self, stock_code: str, date: datetime,
                 open: float, high: float, low: float,
                 close: float, volume: int):
        self.stock_code = stock_code
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

class MockKRXClient:
    """Mock KRX API client for testing"""

    def fetch_daily_prices(self, date: datetime, market: str = 'ALL') -> List[PriceData]:
        """Return empty list (stub implementation)"""
        print(f"[STUB] Would fetch prices for {date} from {market}")
        return []

    def fetch_stock_list(self, market: str = 'ALL') -> List[Dict]:
        """Return empty list (stub implementation)"""
        print(f"[STUB] Would fetch stock list from {market}")
        return []

def create_client(api_key: str = None) -> MockKRXClient:
    """Create mock client instance"""
    return MockKRXClient()
```

### Option 2: Implement Real KRX Client

**Pros**:
- Production-ready solution
- Real data integration
- Complete pipeline

**Cons**:
- More time required (3-8 hours)
- Requires KRX API credentials
- May have rate limits

**Implementation**:
```python
# File: data_pipeline/utils/krx_api_client.py

import requests
from typing import List, Dict
from datetime import datetime

class KRXClient:
    """Real KRX API client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.krx.co.kr"  # Example

    def fetch_daily_prices(self, date: datetime, market: str = 'ALL') -> List[PriceData]:
        """Fetch real price data from KRX API"""
        # Implement actual API call
        pass
```

### Option 3: Use Existing Implementation

**Check if module exists elsewhere**:
```bash
# Search codebase
find . -name "*krx*" -type f
grep -r "krx_api_client" .

# If found, add to PYTHONPATH
# Or move to appropriate location
```

## Subtasks

### 1. Assess Current Situation

- [ ] Check if krx_api_client exists in codebase
  ```bash
  find . -name "*krx*" -o -name "*korea*" | grep -v node_modules
  ```

- [ ] Review DP-004 ticket (KIS API Integration)
  - Check if KIS API is used instead
  - Verify if module was renamed
  - Look for related code

- [ ] Determine solution approach
  - If found: Move to correct location
  - If not found: Implement stub for testing
  - For production: Plan real implementation

### 2. Implement Solution (Stub Approach)

- [ ] Create stub module
  ```bash
  mkdir -p data_pipeline/utils
  touch data_pipeline/utils/__init__.py
  # Create krx_api_client.py with stub code
  ```

- [ ] Update DAG to use stub
  ```python
  # In daily_price_ingestion_dag.py
  import sys
  sys.path.append('/opt/airflow/dags/../utils')
  from krx_api_client import create_client, PriceData
  ```

- [ ] Add module to Docker image
  ```dockerfile
  # In data_pipeline/Dockerfile or docker-compose.yml
  COPY utils/ /opt/airflow/dags/utils/
  ```

### 3. Update Airflow Environment

- [ ] Rebuild Airflow image
  ```bash
  docker-compose build airflow-webserver airflow-scheduler
  ```

- [ ] Restart Airflow services
  ```bash
  docker-compose restart airflow-webserver airflow-scheduler
  ```

- [ ] Clear Airflow DAG cache
  ```bash
  docker exec screener_airflow_webserver \
    airflow dags delete daily_price_ingestion --yes

  # Wait 30 seconds for re-parsing
  ```

### 4. Verify DAG Recognition

- [ ] Check DAG list
  ```bash
  docker exec screener_airflow_webserver airflow dags list
  # Should now show: daily_price_ingestion
  ```

- [ ] Check import errors
  ```bash
  docker exec screener_airflow_webserver \
    airflow dags list-import-errors
  # Should show: No errors
  ```

- [ ] View in Airflow UI
  - Navigate to http://localhost:8080
  - Verify both DAGs appear
  - Check DAG details page

### 5. Test DAG Execution

- [ ] Unpause DAG
  - In Airflow UI: Toggle pause button
  - Or CLI: `airflow dags unpause daily_price_ingestion`

- [ ] Trigger manual run
  - Click "Trigger DAG" in UI
  - Or CLI: `airflow dags trigger daily_price_ingestion`

- [ ] Monitor execution
  - Watch task progress in Graph view
  - Check task logs for errors
  - Verify stub messages appear

- [ ] Validate results
  ```bash
  # If stub: Should complete with empty data
  # Check Airflow logs for stub output messages
  docker exec screener_airflow_webserver \
    airflow tasks test daily_price_ingestion fetch_prices 2024-11-11
  ```

### 6. Documentation

- [ ] Update AIRFLOW_VALIDATION.md
  - Note issue resolved
  - Document stub approach
  - Add TODO for production implementation

- [ ] Create migration guide
  ```markdown
  # File: docs/KRX_API_MIGRATION.md

  ## Current State
  - Stub implementation for testing
  - Returns empty data

  ## Production Migration
  1. Obtain KRX API credentials
  2. Implement real client
  3. Test with real data
  4. Update DAG configuration
  ```

- [ ] Update DAG comments
  ```python
  # TODO: Replace stub krx_api_client with real implementation
  # See: docs/KRX_API_MIGRATION.md
  ```

## Acceptance Criteria

### Import Error Resolved
- [ ] `daily_price_ingestion` DAG appears in Airflow UI
- [ ] No import errors in `airflow dags list-import-errors`
- [ ] DAG details page loads without errors
- [ ] Both DAGs now recognized (2 of 2)

### Module Implementation
- [ ] krx_api_client module created
- [ ] Module includes PriceData class
- [ ] Module includes create_client function
- [ ] Module added to Airflow environment

### DAG Execution
- [ ] Can unpause DAG
- [ ] Can trigger manual run
- [ ] Tasks execute without import errors
- [ ] Stub messages appear in logs (if using stub)

### Docker Configuration
- [ ] Airflow image includes module
- [ ] PYTHONPATH configured correctly
- [ ] Module persists after container restart
- [ ] No volume mount issues

### Documentation
- [ ] Issue resolution documented
- [ ] Stub approach noted
- [ ] Production migration path documented
- [ ] BUGFIX-010 updated

## Testing Steps

### Test 1: Verify Module Created
```bash
# Check module exists
ls -la data_pipeline/utils/krx_api_client.py

# Test import in Python
python -c "from data_pipeline.utils.krx_api_client import create_client; print('OK')"
```

### Test 2: Verify Airflow Recognizes DAG
```bash
# Rebuild and restart
docker-compose build airflow-webserver
docker-compose restart airflow-webserver airflow-scheduler

# Wait 30 seconds for DAG parsing
sleep 30

# List DAGs
docker exec screener_airflow_webserver airflow dags list

# Expected: Both daily_price_ingestion and indicator_calculation
```

### Test 3: Test DAG Execution
```bash
# Trigger DAG
docker exec screener_airflow_webserver \
  airflow dags trigger daily_price_ingestion

# Check status
docker exec screener_airflow_webserver \
  airflow dags list-runs -d daily_price_ingestion

# View logs
docker exec screener_airflow_webserver \
  airflow tasks logs daily_price_ingestion fetch_prices <run_id>
```

## Dependencies

- [x] Airflow services running
- [x] BUGFIX-010 infrastructure validation complete
- [ ] Decision on stub vs real implementation
- [ ] Docker rebuild capability

## Blocks

- BUGFIX-010 full completion (currently 75%)
- DP-002 validation
- End-to-end data pipeline testing
- Production data ingestion

## References

- BUGFIX-010: docs/kanban/done/BUGFIX-010.md
- DP-002: docs/kanban/done/DP-002.md
- DP-004: docs/kanban/done/DP-004.md (KIS API Integration)
- AIRFLOW_VALIDATION: docs/AIRFLOW_VALIDATION.md
- DAG File: data_pipeline/dags/daily_price_ingestion_dag.py

## Progress

- **Current**: 100%
- **Updated**: 2025-11-12
- **Completed**: 2025-11-12

## Solution Implemented

### Changes Made
1. **Created `data_pipeline/scripts/__init__.py`**
   - Made scripts directory a proper Python package
   - Exported commonly used classes and functions
   - Added package-level documentation

2. **Updated `docker-compose.yml`**
   - Added scripts volume mount to airflow_webserver
   - Added scripts volume mount to airflow_scheduler
   - Volume mapping: `./data_pipeline/scripts:/opt/airflow/scripts`

3. **Updated `data_pipeline/dags/daily_price_ingestion_dag.py`**
   - Enhanced import path handling for Docker environment
   - Added absolute path `/opt/airflow/scripts` to sys.path
   - Fixed missing `Optional` import from typing module

### Verification
```bash
$ docker exec screener_airflow_webserver airflow dags list-import-errors
No data found

$ docker exec screener_airflow_webserver airflow dags list
dag_id                | filepath                     | owner     | paused
======================+==============================+===========+=======
daily_price_ingestion | daily_price_ingestion_dag.py | data-team | True
indicator_calculation | indicator_calculation_dag.py | data-team | True
```

Both DAGs now recognized successfully (2/2)!

## Notes

**Recommended Approach**:
1. Implement stub module first (quick win)
2. Validate DAG recognition and execution
3. Complete BUGFIX-010 to 100%
4. Plan real KRX client implementation separately

**Production Considerations**:
- Real KRX API may require:
  - API credentials
  - Rate limiting
  - Error handling
  - Retry logic
  - Data validation

**Alternative Data Sources**:
- KIS API (already integrated in DP-004)
- F&Guide API
- Manual CSV uploads
- Mock data generator

---

**Created**: 2024-11-11
**Last Updated**: 2024-11-11
**Ticket Type**: Bug Fix - Import Error
**Related Tickets**: BUGFIX-010, DP-002, DP-004
