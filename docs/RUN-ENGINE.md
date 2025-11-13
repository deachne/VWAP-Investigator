# Running the VWAP Engine

## Quick Reference Guide

This document explains how to run the VWAP calculation engine manually or in Claude sessions.

---

## Method 1: Command Line (Standalone)

### Calculate VWAPs for a ticker:

```bash
cd ~/Desktop/vwap-validator

# Run the test script
python vwap_engine.py
# Shows INTC by default

# Or create a custom test:
cat > analyze_ticker.py << 'EOF'
from vwap_engine import VWAPEngine
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

# Change ticker here
ticker = 'DIS'
current_price = None  # Leave None for latest market price

engine = VWAPEngine(ticker, api_key)
result = engine.get_all_vwaps(current_price)

print(f"\n{'='*60}")
print(f"{result['ticker']} Analysis")
print(f"Current Price: ${result['current_price']:.2f}")
print(f"{'='*60}\n")

# Current yearly
yearly = result['vwaps']['current_yearly']
print(f"{yearly['label']}")
print(f"  VWAP: ${yearly['vwap']:.2f}")
print(f"  Std Dev: ${yearly['std_dev']:.2f}")
print(f"  Distance: {yearly['distance']['percent_distance']:.2f}%")
print(f"  Sigma: {yearly['distance']['sigma_distance']:.3f}σ")
print(f"  Closest Magnet: {yearly['distance']['closest_level']}σ\n")

# Standard deviation bands
print("Standard Deviation Bands (Yearly):")
for level in [2.0, 1.618, 1.27, 1.0, 0.5, 0.27]:
    up = yearly['vwap'] + (level * yearly['std_dev'])
    down = yearly['vwap'] - (level * yearly['std_dev'])
    print(f"  +{level}σ: ${up:.2f} | -{level}σ: ${down:.2f}")

# Prior quarterly VWAPs
print("\nPrior Quarterly VWAPs (Ghost Levels):")
for prior in result['vwaps']['prior_quarterly']:
    dist_pct = ((result['current_price'] - prior['vwap']) / prior['vwap']) * 100
    print(f"  {prior['label']}: ${prior['vwap']:.2f} ({dist_pct:+.2f}%)")
EOF

python analyze_ticker.py
```

---

## Method 2: In Claude Chat Sessions

### Basic Usage:

```
Analyze [TICKER] using the VWAP engine from:
https://github.com/deachne/VWAP-Investigator

Show exact sigma distances and all prior period VWAPs.
```

### With Specific Price:

```
Use vwap_engine.py from github.com/deachne/VWAP-Investigator

Calculate where DIS is at current price $107.25:
- Exact sigma from yearly VWAP
- Distance to nearest magnet level
- All prior quarterly VWAPs
```

### Using Slash Command:

If `.claude/commands/vwap.md` is set up:

```
/vwap DIS
/vwap INTC 37.89
/vwap CORN
```

---

## Method 3: Through Flask App

### Run the web interface:

```bash
cd ~/Desktop/vwap-validator
python app.py
# Opens browser at localhost:5001
```

Then enter ticker in the UI.

**Note**: Web app currently uses old engine format. Needs frontend update to show all sigma bands.

---

## Understanding The Output

### Sigma Distance Explained:

```
Current Price: $107.25
Yearly VWAP: $108.72
Std Dev: $10.48

Sigma: -0.140σ
```

**What this means:**
- Price is **0.140 standard deviations BELOW** yearly VWAP
- In dollars: $107.25 - $108.72 = -$1.47
- In std dev units: -$1.47 ÷ $10.48 = -0.140σ

### Key Sigma Levels (Your Magnets):

```
+2.618σ ─── Extreme extension (rare)
+2.27σ  ─── Strong extension
+2.0σ   ─── 2 standard deviations
+1.618σ ─── Fibonacci extension
+1.27σ  ─── Your magnet level
+1.0σ   ─── 1 standard deviation
+0.5σ   ─── Half sigma
+0.27σ  ─── Your 27% magnet
VWAP    ═══ The anchor (mean)
-0.27σ  ─── Support magnet (DIS bounced here!)
-0.5σ   ───
-1.0σ   ───
-1.27σ  ───
-1.618σ ───
-2.0σ   ───
-2.27σ  ───
-2.618σ ─── Extreme oversold
```

### Prior Period VWAPs (Ghost Levels):

**These are S/R levels from completed periods:**

```
Prior Quarterly:
  Q3 2025 VWAP: $117.22 ← DIS rejected here yesterday!
  Q2 2025 VWAP: $102.49
  Q1 2025 VWAP: $107.51

Prior Yearly:
  2024 VWAP: $106.01
  2023 VWAP: $XXX.XX
  2022 VWAP: $XXX.XX
```

**Why they matter**: Institutions got positioned at these levels. They defend or break them.

---

## Real-World Example (Disney Nov 13):

### The Setup:
```
Nov 12 Close: $116.65
  ↓
At: Q3 2025 Prior Quarterly VWAP ($117.22)
Result: REJECTED (resistance worked)
```

### The Execution:
```
Nov 13 Open: Gap down
  ↓
Target: -0.27σ below yearly VWAP
Calculation: $108.72 - (0.27 × $10.48) = $105.89
  ↓
Actual Low: $105.85
Accuracy: $0.04 difference (0.04%!)
  ↓
Bounce: To -0.11σ / Daily VWAP zone ($107-108)
```

**This proves the math works.**

---

## Common Analysis Patterns

### YouTuber Pick Validation:
```
YouTuber: "Buy UAL at $91.36"

You: /vwap UAL 91.36

Engine shows:
- Quarterly VWAP: $90.85
- Distance: +0.56%
- Sigma: +0.42σ
- Prior quarterly: $95.20

Rating: GOOD (near quarterly VWAP support)
```

### Anomaly Detection:
```
/vwap AAPL

Engine shows:
- Current sigma: 0.786σ ← Not a "standard" level!
- This is Fibonacci 78.6% harmonic
- Watch for reversal (anomaly = opportunity)
```

### Support/Resistance Validation:
```
/vwap CORN

Prior yearly VWAP: $4.50
Current price: $4.48

Analysis: Testing prior yearly as support
If holds → bounce to current quarterly
If breaks → flush to -0.27σ
```

---

## Tips for Using in Claude Sessions

### 1. Always Ask for EXACT Values
```
❌ "Close to 1.0σ"
✅ "0.973σ" (exact reading)
```

### 2. Request All Prior Periods
```
Show prior quarterly VWAPs - they act as ghost S/R levels
```

### 3. Get Standard Deviation Bands
```
Calculate all sigma bands: ±0.27, ±0.5, ±1.0, ±1.27, ±1.618, ±2.0, ±2.27
```

### 4. Compare to Live Price
```
Current price in TradingView: $107.25
Calculate exact sigma distance from yearly VWAP
```

---

## API Key Location

**In repo:** `.env` file
```
ALPHA_VANTAGE_API_KEY=S3C39Q2JMKXI0ZOD
```

Claude can read this automatically when accessing the repo.

---

## Expected Output Format

```
============================================================
[TICKER] VWAP Analysis
Current Price: $XXX.XX
============================================================

2025 Yearly VWAP
  VWAP: $XXX.XX
  Std Dev: $XX.XX
  Distance: ±XX.XX%
  Sigma: ±X.XXXσ ← EXACT (3 decimals)
  Closest Magnet: ±X.XXσ

Q4 2025 VWAP
  VWAP: $XXX.XX
  Std Dev: $XX.XX
  Sigma: ±X.XXXσ

Prior Quarterly VWAPs (Ghost Levels):
  Q3 2025: $XXX.XX (±XX.XX% from current)
  Q2 2025: $XXX.XX
  Q1 2025: $XXX.XX
  Q4 2024: $XXX.XX

Prior Yearly VWAPs:
  2024: $XXX.XX
  2023: $XXX.XX
  2022: $XXX.XX

Standard Deviation Bands (Yearly):
  +2.0σ: $XXX.XX
  +1.27σ: $XXX.XX
  +1.0σ: $XXX.XX
  +0.27σ: $XXX.XX
  VWAP: $XXX.XX ← Anchor
  -0.27σ: $XXX.XX ← Support target
  -1.0σ: $XXX.XX
  -2.0σ: $XXX.XX
```

---

## Troubleshooting

### "Can't access repository"
```
Make sure repo is public: https://github.com/deachne/VWAP-Investigator
Claude uses GitHub MCP to read files
```

### "API key not found"
```
Provide key directly in prompt:
"Use API key: S3C39Q2JMKXI0ZOD"
```

### "ModuleNotFoundError"
```
Claude needs to install dependencies:
Tell Claude: "Install requirements.txt first"
```

---

## Quick Start Template

**Copy/paste this into any Claude session:**

```
Repository: https://github.com/deachne/VWAP-Investigator
File: vwap_engine.py
API Key: S3C39Q2JMKXI0ZOD (in .env file)

Analyze [TICKER] and show:
1. Current yearly VWAP with EXACT sigma distance
2. Current quarterly VWAP
3. ALL prior quarterly VWAPs (last 4 quarters)
4. Prior yearly VWAPs (last 3 years)
5. Standard deviation bands (±0.27σ, ±1.0σ, ±2.0σ)

Important: Show EXACT sigma values (e.g., 0.757σ), not rounded.
```

---

## Real-Time Validation Workflow

**What you do:**

1. Watch ticker in TradingView (live)
2. Ask Claude to calculate levels
3. Compare Claude's calculations to what you see
4. Validate if price respects the levels

**Example:**

```
You (in TradingView): DIS at $107.25, looks like it's at daily VWAP
You (to Claude): /vwap DIS 107.25
Claude: "Current sigma: -0.140σ from yearly, near daily VWAP"
You: ✅ Confirmed - watching for -0.27σ support at $105.89
```

**Result**: You know EXACTLY where algos will act before they do.

---

## Advanced: Batch Analysis

**Analyze multiple tickers:**

```
Run VWAP engine from github.com/deachne/VWAP-Investigator

Analyze these tickers:
- INTC
- DIS
- AAPL
- TSLA

For each, show:
- Current sigma distance
- Nearest magnet level
- Prior quarterly VWAP (if near current price)
```

---

**This document is your reference for running the engine in any context.**
