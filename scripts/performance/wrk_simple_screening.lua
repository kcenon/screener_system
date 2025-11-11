-- Simple screening query (no filters)
-- This should hit materialized views and return fast

wrk.method = "POST"
wrk.body   = '{}'
wrk.headers["Content-Type"] = "application/json"
