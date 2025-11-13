#!/usr/bin/env python3
"""
Proven VWAP Calculation Engine
Handles: Yearly, Quarterly, Daily, Prior periods (ghost levels)
Multi-timeframe VWAP with standard deviation bands and sigma distance calculations

IMPORTANT METHODOLOGY:
- Current VWAPs (active/updating): Use SIGMA distance (volatility-adjusted)
- Prior VWAPs (static/completed): Use PERCENT distance (price-based only)

See docs/VWAP-DISTANCE-METHODOLOGY.md for detailed explanation.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests


class VWAPEngine:
    """Multi-timeframe VWAP calculation engine with standard deviation bands"""

    def __init__(self, ticker: str = None, api_key: str = None):
        self.ticker = ticker
        self.api_key = api_key
        # Key distance levels (magnet levels)
        self.key_levels = [0.27, 0.5, 1.0, 1.27, 1.618, 2.0, 2.27, 2.618]

    def fetch_daily_data(self, outputsize='full') -> pd.DataFrame:
        """Fetch daily OHLCV data from Alpha Vantage"""
        url = f'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': self.ticker,
            'outputsize': outputsize,
            'apikey': self.api_key
        }

        response = requests.get(url, params=params)
        data = response.json()

        if 'Time Series (Daily)' not in data:
            raise ValueError(f"Error fetching data: {data}")

        time_series = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        df.columns = ['open', 'high', 'low', 'close', 'volume']

        for col in df.columns:
            df[col] = pd.to_numeric(df[col])

        return df

    def calculate_vwap(self, df: pd.DataFrame, start_date: datetime,
                       end_date: Optional[datetime] = None) -> Dict:
        """Calculate VWAP for a specific period with std dev bands"""
        mask = df.index >= start_date
        if end_date:
            mask &= (df.index <= end_date)

        period_df = df[mask].copy()
        if len(period_df) == 0:
            return None

        # Typical price (HLC/3)
        period_df['typical_price'] = (period_df['high'] + period_df['low'] + period_df['close']) / 3

        # VWAP = sum(TP * V) / sum(V)
        period_df['tp_volume'] = period_df['typical_price'] * period_df['volume']
        cumsum_tp_volume = period_df['tp_volume'].cumsum()
        cumsum_volume = period_df['volume'].cumsum()
        period_df['vwap'] = cumsum_tp_volume / cumsum_volume

        # Std deviation
        period_df['deviation'] = period_df['typical_price'] - period_df['vwap']
        period_df['deviation_sq'] = period_df['deviation'] ** 2
        period_df['deviation_sq_volume'] = period_df['deviation_sq'] * period_df['volume']
        cumsum_dev_sq_volume = period_df['deviation_sq_volume'].cumsum()
        period_df['std_dev'] = np.sqrt(cumsum_dev_sq_volume / cumsum_volume)

        final_vwap = period_df['vwap'].iloc[-1]
        final_std = period_df['std_dev'].iloc[-1]

        # Deviation bands
        bands = {}
        for level in self.key_levels:
            bands[f'+{level}σ'] = final_vwap + (level * final_std)
            bands[f'-{level}σ'] = final_vwap - (level * final_std)

        return {
            'vwap': final_vwap,
            'std_dev': final_std,
            'bands': bands,
            'start_date': start_date,
            'end_date': end_date or df.index[-1],
            'num_bars': len(period_df)
        }

    def calculate_current_yearly_vwap(self, df: pd.DataFrame) -> Dict:
        """Calculate current year's VWAP"""
        current_year = datetime.now().year
        start_date = datetime(current_year, 1, 1)
        result = self.calculate_vwap(df, start_date)
        if result:
            result.update({
                'period_type': 'yearly',
                'year': current_year,
                'label': f"{current_year} Yearly VWAP",
                'is_current': True
            })
        return result

    def calculate_prior_yearly_vwaps(self, df: pd.DataFrame, num_years: int = 3) -> List[Dict]:
        """Calculate prior years' VWAPs (ghost levels)"""
        current_year = datetime.now().year
        results = []

        for year in range(current_year - num_years, current_year):
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            result = self.calculate_vwap(df, start_date, end_date)
            if result:
                result.update({
                    'period_type': 'yearly',
                    'year': year,
                    'label': f"{year} Yearly VWAP (Prior)",
                    'is_prior': True
                })
                results.append(result)
        return results

    def calculate_current_quarterly_vwap(self, df: pd.DataFrame) -> Dict:
        """Calculate current quarter's VWAP (true calendar quarter)"""
        now = datetime.now()
        quarter = (now.month - 1) // 3 + 1
        quarter_start_month = (quarter - 1) * 3 + 1
        start_date = datetime(now.year, quarter_start_month, 1)

        result = self.calculate_vwap(df, start_date)
        if result:
            result.update({
                'period_type': 'quarterly',
                'year': now.year,
                'quarter': quarter,
                'label': f"Q{quarter} {now.year} VWAP",
                'is_current': True
            })
        return result

    def calculate_prior_quarterly_vwaps(self, df: pd.DataFrame, num_quarters: int = 4) -> List[Dict]:
        """Calculate prior quarters' VWAPs"""
        now = datetime.now()
        current_quarter = (now.month - 1) // 3 + 1
        current_year = now.year
        results = []

        for i in range(1, num_quarters + 1):
            quarters_back = current_quarter - i
            year = current_year + (quarters_back // 4)
            quarter = quarters_back % 4
            if quarter <= 0:
                quarter += 4
                year -= 1

            quarter_starts = {1: 1, 2: 4, 3: 7, 4: 10}
            start_month = quarter_starts[quarter]
            start_date = datetime(year, start_month, 1)

            if quarter == 4:
                end_date = datetime(year, 12, 31)
            else:
                end_date = datetime(year, start_month + 2, 30)

            result = self.calculate_vwap(df, start_date, end_date)
            if result:
                result.update({
                    'period_type': 'quarterly',
                    'year': year,
                    'quarter': quarter,
                    'label': f"Q{quarter} {year} VWAP (Prior)",
                    'is_prior': True
                })
                results.append(result)
        return results

    def calculate_daily_vwap(self, df: pd.DataFrame) -> Dict:
        """Calculate today's VWAP (from market open)"""
        today = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
        result = self.calculate_vwap(df, today)
        if result:
            result.update({
                'period_type': 'daily',
                'label': "Daily VWAP",
                'is_current': True
            })
        return result

    def calculate_distance_from_vwap(self, current_price: float, vwap_value: float,
                                    std_dev: float) -> Dict:
        """Calculate precise distance from VWAP in % and sigma"""
        absolute_distance = current_price - vwap_value
        percent_distance = (absolute_distance / vwap_value) * 100
        sigma_distance = absolute_distance / std_dev if std_dev > 0 else 0

        # Find closest key level
        closest_level = None
        closest_distance = float('inf')
        for level in self.key_levels:
            for sign in [1, -1]:
                level_sigma = sign * level
                distance_to_level = abs(sigma_distance - level_sigma)
                if distance_to_level < closest_distance:
                    closest_distance = distance_to_level
                    closest_level = level_sigma

        return {
            'absolute_distance': absolute_distance,
            'percent_distance': percent_distance,
            'sigma_distance': sigma_distance,
            'closest_level': closest_level,
            'distance_to_closest_level': closest_distance,
            'is_near_key_level': closest_distance < 0.05
        }

    def get_all_vwaps(self, current_price: Optional[float] = None) -> Dict:
        """Calculate all VWAP types and distances"""
        df = self.fetch_daily_data()

        if current_price is None:
            current_price = float(df['close'].iloc[-1])

        vwaps = {
            'current_yearly': self.calculate_current_yearly_vwap(df),
            'prior_yearly': self.calculate_prior_yearly_vwaps(df, num_years=3),
            'current_quarterly': self.calculate_current_quarterly_vwap(df),
            'prior_quarterly': self.calculate_prior_quarterly_vwaps(df, num_quarters=4),
            'daily': self.calculate_daily_vwap(df),
        }

        # Add distances
        vwap_distances = {}
        for vwap_type, vwap_data in vwaps.items():
            if isinstance(vwap_data, list):
                vwap_distances[vwap_type] = []
                for vwap in vwap_data:
                    if vwap:
                        distance = self.calculate_distance_from_vwap(
                            current_price, vwap['vwap'], vwap['std_dev']
                        )
                        vwap_distances[vwap_type].append({**vwap, 'distance': distance})
            else:
                if vwap_data:
                    distance = self.calculate_distance_from_vwap(
                        current_price, vwap_data['vwap'], vwap_data['std_dev']
                    )
                    vwap_distances[vwap_type] = {**vwap_data, 'distance': distance}

        return {
            'ticker': self.ticker,
            'current_price': current_price,
            'vwaps': vwap_distances,
            'timestamp': datetime.now().isoformat()
        }


# Backwards compatibility with old API (for existing app.py integration)
class VWAPAnalyzer:
    """Wrapper for backwards compatibility with existing code"""

    def __init__(self, engine: VWAPEngine):
        self.engine = engine

    def analyze_price_action(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Comprehensive VWAP analysis - compatible with old interface

        Returns data structure matching old format for app.py integration
        """
        # Set engine properties if not set
        if not self.engine.ticker:
            self.engine.ticker = "UNKNOWN"

        # Calculate all VWAPs using new engine
        all_vwaps = self.engine.get_all_vwaps(current_price)

        # Transform to old format expected by app.py
        vwaps = {}
        deviations = {}

        # Current yearly
        if all_vwaps['vwaps'].get('current_yearly'):
            yearly = all_vwaps['vwaps']['current_yearly']
            vwaps['yearly'] = float(yearly['vwap'])
            deviations['yearly'] = {
                'deviation_pct': float(yearly['distance']['percent_distance']),
                'deviation_dollars': float(yearly['distance']['absolute_distance']),
                'is_above': yearly['distance']['absolute_distance'] > 0,
                'sigma': float(yearly['distance']['sigma_distance'])
            }

        # Current quarterly
        if all_vwaps['vwaps'].get('current_quarterly'):
            quarterly = all_vwaps['vwaps']['current_quarterly']
            vwaps['quarterly'] = float(quarterly['vwap'])
            deviations['quarterly'] = {
                'deviation_pct': float(quarterly['distance']['percent_distance']),
                'deviation_dollars': float(quarterly['distance']['absolute_distance']),
                'is_above': quarterly['distance']['absolute_distance'] > 0,
                'sigma': float(quarterly['distance']['sigma_distance'])
            }

        # Daily
        if all_vwaps['vwaps'].get('daily'):
            daily = all_vwaps['vwaps']['daily']
            vwaps['daily'] = float(daily['vwap'])
            deviations['daily'] = {
                'deviation_pct': float(daily['distance']['percent_distance']),
                'deviation_dollars': float(daily['distance']['absolute_distance']),
                'is_above': daily['distance']['absolute_distance'] > 0,
                'sigma': float(daily['distance']['sigma_distance'])
            }

        return {
            'vwaps': vwaps,
            'current_price': float(current_price),
            'deviations': deviations,
            'timestamp': all_vwaps['timestamp'],
            'magnet_levels': {},  # Will be populated by pattern detector
            'support_resistance': {},
            'all_vwaps_data': all_vwaps  # Full data including prior periods
        }


# Test
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

    engine = VWAPEngine('INTC', api_key)
    result = engine.get_all_vwaps()

    print(f"\n{'='*60}")
    print(f"VWAP Analysis for {result['ticker']}")
    print(f"Current Price: ${result['current_price']:.2f}")
    print(f"{'='*60}\n")

    # Current yearly
    yearly = result['vwaps']['current_yearly']
    print(f"{yearly['label']}")
    print(f"  VWAP: ${yearly['vwap']:.2f}")
    print(f"  Std Dev: ${yearly['std_dev']:.2f}")
    print(f"  Distance: {yearly['distance']['percent_distance']:.2f}%")
    print(f"  Sigma: {yearly['distance']['sigma_distance']:.2f}σ")
    print(f"  Closest Level: {yearly['distance']['closest_level']}σ\n")

    # Current quarterly
    quarterly = result['vwaps']['current_quarterly']
    print(f"{quarterly['label']}")
    print(f"  VWAP: ${quarterly['vwap']:.2f}")
    print(f"  Std Dev: ${quarterly['std_dev']:.2f}")
    print(f"  Distance: {quarterly['distance']['percent_distance']:.2f}%")
    print(f"  Sigma: {quarterly['distance']['sigma_distance']:.2f}σ\n")

    # Prior yearly (ghost levels)
    print("Prior Yearly VWAPs (Ghost Levels):")
    for prior in result['vwaps']['prior_yearly']:
        print(f"  {prior['label']}: ${prior['vwap']:.2f}")
