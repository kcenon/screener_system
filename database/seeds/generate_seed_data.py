#!/usr/bin/env python3
"""
Seed Data Generator for Stock Screening Platform
Generates realistic Korean stock market data for development and testing

Usage:
    python generate_seed_data.py --output seeds/seed_data.sql
    python generate_seed_data.py --database screener_db
"""

import random
import argparse
from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple
import sys


class StockDataGenerator:
    """Generate realistic Korean stock market seed data"""

    # Real Korean stock data for authenticity
    KOSPI_STOCKS = [
        # Major Tech
        ('005930', '삼성전자', 'Samsung Electronics', 'Technology', 'Semiconductors'),
        ('000660', 'SK하이닉스', 'SK Hynix', 'Technology', 'Semiconductors'),
        ('035420', 'NAVER', 'NAVER', 'Technology', 'Internet Services'),
        ('035720', '카카오', 'Kakao', 'Technology', 'Internet Services'),
        ('051910', 'LG화학', 'LG Chem', 'Basic Materials', 'Chemicals'),
        ('006400', '삼성SDI', 'Samsung SDI', 'Technology', 'Batteries'),
        ('207940', '삼성바이오로직스', 'Samsung Biologics', 'Healthcare', 'Biotechnology'),

        # Financial
        ('105560', 'KB금융', 'KB Financial Group', 'Financial', 'Banking'),
        ('055550', '신한지주', 'Shinhan Financial Group', 'Financial', 'Banking'),
        ('086790', '하나금융지주', 'Hana Financial Group', 'Financial', 'Banking'),
        ('316140', '우리금융지주', 'Woori Financial Group', 'Financial', 'Banking'),

        # Auto
        ('005380', '현대차', 'Hyundai Motor', 'Consumer Cyclical', 'Auto Manufacturers'),
        ('000270', '기아', 'Kia', 'Consumer Cyclical', 'Auto Manufacturers'),
        ('012330', '현대모비스', 'Hyundai Mobis', 'Consumer Cyclical', 'Auto Parts'),

        # Steel & Materials
        ('005490', 'POSCO홀딩스', 'POSCO Holdings', 'Basic Materials', 'Steel'),
        ('000810', '삼성화재', 'Samsung Fire & Marine Insurance', 'Financial', 'Insurance'),

        # Energy
        ('015760', '한국전력', 'Korea Electric Power', 'Utilities', 'Electric Utilities'),
        ('010950', 'S-Oil', 'S-Oil', 'Energy', 'Oil & Gas'),

        # Consumer
        ('097950', 'CJ제일제당', 'CJ CheilJedang', 'Consumer Defensive', 'Food Products'),
        ('271560', '오리온', 'Orion', 'Consumer Defensive', 'Confectioners'),
    ]

    # Generate additional synthetic KOSPI stocks
    KOSPI_TEMPLATES = [
        ('Technology', 'Software'),
        ('Technology', 'Electronics'),
        ('Healthcare', 'Pharmaceuticals'),
        ('Healthcare', 'Medical Devices'),
        ('Financial', 'Investment Banking'),
        ('Financial', 'Asset Management'),
        ('Industrial', 'Construction'),
        ('Industrial', 'Machinery'),
        ('Consumer Cyclical', 'Retail'),
        ('Consumer Cyclical', 'Entertainment'),
        ('Consumer Defensive', 'Beverages'),
        ('Consumer Defensive', 'Household Products'),
        ('Communication', 'Telecommunications'),
        ('Utilities', 'Gas Utilities'),
        ('Real Estate', 'REIT'),
    ]

    KOSDAQ_TEMPLATES = [
        ('Technology', 'Software'),
        ('Technology', 'Semiconductors'),
        ('Technology', 'IT Services'),
        ('Healthcare', 'Biotechnology'),
        ('Healthcare', 'Medical Equipment'),
        ('Industrial', 'Aerospace'),
        ('Consumer Cyclical', 'Gaming'),
        ('Consumer Cyclical', 'E-commerce'),
        ('Communication', 'Media'),
        ('Basic Materials', 'Chemicals'),
    ]

    # Korean company name patterns
    COMPANY_PREFIXES = ['한국', '대한', '동양', '서울', '부산', '인천', '경기', '강원', '제주']
    COMPANY_MIDDLES = ['테크', '바이오', '제약', '전자', '화학', '금융', '건설', '식품', '유통', '물산']
    COMPANY_SUFFIXES = ['', '홀딩스', '그룹', '코리아', '인터내셔널']

    def __init__(self, num_kospi: int = 100, num_kosdaq: int = 50, days: int = 252):
        self.num_kospi = num_kospi
        self.num_kosdaq = num_kosdaq
        self.days = days
        self.stocks: List[Dict] = []

    def generate_korean_company_name(self) -> Tuple[str, str]:
        """Generate realistic Korean company name"""
        kr_name = random.choice(self.COMPANY_PREFIXES) + random.choice(self.COMPANY_MIDDLES)
        if random.random() > 0.7:
            kr_name += random.choice(self.COMPANY_SUFFIXES)

        # Romanization (simplified)
        en_name = kr_name + ' Corp.'
        return kr_name, en_name

    def generate_stock_code(self, existing_codes: set) -> str:
        """Generate unique 6-digit stock code"""
        while True:
            code = f"{random.randint(0, 999999):06d}"
            if code not in existing_codes:
                return code

    def generate_stocks(self) -> List[Dict]:
        """Generate stock master data"""
        stocks = []
        existing_codes = set()

        # Add real KOSPI stocks
        for code, name_kr, name_en, sector, industry in self.KOSPI_STOCKS:
            existing_codes.add(code)
            stocks.append({
                'code': code,
                'name': name_kr,
                'name_english': name_en,
                'market': 'KOSPI',
                'sector': sector,
                'industry': industry,
                'listing_date': self._random_date(-3650, -365),  # 1-10 years ago
                'shares_outstanding': random.randint(100_000_000, 5_000_000_000),
            })

        # Generate additional KOSPI stocks
        remaining_kospi = self.num_kospi - len(self.KOSPI_STOCKS)
        for _ in range(remaining_kospi):
            code = self.generate_stock_code(existing_codes)
            existing_codes.add(code)
            name_kr, name_en = self.generate_korean_company_name()
            sector, industry = random.choice(self.KOSPI_TEMPLATES)

            stocks.append({
                'code': code,
                'name': name_kr,
                'name_english': name_en,
                'market': 'KOSPI',
                'sector': sector,
                'industry': industry,
                'listing_date': self._random_date(-3650, -365),
                'shares_outstanding': random.randint(100_000_000, 2_000_000_000),
            })

        # Generate KOSDAQ stocks
        for _ in range(self.num_kosdaq):
            code = self.generate_stock_code(existing_codes)
            existing_codes.add(code)
            name_kr, name_en = self.generate_korean_company_name()
            sector, industry = random.choice(self.KOSDAQ_TEMPLATES)

            stocks.append({
                'code': code,
                'name': name_kr,
                'name_english': name_en,
                'market': 'KOSDAQ',
                'sector': sector,
                'industry': industry,
                'listing_date': self._random_date(-2920, -180),  # 0.5-8 years ago
                'shares_outstanding': random.randint(50_000_000, 500_000_000),
            })

        self.stocks = stocks
        return stocks

    def generate_price_history(self, stock: Dict) -> List[Dict]:
        """Generate realistic daily price history"""
        prices = []

        # Initial price based on market cap tier
        if stock['market'] == 'KOSPI':
            base_price = random.randint(10000, 100000)
        else:
            base_price = random.randint(5000, 50000)

        current_price = base_price

        # Generate prices for last 252 trading days
        for i in range(self.days):
            trade_date = datetime.now() - timedelta(days=self.days - i)

            # Skip weekends (simplified - doesn't account for holidays)
            if trade_date.weekday() >= 5:
                continue

            # Random walk with slight upward bias
            daily_change = random.uniform(-0.03, 0.035)
            current_price = max(100, current_price * (1 + daily_change))

            # OHLC generation
            open_price = int(current_price * random.uniform(0.98, 1.02))
            close_price = int(current_price)
            high_price = int(max(open_price, close_price) * random.uniform(1.00, 1.02))
            low_price = int(min(open_price, close_price) * random.uniform(0.98, 1.00))

            # Volume proportional to market cap
            base_volume = stock['shares_outstanding'] // 1000
            volume = int(base_volume * random.uniform(0.5, 2.0))

            trading_value = volume * close_price
            market_cap = stock['shares_outstanding'] * close_price

            prices.append({
                'stock_code': stock['code'],
                'trade_date': trade_date.date(),
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'close_price': close_price,
                'adjusted_close': close_price,  # Simplified - no adjustments
                'volume': volume,
                'trading_value': trading_value,
                'market_cap': market_cap,
            })

        return prices

    def generate_financial_statements(self, stock: Dict, latest_price: int) -> List[Dict]:
        """Generate quarterly financial statements (last 4 quarters)"""
        statements = []

        # Base revenue proportional to market cap
        market_cap = stock['shares_outstanding'] * latest_price
        annual_revenue = int(market_cap * random.uniform(0.3, 1.5))

        for quarter in range(1, 5):
            # Quarterly revenue with seasonal variation
            quarterly_revenue = int(annual_revenue / 4 * random.uniform(0.8, 1.3))

            # Profit margins
            gross_margin = random.uniform(0.20, 0.50)
            operating_margin = random.uniform(0.05, 0.25)
            net_margin = random.uniform(0.03, 0.20)

            gross_profit = int(quarterly_revenue * gross_margin)
            operating_profit = int(quarterly_revenue * operating_margin)
            net_profit = int(quarterly_revenue * net_margin)

            # Balance sheet (simplified)
            total_assets = int(market_cap * random.uniform(1.2, 2.5))
            debt_ratio = random.uniform(0.15, 0.60)
            total_liabilities = int(total_assets * debt_ratio)
            equity = total_assets - total_liabilities

            # Cash flows
            operating_cf = int(net_profit * random.uniform(1.0, 1.5))
            capex = int(quarterly_revenue * random.uniform(0.05, 0.15))
            free_cf = operating_cf - capex

            fiscal_year = 2024 if quarter <= 3 else 2023
            actual_quarter = quarter if quarter <= 3 else 4
            report_date = date(fiscal_year, actual_quarter * 3, 1)

            statements.append({
                'stock_code': stock['code'],
                'period_type': 'quarterly',
                'fiscal_year': fiscal_year,
                'fiscal_quarter': actual_quarter,
                'report_date': report_date,
                'revenue': quarterly_revenue,
                'cost_of_revenue': quarterly_revenue - gross_profit,
                'gross_profit': gross_profit,
                'operating_profit': operating_profit,
                'net_profit': net_profit,
                'total_assets': total_assets,
                'total_liabilities': total_liabilities,
                'equity': equity,
                'operating_cash_flow': operating_cf,
                'free_cash_flow': free_cf,
                'capital_expenditure': capex,
            })

        return statements

    def generate_indicators(self, stock: Dict, latest_price: int, financials: List[Dict]) -> Dict:
        """Calculate technical and fundamental indicators"""
        latest_financial = financials[0] if financials else {}

        # Valuation metrics
        market_cap = stock['shares_outstanding'] * latest_price
        annual_revenue = sum(f.get('revenue', 0) for f in financials)
        annual_profit = sum(f.get('net_profit', 0) for f in financials)

        eps = annual_profit / stock['shares_outstanding'] if stock['shares_outstanding'] > 0 else 0
        per = latest_price / eps if eps > 0 else random.uniform(10, 30)

        book_value = latest_financial.get('equity', market_cap * 0.6)
        bps = book_value / stock['shares_outstanding'] if stock['shares_outstanding'] > 0 else latest_price * 0.8
        pbr = latest_price / bps if bps > 0 else random.uniform(0.5, 3.0)

        psr = market_cap / annual_revenue if annual_revenue > 0 else random.uniform(0.5, 5.0)

        # Profitability metrics
        roe = (annual_profit / book_value * 100) if book_value > 0 else random.uniform(5, 25)
        roa = (annual_profit / latest_financial.get('total_assets', market_cap * 1.5) * 100)

        gross_margin = (latest_financial.get('gross_profit', 0) / latest_financial.get('revenue', 1) * 100) if latest_financial.get('revenue') else random.uniform(20, 50)
        operating_margin = (latest_financial.get('operating_profit', 0) / latest_financial.get('revenue', 1) * 100) if latest_financial.get('revenue') else random.uniform(5, 25)
        net_margin = (annual_profit / annual_revenue * 100) if annual_revenue > 0 else random.uniform(3, 20)

        # Growth metrics
        revenue_growth = random.uniform(-10, 30)
        profit_growth = random.uniform(-15, 40)

        # Stability metrics
        debt_to_equity = (latest_financial.get('total_liabilities', 0) / latest_financial.get('equity', 1) * 100) if latest_financial.get('equity') else random.uniform(20, 80)
        current_ratio = random.uniform(1.0, 3.0)

        # Quality scores
        piotroski_f_score = random.randint(5, 9)
        quality_score = min(100, int(piotroski_f_score * 10 + random.uniform(0, 20)))
        value_score = min(100, int((30 - min(per, 30)) / 30 * 50 + (3 - min(pbr, 3)) / 3 * 30 + random.uniform(0, 20)))
        growth_score = min(100, int(max(0, revenue_growth + profit_growth) / 2 + random.uniform(20, 40)))
        overall_score = int((quality_score + value_score + growth_score) / 3)

        return {
            'stock_code': stock['code'],
            'calculation_date': date.today(),
            'per': round(per, 2),
            'pbr': round(pbr, 2),
            'psr': round(psr, 2),
            'dividend_yield': round(random.uniform(0, 5), 2),
            'roe': round(roe, 2),
            'roa': round(roa, 2),
            'gross_margin': round(gross_margin, 2),
            'operating_margin': round(operating_margin, 2),
            'net_margin': round(net_margin, 2),
            'revenue_growth_yoy': round(revenue_growth, 2),
            'profit_growth_yoy': round(profit_growth, 2),
            'debt_to_equity': round(debt_to_equity, 2),
            'current_ratio': round(current_ratio, 2),
            'piotroski_f_score': piotroski_f_score,
            'quality_score': quality_score,
            'value_score': value_score,
            'growth_score': growth_score,
            'overall_score': overall_score,
        }

    def _random_date(self, start_days: int, end_days: int) -> date:
        """Generate random date relative to today"""
        days = random.randint(start_days, end_days)
        return (datetime.now() + timedelta(days=days)).date()

    def generate_sql(self, output_file: str):
        """Generate SQL seed file"""
        print(f"Generating seed data for {self.num_kospi} KOSPI + {self.num_kosdaq} KOSDAQ stocks...")

        stocks = self.generate_stocks()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("""-- ============================================================================
-- Auto-generated Seed Data for Stock Screening Platform
-- Generated: {}
-- Stocks: {} KOSPI + {} KOSDAQ = {} total
-- Price History: {} trading days per stock
-- ============================================================================

BEGIN;

""".format(datetime.now().isoformat(), self.num_kospi, self.num_kosdaq,
           len(stocks), self.days))

            # Stocks
            f.write("-- ============================================================================\n")
            f.write(f"-- STOCKS ({len(stocks)} total)\n")
            f.write("-- ============================================================================\n\n")
            f.write("INSERT INTO stocks (code, name, name_english, market, sector, industry, listing_date, shares_outstanding) VALUES\n")

            stock_values = []
            for stock in stocks:
                stock_values.append("('{}', '{}', '{}', '{}', '{}', '{}', '{}', {})".format(
                    stock['code'], stock['name'], stock['name_english'],
                    stock['market'], stock['sector'], stock['industry'],
                    stock['listing_date'], stock['shares_outstanding']
                ))
            f.write(',\n'.join(stock_values))
            f.write("\nON CONFLICT (code) DO NOTHING;\n\n")

            print(f"✓ Generated {len(stocks)} stocks")

            # Prices
            f.write("-- ============================================================================\n")
            f.write("-- DAILY PRICES (bulk insert for performance)\n")
            f.write("-- ============================================================================\n\n")

            all_prices = []
            for i, stock in enumerate(stocks):
                if i % 10 == 0:
                    print(f"  Generating prices for stock {i+1}/{len(stocks)}...", end='\r')
                prices = self.generate_price_history(stock)
                all_prices.extend(prices)

            print(f"\n✓ Generated {len(all_prices)} price records")

            # Write prices in batches of 1000 for better performance
            batch_size = 1000
            for i in range(0, len(all_prices), batch_size):
                batch = all_prices[i:i+batch_size]
                f.write(f"-- Batch {i//batch_size + 1} ({len(batch)} records)\n")
                f.write("INSERT INTO daily_prices (stock_code, trade_date, open_price, high_price, low_price, close_price, adjusted_close, volume, trading_value, market_cap) VALUES\n")

                price_values = []
                for price in batch:
                    price_values.append("('{}', '{}', {}, {}, {}, {}, {}, {}, {}, {})".format(
                        price['stock_code'], price['trade_date'],
                        price['open_price'], price['high_price'], price['low_price'],
                        price['close_price'], price['adjusted_close'],
                        price['volume'], price['trading_value'], price['market_cap']
                    ))
                f.write(',\n'.join(price_values))
                f.write("\nON CONFLICT (stock_code, trade_date) DO NOTHING;\n\n")

            # Financial statements
            f.write("-- ============================================================================\n")
            f.write("-- FINANCIAL STATEMENTS\n")
            f.write("-- ============================================================================\n\n")

            all_financials = []
            for i, stock in enumerate(stocks):
                if i % 10 == 0:
                    print(f"  Generating financials for stock {i+1}/{len(stocks)}...", end='\r')
                # Get latest price for calculations
                latest_price = all_prices[-1]['close_price'] if all_prices else 50000
                financials = self.generate_financial_statements(stock, latest_price)
                all_financials.extend(financials)

            print(f"\n✓ Generated {len(all_financials)} financial statements")

            f.write("INSERT INTO financial_statements (stock_code, period_type, fiscal_year, fiscal_quarter, report_date, revenue, cost_of_revenue, gross_profit, operating_profit, net_profit, total_assets, total_liabilities, equity, operating_cash_flow, free_cash_flow, capital_expenditure) VALUES\n")

            fin_values = []
            for fin in all_financials:
                fin_values.append("('{}', '{}', {}, {}, '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(
                    fin['stock_code'], fin['period_type'], fin['fiscal_year'], fin['fiscal_quarter'],
                    fin['report_date'], fin['revenue'], fin['cost_of_revenue'], fin['gross_profit'],
                    fin['operating_profit'], fin['net_profit'], fin['total_assets'],
                    fin['total_liabilities'], fin['equity'], fin['operating_cash_flow'],
                    fin['free_cash_flow'], fin['capital_expenditure']
                ))
            f.write(',\n'.join(fin_values))
            f.write("\nON CONFLICT (stock_code, period_type, fiscal_year, fiscal_quarter) DO NOTHING;\n\n")

            # Indicators
            f.write("-- ============================================================================\n")
            f.write("-- CALCULATED INDICATORS\n")
            f.write("-- ============================================================================\n\n")

            f.write("INSERT INTO calculated_indicators (stock_code, calculation_date, per, pbr, psr, dividend_yield, roe, roa, gross_margin, operating_margin, net_margin, revenue_growth_yoy, profit_growth_yoy, debt_to_equity, current_ratio, piotroski_f_score, quality_score, value_score, growth_score, overall_score) VALUES\n")

            indicator_values = []
            for i, stock in enumerate(stocks):
                if i % 10 == 0:
                    print(f"  Generating indicators for stock {i+1}/{len(stocks)}...", end='\r')

                # Get stock's financial data
                stock_financials = [f for f in all_financials if f['stock_code'] == stock['code']]
                stock_prices = [p for p in all_prices if p['stock_code'] == stock['code']]
                latest_price = stock_prices[-1]['close_price'] if stock_prices else 50000

                indicators = self.generate_indicators(stock, latest_price, stock_financials)

                indicator_values.append("('{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(
                    indicators['stock_code'], indicators['calculation_date'],
                    indicators['per'], indicators['pbr'], indicators['psr'], indicators['dividend_yield'],
                    indicators['roe'], indicators['roa'], indicators['gross_margin'],
                    indicators['operating_margin'], indicators['net_margin'],
                    indicators['revenue_growth_yoy'], indicators['profit_growth_yoy'],
                    indicators['debt_to_equity'], indicators['current_ratio'],
                    indicators['piotroski_f_score'], indicators['quality_score'],
                    indicators['value_score'], indicators['growth_score'], indicators['overall_score']
                ))

            f.write(',\n'.join(indicator_values))
            f.write("\nON CONFLICT (stock_code, calculation_date) DO NOTHING;\n\n")

            print(f"\n✓ Generated {len(indicator_values)} indicator records")

            f.write("COMMIT;\n\n")
            f.write("-- ============================================================================\n")
            f.write("-- Seed data generation complete!\n")
            f.write(f"-- Total stocks: {len(stocks)}\n")
            f.write(f"-- Total prices: {len(all_prices)}\n")
            f.write(f"-- Total financials: {len(all_financials)}\n")
            f.write(f"-- Total indicators: {len(indicator_values)}\n")
            f.write("-- ============================================================================\n")

        print(f"\n✅ Seed data written to {output_file}")
        print(f"   Stocks: {len(stocks)}")
        print(f"   Prices: {len(all_prices)}")
        print(f"   Financials: {len(all_financials)}")
        print(f"   Indicators: {len(indicator_values)}")


def main():
    parser = argparse.ArgumentParser(description='Generate seed data for stock screening platform')
    parser.add_argument('--kospi', type=int, default=100, help='Number of KOSPI stocks (default: 100)')
    parser.add_argument('--kosdaq', type=int, default=50, help='Number of KOSDAQ stocks (default: 50)')
    parser.add_argument('--days', type=int, default=252, help='Number of trading days (default: 252)')
    parser.add_argument('--output', type=str, default='seeds/seed_data.sql', help='Output SQL file')

    args = parser.parse_args()

    generator = StockDataGenerator(
        num_kospi=args.kospi,
        num_kosdaq=args.kosdaq,
        days=args.days
    )

    generator.generate_sql(args.output)


if __name__ == '__main__':
    main()
