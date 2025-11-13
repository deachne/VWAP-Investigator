"""
VWAP Trade Validator - Flask Web Application
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import numpy as np

from vwap_engine import VWAPEngine, VWAPAnalyzer
from alpha_vantage import AlphaVantageClient
from pattern_detector import PatternDetector
from scoring import LevelScorer
from database import TradeDatabase


def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize components
vwap_engine = VWAPEngine()
vwap_analyzer = VWAPAnalyzer(vwap_engine)
pattern_detector = PatternDetector(lookback_days=30)
level_scorer = LevelScorer()
db = TradeDatabase()

# Initialize API client (will use env var)
try:
    api_client = AlphaVantageClient()
except ValueError as e:
    print(f"Warning: {e}")
    api_client = None


@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze a stock symbol with VWAP calculations.

    Request JSON:
        {
            "symbol": "AAPL",
            "entry_price": 150.00  (optional)
        }

    Returns:
        Complete VWAP analysis with patterns and scoring
    """
    try:
        data = request.json
        symbol = data.get('symbol', '').upper().strip()
        entry_price = data.get('entry_price')

        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400

        if not api_client:
            return jsonify({
                'error': 'API key not configured. Please set ALPHA_VANTAGE_API_KEY environment variable.'
            }), 500

        # Fetch market data
        try:
            daily_df = api_client.fetch_daily(symbol, outputsize='full')
            quote = api_client.fetch_quote(symbol)
            current_price = entry_price if entry_price else quote['price']
        except Exception as e:
            return jsonify({'error': f'Failed to fetch data: {str(e)}'}), 400

        # Calculate VWAPs and analyze
        analysis = vwap_analyzer.analyze_price_action(daily_df, current_price)

        # Detect patterns
        patterns = pattern_detector.detect_all_patterns(
            daily_df,
            analysis['vwaps'],
            current_price
        )

        # Score levels
        top_levels = level_scorer.get_top_levels(
            analysis['vwaps'],
            analysis.get('magnet_levels', {}),
            current_price,
            patterns,
            top_n=8
        )

        # Analyze entry quality if entry price provided
        entry_analysis = None
        if entry_price:
            entry_analysis = level_scorer.analyze_entry_quality(
                entry_price,
                analysis['vwaps'],
                current_price,
                patterns
            )

        response = {
            'symbol': symbol,
            'current_price': current_price,
            'entry_price': entry_price,
            'quote': quote,
            'vwaps': analysis['vwaps'],
            'deviations': analysis.get('deviations', {}),
            'magnet_levels': analysis.get('magnet_levels', {}),
            'patterns': patterns,
            'top_levels': top_levels,
            'entry_analysis': entry_analysis,
            'support_resistance': analysis.get('support_resistance', {}),
            'timestamp': analysis.get('timestamp')
        }

        # Convert numpy types to native Python types for JSON serialization
        response = convert_numpy_types(response)

        return jsonify(response)

    except Exception as e:
        import traceback
        print("\n" + "="*50)
        print("ERROR IN ANALYZE ENDPOINT:")
        print("="*50)
        traceback.print_exc()
        print("="*50 + "\n")
        return jsonify({'error': str(e)}), 500


@app.route('/api/save-trade', methods=['POST'])
def save_trade():
    """
    Save a trade annotation to database.

    Request JSON:
        {
            "symbol": "AAPL",
            "entry_price": 150.00,
            "current_price": 152.00,
            "rating": "good",
            "notes": "Good setup at quarterly VWAP"
        }
    """
    try:
        data = request.json

        trade_id = db.save_trade(
            symbol=data['symbol'],
            entry_price=data['entry_price'],
            current_price=data.get('current_price'),
            rating=data.get('rating'),
            notes=data.get('notes'),
            vwap_data=data.get('vwap_data'),
            patterns=data.get('patterns')
        )

        return jsonify({
            'success': True,
            'trade_id': trade_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/trades', methods=['GET'])
def get_trades():
    """
    Get saved trades with optional filtering.

    Query params:
        symbol: Filter by symbol
        rating: Filter by rating (good/bad/neutral)
        limit: Max results (default 50)
    """
    try:
        symbol = request.args.get('symbol')
        rating = request.args.get('rating')
        limit = int(request.args.get('limit', 50))

        trades = db.get_trades(symbol=symbol, rating=rating, limit=limit)

        return jsonify({
            'trades': trades,
            'count': len(trades)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get database statistics."""
    try:
        stats = db.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['GET'])
def export_trades():
    """Export trades to CSV."""
    try:
        filename = f"vwap_trades_export_{datetime.now().strftime('%Y%m%d')}.csv"
        db.export_to_csv(filename)
        return jsonify({
            'success': True,
            'filename': filename,
            'message': f'Trades exported to {filename}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Clear API data cache."""
    try:
        if api_client:
            symbol = request.json.get('symbol') if request.json else None
            api_client.clear_cache(symbol)
            return jsonify({
                'success': True,
                'message': f'Cache cleared for {symbol}' if symbol else 'All cache cleared'
            })
        return jsonify({'error': 'API client not initialized'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'api_configured': api_client is not None,
        'database_connected': db.conn is not None
    })


if __name__ == '__main__':
    import webbrowser
    from threading import Timer

    def open_browser():
        webbrowser.open('http://localhost:5001')

    # Open browser after 1 second
    Timer(1, open_browser).start()

    # Run Flask app
    print("\n" + "="*50)
    print("VWAP Trade Validator Starting...")
    print("="*50)
    print("\nServer running at: http://localhost:5001")
    print("Browser will open automatically...\n")

    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
