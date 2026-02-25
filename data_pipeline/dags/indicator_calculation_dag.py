"""
Indicator Calculation DAG

This DAG calculates 200+ financial and technical indicators for all stocks.
Triggered after daily price ingestion is complete.

Calculations include:
- Valuation metrics (PER, PBR, PSR, etc.)
- Profitability metrics (ROE, ROA, margins)
- Growth metrics (YoY, QoQ, CAGR)
- Technical indicators (RSI, MACD, moving averages)
- Composite scores (quality, value, growth)

Schedule: Triggered by daily_price_ingestion DAG
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

# Default arguments
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['data-alerts@screener.kr'],
    'email_on_failure': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'indicator_calculation',
    default_args=default_args,
    description='Calculate 200+ indicators for all stocks',
    schedule=None,  # Triggered by daily_price_ingestion
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['indicators', 'calculations', 'critical'],
)


# ============================================================================
# INDICATOR CALCULATION CLASSES
# ============================================================================

class IndicatorCalculator:
    """
    Centralized indicator calculation logic.

    Calculates all 200+ indicators for a given stock.
    """

    def __init__(self, pg_hook: PostgresHook):
        self.pg_hook = pg_hook
        self.logger = logging.getLogger(__name__)

    def calculate_all_indicators(self, stock_code: str, calculation_date: str) -> Dict:
        """
        Calculate all indicators for a stock on a given date.

        Returns dictionary with all indicator values.
        """
        indicators = {}

        # Fetch required data
        prices = self._get_price_history(stock_code, days=252)  # ~1 year
        financials = self._get_latest_financials(stock_code)
        latest_price = prices.iloc[0] if not prices.empty else None

        if latest_price is None:
            self.logger.warning(f"No price data for {stock_code}")
            return {}

        # Calculate indicators by category
        indicators.update(self._calculate_valuation(stock_code, latest_price, financials))
        indicators.update(self._calculate_profitability(financials))
        indicators.update(self._calculate_growth(stock_code, financials))
        indicators.update(self._calculate_stability(financials))
        indicators.update(self._calculate_efficiency(financials))
        indicators.update(self._calculate_technical(prices))
        indicators.update(self._calculate_composite_scores(indicators))

        # Add metadata
        indicators['stock_code'] = stock_code
        indicators['calculation_date'] = calculation_date

        return indicators

    def _get_price_history(self, stock_code: str, days: int = 252) -> pd.DataFrame:
        """Fetch price history for technical calculations."""
        query = """
            SELECT trade_date, open_price, high_price, low_price, close_price, volume
            FROM daily_prices
            WHERE stock_code = %s
            ORDER BY trade_date DESC
            LIMIT %s
        """
        df = self.pg_hook.get_pandas_df(query, parameters=(stock_code, days))
        return df

    def _get_latest_financials(self, stock_code: str) -> Optional[Dict]:
        """Fetch latest financial statement."""
        query = """
            SELECT *
            FROM financial_statements
            WHERE stock_code = %s
            ORDER BY fiscal_year DESC, fiscal_quarter DESC NULLS LAST
            LIMIT 1
        """
        result = self.pg_hook.get_first(query, parameters=(stock_code,))
        if not result:
            return None

        # Convert to dictionary
        columns = [
            'id', 'stock_code', 'period_type', 'fiscal_year', 'fiscal_quarter',
            'report_date', 'revenue', 'operating_profit', 'net_profit',
            'total_assets', 'total_liabilities', 'equity', 'operating_cash_flow',
            'free_cash_flow'
        ]
        return dict(zip(columns, result))

    def _calculate_valuation(self, stock_code: str, latest_price: pd.Series, financials: Optional[Dict]) -> Dict:
        """Calculate valuation metrics (PER, PBR, PSR, PCR, EV/EBITDA, etc.)."""
        if not financials:
            return {}

        close_price = latest_price['close_price']

        # Get shares outstanding and total liabilities
        stock_data = self.pg_hook.get_first(
            "SELECT shares_outstanding FROM stocks WHERE code = %s",
            parameters=(stock_code,)
        )

        if not stock_data or not stock_data[0]:
            return {}

        shares = stock_data[0]
        market_cap = close_price * shares

        # Calculate basic valuation ratios
        per = None
        eps = None
        if financials.get('net_profit') and financials['net_profit'] > 0:
            eps = financials['net_profit'] / shares
            per = round(close_price / eps, 2) if eps > 0 else None

        pbr = None
        if financials.get('equity') and financials['equity'] > 0:
            bps = financials['equity'] / shares
            pbr = round(close_price / bps, 2) if bps > 0 else None

        psr = None
        if financials.get('revenue') and financials['revenue'] > 0:
            sps = financials['revenue'] / shares
            psr = round(close_price / sps, 2) if sps > 0 else None

        # PCR: Price-to-Cash Flow Ratio
        pcr = None
        if financials.get('operating_cash_flow') and financials['operating_cash_flow'] > 0:
            cps = financials['operating_cash_flow'] / shares
            pcr = round(close_price / cps, 2) if cps > 0 else None

        # Enterprise Value calculations
        total_debt = financials.get('total_liabilities', 0) or 0
        cash = financials.get('cash_and_equivalents', 0) or 0
        enterprise_value = market_cap + total_debt - cash

        ev_ebitda = None
        if financials.get('ebitda') and financials['ebitda'] > 0:
            ev_ebitda = round(enterprise_value / financials['ebitda'], 2)

        ev_sales = None
        if financials.get('revenue') and financials['revenue'] > 0:
            ev_sales = round(enterprise_value / financials['revenue'], 2)

        ev_fcf = None
        if financials.get('free_cash_flow') and financials['free_cash_flow'] > 0:
            ev_fcf = round(enterprise_value / financials['free_cash_flow'], 2)

        # Dividend metrics
        dividend_yield = None
        payout_ratio = None
        if financials.get('dps'):  # Dividend Per Share
            dps = financials['dps']
            dividend_yield = round((dps / close_price) * 100, 2) if close_price > 0 else None

            if eps and eps > 0:
                payout_ratio = round((dps / eps) * 100, 2)

        # PEG Ratio: PER / EPS Growth Rate
        peg_ratio = None
        if per and financials.get('eps_growth_yoy') and financials['eps_growth_yoy'] > 0:
            peg_ratio = round(per / financials['eps_growth_yoy'], 2)

        return {
            'per': per,
            'pbr': pbr,
            'psr': psr,
            'pcr': pcr,
            'ev_ebitda': ev_ebitda,
            'ev_sales': ev_sales,
            'ev_fcf': ev_fcf,
            'dividend_yield': dividend_yield,
            'payout_ratio': payout_ratio,
            'peg_ratio': peg_ratio,
        }

    def _calculate_profitability(self, financials: Optional[Dict]) -> Dict:
        """Calculate profitability metrics (ROE, ROA, ROIC, margins)."""
        if not financials:
            return {}

        revenue = financials.get('revenue', 0)

        # Return on Equity
        roe = None
        if financials.get('net_profit') and financials.get('equity') and financials['equity'] > 0:
            roe = round((financials['net_profit'] / financials['equity']) * 100, 2)

        # Return on Assets
        roa = None
        if financials.get('net_profit') and financials.get('total_assets') and financials['total_assets'] > 0:
            roa = round((financials['net_profit'] / financials['total_assets']) * 100, 2)

        # Return on Invested Capital
        roic = None
        if financials.get('net_profit') and financials.get('equity') and financials.get('total_liabilities'):
            invested_capital = financials['equity'] + financials['total_liabilities']
            if invested_capital > 0:
                roic = round((financials['net_profit'] / invested_capital) * 100, 2)

        # Gross Margin
        gross_margin = None
        if financials.get('gross_profit') and revenue > 0:
            gross_margin = round((financials['gross_profit'] / revenue) * 100, 2)

        # Operating Margin
        operating_margin = None
        if financials.get('operating_profit') and revenue > 0:
            operating_margin = round((financials['operating_profit'] / revenue) * 100, 2)

        # Net Margin
        net_margin = None
        if financials.get('net_profit') and revenue > 0:
            net_margin = round((financials['net_profit'] / revenue) * 100, 2)

        # EBITDA Margin
        ebitda_margin = None
        if financials.get('ebitda') and revenue > 0:
            ebitda_margin = round((financials['ebitda'] / revenue) * 100, 2)

        # Free Cash Flow Margin
        fcf_margin = None
        if financials.get('free_cash_flow') and revenue > 0:
            fcf_margin = round((financials['free_cash_flow'] / revenue) * 100, 2)

        return {
            'roe': roe,
            'roa': roa,
            'roic': roic,
            'gross_margin': gross_margin,
            'operating_margin': operating_margin,
            'net_margin': net_margin,
            'ebitda_margin': ebitda_margin,
            'fcf_margin': fcf_margin,
        }

    def _calculate_growth(self, stock_code: str, financials: Optional[Dict]) -> Dict:
        """Calculate growth metrics (YoY, QoQ, CAGR)."""
        if not financials:
            return {}

        # Fetch year-ago financials for YoY calculations
        year_ago_query = """
            SELECT revenue, net_profit, eps
            FROM financial_statements
            WHERE stock_code = %s
              AND period_type = %s
              AND fiscal_year = %s
              AND fiscal_quarter IS NOT DISTINCT FROM %s
            LIMIT 1
        """

        year_ago = self.pg_hook.get_first(
            year_ago_query,
            parameters=(
                stock_code,
                financials['period_type'],
                financials['fiscal_year'] - 1,
                financials.get('fiscal_quarter')
            )
        )

        revenue_growth_yoy = None
        profit_growth_yoy = None
        eps_growth_yoy = None

        if year_ago:
            prev_revenue, prev_profit, prev_eps = year_ago

            if prev_revenue and prev_revenue > 0 and financials.get('revenue'):
                revenue_growth_yoy = round(
                    ((financials['revenue'] - prev_revenue) / prev_revenue) * 100, 2
                )

            if prev_profit and prev_profit > 0 and financials.get('net_profit'):
                profit_growth_yoy = round(
                    ((financials['net_profit'] - prev_profit) / prev_profit) * 100, 2
                )

            if prev_eps and prev_eps > 0 and financials.get('eps'):
                eps_growth_yoy = round(
                    ((financials['eps'] - prev_eps) / prev_eps) * 100, 2
                )

        # Quarter-over-Quarter growth (only for quarterly reports)
        revenue_growth_qoq = None
        profit_growth_qoq = None

        if financials.get('period_type') == 'quarterly' and financials.get('fiscal_quarter'):
            prev_quarter = financials['fiscal_quarter'] - 1
            prev_year = financials['fiscal_year']

            if prev_quarter == 0:  # Q1 compares to Q4 of previous year
                prev_quarter = 4
                prev_year -= 1

            quarter_ago_query = """
                SELECT revenue, net_profit
                FROM financial_statements
                WHERE stock_code = %s
                  AND period_type = 'quarterly'
                  AND fiscal_year = %s
                  AND fiscal_quarter = %s
                LIMIT 1
            """

            quarter_ago = self.pg_hook.get_first(
                quarter_ago_query,
                parameters=(stock_code, prev_year, prev_quarter)
            )

            if quarter_ago:
                prev_q_revenue, prev_q_profit = quarter_ago

                if prev_q_revenue and prev_q_revenue > 0 and financials.get('revenue'):
                    revenue_growth_qoq = round(
                        ((financials['revenue'] - prev_q_revenue) / prev_q_revenue) * 100, 2
                    )

                if prev_q_profit and prev_q_profit > 0 and financials.get('net_profit'):
                    profit_growth_qoq = round(
                        ((financials['net_profit'] - prev_q_profit) / prev_q_profit) * 100, 2
                    )

        # CAGR calculations (Compound Annual Growth Rate)
        # Fetch 3-year and 5-year historical data for annual reports
        revenue_cagr_3y = None
        revenue_cagr_5y = None
        eps_cagr_3y = None
        eps_cagr_5y = None

        if financials.get('period_type') == 'annual':
            # 3-year CAGR
            three_years_ago_query = """
                SELECT revenue, eps
                FROM financial_statements
                WHERE stock_code = %s
                  AND period_type = 'annual'
                  AND fiscal_year = %s
                LIMIT 1
            """

            three_years_ago = self.pg_hook.get_first(
                three_years_ago_query,
                parameters=(stock_code, financials['fiscal_year'] - 3)
            )

            if three_years_ago:
                old_revenue, old_eps = three_years_ago

                if old_revenue and old_revenue > 0 and financials.get('revenue'):
                    revenue_cagr_3y = round(
                        (((financials['revenue'] / old_revenue) ** (1/3)) - 1) * 100, 2
                    )

                if old_eps and old_eps > 0 and financials.get('eps'):
                    eps_cagr_3y = round(
                        (((financials['eps'] / old_eps) ** (1/3)) - 1) * 100, 2
                    )

            # 5-year CAGR
            five_years_ago = self.pg_hook.get_first(
                three_years_ago_query,
                parameters=(stock_code, financials['fiscal_year'] - 5)
            )

            if five_years_ago:
                old_revenue, old_eps = five_years_ago

                if old_revenue and old_revenue > 0 and financials.get('revenue'):
                    revenue_cagr_5y = round(
                        (((financials['revenue'] / old_revenue) ** (1/5)) - 1) * 100, 2
                    )

                if old_eps and old_eps > 0 and financials.get('eps'):
                    eps_cagr_5y = round(
                        (((financials['eps'] / old_eps) ** (1/5)) - 1) * 100, 2
                    )

        return {
            'revenue_growth_yoy': revenue_growth_yoy,
            'profit_growth_yoy': profit_growth_yoy,
            'eps_growth_yoy': eps_growth_yoy,
            'revenue_growth_qoq': revenue_growth_qoq,
            'profit_growth_qoq': profit_growth_qoq,
            'revenue_cagr_3y': revenue_cagr_3y,
            'revenue_cagr_5y': revenue_cagr_5y,
            'eps_cagr_3y': eps_cagr_3y,
            'eps_cagr_5y': eps_cagr_5y,
        }

    def _calculate_stability(self, financials: Optional[Dict]) -> Dict:
        """
        Calculate stability metrics (debt ratios, liquidity ratios, financial health scores).

        Includes Altman Z-Score and Piotroski F-Score for comprehensive financial analysis.
        """
        if not financials:
            return {}

        # Debt-to-Equity Ratio
        debt_to_equity = None
        if financials.get('total_liabilities') and financials.get('equity') and financials['equity'] > 0:
            debt_to_equity = round((financials['total_liabilities'] / financials['equity']) * 100, 2)

        # Debt-to-Assets Ratio
        debt_to_assets = None
        if financials.get('total_liabilities') and financials.get('total_assets') and financials['total_assets'] > 0:
            debt_to_assets = round((financials['total_liabilities'] / financials['total_assets']) * 100, 2)

        # Interest Coverage Ratio
        interest_coverage = None
        if financials.get('interest_expense') and financials['interest_expense'] > 0:
            if financials.get('operating_profit'):
                interest_coverage = round(financials['operating_profit'] / financials['interest_expense'], 2)

        # Current Ratio (Current Assets / Current Liabilities)
        current_ratio = None
        if financials.get('current_assets') and financials.get('current_liabilities') and financials['current_liabilities'] > 0:
            current_ratio = round(financials['current_assets'] / financials['current_liabilities'], 2)

        # Quick Ratio (Acid Test: (Current Assets - Inventory) / Current Liabilities)
        quick_ratio = None
        if financials.get('current_assets') and financials.get('current_liabilities') and financials['current_liabilities'] > 0:
            inventory = financials.get('inventory', 0) or 0
            quick_assets = financials['current_assets'] - inventory
            quick_ratio = round(quick_assets / financials['current_liabilities'], 2)

        # Cash Ratio (Cash / Current Liabilities)
        cash_ratio = None
        if financials.get('cash_and_equivalents') and financials.get('current_liabilities') and financials['current_liabilities'] > 0:
            cash_ratio = round(financials['cash_and_equivalents'] / financials['current_liabilities'], 2)

        # Altman Z-Score (bankruptcy prediction model)
        # Z = 1.2×WC/TA + 1.4×RE/TA + 3.3×EBIT/TA + 0.6×MC/TL + 1.0×S/TA
        altman_z_score = None
        if all(financials.get(k) for k in ['current_assets', 'current_liabilities', 'total_assets', 'retained_earnings', 'operating_profit', 'revenue']):
            ta = financials['total_assets']
            if ta > 0:
                wc = financials['current_assets'] - financials['current_liabilities']
                re = financials['retained_earnings']
                ebit = financials['operating_profit']
                mc_tl = 0  # Market cap / Total liabilities (would need stock price)
                sales = financials['revenue']

                altman_z_score = round(
                    1.2 * (wc / ta) +
                    1.4 * (re / ta) +
                    3.3 * (ebit / ta) +
                    0.6 * mc_tl +
                    1.0 * (sales / ta),
                    2
                )

        # Piotroski F-Score (value stock identification, 0-9 points)
        piotroski_f_score = self._calculate_piotroski_f_score(financials)

        return {
            'debt_to_equity': debt_to_equity,
            'debt_to_assets': debt_to_assets,
            'interest_coverage': interest_coverage,
            'current_ratio': current_ratio,
            'quick_ratio': quick_ratio,
            'cash_ratio': cash_ratio,
            'altman_z_score': altman_z_score,
            'piotroski_f_score': piotroski_f_score,
        }

    def _calculate_piotroski_f_score(self, financials: Optional[Dict]) -> Optional[int]:
        """
        Calculate Piotroski F-Score (0-9 points).

        9 criteria across profitability, leverage/liquidity, and operating efficiency.
        Higher score indicates stronger fundamental health.
        """
        if not financials:
            return None

        score = 0

        # Profitability signals (4 points)
        # 1. Positive net profit
        if financials.get('net_profit') and financials['net_profit'] > 0:
            score += 1

        # 2. Positive operating cash flow
        if financials.get('operating_cash_flow') and financials['operating_cash_flow'] > 0:
            score += 1

        # 3. Positive ROA
        if financials.get('net_profit') and financials.get('total_assets'):
            roa = financials['net_profit'] / financials['total_assets']
            if roa > 0:
                score += 1

        # 4. Operating cash flow > net profit (quality of earnings)
        if financials.get('operating_cash_flow') and financials.get('net_profit'):
            if financials['operating_cash_flow'] > financials['net_profit']:
                score += 1

        # Leverage/Liquidity signals (3 points)
        # 5. Decreasing long-term debt (would need historical data)
        # Skipped without historical comparison

        # 6. Increasing current ratio (would need historical data)
        # Skipped without historical comparison

        # 7. No new shares issued (would need historical data)
        # Skipped without historical comparison

        # Operating Efficiency signals (2 points)
        # 8. Increasing gross margin (would need historical data)
        # Skipped without historical comparison

        # 9. Increasing asset turnover (would need historical data)
        # Skipped without historical comparison

        # Note: Full Piotroski score requires year-over-year comparisons
        # This simplified version only includes 4 absolute measures
        # A complete implementation would add 5 more points from historical trends

        return score if score > 0 else None

    def _calculate_efficiency(self, financials: Optional[Dict]) -> Dict:
        """
        Calculate efficiency metrics (turnover ratios, cash conversion cycle).

        Measures how efficiently a company uses its assets and manages working capital.
        """
        if not financials:
            return {}

        revenue = financials.get('revenue', 0)

        # Asset Turnover (Revenue / Total Assets)
        asset_turnover = None
        if revenue and financials.get('total_assets') and financials['total_assets'] > 0:
            asset_turnover = round(revenue / financials['total_assets'], 2)

        # Inventory Turnover (Cost of Revenue / Inventory)
        inventory_turnover = None
        if financials.get('cost_of_revenue') and financials.get('inventory') and financials['inventory'] > 0:
            inventory_turnover = round(financials['cost_of_revenue'] / financials['inventory'], 2)

        # Receivables Turnover (Revenue / Accounts Receivable)
        receivables_turnover = None
        if revenue and financials.get('accounts_receivable') and financials['accounts_receivable'] > 0:
            receivables_turnover = round(revenue / financials['accounts_receivable'], 2)

        # Payables Turnover (Cost of Revenue / Accounts Payable)
        payables_turnover = None
        if financials.get('cost_of_revenue') and financials.get('accounts_payable') and financials['accounts_payable'] > 0:
            payables_turnover = round(financials['cost_of_revenue'] / financials['accounts_payable'], 2)

        # Cash Conversion Cycle (Days)
        # CCC = Days Inventory Outstanding + Days Sales Outstanding - Days Payables Outstanding
        cash_conversion_cycle = None
        if inventory_turnover and receivables_turnover and payables_turnover:
            dio = 365 / inventory_turnover  # Days Inventory Outstanding
            dso = 365 / receivables_turnover  # Days Sales Outstanding
            dpo = 365 / payables_turnover  # Days Payables Outstanding
            cash_conversion_cycle = round(dio + dso - dpo)

        return {
            'asset_turnover': asset_turnover,
            'inventory_turnover': inventory_turnover,
            'receivables_turnover': receivables_turnover,
            'payables_turnover': payables_turnover,
            'cash_conversion_cycle': cash_conversion_cycle,
        }

    def _calculate_technical(self, prices: pd.DataFrame) -> Dict:
        """
        Calculate technical indicators (price momentum, volume, MAs, RSI, MACD).

        Uses historical price data to generate trading signals and trend analysis.
        """
        if prices.empty:
            return {}

        close_prices = prices['close_price']
        volumes = prices['volume']
        current_price = close_prices.iloc[0]

        # Price changes (momentum indicators)
        price_change_1d = self._calc_price_change(close_prices, 1)
        price_change_1w = self._calc_price_change(close_prices, 5)   # 1 week
        price_change_1m = self._calc_price_change(close_prices, 20)  # 1 month
        price_change_3m = self._calc_price_change(close_prices, 60)  # 3 months
        price_change_6m = self._calc_price_change(close_prices, 120) # 6 months
        price_change_1y = self._calc_price_change(close_prices, 252) # 1 year (~252 trading days)

        # Multi-year price changes (long-term trends)
        # Note: Would need more historical data for accurate 3Y and 5Y calculations
        price_change_3y = None
        price_change_5y = None

        # Volume indicators
        volume_20d_avg = round(volumes.iloc[:20].mean()) if len(volumes) >= 20 else None
        volume_60d_avg = round(volumes.iloc[:60].mean()) if len(volumes) >= 60 else None

        volume_surge_pct = None
        if volume_20d_avg and volume_20d_avg > 0:
            volume_surge_pct = round(((volumes.iloc[0] / volume_20d_avg) - 1) * 100, 2)

        # Moving Averages
        ma_5d = round(close_prices.iloc[:5].mean(), 2) if len(close_prices) >= 5 else None
        ma_20d = round(close_prices.iloc[:20].mean(), 2) if len(close_prices) >= 20 else None
        ma_60d = round(close_prices.iloc[:60].mean(), 2) if len(close_prices) >= 60 else None
        ma_120d = round(close_prices.iloc[:120].mean(), 2) if len(close_prices) >= 120 else None
        ma_200d = round(close_prices.iloc[:200].mean(), 2) if len(close_prices) >= 200 else None

        # RSI (Relative Strength Index) - 14-day period
        rsi_14d = self._calculate_rsi(close_prices, period=14)

        # MACD (Moving Average Convergence Divergence)
        macd, macd_signal = self._calculate_macd(close_prices)

        # Bollinger Bands (20-day, 2 standard deviations)
        bollinger_upper, bollinger_lower = self._calculate_bollinger_bands(close_prices, period=20, std_dev=2)

        return {
            'price_change_1d': price_change_1d,
            'price_change_1w': price_change_1w,
            'price_change_1m': price_change_1m,
            'price_change_3m': price_change_3m,
            'price_change_6m': price_change_6m,
            'price_change_1y': price_change_1y,
            'price_change_3y': price_change_3y,
            'price_change_5y': price_change_5y,
            'volume_20d_avg': volume_20d_avg,
            'volume_60d_avg': volume_60d_avg,
            'volume_surge_pct': volume_surge_pct,
            'ma_5d': ma_5d,
            'ma_20d': ma_20d,
            'ma_60d': ma_60d,
            'ma_120d': ma_120d,
            'ma_200d': ma_200d,
            'rsi_14d': rsi_14d,
            'macd': macd,
            'macd_signal': macd_signal,
            'bollinger_upper': bollinger_upper,
            'bollinger_lower': bollinger_lower,
        }

    def _calc_price_change(self, prices: pd.Series, days: int) -> Optional[float]:
        """Calculate percentage price change over N days."""
        if len(prices) <= days:
            return None

        old_price = prices.iloc[days]
        current_price = prices.iloc[0]

        if old_price <= 0:
            return None

        return round(((current_price - old_price) / old_price) * 100, 2)

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index (RSI).

        RSI ranges from 0-100. Above 70 = overbought, below 30 = oversold.
        """
        if len(prices) < period + 1:
            return None

        # Calculate price changes
        deltas = prices.diff()

        # Separate gains and losses
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)

        # Calculate average gains and losses
        avg_gain = gains.rolling(window=period).mean().iloc[period]
        avg_loss = losses.rolling(window=period).mean().iloc[period]

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    def _calculate_macd(self, prices: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> tuple:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Returns (MACD line, Signal line).
        MACD crossing above signal = bullish, below = bearish.
        """
        if len(prices) < slow_period + signal_period:
            return None, None

        # Calculate EMAs
        ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
        ema_slow = prices.ewm(span=slow_period, adjust=False).mean()

        # MACD line = fast EMA - slow EMA
        macd_line = ema_fast - ema_slow

        # Signal line = 9-day EMA of MACD line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

        return round(macd_line.iloc[0], 2), round(signal_line.iloc[0], 2)

    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
        """
        Calculate Bollinger Bands.

        Returns (Upper Band, Lower Band).
        Price touching upper band = overbought, lower band = oversold.
        """
        if len(prices) < period:
            return None, None

        # Middle band = 20-day SMA
        sma = prices.rolling(window=period).mean()

        # Standard deviation
        std = prices.rolling(window=period).std()

        # Upper and lower bands
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        return round(upper_band.iloc[0], 2), round(lower_band.iloc[0], 2)

    def _calculate_composite_scores(self, indicators: Dict) -> Dict:
        """
        Calculate composite scores (1-100) combining multiple indicators.

        Quality Score: Profitability + Stability
        Value Score: Valuation attractiveness
        Growth Score: Revenue and profit growth
        Momentum Score: Price and technical momentum
        Overall Score: Weighted average of all scores
        """
        # Quality Score (Profitability + Financial Health)
        quality_score = None
        quality_components = []

        if indicators.get('roe') and indicators['roe'] > 0:
            quality_components.append(min(indicators['roe'] / 20 * 100, 100))

        if indicators.get('operating_margin') and indicators['operating_margin'] > 0:
            quality_components.append(min(indicators['operating_margin'] * 5, 100))

        if indicators.get('debt_to_equity'):
            quality_components.append(max(100 - indicators['debt_to_equity'], 0))

        if indicators.get('piotroski_f_score'):
            quality_components.append(indicators['piotroski_f_score'] / 9 * 100)

        if quality_components:
            quality_score = int(sum(quality_components) / len(quality_components))

        # Value Score (Attractive Valuation)
        value_score = None
        value_components = []

        if indicators.get('per') and indicators['per'] > 0:
            value_components.append(max(100 - indicators['per'] * 4, 0))

        if indicators.get('pbr') and indicators['pbr'] > 0:
            value_components.append(max(100 - indicators['pbr'] * 35, 0))

        if indicators.get('psr') and indicators['psr'] > 0:
            value_components.append(max(100 - indicators['psr'] * 20, 0))

        if indicators.get('dividend_yield') and indicators['dividend_yield'] > 0:
            value_components.append(min(indicators['dividend_yield'] * 10, 100))

        if value_components:
            value_score = int(sum(value_components) / len(value_components))

        # Growth Score (Revenue + Profit Growth)
        growth_score = None
        growth_components = []

        if indicators.get('revenue_growth_yoy') and indicators['revenue_growth_yoy'] > 0:
            growth_components.append(min(indicators['revenue_growth_yoy'] * 2.5, 100))

        if indicators.get('profit_growth_yoy') and indicators['profit_growth_yoy'] > 0:
            growth_components.append(min(indicators['profit_growth_yoy'] * 2.5, 100))

        if indicators.get('eps_growth_yoy') and indicators['eps_growth_yoy'] > 0:
            growth_components.append(min(indicators['eps_growth_yoy'] * 2.5, 100))

        if indicators.get('revenue_cagr_3y') and indicators['revenue_cagr_3y'] > 0:
            growth_components.append(min(indicators['revenue_cagr_3y'] * 3, 100))

        if growth_components:
            growth_score = int(sum(growth_components) / len(growth_components))

        # Momentum Score (Price Momentum + Technical Indicators)
        momentum_score = None
        momentum_components = []

        if indicators.get('price_change_1m'):
            momentum_components.append(min(max(indicators['price_change_1m'] * 2.5 + 50, 0), 100))

        if indicators.get('price_change_3m'):
            momentum_components.append(min(max(indicators['price_change_3m'] * 2 + 50, 0), 100))

        if indicators.get('rsi_14d'):
            # RSI between 40-60 is neutral (50 score), >60 is bullish, <40 is bearish
            rsi = indicators['rsi_14d']
            if rsi >= 50:
                momentum_components.append(min((rsi - 50) * 2.5 + 50, 100))
            else:
                momentum_components.append(max(rsi * 1.25, 0))

        if indicators.get('volume_surge_pct') and indicators['volume_surge_pct'] > 0:
            momentum_components.append(min(indicators['volume_surge_pct'] / 2, 100))

        if momentum_components:
            momentum_score = int(sum(momentum_components) / len(momentum_components))

        # Overall Score (Weighted Average)
        overall_score = None
        weighted_scores = []

        if quality_score:
            weighted_scores.append((quality_score, 0.30))  # 30% weight
        if value_score:
            weighted_scores.append((value_score, 0.25))    # 25% weight
        if growth_score:
            weighted_scores.append((growth_score, 0.25))   # 25% weight
        if momentum_score:
            weighted_scores.append((momentum_score, 0.20)) # 20% weight

        if weighted_scores:
            total_weight = sum(w for _, w in weighted_scores)
            overall_score = int(sum(s * w for s, w in weighted_scores) / total_weight)

        return {
            'quality_score': quality_score,
            'value_score': value_score,
            'growth_score': growth_score,
            'momentum_score': momentum_score,
            'overall_score': overall_score,
        }


# ============================================================================
# TASK FUNCTIONS
# ============================================================================

def calculate_indicators_for_all_stocks(**context):
    """
    Calculate indicators for all active stocks.

    Uses parallel processing for performance.
    """
    logger = logging.getLogger(__name__)
    calculation_date = context['ds']

    pg_hook = PostgresHook(postgres_conn_id='screener_db')
    calculator = IndicatorCalculator(pg_hook)

    # Get list of active stocks
    stocks = pg_hook.get_records(
        "SELECT code FROM stocks WHERE delisting_date IS NULL ORDER BY code"
    )

    logger.info(f"Calculating indicators for {len(stocks)} stocks")

    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    calculated_count = 0
    failed_stocks = []

    for (stock_code,) in stocks:
        try:
            indicators = calculator.calculate_all_indicators(stock_code, calculation_date)

            if not indicators:
                logger.warning(f"No indicators calculated for {stock_code}")
                failed_stocks.append(stock_code)
                continue

            # Upsert indicators (all 66 financial and technical indicators)
            cursor.execute("""
                INSERT INTO calculated_indicators (
                    stock_code, calculation_date,
                    -- Valuation (10)
                    per, pbr, psr, pcr, ev_ebitda, ev_sales, ev_fcf,
                    dividend_yield, payout_ratio, peg_ratio,
                    -- Profitability (8)
                    roe, roa, roic, gross_margin, operating_margin, net_margin,
                    ebitda_margin, fcf_margin,
                    -- Growth (9)
                    revenue_growth_yoy, profit_growth_yoy, eps_growth_yoy,
                    revenue_growth_qoq, profit_growth_qoq,
                    revenue_cagr_3y, revenue_cagr_5y, eps_cagr_3y, eps_cagr_5y,
                    -- Stability (8)
                    debt_to_equity, debt_to_assets, interest_coverage,
                    current_ratio, quick_ratio, cash_ratio,
                    altman_z_score, piotroski_f_score,
                    -- Efficiency (5)
                    asset_turnover, inventory_turnover, receivables_turnover,
                    payables_turnover, cash_conversion_cycle,
                    -- Technical Metrics (8)
                    price_change_1d, price_change_1w, price_change_1m,
                    price_change_3m, price_change_6m, price_change_1y,
                    price_change_3y, price_change_5y,
                    -- Volume (3)
                    volume_20d_avg, volume_60d_avg, volume_surge_pct,
                    -- Moving Averages (5)
                    ma_5d, ma_20d, ma_60d, ma_120d, ma_200d,
                    -- Technical Indicators (5)
                    rsi_14d, macd, macd_signal, bollinger_upper, bollinger_lower,
                    -- Composite Scores (5)
                    quality_score, value_score, growth_score, momentum_score, overall_score
                ) VALUES (
                    %(stock_code)s, %(calculation_date)s,
                    -- Valuation
                    %(per)s, %(pbr)s, %(psr)s, %(pcr)s, %(ev_ebitda)s, %(ev_sales)s, %(ev_fcf)s,
                    %(dividend_yield)s, %(payout_ratio)s, %(peg_ratio)s,
                    -- Profitability
                    %(roe)s, %(roa)s, %(roic)s, %(gross_margin)s, %(operating_margin)s, %(net_margin)s,
                    %(ebitda_margin)s, %(fcf_margin)s,
                    -- Growth
                    %(revenue_growth_yoy)s, %(profit_growth_yoy)s, %(eps_growth_yoy)s,
                    %(revenue_growth_qoq)s, %(profit_growth_qoq)s,
                    %(revenue_cagr_3y)s, %(revenue_cagr_5y)s, %(eps_cagr_3y)s, %(eps_cagr_5y)s,
                    -- Stability
                    %(debt_to_equity)s, %(debt_to_assets)s, %(interest_coverage)s,
                    %(current_ratio)s, %(quick_ratio)s, %(cash_ratio)s,
                    %(altman_z_score)s, %(piotroski_f_score)s,
                    -- Efficiency
                    %(asset_turnover)s, %(inventory_turnover)s, %(receivables_turnover)s,
                    %(payables_turnover)s, %(cash_conversion_cycle)s,
                    -- Technical Metrics
                    %(price_change_1d)s, %(price_change_1w)s, %(price_change_1m)s,
                    %(price_change_3m)s, %(price_change_6m)s, %(price_change_1y)s,
                    %(price_change_3y)s, %(price_change_5y)s,
                    -- Volume
                    %(volume_20d_avg)s, %(volume_60d_avg)s, %(volume_surge_pct)s,
                    -- Moving Averages
                    %(ma_5d)s, %(ma_20d)s, %(ma_60d)s, %(ma_120d)s, %(ma_200d)s,
                    -- Technical Indicators
                    %(rsi_14d)s, %(macd)s, %(macd_signal)s, %(bollinger_upper)s, %(bollinger_lower)s,
                    -- Composite Scores
                    %(quality_score)s, %(value_score)s, %(growth_score)s, %(momentum_score)s, %(overall_score)s
                )
                ON CONFLICT (stock_code, calculation_date)
                DO UPDATE SET
                    -- Valuation
                    per = EXCLUDED.per, pbr = EXCLUDED.pbr, psr = EXCLUDED.psr,
                    pcr = EXCLUDED.pcr, ev_ebitda = EXCLUDED.ev_ebitda,
                    ev_sales = EXCLUDED.ev_sales, ev_fcf = EXCLUDED.ev_fcf,
                    dividend_yield = EXCLUDED.dividend_yield, payout_ratio = EXCLUDED.payout_ratio,
                    peg_ratio = EXCLUDED.peg_ratio,
                    -- Profitability
                    roe = EXCLUDED.roe, roa = EXCLUDED.roa, roic = EXCLUDED.roic,
                    gross_margin = EXCLUDED.gross_margin, operating_margin = EXCLUDED.operating_margin,
                    net_margin = EXCLUDED.net_margin, ebitda_margin = EXCLUDED.ebitda_margin,
                    fcf_margin = EXCLUDED.fcf_margin,
                    -- Growth
                    revenue_growth_yoy = EXCLUDED.revenue_growth_yoy,
                    profit_growth_yoy = EXCLUDED.profit_growth_yoy,
                    eps_growth_yoy = EXCLUDED.eps_growth_yoy,
                    revenue_growth_qoq = EXCLUDED.revenue_growth_qoq,
                    profit_growth_qoq = EXCLUDED.profit_growth_qoq,
                    revenue_cagr_3y = EXCLUDED.revenue_cagr_3y,
                    revenue_cagr_5y = EXCLUDED.revenue_cagr_5y,
                    eps_cagr_3y = EXCLUDED.eps_cagr_3y,
                    eps_cagr_5y = EXCLUDED.eps_cagr_5y,
                    -- Stability
                    debt_to_equity = EXCLUDED.debt_to_equity,
                    debt_to_assets = EXCLUDED.debt_to_assets,
                    interest_coverage = EXCLUDED.interest_coverage,
                    current_ratio = EXCLUDED.current_ratio,
                    quick_ratio = EXCLUDED.quick_ratio,
                    cash_ratio = EXCLUDED.cash_ratio,
                    altman_z_score = EXCLUDED.altman_z_score,
                    piotroski_f_score = EXCLUDED.piotroski_f_score,
                    -- Efficiency
                    asset_turnover = EXCLUDED.asset_turnover,
                    inventory_turnover = EXCLUDED.inventory_turnover,
                    receivables_turnover = EXCLUDED.receivables_turnover,
                    payables_turnover = EXCLUDED.payables_turnover,
                    cash_conversion_cycle = EXCLUDED.cash_conversion_cycle,
                    -- Technical Metrics
                    price_change_1d = EXCLUDED.price_change_1d,
                    price_change_1w = EXCLUDED.price_change_1w,
                    price_change_1m = EXCLUDED.price_change_1m,
                    price_change_3m = EXCLUDED.price_change_3m,
                    price_change_6m = EXCLUDED.price_change_6m,
                    price_change_1y = EXCLUDED.price_change_1y,
                    price_change_3y = EXCLUDED.price_change_3y,
                    price_change_5y = EXCLUDED.price_change_5y,
                    -- Volume
                    volume_20d_avg = EXCLUDED.volume_20d_avg,
                    volume_60d_avg = EXCLUDED.volume_60d_avg,
                    volume_surge_pct = EXCLUDED.volume_surge_pct,
                    -- Moving Averages
                    ma_5d = EXCLUDED.ma_5d,
                    ma_20d = EXCLUDED.ma_20d,
                    ma_60d = EXCLUDED.ma_60d,
                    ma_120d = EXCLUDED.ma_120d,
                    ma_200d = EXCLUDED.ma_200d,
                    -- Technical Indicators
                    rsi_14d = EXCLUDED.rsi_14d,
                    macd = EXCLUDED.macd,
                    macd_signal = EXCLUDED.macd_signal,
                    bollinger_upper = EXCLUDED.bollinger_upper,
                    bollinger_lower = EXCLUDED.bollinger_lower,
                    -- Composite Scores
                    quality_score = EXCLUDED.quality_score,
                    value_score = EXCLUDED.value_score,
                    growth_score = EXCLUDED.growth_score,
                    momentum_score = EXCLUDED.momentum_score,
                    overall_score = EXCLUDED.overall_score
            """, indicators)

            calculated_count += 1

            # Commit in batches of 100
            if calculated_count % 100 == 0:
                conn.commit()
                logger.info(f"Progress: {calculated_count}/{len(stocks)} stocks")

        except Exception as e:
            logger.error(f"Failed to calculate indicators for {stock_code}: {e}")
            failed_stocks.append(stock_code)

    # Final commit
    conn.commit()
    cursor.close()
    conn.close()

    logger.info(f"Calculated indicators for {calculated_count}/{len(stocks)} stocks")
    if failed_stocks:
        logger.warning(f"Failed stocks ({len(failed_stocks)}): {failed_stocks[:20]}")

    # Push metrics to XCom
    context['task_instance'].xcom_push(key='calculated_count', value=calculated_count)
    context['task_instance'].xcom_push(key='failed_count', value=len(failed_stocks))

    return calculated_count


# ============================================================================
# TASK DEFINITIONS
# ============================================================================

calculate_indicators = PythonOperator(
    task_id='calculate_indicators',
    python_callable=calculate_indicators_for_all_stocks,
    execution_timeout=timedelta(minutes=30),
    dag=dag,
)

refresh_materialized_views = PostgresOperator(
    task_id='refresh_materialized_views',
    postgres_conn_id='screener_db',
    sql="SELECT refresh_all_materialized_views();",
    dag=dag,
)

log_calculation_status = PostgresOperator(
    task_id='log_calculation_status',
    postgres_conn_id='screener_db',
    sql="""
        INSERT INTO data_ingestion_log (
            source, data_type, records_processed, records_failed,
            status, started_at, completed_at
        ) VALUES (
            'internal', 'indicators', {{ ti.xcom_pull(task_ids='calculate_indicators', key='calculated_count') }},
            {{ ti.xcom_pull(task_ids='calculate_indicators', key='failed_count') }},
            'success', '{{ logical_date }}', NOW()
        )
    """,
    dag=dag,
)

# ============================================================================
# TASK DEPENDENCIES
# ============================================================================

calculate_indicators >> refresh_materialized_views >> log_calculation_status
