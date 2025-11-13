"""
Database operations for storing trade annotations.
Uses SQLite for local storage.
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
import json


class TradeDatabase:
    """SQLite database for trade annotations and analysis."""

    def __init__(self, db_path: str = 'trades.db'):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._init_database()

    def _init_database(self):
        """Create tables if they don't exist."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries

        cursor = self.conn.cursor()

        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL,
                rating TEXT CHECK(rating IN ('good', 'bad', 'neutral')),
                notes TEXT,
                vwap_data TEXT,
                patterns TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Annotations table (for specific levels/patterns)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER NOT NULL,
                level_type TEXT NOT NULL,
                level_value REAL NOT NULL,
                timeframe TEXT,
                annotation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trade_id) REFERENCES trades (id)
            )
        ''')

        self.conn.commit()

    def save_trade(self, symbol: str, entry_price: float, current_price: float,
                   rating: Optional[str] = None, notes: Optional[str] = None,
                   vwap_data: Optional[Dict] = None,
                   patterns: Optional[Dict] = None) -> int:
        """
        Save a trade analysis to database.

        Args:
            symbol: Stock ticker
            entry_price: Entry price
            current_price: Current price
            rating: 'good', 'bad', or 'neutral'
            notes: Optional notes
            vwap_data: VWAP analysis data
            patterns: Pattern detection data

        Returns:
            Trade ID
        """
        cursor = self.conn.cursor()

        vwap_json = json.dumps(vwap_data) if vwap_data else None
        patterns_json = json.dumps(patterns) if patterns else None

        cursor.execute('''
            INSERT INTO trades (symbol, entry_price, current_price, rating, notes, vwap_data, patterns)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, entry_price, current_price, rating, notes, vwap_json, patterns_json))

        self.conn.commit()
        return cursor.lastrowid

    def update_trade(self, trade_id: int, rating: Optional[str] = None,
                    notes: Optional[str] = None):
        """
        Update an existing trade.

        Args:
            trade_id: Trade ID to update
            rating: New rating
            notes: New notes
        """
        cursor = self.conn.cursor()

        updates = []
        params = []

        if rating:
            updates.append('rating = ?')
            params.append(rating)

        if notes:
            updates.append('notes = ?')
            params.append(notes)

        updates.append('updated_at = ?')
        params.append(datetime.now().isoformat())

        params.append(trade_id)

        query = f"UPDATE trades SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        self.conn.commit()

    def get_trade(self, trade_id: int) -> Optional[Dict]:
        """Get a single trade by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_trades(self, symbol: Optional[str] = None,
                   rating: Optional[str] = None,
                   limit: int = 50) -> List[Dict]:
        """
        Get trades with optional filtering.

        Args:
            symbol: Filter by symbol
            rating: Filter by rating
            limit: Maximum number of results

        Returns:
            List of trade dictionaries
        """
        cursor = self.conn.cursor()

        query = 'SELECT * FROM trades WHERE 1=1'
        params = []

        if symbol:
            query += ' AND symbol = ?'
            params.append(symbol)

        if rating:
            query += ' AND rating = ?'
            params.append(rating)

        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def save_annotation(self, trade_id: int, level_type: str, level_value: float,
                       timeframe: str, annotation: str):
        """
        Save an annotation for a specific level.

        Args:
            trade_id: Associated trade ID
            level_type: 'vwap' or 'magnet'
            level_value: Price level
            timeframe: Timeframe (daily, quarterly, etc.)
            annotation: Annotation text
        """
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO annotations (trade_id, level_type, level_value, timeframe, annotation)
            VALUES (?, ?, ?, ?, ?)
        ''', (trade_id, level_type, level_value, timeframe, annotation))

        self.conn.commit()

    def get_annotations(self, trade_id: int) -> List[Dict]:
        """Get all annotations for a trade."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM annotations WHERE trade_id = ?', (trade_id,))
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_statistics(self) -> Dict:
        """Get overall statistics."""
        cursor = self.conn.cursor()

        stats = {}

        # Total trades
        cursor.execute('SELECT COUNT(*) as count FROM trades')
        stats['total_trades'] = cursor.fetchone()['count']

        # Ratings breakdown
        cursor.execute('''
            SELECT rating, COUNT(*) as count
            FROM trades
            WHERE rating IS NOT NULL
            GROUP BY rating
        ''')
        stats['ratings'] = {row['rating']: row['count'] for row in cursor.fetchall()}

        # Most analyzed symbols
        cursor.execute('''
            SELECT symbol, COUNT(*) as count
            FROM trades
            GROUP BY symbol
            ORDER BY count DESC
            LIMIT 10
        ''')
        stats['top_symbols'] = [dict(row) for row in cursor.fetchall()]

        return stats

    def export_to_csv(self, filename: str = 'trades_export.csv'):
        """Export trades to CSV file."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM trades ORDER BY created_at DESC')
        rows = cursor.fetchall()

        if not rows:
            return

        import csv
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row))

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
