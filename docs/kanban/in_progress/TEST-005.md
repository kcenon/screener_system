# TEST-005: Stock API Endpoints Tests

**Type**: TEST
**Priority**: P0
**Status**: REVIEW
**Created**: 2025-11-16
**Started**: 2025-11-17
**Completed**: 2025-11-17
**Effort**: 4 hours (actual)
**Phase**: Phase 1 - Critical Tests

---

## Description

Implement comprehensive integration tests for stock-related API endpoints. These are the most critical API endpoints for the stock screening platform, handling stock listings, details, price history, and financial data.

## Current Status

- **Test File**: `backend/tests/api/test_stocks.py` ✅ **CREATED**
- **Test Count**: 30+ comprehensive integration tests
- **Test Classes**:
  - `TestStockListEndpoints` (10 tests)
  - `TestStockDetailEndpoint` (4 tests)
  - `TestPriceHistoryEndpoint` (7 tests)
  - `TestFinancialDataEndpoint` (9 tests)
- **Fixtures Created**: `sample_stocks`, `sample_prices`, `sample_financials`
- **Endpoints Covered**:
  - ✅ `GET /api/v1/stocks/` (listing with pagination and filters)
  - ✅ `GET /api/v1/stocks/search` (search by name/code)
  - ✅ `GET /api/v1/stocks/{symbol}` (detail)
  - ✅ `GET /api/v1/stocks/{symbol}/prices` (price history)
  - ✅ `GET /api/v1/stocks/{symbol}/financials` (financials)

## Test Requirements

### 1. Stock Listing Endpoint (1.5h)

```python
def test_get_stocks_list():
    """Test GET /stocks/ returns stock list"""

def test_get_stocks_with_pagination():
    """Test pagination parameters (skip, limit)"""

def test_get_stocks_with_filters():
    """Test filtering by sector, market_cap, etc."""

def test_get_stocks_sorting():
    """Test sorting by price, volume, change%"""

def test_get_stocks_empty_result():
    """Test response when no stocks match filters"""

def test_get_stocks_invalid_parameters():
    """Test error handling for invalid parameters"""

def test_get_stocks_authentication_required():
    """Test endpoint requires authentication"""
```

### 2. Stock Detail Endpoint (1h)

```python
def test_get_stock_by_symbol():
    """Test GET /stocks/{symbol} returns stock details"""

def test_get_stock_includes_all_fields():
    """Test response includes all required fields"""

def test_get_stock_not_found():
    """Test 404 response for non-existent symbol"""

def test_get_stock_invalid_symbol():
    """Test error handling for invalid symbol format"""

def test_get_stock_authentication_required():
    """Test endpoint requires authentication"""
```

### 3. Price History Endpoint (1h)

```python
def test_get_stock_prices():
    """Test GET /stocks/{symbol}/prices returns price history"""

def test_get_stock_prices_date_range():
    """Test filtering by start_date and end_date"""

def test_get_stock_prices_timeframe():
    """Test different timeframes (1D, 1W, 1M, 3M, 1Y)"""

def test_get_stock_prices_empty_range():
    """Test response when no prices in date range"""

def test_get_stock_prices_invalid_dates():
    """Test error handling for invalid date formats"""

def test_get_stock_prices_stock_not_found():
    """Test 404 when stock doesn't exist"""
```

### 4. Financial Data Endpoint (0.5h)

```python
def test_get_stock_financials():
    """Test GET /stocks/{symbol}/financials returns financial data"""

def test_get_stock_financials_includes_metrics():
    """Test response includes key financial metrics"""

def test_get_stock_financials_not_available():
    """Test response when financials not available"""

def test_get_stock_financials_stock_not_found():
    """Test 404 when stock doesn't exist"""
```

## Acceptance Criteria

- [x] All stock API endpoints tested (GET /stocks/, /{symbol}, /prices, /financials, /search)
- [x] Pagination tested (page, per_page parameters)
- [x] Filtering and sorting tested (market, sector, date ranges)
- [x] Error cases tested (404, 422 validation errors)
- [x] Response schemas validated (correct JSON structure)
- [x] Test fixtures created with realistic sample data
- [x] Edge cases covered (empty results, invalid parameters, non-existent stocks)
- [ ] Test coverage for stock endpoints reaches >85% (pending CI/CD verification)
- [ ] All tests pass in CI/CD pipeline (pending PR merge)

## Dependencies

- pytest
- FastAPI TestClient
- Test database with sample stock data
- Authentication fixtures (valid/invalid tokens)

## Testing Strategy

1. **Integration Tests**: Test complete HTTP request/response cycle
2. **Database Tests**: Use test database with fixture data
3. **Authentication Tests**: Test with valid and invalid tokens
4. **Schema Validation**: Verify response matches Pydantic schemas
5. **Edge Cases**: Empty results, invalid parameters, missing data

## Related Files

- Source: `backend/app/api/v1/endpoints/stocks.py`
- Test: `backend/tests/api/test_stocks.py` (to be created)
- Schemas: `backend/app/schemas/stock.py`
- Models: `backend/app/models/stock.py`

## Test Data Requirements

Create fixtures with:
- 20+ stock records (various sectors, market caps)
- Price history data (1+ year of daily prices)
- Financial data for 10+ stocks
- Mix of active and delisted stocks

## Notes

- Use FastAPI TestClient for integration tests
- Create reusable fixtures for test data
- Test with both authenticated and unauthenticated requests
- Verify response times are acceptable (<500ms)
- Test pagination edge cases (first page, last page, beyond last page)

---

**References**: TEST_IMPROVEMENT_PLAN.md - Phase 1, Item #5
