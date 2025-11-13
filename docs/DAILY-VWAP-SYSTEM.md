# Daily VWAP System - The Intraday Beast

## Core Principle

**Daily VWAPs are fundamentally different from higher timeframe VWAPs.**

They reset every market open, creating a NEW statistical system each day, while higher timeframe VWAPs (yearly, quarterly) provide the TARGET framework.

---

## How Daily VWAPs Work

### Reset Behavior

**Daily VWAP:**
- Resets every day at market open (9:30 AM ET)
- Calculates from 9:30 AM to current bar
- Std dev bands calculated from today's range
- At 4:00 PM close → becomes STATIC (prior daily VWAP)

**Higher Timeframe VWAPs:**
- Yearly: Calculates from Jan 1, accumulates all year
- Quarterly: Calculates from quarter start, accumulates
- Continuous growth, no daily reset

---

## Prior Daily VWAPs as Ghost Levels

### The Constellation Effect

**Each completed trading day leaves behind 9+ ghost levels:**

```
Nov 12, 2025 (Yesterday) - COMPLETED DAY:
├── Daily VWAP: $273.50 (now static)
├── +2.618σ: $276.50
├── +2.27σ: $275.80
├── +2.0σ: $275.00 ← Resistance on Nov 13!
├── +1.27σ: $274.70
├── +1.0σ: $274.20 ← Support on Nov 13!
├── -1.0σ: $272.80
├── -2.0σ: $271.00 ← Caught flush on Nov 13!
└── (more bands...)

These levels are NOW price-based S/R for Nov 13+
Distance measured in PERCENT (they're static now)
```

### How Many Days Back?

**Recommendation: Track last 5 trading days**

```
Prior Daily VWAPs:
├── T-1 (yesterday): Strongest ghost levels
├── T-2 (2 days ago): Strong
├── T-3 (3 days ago): Moderate
├── T-4 (4 days ago): Weak
└── T-5 (5 days ago): Very weak

Each day = 9 ghost levels × 5 days = 45 ghost levels!
```

**Why stop at 5?**
- Levels older than 5 days lose relevance
- Intraday traders care about recent price memory
- Too many levels = chart clutter

---

## Daily VWAPs Use Higher Timeframes as Targets

### The Target Hierarchy

**Intraday traders ask:**
"Where is price going today?"

**Answer:** Higher timeframe VWAP levels

```
AAPL Example (Nov 13):

Current Price: $273.05
Daily VWAP: $272.45 (today's anchor)

Upside Targets:
├── Q4 2025 Quarterly VWAP: $280.50 (current quarter target)
├── 2025 Yearly VWAP +1σ: $285.00 (bullish extension)
└── Q3 2025 Prior Quarterly: $290.50 (resistance from last quarter)

Downside Targets:
├── 2025 Yearly VWAP: $270.00 (mean reversion)
├── 2025 Yearly VWAP -1σ: $265.00 (support)
└── 2024 Yearly Prior: $260.00 (major support)
```

**Intraday moves are bounces between higher timeframe levels.**

### Trading Style Differences

**Intraday Trader:**
```
Timeframe: 5-min, 15-min charts
Reference: Daily VWAP + prior daily bands
Targets: Higher timeframe VWAPs (quarterly, yearly)
Holds: Minutes to hours
```

**Swing Trader:**
```
Timeframe: Daily, 4-hour charts
Reference: Quarterly VWAP + prior quarterly bands
Targets: Yearly VWAPs, prior yearly levels
Holds: Days to weeks
```

**Long-term Investor:**
```
Timeframe: Weekly, monthly charts
Reference: Yearly VWAP + prior yearly levels
Targets: Multi-year VWAPs, major std dev extensions
Holds: Months to years
```

**All three use the SAME VWAP framework, just different timeframe anchors.**

---

## Pre-Market Range = Fibonacci Grid

### The Pre-Market Story

**Pre-market trading (4:00 AM - 9:30 AM) establishes the day's Fibonacci levels:**

```
Pre-market Action:
├── Low: $272.00 (oversold)
├── High: $276.50 (resistance)
└── Range: $4.50

This range DEFINES the day's Fib grid:
├── 0% (base): $272.00
├── 27.0%: $273.21
├── 50.0%: $274.25
├── 61.8%: $274.78
├── 78.6%: $275.64
├── 100%: $276.50
├── 127.2%: $277.72
├── 161.8%: $279.30
└── Extensions continue...
```

### Market Reads the Story

**Regular session (9:30 AM - 4:00 PM) systematically tests these levels:**

```
AAPL Nov 13 Example:
09:00: Open at 100% Fib ($275.00)
09:15: Rally to 161.8% Fib ($276.57) → High $276.70 ✅
09:30: Reject, fall to 78.6% Fib ($274.45)
10:00: Test 61.8% Fib ($274.03) - multiple touches
10:30: Break down to 50% Fib ($273.73)
11:00: Flush to 27% Fib ($273.14)
11:30: Current at daily VWAP base ($272.45)

Algos traded EXACT Fibonacci levels from pre-market range
```

### "The Market Wrote the Story in Pre-Market"

**Your insight:**

The pre-market range ISN'T random volatility - it's algos **establishing the grid** for the day:

1. **Pre-market participants** (institutions, international traders) set range
2. **Algos calculate** all Fibonacci retracements from that range
3. **Regular session algos** execute trades at those exact levels
4. **Price moves in predictable increments** (27%, 50%, 61.8%, etc.)

**It's not chaos - it's a programmed execution plan.**

---

## The Triple Confluence System (Intraday)

**Three layers operate simultaneously:**

### Layer 1: Current Daily VWAP (Dynamic)
```
Today's VWAP: $272.45 (updating every 5-min bar)
├── Anchor for mean reversion
├── Std dev bands show normal range
└── Sigma distance shows if extended
```

### Layer 2: Prior Daily VWAPs (Static Ghost Levels)
```
Yesterday's levels (Nov 12):
├── VWAP: $273.50
├── +2σ: $275.00 ← Acted as resistance today
├── +1σ: $274.20 ← Support after rejection
├── -2σ: $271.00 ← Caught the flush

2 Days Ago (Nov 11):
├── VWAP: $270.50
├── +2σ: $273.00 ← Rally target
└── Bands...
```

### Layer 3: Pre-Market Fibonacci Grid (Daily Script)
```
From pre-market range ($272-$276.50):
├── 161.8%: $279.30 (extension target)
├── 100%: $276.50 (pre-market high)
├── 78.6%: $275.64
├── 61.8%: $274.78 ← Multiple tests
├── 50%: $274.25
├── 27%: $273.21
└── 0%: $272.00 (pre-market low)
```

### When All Three Align = STRONGEST LEVELS

**Example Confluence:**
```
Price: $274.03

Alignment:
├── 61.8% Fib: $274.03 ✅
├── Yesterday +1σ: $274.20 (within $0.17)
├── 2 days ago +2σ: $273.90 (within $0.13)
└── Today's VWAP +0.5σ: $273.95 (within $0.08)

All within 0.3% range = TRIPLE CONFLUENCE
→ Price respects this zone (visible in multiple touches)
→ Strongest intraday S/R
```

---

## Distance Measurements (Intraday Rules)

### Current Daily VWAP (Today's):
```
VWAP: $272.45
Std Dev: $1.20 (today's volatility)
Price: $273.05

Distance: +0.50σ ✅ SIGMA (active, same context)
Also: +0.22% (for comparison)
```

### Prior Daily VWAPs (Yesterday's, etc.):
```
Nov 12 VWAP: $273.50
Price: $273.05

Distance: -0.16% ✅ PERCENT (static level)
NOT sigma (different day's volatility)
```

### Higher Timeframe VWAPs (Targets):
```
Quarterly VWAP: $280.50
Price: $273.05

Distance: -2.65% ✅ PERCENT
Or: "Working toward quarterly VWAP 7.45 points away"
```

**Intraday = percent-based targets to higher timeframe VWAPs**

---

## Calculation Requirements for Daily System

### The Engine Must Provide:

```python
{
    'intraday_analysis': {

        # Today's active VWAP
        'current_daily': {
            'vwap': 272.45,
            'std_dev': 1.20,
            'distance': {
                'sigma': +0.50,  # From today's VWAP
                'percent': +0.22
            },
            'bands': {
                '+2.618σ': 275.59,
                '+2.27σ': 275.17,
                '+2.0σ': 274.85,
                '+1.618σ': 274.39,
                '+1.27σ': 273.97,
                '+1.0σ': 273.65,
                '+0.5σ': 273.05,
                '+0.27σ': 272.77,
                'VWAP': 272.45,
                '-0.27σ': 272.13,
                '-0.5σ': 271.85,
                '-1.0σ': 271.25,
                '-1.27σ': 270.93,
                '-1.618σ': 270.51,
                '-2.0σ': 270.05,
                '-2.27σ': 269.73,
                '-2.618σ': 269.31
            }
        },

        # Prior daily VWAPs (last 5 days)
        'prior_daily_vwaps': [
            {
                'date': '2025-11-12',
                'vwap': 273.50,
                'percent_from_current': +0.16,
                'bands': {
                    '+2σ': 275.00,  # These are STATIC now
                    '+1σ': 274.20,
                    '-1σ': 272.80,
                    '-2σ': 271.00
                }
            },
            {
                'date': '2025-11-11',
                'vwap': 270.50,
                'percent_from_current': -0.71,
                'bands': {
                    '+2σ': 273.00,
                    '+1σ': 271.75,
                    '-1σ': 269.25,
                    '-2σ': 268.00
                }
            }
            // ... last 5 days
        ],

        # Pre-market Fibonacci grid (if applicable)
        'premarket_fib_grid': {
            'low': 272.00,
            'high': 276.50,
            'levels': {
                '0%': 272.00,
                '27%': 273.21,
                '50%': 274.25,
                '61.8%': 274.78,
                '78.6%': 275.64,
                '100%': 276.50,
                '127.2%': 277.72,
                '161.8%': 279.30,
                '178.6%': 280.04
            }
        },

        # Higher timeframe targets (for swing/position)
        'upside_targets': [
            {
                'label': 'Q4 2025 Quarterly VWAP',
                'price': 280.50,
                'distance_percent': +2.73
            },
            {
                'label': '2025 Yearly VWAP +1σ',
                'price': 285.00,
                'distance_percent': +4.38
            }
        ],

        'downside_targets': [
            {
                'label': '2025 Yearly VWAP',
                'price': 270.00,
                'distance_percent': -1.12
            },
            {
                'label': '2025 Yearly VWAP -1σ',
                'price': 265.00,
                'distance_percent': -2.95
            }
        ]
    }
}
```

---

## Daily VWAP Lifecycle

### Phase 1: Market Open (9:30 AM)
```
Daily VWAP initializes at opening price
First std dev = 0 (no range yet)
First 5-10 bars establish initial volatility
```

### Phase 2: Morning Session (9:30 AM - 12:00 PM)
```
VWAP establishes direction (above/below)
Std dev bands expand as range develops
Algos test bands (+1σ, +2σ or -1σ, -2σ)
Price respects bands as micro S/R
```

### Phase 3: Midday (12:00 PM - 2:00 PM)
```
VWAP often flattens (low volatility)
Price mean reverts toward VWAP
Consolidation between ±0.5σ bands
```

### Phase 4: Afternoon (2:00 PM - 4:00 PM)
```
Final moves toward close
Either extends from VWAP or reverts to it
Close price sets final VWAP value
```

### Phase 5: After Close (4:00 PM)
```
Daily VWAP FREEZES at $273.50
All std dev bands become STATIC
Tomorrow these are ghost levels (percent distance only)
```

---

## Prior Daily Bands as Intraday S/R

### AAPL Example (Nov 13):

**What happened:**
```
Nov 12 Daily VWAP (completed): $273.50
Nov 12 +2σ band: $275.00

Nov 13 Price Action:
├── Open near $275
├── Tested $275.00 (yesterday's +2σ)
├── REJECTED (resistance worked!)
├── Fell to yesterday's +1σ ($274.20)
└── Later flushed to yesterday's -2σ ($271.00)

Yesterday's std dev bands acted as TODAY's S/R
Measured in PERCENT (static levels now)
```

### The Pattern:

**Prior daily VWAP bands are especially strong during:**
1. **First hour of trading** (9:30-10:30 AM)
   - Algos test yesterday's levels immediately
   - Yesterday's +2σ often = today's resistance
   - Yesterday's -2σ often = today's support

2. **Breakdown/Breakout scenarios**
   - Breaking yesterday's +2σ = bullish continuation
   - Breaking yesterday's -2σ = bearish continuation
   - Rejection = mean reversion back to today's VWAP

3. **Confluence with Fib levels**
   - Yesterday's +1σ aligns with 61.8% Fib = strongest level
   - Multiple prior bands align = major zone

---

## Higher Timeframe VWAPs as Targets

### Intraday Trading Context

**Daily VWAP tells you the intraday mean, but higher VWAPs tell you the TREND direction.**

```
Scenario 1: Price Above Quarterly VWAP
├── Daily VWAP: $272.45 (intraday anchor)
├── Quarterly VWAP: $265.00 (below)
└── Analysis: Bullish trend, pullbacks to daily VWAP = buy opportunities

Scenario 2: Price Below Quarterly VWAP
├── Daily VWAP: $272.45 (intraday anchor)
├── Quarterly VWAP: $278.00 (above)
└── Analysis: Bearish trend, rallies to daily VWAP = sell opportunities
```

### Target Calculation

**For intraday traders:**
```
Current: $273.05
Daily VWAP: $272.45 (today's mean)

Upside Targets (Distance from current):
1. Yesterday's VWAP: $273.50 (+0.16%) ← First resistance
2. Yesterday's +1σ: $274.20 (+0.42%) ← Second resistance
3. Quarterly VWAP: $280.50 (+2.73%) ← Major target
4. Quarterly VWAP +1σ: $285.00 (+4.38%) ← Extended target

Downside Targets:
1. Today's VWAP: $272.45 (-0.22%) ← Mean reversion
2. Yesterday's -1σ: $272.80 (-0.09%) ← Support
3. Yearly VWAP: $270.00 (-1.12%) ← Major support
4. Yearly VWAP -1σ: $265.00 (-2.95%) ← Deep support
```

**Intraday traders scale in/out as price moves between these levels.**

---

## Pre-Market Fibonacci Methodology

### Why Pre-Market Matters

**Pre-market establishes the day's volatility expectation:**

```
Small pre-market range ($2.00):
├── Low vol expected
├── Tight Fib levels
└── Scalping environment

Large pre-market range ($8.00):
├── High vol expected
├── Wide Fib levels
└── Swing trading environment
```

### Calculation

**Use the pre-market high/low range:**

```python
def calculate_premarket_fib_grid(premarket_low, premarket_high):
    """
    Calculate Fibonacci retracement/extension levels from pre-market range
    """
    range_size = premarket_high - premarket_low

    fib_levels = {
        # Retracements (from high back down)
        '0%': premarket_low,
        '27%': premarket_low + (range_size * 0.27),
        '50%': premarket_low + (range_size * 0.50),
        '61.8%': premarket_low + (range_size * 0.618),
        '78.6%': premarket_low + (range_size * 0.786),
        '100%': premarket_high,

        # Extensions (beyond high)
        '127.2%': premarket_low + (range_size * 1.272),
        '161.8%': premarket_low + (range_size * 1.618),
        '178.6%': premarket_low + (range_size * 1.786),
        '200%': premarket_low + (range_size * 2.0),
        '227%': premarket_low + (range_size * 2.27),
        '261.8%': premarket_low + (range_size * 2.618)
    }

    return fib_levels
```

### Confluence Detection

**When Fib levels align with VWAP levels:**

```
Example:
├── 61.8% Fib from pre-market: $274.03
├── Yesterday's +1σ: $274.20
├── 2 days ago +2σ: $273.90
└── Range: $0.30 (0.11% spread)

TRIPLE CONFLUENCE = Strongest intraday level
→ Price will test/respect this zone
→ Volume spikes here
→ Decision point for direction
```

---

## Rules for Intraday VWAP Trading

### Rule 1: Daily VWAP Is the Anchor
**Price gravitates toward daily VWAP throughout the session**

- Above VWAP + staying above = bullish
- Below VWAP + staying below = bearish
- Whipsawing across = choppy, avoid

### Rule 2: Prior Daily Bands Are Ghost S/R
**Yesterday's std dev bands act as today's support/resistance**

- Most important: T-1 (yesterday)
- Still relevant: T-2, T-3, T-4, T-5
- Measure distance in PERCENT (static levels)

### Rule 3: Higher Timeframes Set Targets
**Daily moves are bounded by quarterly/yearly VWAPs**

- Above quarterly VWAP = aim for yearly VWAP levels
- Below quarterly VWAP = defend yearly VWAP support
- Major trend changes = breaking yearly VWAP

### Rule 4: Pre-Market Defines the Grid
**Pre-market range creates Fibonacci levels for regular session**

- Large pre-market range = volatile day
- Small pre-market range = tight range day
- Fib levels from pre-market act as intraday magnets

### Rule 5: Confluence = Priority
**When multiple systems align, prioritize those levels**

- VWAP + Fib alignment = strongest
- Prior band + current band alignment = strong
- Random overlap = still relevant but lower priority

---

## Trading Applications

### Intraday Scalping
```
Timeframe: 1-min, 5-min
Reference: Current daily VWAP ±0.27σ, ±0.5σ
Targets: Prior daily bands, Fib levels
Hold time: Minutes
```

### Day Trading
```
Timeframe: 5-min, 15-min
Reference: Current daily VWAP ±1σ, ±2σ
Targets: Higher timeframe VWAPs (quarterly)
Hold time: Hours
```

### Swing Trading (Uses Daily VWAP on Daily Chart)
```
Timeframe: Daily chart
Reference: Quarterly VWAP ±1σ, ±2σ
Targets: Yearly VWAP levels, prior yearly
Hold time: Days to weeks
```

---

## Data Requirements

### For Full Intraday System:

**Historical Data Needed:**
- Last 5 days: Daily OHLCV (for prior daily VWAPs)
- Last 1 year: Daily OHLCV (for yearly/quarterly VWAPs)
- Pre-market data: High/Low before 9:30 AM (for Fib grid)
- Intraday bars: 5-min or 1-min (for current daily VWAP calculation)

**API Considerations:**
- Free Alpha Vantage: Daily data only (no intraday)
- Premium Alpha Vantage: 5-min intraday available
- IEX Cloud / Polygon: Real-time intraday + pre-market data

---

## Key Differences from Higher Timeframes

| Feature | Daily VWAP | Yearly/Quarterly VWAP |
|---------|------------|----------------------|
| Reset frequency | Every day (9:30 AM) | Never (continuous) |
| Volatility context | Single day's range | Months/year of range |
| Prior levels | Ghost S/R for days | Ghost S/R for months/years |
| Distance metric (prior) | Percent | Percent |
| Distance metric (current) | Sigma | Sigma |
| Primary use | Intraday trading | Swing/position trading |
| Time relevance | 1-5 days | Months to years |
| Band spacing | Tight (small std dev) | Wide (large std dev) |
| Target framework | Higher timeframe VWAPs | Multi-year levels |

---

## Advanced: The Opening Range VWAP

**Some traders use "First 30-min VWAP" as a separate level:**

```
Opening Range (9:30-10:00 AM):
├── Calculate VWAP from first 30 minutes
├── This becomes a pivot for the day
├── Above OR30 VWAP = bullish bias
├── Below OR30 VWAP = bearish bias

Compare to Daily VWAP:
├── If OR30 > Daily VWAP → Morning strength
├── If OR30 < Daily VWAP → Morning weakness
```

**This is advanced - not required for basic system.**

---

## Implementation Priority

### Phase 1 (Critical):
- [x] Current daily VWAP calculation
- [ ] Prior daily VWAPs (last 5 days)
- [ ] Prior daily std dev bands as ghost levels
- [ ] Distance in percent for prior dailies

### Phase 2 (Important):
- [ ] Pre-market range detection
- [ ] Fibonacci grid calculation from pre-market
- [ ] Confluence detection (VWAP + Fib + prior bands)

### Phase 3 (Advanced):
- [ ] Intraday bar-by-bar VWAP updates
- [ ] Real-time sigma distance tracking
- [ ] Opening range (OR30) VWAP
- [ ] Volume-weighted confluence scoring

---

## Summary

**Daily VWAPs are unique because:**

1. **They reset daily** - fresh statistical system each market open
2. **They leave ghosts** - each day's VWAP + bands = tomorrow's S/R
3. **They use higher timeframes as targets** - quarterly/yearly VWAPs guide direction
4. **They combine with Fib grids** - pre-market range defines intraday levels
5. **They're short-term** - 1-5 day relevance vs months/years for higher TFs

**For intraday trading, daily VWAP system is THE primary framework.**

**For swing/position trading, daily VWAPs are noise - focus on quarterly/yearly.**

**Know which timeframe you're trading, use the appropriate VWAP reference.**

---

**This methodology must be coded into the engine for proper intraday support.**
