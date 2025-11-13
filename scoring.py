"""
Level Scoring System
AI-weighted scoring to rank VWAP levels by importance.
"""

from typing import Dict, List
from datetime import datetime


class LevelScorer:
    """Scores and ranks VWAP levels by trading importance."""

    # Scoring weights
    WEIGHTS = {
        'proximity': 0.35,      # How close to current price
        'timeframe': 0.25,      # Importance of timeframe
        'pattern': 0.20,        # Pattern strength
        'touches': 0.15,        # Historical touches
        'confluence': 0.05      # Confluence with other levels
    }

    TIMEFRAME_SCORES = {
        'yearly': 100,
        'quarterly': 85,
        'three_month': 70,
        'daily': 50
    }

    def __init__(self):
        self.level_cache = {}

    def score_level(self, level: Dict, current_price: float,
                   patterns: Dict = None) -> float:
        """
        Calculate composite score for a VWAP level.

        Args:
            level: Level dictionary with metadata
            current_price: Current stock price
            patterns: Optional pattern detection results

        Returns:
            Score from 0-100
        """
        scores = {}

        # Proximity score (closer = better)
        distance = abs(current_price - level.get('level', 0))
        distance_pct = distance / current_price if current_price > 0 else 1
        proximity_score = max(0, 100 * (1 - distance_pct * 10))  # 10% away = 0 score
        scores['proximity'] = proximity_score

        # Timeframe score
        timeframe = level.get('timeframe', 'daily')
        scores['timeframe'] = self.TIMEFRAME_SCORES.get(timeframe, 50)

        # Pattern score
        pattern_score = 0
        if patterns:
            # Check if level is in unbroken priors
            unbroken = any(p['level'] == level.get('level')
                          for p in patterns.get('unbroken_priors', []))
            if unbroken:
                pattern_score += 30

            # Check for confluences
            in_confluence = any(level.get('level') in
                              [c['level'] for c in patterns.get('confluences', [])])
            if in_confluence:
                pattern_score += 25

            # Check for recent reclaims
            recent_reclaim = any(
                p['level'] == level.get('level') and p['days_ago'] <= 3
                for p in patterns.get('reclaims', [])
            )
            if recent_reclaim:
                pattern_score += 20

        scores['pattern'] = min(pattern_score, 100)

        # Touches score (from magnet interactions)
        touches = level.get('touches', 0)
        touches_score = min(touches * 20, 100)  # 5+ touches = 100
        scores['touches'] = touches_score

        # Confluence score
        confluence_count = level.get('confluence_count', 0)
        confluence_score = min(confluence_count * 33, 100)  # 3+ levels = 100
        scores['confluence'] = confluence_score

        # Calculate weighted total
        total_score = sum(
            scores.get(key, 0) * weight
            for key, weight in self.WEIGHTS.items()
        )

        return round(total_score, 1)

    def rank_levels(self, levels: List[Dict], current_price: float,
                   patterns: Dict = None) -> List[Dict]:
        """
        Score and rank multiple levels.

        Args:
            levels: List of level dictionaries
            current_price: Current stock price
            patterns: Optional pattern detection results

        Returns:
            Sorted list of levels with scores
        """
        scored_levels = []

        for level in levels:
            score = self.score_level(level, current_price, patterns)
            scored_levels.append({
                **level,
                'score': score,
                'rank': 0  # Will be set after sorting
            })

        # Sort by score (descending)
        scored_levels.sort(key=lambda x: x['score'], reverse=True)

        # Assign ranks
        for i, level in enumerate(scored_levels, 1):
            level['rank'] = i

        return scored_levels

    def get_top_levels(self, vwaps: Dict, magnets: Dict, current_price: float,
                      patterns: Dict = None, top_n: int = 5) -> List[Dict]:
        """
        Get top N most important levels from VWAPs and magnets.

        Args:
            vwaps: VWAP values by timeframe
            magnets: Magnet levels by timeframe
            current_price: Current stock price
            patterns: Pattern detection results
            top_n: Number of top levels to return

        Returns:
            Top N ranked levels
        """
        all_levels = []

        # Add VWAP levels
        for timeframe, vwap in vwaps.items():
            if vwap > 0:
                all_levels.append({
                    'type': 'vwap',
                    'timeframe': timeframe,
                    'level': vwap,
                    'label': f'{timeframe.upper()} VWAP'
                })

        # Add magnet levels
        for timeframe, magnet_list in magnets.items():
            for magnet in magnet_list[:3]:  # Top 3 magnets per timeframe
                all_levels.append({
                    'type': 'magnet',
                    'timeframe': timeframe,
                    'level': magnet['level'],
                    'deviation_pct': magnet.get('deviation_pct', 0),
                    'label': f'{timeframe.upper()} {magnet["deviation_pct"]}% Magnet'
                })

        # Score and rank
        ranked = self.rank_levels(all_levels, current_price, patterns)

        return ranked[:top_n]

    def create_level_summary(self, top_levels: List[Dict]) -> str:
        """
        Create human-readable summary of top levels.

        Args:
            top_levels: Ranked list of levels

        Returns:
            Formatted string summary
        """
        if not top_levels:
            return "No significant levels detected."

        lines = ["Top Trading Levels (Ranked by AI):"]
        lines.append("-" * 50)

        for level in top_levels:
            rank = level['rank']
            score = level['score']
            price = level['level']
            label = level.get('label', 'Level')

            lines.append(f"{rank}. {label}: ${price:.2f} (Score: {score})")

        return "\n".join(lines)

    def analyze_entry_quality(self, entry_price: float, vwaps: Dict,
                              current_price: float, patterns: Dict = None) -> Dict:
        """
        Analyze the quality of a potential entry price.

        Args:
            entry_price: Proposed entry price
            vwaps: VWAP levels
            current_price: Current market price
            patterns: Pattern data

        Returns:
            Dictionary with quality assessment
        """
        # Find closest VWAP
        closest_vwap = None
        min_distance = float('inf')

        for timeframe, vwap in vwaps.items():
            if vwap <= 0:
                continue
            distance = abs(entry_price - vwap)
            if distance < min_distance:
                min_distance = distance
                closest_vwap = {'timeframe': timeframe, 'level': vwap}

        if not closest_vwap:
            return {'quality': 'unknown', 'reason': 'No VWAP data available'}

        # Calculate quality based on proximity to VWAP
        distance_pct = (min_distance / entry_price) * 100

        if distance_pct < 0.5:  # Within 0.5%
            quality = 'excellent'
            reason = f"Entry within 0.5% of {closest_vwap['timeframe']} VWAP"
        elif distance_pct < 1.5:  # Within 1.5%
            quality = 'good'
            reason = f"Entry within 1.5% of {closest_vwap['timeframe']} VWAP"
        elif distance_pct < 3.0:  # Within 3%
            quality = 'fair'
            reason = f"Entry within 3% of {closest_vwap['timeframe']} VWAP"
        else:
            quality = 'poor'
            reason = f"Entry {distance_pct:.1f}% away from nearest VWAP"

        # Check for pattern confirmations
        confirmations = []
        if patterns:
            if any(p.get('level') == closest_vwap['level']
                  for p in patterns.get('unbroken_priors', [])):
                confirmations.append("Unbroken prior support")

            if any(closest_vwap['level'] in
                  [c['level'] for c in patterns.get('confluences', [])]):
                confirmations.append("Confluence zone")

        return {
            'quality': quality,
            'reason': reason,
            'closest_vwap': closest_vwap,
            'distance_pct': round(distance_pct, 2),
            'confirmations': confirmations
        }
