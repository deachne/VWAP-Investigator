"""
Alpha Vantage API Integration
Fetches historical price data with intelligent caching.
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict
import json


class AlphaVantageClient:
    """Client for fetching stock data from Alpha Vantage API."""

    BASE_URL = "https://www.alphavantage.co/query"
    CACHE_DURATION = timedelta(hours=1)  # Cache data for 1 hour

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize client with API key.

        Args:
            api_key: Alpha Vantage API key (or reads from ALPHA_VANTAGE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            raise ValueError("Alpha Vantage API key required. Set ALPHA_VANTAGE_API_KEY env var.")

        self.cache = {}
        self.cache_times = {}

    def fetch_intraday(self, symbol: str, interval: str = '5min',
                       outputsize: str = 'full') -> pd.DataFrame:
        """
        Fetch intraday data for a symbol.

        Args:
            symbol: Stock ticker symbol
            interval: Time interval (1min, 5min, 15min, 30min, 60min)
            outputsize: 'compact' (100 points) or 'full' (all available)

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        cache_key = f"{symbol}_intraday_{interval}"

        # Check cache
        if self._is_cached(cache_key):
            return self.cache[cache_key]

        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'outputsize': outputsize,
            'apikey': self.api_key
        }

        data = self._make_request(params)

        # Parse response
        time_series_key = f'Time Series ({interval})'
        if time_series_key not in data:
            raise ValueError(f"No data returned for {symbol}. Check symbol and API key.")

        time_series = data[time_series_key]

        # Convert to DataFrame
        df = self._parse_time_series(time_series)

        # Cache result
        self.cache[cache_key] = df
        self.cache_times[cache_key] = datetime.now()

        return df

    def fetch_daily(self, symbol: str, outputsize: str = 'full') -> pd.DataFrame:
        """
        Fetch daily data for a symbol.

        Args:
            symbol: Stock ticker symbol
            outputsize: 'compact' (100 days) or 'full' (20+ years)

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        cache_key = f"{symbol}_daily"

        # Check cache
        if self._is_cached(cache_key):
            return self.cache[cache_key]

        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize,
            'apikey': self.api_key
        }

        data = self._make_request(params)

        # Parse response
        if 'Time Series (Daily)' not in data:
            raise ValueError(f"No data returned for {symbol}. Check symbol and API key.")

        time_series = data['Time Series (Daily)']

        # Convert to DataFrame
        df = self._parse_time_series(time_series)

        # Cache result
        self.cache[cache_key] = df
        self.cache_times[cache_key] = datetime.now()

        return df

    def fetch_quote(self, symbol: str) -> Dict:
        """
        Fetch current quote for a symbol.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with current price, volume, etc.
        """
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }

        data = self._make_request(params)

        if 'Global Quote' not in data:
            raise ValueError(f"No quote data returned for {symbol}")

        quote = data['Global Quote']

        return {
            'symbol': quote.get('01. symbol', symbol),
            'price': float(quote.get('05. price', 0)),
            'volume': int(quote.get('06. volume', 0)),
            'latest_trading_day': quote.get('07. latest trading day', ''),
            'previous_close': float(quote.get('08. previous close', 0)),
            'change': float(quote.get('09. change', 0)),
            'change_percent': quote.get('10. change percent', '0%')
        }

    def _make_request(self, params: Dict) -> Dict:
        """Make API request with error handling."""
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Check for API error messages
            if 'Error Message' in data:
                raise ValueError(f"API Error: {data['Error Message']}")

            if 'Note' in data:
                raise ValueError(f"API Limit: {data['Note']}")

            return data

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch data: {str(e)}")

    def _parse_time_series(self, time_series: Dict) -> pd.DataFrame:
        """Parse Alpha Vantage time series data into DataFrame."""
        records = []

        for timestamp, values in time_series.items():
            records.append({
                'timestamp': timestamp,
                'open': float(values.get('1. open', 0)),
                'high': float(values.get('2. high', 0)),
                'low': float(values.get('3. low', 0)),
                'close': float(values.get('4. close', 0)),
                'volume': int(values.get('5. volume', 0))
            })

        df = pd.DataFrame(records)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        return df

    def _is_cached(self, cache_key: str) -> bool:
        """Check if cache is valid."""
        if cache_key not in self.cache:
            return False

        cache_time = self.cache_times.get(cache_key)
        if not cache_time:
            return False

        # Check if cache is still valid
        if datetime.now() - cache_time > self.CACHE_DURATION:
            # Clear expired cache
            del self.cache[cache_key]
            del self.cache_times[cache_key]
            return False

        return True

    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear cache for a symbol or all symbols.

        Args:
            symbol: Optional symbol to clear. If None, clears all cache.
        """
        if symbol:
            keys_to_remove = [k for k in self.cache.keys() if k.startswith(symbol)]
            for key in keys_to_remove:
                del self.cache[key]
                del self.cache_times[key]
        else:
            self.cache.clear()
            self.cache_times.clear()
