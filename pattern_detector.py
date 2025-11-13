"""
Pattern Detection for VWAP Trading
Detects key patterns: unbroken priors, failed breaks, confluences, reclaims.
"""

from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, timedelta


class PatternDetector:
    """Detects trading patterns in VWAP price action."""

    def __init__(self, lookback_days: int = 30):
        """
        Initialize pattern detector.

        Args:
            lookback_days: Number of days to look back for pattern detection
        """
        self.lookback_days = lookback_days

    def detect_all_patterns(self, df: pd.DataFrame, vwaps: Dict,
                           current_price: float) -> Dict:
        """
        Detect all patterns for a given dataset.

        Args:
            df: Historical price data
            vwaps: Dictionary of VWAP values by timeframe
            current_price: Current stock price

        Returns:
            Dictionary of detected patterns
        """
        patterns = {
            'unbroken_priors': self.find_unbroken_priors(df, vwaps),
            'failed_breaks': self.find_failed_breaks(df, vwaps),
            'confluences': self.find_confluences(vwaps, current_price),
            'reclaims': self.find_reclaims(df, vwaps),
            'magnet_interactions': self.find_magnet_interactions(df, vwaps)
        }

        return patterns

    def find_unbroken_priors(self, df: pd.DataFrame, vwaps: Dict) -> List[Dict]:
        """
        Find VWAP levels that have not been broken recently.

        Args:
            df: Historical price data
            vwaps: VWAP levels by timeframe

        Returns:
            List of unbroken VWAP levels with metadata
        """
        if df.empty:
            return []

        # Get recent data
        cutoff_date = df['timestamp'].max() - timedelta(days=self.lookback_days)
        recent_df = df[df['timestamp'] >= cutoff_date]

        unbroken = []

        for timeframe, vwap in vwaps.items():
            if vwap <= 0:
                continue

            # Check if price has broken above/below this VWAP
            max_high = recent_df['high'].max()
            min_low = recent_df['low'].min()
            current_close = recent_df['close'].iloc[-1]

            # Determine if it's an unbroken support or resistance
            if current_close > vwap and min_low > vwap:
                unbroken.append({
                    'timeframe': timeframe,
                    'level': vwap,
                    'type': 'support',
                    'days_unbroken': self.lookback_days,
                    'distance_from_price': abs(current_close - vwap),
                    'strength': 'strong'
                })
            elif current_close < vwap and max_high < vwap:
                unbroken.append({
                    'timeframe': timeframe,
                    'level': vwap,
                    'type': 'resistance',
                    'days_unbroken': self.lookback_days,
                    'distance_from_price': abs(current_close - vwap),
                    'strength': 'strong'
                })

        return unbroken

    def find_failed_breaks(self, df: pd.DataFrame, vwaps: Dict,
                          lookback: int = 10) -> List[Dict]:
        """
        Find recent failed breakout attempts of VWAP levels.

        Args:
            df: Historical price data
            vwaps: VWAP levels by timeframe
            lookback: Days to look back for failed breaks

        Returns:
            List of failed break patterns
        """
        if df.empty:
            return []

        cutoff_date = df['timestamp'].max() - timedelta(days=lookback)
        recent_df = df[df['timestamp'] >= cutoff_date].copy()

        failed_breaks = []

        for timeframe, vwap in vwaps.items():
            if vwap <= 0:
                continue

            # Find candles that touched/crossed VWAP but closed on the wrong side
            for idx, row in recent_df.iterrows():
                # Check for failed bullish break
                if row['high'] >= vwap and row['close'] < vwap:
                    failed_breaks.append({
                        'timeframe': timeframe,
                        'level': vwap,
                        'type': 'failed_bullish_break',
                        'date': row['timestamp'],
                        'candle_close': row['close'],
                        'days_ago': (recent_df['timestamp'].max() - row['timestamp']).days
                    })

                # Check for failed bearish break
                if row['low'] <= vwap and row['close'] > vwap:
                    failed_breaks.append({
                        'timeframe': timeframe,
                        'level': vwap,
                        'type': 'failed_bearish_break',
                        'date': row['timestamp'],
                        'candle_close': row['close'],
                        'days_ago': (recent_df['timestamp'].max() - row['timestamp']).days
                    })

        return failed_breaks

    def find_confluences(self, vwaps: Dict, current_price: float,
                        threshold: float = 0.01) -> List[Dict]:
        """
        Find areas where multiple VWAP levels converge.

        Args:
            vwaps: VWAP levels by timeframe
            current_price: Current stock price
            threshold: Percentage threshold for confluence (default 1%)

        Returns:
            List of confluence zones
        """
        confluences = []
        vwap_list = [(tf, vwap) for tf, vwap in vwaps.items() if vwap > 0]

        # Check each pair of VWAPs
        for i, (tf1, vwap1) in enumerate(vwap_list):
            confluent_levels = [(tf1, vwap1)]

            for tf2, vwap2 in vwap_list[i+1:]:
                # Check if vwaps are within threshold
                if abs(vwap1 - vwap2) / vwap1 <= threshold:
                    confluent_levels.append((tf2, vwap2))

            # If we found a confluence (2+ levels close together)
            if len(confluent_levels) >= 2:
                avg_level = sum(v for _, v in confluent_levels) / len(confluent_levels)
                distance = abs(current_price - avg_level)

                confluences.append({
                    'level': avg_level,
                    'timeframes': [tf for tf, _ in confluent_levels],
                    'count': len(confluent_levels),
                    'strength': 'very_strong' if len(confluent_levels) >= 3 else 'strong',
                    'distance_from_price': distance,
                    'is_nearby': distance / current_price < 0.02  # Within 2%
                })

        # Remove duplicates and sort by strength
        unique_confluences = []
        seen_levels = set()

        for conf in sorted(confluences, key=lambda x: -x['count']):
            level_key = round(conf['level'], 2)
            if level_key not in seen_levels:
                seen_levels.add(level_key)
                unique_confluences.append(conf)

        return unique_confluences

    def find_reclaims(self, df: pd.DataFrame, vwaps: Dict,
                     lookback: int = 5) -> List[Dict]:
        """
        Find recent reclaims of VWAP levels (price crossing back above/below).

        Args:
            df: Historical price data
            vwaps: VWAP levels by timeframe
            lookback: Days to look back for reclaims

        Returns:
            List of reclaim patterns
        """
        if df.empty:
            return []

        cutoff_date = df['timestamp'].max() - timedelta(days=lookback)
        recent_df = df[df['timestamp'] >= cutoff_date].copy()

        if len(recent_df) < 2:
            return []

        reclaims = []

        for timeframe, vwap in vwaps.items():
            if vwap <= 0:
                continue

            # Check for price crossing VWAP
            recent_df['above_vwap'] = recent_df['close'] > vwap
            recent_df['crosses'] = recent_df['above_vwap'].diff()

            # Find crossover points
            bullish_crosses = recent_df[recent_df['crosses'] == True]
            bearish_crosses = recent_df[recent_df['crosses'] == -1]

            for _, row in bullish_crosses.iterrows():
                reclaims.append({
                    'timeframe': timeframe,
                    'level': vwap,
                    'type': 'bullish_reclaim',
                    'date': row['timestamp'],
                    'days_ago': (recent_df['timestamp'].max() - row['timestamp']).days,
                    'close_price': row['close']
                })

            for _, row in bearish_crosses.iterrows():
                reclaims.append({
                    'timeframe': timeframe,
                    'level': vwap,
                    'type': 'bearish_breakdown',
                    'date': row['timestamp'],
                    'days_ago': (recent_df['timestamp'].max() - row['timestamp']).days,
                    'close_price': row['close']
                })

        return sorted(reclaims, key=lambda x: x['days_ago'])

    def find_magnet_interactions(self, df: pd.DataFrame, vwaps: Dict) -> List[Dict]:
        """
        Find where price has interacted with 27% magnet levels.

        Args:
            df: Historical price data
            vwaps: VWAP levels by timeframe

        Returns:
            List of magnet interaction events
        """
        if df.empty:
            return []

        MAGNET_LEVELS = [0.27, 1.27, 2.27]
        interactions = []

        cutoff_date = df['timestamp'].max() - timedelta(days=self.lookback_days)
        recent_df = df[df['timestamp'] >= cutoff_date]

        for timeframe, vwap in vwaps.items():
            if vwap <= 0:
                continue

            for pct in MAGNET_LEVELS:
                magnet_above = vwap * (1 + pct)
                magnet_below = vwap * (1 - pct)

                # Check for touches within 0.5% of magnet level
                tolerance = magnet_above * 0.005

                touches_above = recent_df[
                    (recent_df['high'] >= magnet_above - tolerance) &
                    (recent_df['high'] <= magnet_above + tolerance)
                ]

                touches_below = recent_df[
                    (recent_df['low'] >= magnet_below - tolerance) &
                    (recent_df['low'] <= magnet_below + tolerance)
                ]

                if not touches_above.empty:
                    interactions.append({
                        'timeframe': timeframe,
                        'magnet_level': magnet_above,
                        'magnet_pct': f"+{int(pct * 100)}%",
                        'touches': len(touches_above),
                        'last_touch': touches_above['timestamp'].iloc[-1],
                        'acted_as': 'resistance'
                    })

                if not touches_below.empty:
                    interactions.append({
                        'timeframe': timeframe,
                        'magnet_level': magnet_below,
                        'magnet_pct': f"-{int(pct * 100)}%",
                        'touches': len(touches_below),
                        'last_touch': touches_below['timestamp'].iloc[-1],
                        'acted_as': 'support'
                    })

        return sorted(interactions, key=lambda x: x['touches'], reverse=True)
