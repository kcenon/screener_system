-- Complex screening query (10+ filters)
-- This tests query optimization with multiple conditions

wrk.method = "POST"
wrk.body   = [[{
  "market": "KOSPI",
  "min_per": 5,
  "max_per": 15,
  "min_roe": 10,
  "max_pbr": 2,
  "min_market_cap": 100000000000,
  "min_volume": 100000,
  "min_rsi_14": 30,
  "max_rsi_14": 70,
  "min_macd": -10,
  "max_macd": 10
}]]
wrk.headers["Content-Type"] = "application/json"
