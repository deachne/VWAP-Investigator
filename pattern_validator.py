#!/usr/bin/env python3
"""
Historical Pattern Validator
Tests VWAP patterns across diverse stock universe to prove they work statistically.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from vwap_engine import VWAPEngine
import os
from dotenv import load_dotenv
import time

load_dotenv()


class PatternValidator:
    """Validates VWAP patterns using historical data"""

    # Diverse stock universe (not all tech!)
    STOCK_UNIVERSE = {
        # Technology (4)
        'tech': ['AAPL', 'INTC', 'NVDA', 'MSFT'],

        # Financials (3)
        'financials': ['JPM', 'BAC', 'GS'],

        # Industrials (3)
        'industrials': ['CAT', 'BA', 'UNP'],

        # Consumer (3)
        'consumer': ['DIS', 'NKE', 'MCD'],

        # Energy (2)
        'energy': ['XOM', 'CVX'],

        # Agriculture/Commodities (2)
        'agriculture': ['DE', 'ADM'],

        # Healthcare (2)
        'healthcare': ['JNJ', 'UNH'],

        # Airlines (1)
        'airlines': ['UAL']
    }

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.results_cache = {}

    def get_all_tickers(self) -> List[str]:
        """Get flattened list of all tickers"""
        tickers = []
        for sector, ticker_list in self.STOCK_UNIVERSE.items():
            tickers.extend(ticker_list)
        return tickers

    def test_prior_quarterly_rejection(self, tickers: List[str] = None,
                                       tolerance_pct: float = 0.5) -> Dict:
        """
        Test Pattern 1: Prior Quarterly VWAP Rejection

        Find all instances where price touched prior quarterly VWAP
        and analyze if it rejected or broke through.

        Args:
            tickers: List of tickers to test (or None for all)
            tolerance_pct: % tolerance for "touch" (default 0.5%)

        Returns:
            Statistical validation results
        """
        if tickers is None:
            tickers = self.get_all_tickers()

        print(f"\n{'='*70}")
        print(f"PATTERN TEST: Prior Quarterly VWAP Rejection")
        print(f"{'='*70}")
        print(f"Testing {len(tickers)} stocks across sectors...")
        print(f"Tolerance: ±{tolerance_pct}%\n")

        all_results = []

        for i, ticker in enumerate(tickers, 1):
            print(f"[{i}/{len(tickers)}] Analyzing {ticker}...", end=' ')

            try:
                engine = VWAPEngine(ticker, self.api_key)
                df = engine.fetch_daily_data(outputsize='full')

                # Analyze quarterly rejections
                results = self._analyze_quarterly_rejections(df, engine, tolerance_pct)
                all_results.extend(results)

                print(f"✓ ({len(results)} instances)")

                # API rate limit (5 calls/min)
                if i % 5 == 0:
                    print("  ⏸ Rate limit pause (60s)...")
                    time.sleep(60)
                else:
                    time.sleep(1)

            except Exception as e:
                print(f"✗ Error: {str(e)[:50]}")
                continue

        # Aggregate results
        return self._aggregate_rejection_results(all_results)

    def _analyze_quarterly_rejections(self, df: pd.DataFrame, engine: VWAPEngine,
                                      tolerance_pct: float) -> List[Dict]:
        """Find quarterly rejection instances in historical data"""
        results = []

        # Get all prior quarters
        quarters = self._get_historical_quarters(df)

        for quarter_data in quarters:
            # Calculate VWAP for this quarter
            q_vwap = engine.calculate_vwap(
                df,
                quarter_data['start'],
                quarter_data['end']
            )

            if not q_vwap:
                continue

            # Get data AFTER quarter (when it becomes a prior level)
            future_data = df[df.index > quarter_data['end']].head(60)  # Next 60 days

            if future_data.empty:
                continue

            # Find touches of this prior quarterly VWAP
            tolerance = q_vwap['vwap'] * (tolerance_pct / 100)
            touches = future_data[
                (future_data['high'] >= q_vwap['vwap'] - tolerance) &
                (future_data['low'] <= q_vwap['vwap'] + tolerance)
            ]

            for touch_idx, touch_bar in touches.iterrows():
                # Analyze what happened after touch
                outcome = self._analyze_touch_outcome(
                    future_data,
                    touch_idx,
                    q_vwap['vwap'],
                    'rejection'
                )

                if outcome:
                    outcome['ticker'] = engine.ticker
                    outcome['quarter'] = quarter_data['label']
                    outcome['prior_vwap'] = q_vwap['vwap']
                    results.append(outcome)

        return results

    def _analyze_touch_outcome(self, df: pd.DataFrame, touch_date,
                               level: float, pattern_type: str) -> Optional[Dict]:
        """Analyze what happened after touching a level"""

        touch_bar = df.loc[touch_date]
        future_bars = df[df.index > touch_date].head(20)  # Next 20 bars

        if future_bars.empty:
            return None

        # Determine if rejected (closed below for resistance touch)
        touched_from_below = touch_bar['close'] < level

        if touched_from_below:
            # Testing resistance
            rejected = touch_bar['close'] < level and touch_bar['high'] >= level

            if rejected:
                # Find how far it fell
                lowest = future_bars['low'].min()
                bars_to_low = future_bars['low'].idxmin()
                bars_count = len(df.loc[touch_date:bars_to_low])
                reversal_size = ((lowest - level) / level) * 100

                return {
                    'type': 'rejection',
                    'rejected': True,
                    'date': touch_date,
                    'touch_price': touch_bar['high'],
                    'close': touch_bar['close'],
                    'reversal_size_pct': reversal_size,
                    'bars_to_low': bars_count,
                    'lowest_price': lowest
                }

        return None

    def test_sigma_support(self, tickers: List[str] = None,
                          sigma_level: float = -0.27) -> Dict:
        """
        Test Pattern 2: Sigma Support Bounce

        Find all instances where price touched a sigma level from yearly VWAP
        and analyze bounce behavior.

        Args:
            tickers: List of tickers to test
            sigma_level: Sigma level to test (default -0.27)

        Returns:
            Statistical validation results
        """
        if tickers is None:
            tickers = self.get_all_tickers()

        print(f"\n{'='*70}")
        print(f"PATTERN TEST: {sigma_level}σ Yearly VWAP Support")
        print(f"{'='*70}")
        print(f"Testing {len(tickers)} stocks across sectors...\n")

        all_results = []

        for i, ticker in enumerate(tickers, 1):
            print(f"[{i}/{len(tickers)}] Analyzing {ticker}...", end=' ')

            try:
                engine = VWAPEngine(ticker, self.api_key)
                df = engine.fetch_daily_data(outputsize='full')

                # Analyze sigma touches
                results = self._analyze_sigma_touches(df, engine, sigma_level)
                all_results.extend(results)

                print(f"✓ ({len(results)} instances)")

                # Rate limit
                if i % 5 == 0:
                    print("  ⏸ Rate limit pause (60s)...")
                    time.sleep(60)
                else:
                    time.sleep(1)

            except Exception as e:
                print(f"✗ Error: {str(e)[:50]}")
                continue

        return self._aggregate_sigma_results(all_results)

    def _analyze_sigma_touches(self, df: pd.DataFrame, engine: VWAPEngine,
                               sigma_level: float) -> List[Dict]:
        """Find sigma level touches in historical data"""
        results = []

        # Calculate yearly VWAP for each year in data
        years = df.index.year.unique()

        for year in years:
            year_start = datetime(year, 1, 1)
            year_data = df[df.index.year == year]

            if year_data.empty:
                continue

            # Calculate VWAP for this year progressively
            for i in range(30, len(year_data)):  # Start after 30 bars
                current_date = year_data.index[i]
                current_slice = df[
                    (df.index >= year_start) &
                    (df.index <= current_date)
                ]

                # Calculate VWAP up to this point
                vwap_data = engine.calculate_vwap(current_slice, year_start)

                if not vwap_data:
                    continue

                # Calculate sigma level
                sigma_price = vwap_data['vwap'] + (sigma_level * vwap_data['std_dev'])
                tolerance = vwap_data['vwap'] * 0.005  # 0.5% tolerance

                # Check if current bar touched this level
                current_bar = year_data.iloc[i]

                if (current_bar['low'] <= sigma_price + tolerance and
                    current_bar['high'] >= sigma_price - tolerance):

                    # Analyze bounce
                    future = year_data.iloc[i:i+20]
                    if len(future) > 5:
                        outcome = self._analyze_bounce_outcome(
                            future,
                            sigma_price,
                            vwap_data['vwap']
                        )

                        if outcome:
                            outcome['ticker'] = engine.ticker
                            outcome['year'] = year
                            outcome['sigma_level'] = sigma_level
                            outcome['vwap'] = vwap_data['vwap']
                            outcome['std_dev'] = vwap_data['std_dev']
                            results.append(outcome)

        return results

    def _analyze_bounce_outcome(self, future_df: pd.DataFrame,
                                support_level: float, vwap: float) -> Optional[Dict]:
        """Analyze what happened after touching support"""

        if future_df.empty or len(future_df) < 5:
            return None

        touch_bar = future_df.iloc[0]

        # Check if it bounced (closed above support)
        bounced = touch_bar['close'] > support_level

        if bounced:
            # Find high in next 20 bars
            highest = future_df['high'].max()
            bars_to_high = future_df['high'].idxmax()
            bars_count = len(future_df.loc[touch_bar.name:bars_to_high])

            bounce_size = ((highest - support_level) / support_level) * 100
            reached_vwap = highest >= vwap

            return {
                'bounced': True,
                'date': touch_bar.name,
                'touch_low': touch_bar['low'],
                'close': touch_bar['close'],
                'bounce_size_pct': bounce_size,
                'bars_to_high': bars_count,
                'highest_price': highest,
                'reached_vwap': reached_vwap
            }

        return None

    def _get_historical_quarters(self, df: pd.DataFrame) -> List[Dict]:
        """Get all complete quarters from data"""
        quarters = []
        years = df.index.year.unique()

        for year in years:
            for q in range(1, 5):
                q_start_month = (q - 1) * 3 + 1
                start = datetime(year, q_start_month, 1)

                if q == 4:
                    end = datetime(year, 12, 31)
                else:
                    end = datetime(year, q_start_month + 2, 28)

                # Only include if we have data
                q_data = df[(df.index >= start) & (df.index <= end)]
                if not q_data.empty:
                    quarters.append({
                        'year': year,
                        'quarter': q,
                        'start': start,
                        'end': end,
                        'label': f'Q{q} {year}'
                    })

        return quarters

    def _aggregate_rejection_results(self, results: List[Dict]) -> Dict:
        """Aggregate rejection pattern results"""

        if not results:
            return {'error': 'No instances found'}

        total = len(results)
        rejections = [r for r in results if r.get('rejected')]

        return {
            'pattern': 'Prior Quarterly VWAP Rejection',
            'total_instances': total,
            'rejections': len(rejections),
            'rejection_rate': len(rejections) / total * 100,
            'avg_reversal_size': np.mean([r['reversal_size_pct'] for r in rejections]),
            'avg_bars_to_low': np.mean([r['bars_to_low'] for r in rejections]),
            'instances_by_ticker': self._group_by_ticker(results),
            'instances_by_year': self._group_by_year(results)
        }

    def _aggregate_sigma_results(self, results: List[Dict]) -> Dict:
        """Aggregate sigma support pattern results"""

        if not results:
            return {'error': 'No instances found'}

        total = len(results)
        bounces = [r for r in results if r.get('bounced')]
        reached_vwap = [r for r in bounces if r.get('reached_vwap')]

        return {
            'pattern': f'{results[0]["sigma_level"]}σ Yearly VWAP Support',
            'total_instances': total,
            'bounces': len(bounces),
            'bounce_rate': len(bounces) / total * 100,
            'reached_vwap': len(reached_vwap),
            'vwap_reach_rate': len(reached_vwap) / len(bounces) * 100 if bounces else 0,
            'avg_bounce_size': np.mean([r['bounce_size_pct'] for r in bounces]),
            'avg_bars_to_high': np.mean([r['bars_to_high'] for r in bounces]),
            'instances_by_ticker': self._group_by_ticker(results),
            'instances_by_sector': self._group_by_sector(results)
        }

    def _group_by_ticker(self, results: List[Dict]) -> Dict:
        """Group results by ticker"""
        by_ticker = {}
        for r in results:
            ticker = r.get('ticker')
            if ticker not in by_ticker:
                by_ticker[ticker] = []
            by_ticker[ticker].append(r)
        return {t: len(r) for t, r in by_ticker.items()}

    def _group_by_year(self, results: List[Dict]) -> Dict:
        """Group results by year"""
        by_year = {}
        for r in results:
            year = r.get('year') or r.get('date').year
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(r)
        return {y: len(r) for y, r in by_year.items()}

    def _group_by_sector(self, results: List[Dict]) -> Dict:
        """Group results by sector"""
        by_sector = {}
        for r in results:
            ticker = r.get('ticker')
            sector = self._get_sector(ticker)
            if sector not in by_sector:
                by_sector[sector] = []
            by_sector[sector].append(r)
        return {s: len(r) for s, r in by_sector.items()}

    def _get_sector(self, ticker: str) -> str:
        """Get sector for a ticker"""
        for sector, tickers in self.STOCK_UNIVERSE.items():
            if ticker in tickers:
                return sector
        return 'unknown'

    def print_report(self, results: Dict):
        """Print formatted validation report"""

        print(f"\n{'='*70}")
        print(f"VALIDATION REPORT: {results['pattern']}")
        print(f"{'='*70}\n")

        print(f"Total Instances Found: {results['total_instances']}")

        if 'rejections' in results:
            print(f"Rejections: {results['rejections']} ({results['rejection_rate']:.1f}%)")
            print(f"Avg Reversal: {results['avg_reversal_size']:.2f}%")
            print(f"Avg Bars to Low: {results['avg_bars_to_low']:.1f}")

        if 'bounces' in results:
            print(f"Bounces: {results['bounces']} ({results['bounce_rate']:.1f}%)")
            print(f"Reached VWAP: {results['reached_vwap']} ({results['vwap_reach_rate']:.1f}%)")
            print(f"Avg Bounce: {results['avg_bounce_size']:.2f}%")
            print(f"Avg Bars to High: {results['avg_bars_to_high']:.1f}")

        print(f"\nBy Ticker:")
        for ticker, count in sorted(results['instances_by_ticker'].items(),
                                    key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {ticker}: {count}")

        if 'instances_by_sector' in results:
            print(f"\nBy Sector:")
            for sector, count in sorted(results['instances_by_sector'].items(),
                                       key=lambda x: x[1], reverse=True):
                print(f"  {sector}: {count}")

        # Validation status
        print(f"\n{'='*70}")
        if results.get('rejection_rate', 0) >= 80 or results.get('bounce_rate', 0) >= 80:
            print("STATUS: ✅ PATTERN VALIDATED (>80% success rate)")
        elif results.get('rejection_rate', 0) >= 70 or results.get('bounce_rate', 0) >= 70:
            print("STATUS: ⚠️ PATTERN VIABLE (70-80% success rate)")
        else:
            print("STATUS: ❌ PATTERN NOT VALIDATED (<70% success rate)")
        print(f"{'='*70}\n")


# Main execution
if __name__ == "__main__":
    validator = PatternValidator()

    print("\nVWAP Pattern Validator")
    print("="*70)
    print("\nStock Universe (20 stocks across 8 sectors):")
    for sector, tickers in validator.STOCK_UNIVERSE.items():
        print(f"  {sector.upper()}: {', '.join(tickers)}")

    print("\n" + "="*70)
    print("Select test to run:")
    print("1. Prior Quarterly VWAP Rejection")
    print("2. -0.27σ Yearly VWAP Support")
    print("3. Both tests")
    print("="*70)

    choice = input("\nEnter choice (1-3): ").strip()

    # Limit for testing (use all for production)
    test_tickers = validator.get_all_tickers()[:5]  # Start with 5 for testing

    if choice == '1' or choice == '3':
        results = validator.test_prior_quarterly_rejection(test_tickers)
        validator.print_report(results)

    if choice == '2' or choice == '3':
        results = validator.test_sigma_support(test_tickers)
        validator.print_report(results)
