# VWAP Trading Platform

A commodity trading intelligence platform for validating trade setups using multi-timeframe VWAP (Volume-Weighted Average Price) analysis, pattern detection, and AI-powered validation.

**📋 Full Documentation:** See [`docs/PLATFORM-MERGE-PLAN.md`](docs/PLATFORM-MERGE-PLAN.md) for complete architecture and roadmap.

**Status:** Prototype phase → Phase 1 restructure in progress

## Features

- **Multi-Timeframe VWAP**: Calculates VWAP for Yearly, Quarterly, 3-Month, and Daily periods
- **27% Magnet Levels**: Automatically detects 27%, 127%, 227% deviation levels from each VWAP
- **Pattern Recognition**: Identifies unbroken priors, failed breaks, confluences, and reclaims
- **AI-Weighted Scoring**: Ranks levels by importance using proximity, timeframe, patterns, and historical touches
- **Trade Annotation**: Save and rate your setups (good/bad/neutral) with notes
- **Dark Mode Interface**: Professional terminal-style UI optimized for traders
- **Export to CSV**: Build your database of analyzed setups for statistical analysis
- **Real-Time Data**: Powered by Alpha Vantage API with intelligent caching

## Screenshot

(Dark mode interface with VWAP levels, patterns, and interactive charts)

## Installation

### Prerequisites

- Python 3.8 or higher
- Alpha Vantage API key (free at https://www.alphavantage.co/support/#api-key)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/deachne/VWAP-Investigator.git
   cd VWAP-Investigator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your Alpha Vantage API key
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

   The browser will open automatically to `http://localhost:5000`

## Usage

### Analyze a Stock

1. Enter a stock symbol (e.g., `INTC`, `AAPL`, `TSLA`)
2. Optionally enter an entry price (leave blank for current price)
3. Click "Analyze"

### View Results

The analysis includes:

- **VWAP Levels**: All timeframes with deviations
- **Top Levels**: AI-ranked levels by importance (scored 0-100)
- **Patterns**: Detected patterns like unbroken priors, confluences, reclaims
- **Chart**: Visual representation of price and VWAP levels
- **Entry Analysis**: Quality assessment (Excellent/Good/Fair/Poor)

### Save Trades

1. Rate the setup (Good/Neutral/Bad)
2. Add notes about what you observed
3. Click "Save to Database"

### Export Data

Click "Export to CSV" to download all your annotated setups for analysis.

## Project Structure

```
vwap-validator/
├── app.py                  # Flask web server
├── vwap_engine.py          # Core VWAP calculation engine
├── alpha_vantage.py        # API client with caching
├── pattern_detector.py     # Pattern recognition system
├── scoring.py              # AI-weighted level scoring
├── database.py             # SQLite operations
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore             # Git ignore rules
├── templates/
│   └── index.html         # Frontend interface
└── static/
    ├── style.css          # Dark mode styling
    └── app.js             # Frontend logic
```

## API Endpoints

### `POST /api/analyze`
Analyze a stock symbol with VWAP calculations

**Request:**
```json
{
  "symbol": "INTC",
  "entry_price": 45.50
}
```

**Response:**
```json
{
  "symbol": "INTC",
  "current_price": 45.75,
  "vwaps": {
    "yearly": 45.20,
    "quarterly": 44.85,
    "three_month": 46.10,
    "daily": 45.60
  },
  "top_levels": [...],
  "patterns": {...},
  "entry_analysis": {...}
}
```

### `POST /api/save-trade`
Save a trade annotation

### `GET /api/trades`
Get saved trades with filtering

### `GET /api/statistics`
Get database statistics

### `GET /api/export`
Export trades to CSV

## How It Works

### VWAP Calculation

VWAP = Σ(Price × Volume) / Σ(Volume)

The engine calculates VWAP from:
- **Yearly**: January 1st to present
- **Quarterly**: Start of current quarter to present
- **3-Month**: Last 90 days
- **Daily**: Market open (9:30 AM) to present

### 27% Magnet Levels

Based on the observation that price tends to gravitate toward 27% deviations from VWAP:
- 27%, 127%, 227%, 327%, 427% above/below each VWAP
- Acts as natural support/resistance zones

### Pattern Detection

- **Unbroken Priors**: VWAPs that haven't been broken recently
- **Failed Breaks**: Price touched but failed to close beyond VWAP
- **Confluences**: Multiple VWAPs or magnets converging
- **Reclaims**: Recent crossovers of VWAP levels

### AI Scoring Algorithm

Levels are scored 0-100 based on:
- **Proximity** (35%): Distance from current price
- **Timeframe** (25%): Importance of timeframe (yearly > quarterly > 3-month > daily)
- **Pattern** (20%): Strength of patterns at this level
- **Touches** (15%): Historical interactions
- **Confluence** (5%): Number of converging levels

## Development

### Tech Stack

- **Backend**: Python 3.8+, Flask, Pandas, NumPy
- **Frontend**: Vanilla JavaScript, Chart.js, CSS3
- **Database**: SQLite
- **API**: Alpha Vantage (free tier: 25 requests/day, 5 calls/minute)

### Running Tests

```bash
# Run with test symbol
python app.py
# Navigate to http://localhost:5000
# Enter: INTC
```

### Contributing

Pull requests welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a PR with clear description

## API Key Limitations

**Free Tier (Alpha Vantage):**
- 25 API calls per day
- 5 calls per minute
- Data cached for 1 hour to minimize calls

**Workaround:**
- Analyze stocks once and save them
- Use cached data for repeated analysis
- Upgrade to premium for unlimited calls

## Roadmap

- [ ] Add webhook support for Discord/Slack alerts
- [ ] Implement backtesting engine
- [ ] Add custom magnet level percentages
- [ ] Multi-symbol batch analysis
- [ ] Export to Google Sheets integration
- [ ] Mobile responsive design improvements
- [ ] TradingView chart integration

## Use Cases

### 1. YouTuber Pick Validation
YouTuber says: "Buy UAL at $91.36"
1. Enter: UAL, $91.36
2. Check if entry aligns with quarterly VWAP
3. Rate it Good/Bad based on patterns
4. Build library of 100 picks for statistical analysis

### 2. Daily Setup Screening
1. Scan your watchlist each morning
2. Identify stocks near important VWAPs
3. Save confluences for potential trades
4. Track which patterns work best

### 3. Post-Trade Review
1. Enter your actual entry price
2. See what VWAP levels were active
3. Document what you saw vs what you should have seen
4. Improve pattern recognition over time

## FAQ

**Q: Why is the chart simple?**
A: Focus is on VWAP analysis, not detailed charting. Use TradingView for charts, this tool for validation.

**Q: Can I use this for crypto?**
A: Currently supports stocks only (Alpha Vantage limitation). Crypto support planned.

**Q: Is this financial advice?**
A: No. This is an educational tool for analyzing VWAP levels. Trade at your own risk.

**Q: How accurate are the patterns?**
A: Patterns are detected algorithmically but require human interpretation. Always combine with your own analysis.

## License

MIT License - see LICENSE file for details

## Credits

- Built with [Flask](https://flask.palletsprojects.com/)
- Data from [Alpha Vantage](https://www.alphavantage.co/)
- Charts by [Chart.js](https://www.chartjs.org/)
- Inspired by professional VWAP traders and the 27% phenomenon

## Support

Issues? Questions? [Open an issue](https://github.com/deachne/VWAP-Investigator/issues)

---

**Built for traders, by traders. Happy analyzing! 📈**
