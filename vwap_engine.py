"""
VWAP Calculation Engine
Calculates Volume-Weighted Average Price across multiple timeframes
with 27% magnet level detection.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np


class VWAPEngine:
    """Core VWAP calculation engine with multi-timeframe support."""

    # Magnet percentages for detection
    MAGNET_LEVELS = [0.27, 1.27, 2.27, 3.27, 4.27]

    def __init__(self):
        self.cache = {}

    def calculate_vwap(self, df: pd.DataFrame, start_date: Optional[str] = None) -> float:
        """
        Calculate VWAP from price/volume data.

        Args:
            df: DataFrame with columns: timestamp, close, volume
            start_date: Optional start date to filter from

        Returns:
            VWAP value as float
        """
        if df.empty:
            return 0.0

        if start_date:
            df = df[df['timestamp'] >= start_date].copy()

        if df.empty or df['volume'].sum() == 0:
            return 0.0

        df['vwap_contribution'] = df['close'] * df['volume']
        total_volume = df['volume'].sum()
        total_value = df['vwap_contribution'].sum()

        return total_value / total_volume if total_volume > 0 else 0.0

    def calculate_all_vwaps(self, df: pd.DataFrame, current_price: Optional[float] = None) -> Dict:
        """
        Calculate VWAP for all timeframes.

        Args:
            df: DataFrame with price/volume data
            current_price: Optional current price for deviation calculation

        Returns:
            Dictionary with VWAP values for all timeframes
        """
        if df.empty:
            return self._empty_result()

        # Ensure timestamp column is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        latest_date = df['timestamp'].max()
        current_price = current_price or df['close'].iloc[-1]

        # Calculate timeframe start dates
        daily_start = latest_date.replace(hour=9, minute=30, second=0, microsecond=0)
        if latest_date.time() < datetime.strptime("09:30", "%H:%M").time():
            daily_start -= timedelta(days=1)

        three_month_start = latest_date - timedelta(days=90)
        quarter_start = self._get_quarter_start(latest_date)
        year_start = datetime(latest_date.year, 1, 1)

        # Calculate VWAPs
        vwaps = {
            'yearly': self.calculate_vwap(df, year_start.strftime('%Y-%m-%d')),
            'quarterly': self.calculate_vwap(df, quarter_start.strftime('%Y-%m-%d')),
            'three_month': self.calculate_vwap(df, three_month_start.strftime('%Y-%m-%d')),
            'daily': self.calculate_vwap(df, daily_start.strftime('%Y-%m-%d %H:%M:%S')),
        }

        # Calculate deviations
        deviations = {}
        for tf, vwap in vwaps.items():
            if vwap > 0:
                dev = ((current_price - vwap) / vwap) * 100
                deviations[tf] = {
                    'deviation_pct': round(dev, 2),
                    'deviation_dollars': round(current_price - vwap, 2),
                    'is_above': current_price > vwap
                }

        return {
            'vwaps': vwaps,
            'current_price': current_price,
            'deviations': deviations,
            'timestamp': latest_date.isoformat()
        }

    def find_magnet_levels(self, vwap: float, current_price: float,
                          price_range: Tuple[float, float] = None) -> List[Dict]:
        """
        Find 27% magnet levels near current price.

        Args:
            vwap: VWAP value
            current_price: Current stock price
            price_range: Optional (min, max) to filter results

        Returns:
            List of magnet level dictionaries
        """
        if vwap <= 0:
            return []

        magnets = []

        for pct in self.MAGNET_LEVELS:
            # Calculate levels above VWAP
            level_above = vwap * (1 + pct)
            magnets.append({
                'level': round(level_above, 2),
                'deviation_pct': round(pct * 100, 1),
                'type': 'above',
                'distance_from_price': abs(current_price - level_above),
                'is_nearby': abs(current_price - level_above) / current_price < 0.05
            })

            # Calculate levels below VWAP (except for 0%)
            if pct > 0:
                level_below = vwap * (1 - pct)
                magnets.append({
                    'level': round(level_below, 2),
                    'deviation_pct': round(-pct * 100, 1),
                    'type': 'below',
                    'distance_from_price': abs(current_price - level_below),
                    'is_nearby': abs(current_price - level_below) / current_price < 0.05
                })

        # Filter by price range if provided
        if price_range:
            min_price, max_price = price_range
            magnets = [m for m in magnets if min_price <= m['level'] <= max_price]

        # Sort by distance from current price
        magnets.sort(key=lambda x: x['distance_from_price'])

        return magnets

    def find_all_magnet_levels(self, vwaps: Dict, current_price: float) -> Dict:
        """
        Find magnet levels for all VWAP timeframes.

        Args:
            vwaps: Dictionary of VWAP values by timeframe
            current_price: Current stock price

        Returns:
            Dictionary of magnet levels by timeframe
        """
        all_magnets = {}

        for timeframe, vwap in vwaps.items():
            if vwap > 0:
                magnets = self.find_magnet_levels(vwap, current_price)
                # Only include nearby levels (within 10% of current price)
                nearby = [m for m in magnets if m['distance_from_price'] / current_price < 0.10]
                all_magnets[timeframe] = nearby[:5]  # Top 5 closest

        return all_magnets

    def _get_quarter_start(self, date: datetime) -> datetime:
        """Get the start date of the current quarter."""
        quarter = (date.month - 1) // 3
        month = quarter * 3 + 1
        return datetime(date.year, month, 1)

    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            'vwaps': {
                'yearly': 0,
                'quarterly': 0,
                'three_month': 0,
                'daily': 0
            },
            'current_price': 0,
            'deviations': {},
            'timestamp': datetime.now().isoformat()
        }


class VWAPAnalyzer:
    """Higher-level VWAP analysis with pattern detection."""

    def __init__(self, engine: VWAPEngine):
        self.engine = engine

    def analyze_price_action(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Comprehensive VWAP analysis including patterns and levels.

        Args:
            df: Historical price/volume data
            current_price: Current stock price

        Returns:
            Complete analysis dictionary
        """
        # Calculate all VWAPs
        vwap_data = self.engine.calculate_all_vwaps(df, current_price)

        # Find magnet levels
        magnets = self.engine.find_all_magnet_levels(vwap_data['vwaps'], current_price)

        # Determine strongest level
        strongest = self._find_strongest_level(vwap_data['vwaps'], magnets, current_price)

        # Support/Resistance analysis
        sr_analysis = self._analyze_support_resistance(df, current_price, vwap_data['vwaps'])

        return {
            **vwap_data,
            'magnet_levels': magnets,
            'strongest_level': strongest,
            'support_resistance': sr_analysis
        }

    def _find_strongest_level(self, vwaps: Dict, magnets: Dict, current_price: float) -> Dict:
        """Identify the strongest VWAP level near current price."""
        candidates = []

        # Add VWAP levels
        for tf, vwap in vwaps.items():
            if vwap > 0:
                distance = abs(current_price - vwap)
                if distance / current_price < 0.05:  # Within 5%
                    candidates.append({
                        'type': 'vwap',
                        'timeframe': tf,
                        'level': vwap,
                        'distance': distance
                    })

        # Add magnet levels
        for tf, magnet_list in magnets.items():
            for magnet in magnet_list[:2]:  # Top 2 per timeframe
                candidates.append({
                    'type': 'magnet',
                    'timeframe': tf,
                    'level': magnet['level'],
                    'distance': magnet['distance_from_price'],
                    'deviation_pct': magnet['deviation_pct']
                })

        if not candidates:
            return {}

        # Sort by distance and return closest
        candidates.sort(key=lambda x: x['distance'])
        return candidates[0]

    def _analyze_support_resistance(self, df: pd.DataFrame, current_price: float,
                                    vwaps: Dict) -> Dict:
        """Analyze support and resistance levels."""
        if df.empty:
            return {}

        # Find recent highs and lows
        recent_df = df.tail(20)
        recent_high = recent_df['high'].max()
        recent_low = recent_df['low'].min()

        # Determine if VWAPs are acting as support or resistance
        sr_levels = []
        for tf, vwap in vwaps.items():
            if vwap > 0:
                if current_price > vwap:
                    sr_levels.append({
                        'level': vwap,
                        'type': 'support',
                        'timeframe': tf
                    })
                else:
                    sr_levels.append({
                        'level': vwap,
                        'type': 'resistance',
                        'timeframe': tf
                    })

        return {
            'levels': sr_levels,
            'recent_high': recent_high,
            'recent_low': recent_low,
            'range_pct': ((recent_high - recent_low) / recent_low) * 100
        }


def calculate_vwap_simple(prices: List[float], volumes: List[int]) -> float:
    """
    Simple VWAP calculation from lists.

    Args:
        prices: List of prices
        volumes: List of volumes

    Returns:
        VWAP value
    """
    if len(prices) != len(volumes) or not prices:
        return 0.0

    total_value = sum(p * v for p, v in zip(prices, volumes))
    total_volume = sum(volumes)

    return total_value / total_volume if total_volume > 0 else 0.0
