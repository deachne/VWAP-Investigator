# VWAP Distance Methodology

## Critical Distinction: Sigma vs Percent Distance

**This document defines the core measurement methodology for the VWAP Trading Platform.**

---

## The Rule

### Current VWAPs → Sigma Distance
**Use standard deviation (σ) for active/updating VWAPs**

```
Current Year (2025) VWAP: $108.72
Std Dev: $10.48 (current volatility)
Price: $107.25

Distance: -0.140σ ✅ CORRECT
Why: Both price and VWAP exist in the same volatility context
```

### Prior VWAPs → Percent Distance
**Use percentage for completed/static VWAPs**

```
Q3 2025 VWAP (Prior): $117.22 (period ended Sept 30)
Std Dev: $2.50 (Q3's historical volatility)
Price: $107.25 (current, in Q4 volatility)

Distance: -8.50% ✅ CORRECT
NOT: -3.99σ ❌ WRONG (different volatility contexts)
```

---

## Why This Matters

### The Problem with Sigma on Prior VWAPs:

**Prior VWAPs are static price levels** - they don't update, they don't have current volatility context.

**Example:**
```
Q3 2025 (July-Sept):
├── VWAP calculated: $117.22
├── Std Dev during Q3: $2.50
└── Period ended: Sept 30

Q4 2025 (Oct-Dec):
├── Current price: $107.25
├── Current volatility: Different from Q3
└── Using Q3's std dev = meaningless comparison
```

**If you calculate:**
```
($107.25 - $117.22) / $2.50 = -3.99σ
```

**This says**: "Price is -3.99 Q3 standard deviations away"

**Problem**: We're not in Q3 anymore! Q3's volatility was $2.50, but current volatility (Q4) is $10.48. Completely different context.

---

## Current VWAPs: Why Sigma Works

**Active VWAPs update with each bar**, so std dev measures CURRENT volatility:

```
2025 Yearly VWAP (Active):
├── Includes all bars from Jan 1 to today
├── VWAP: $108.72 (updates daily)
├── Std Dev: $10.48 (measures current volatility range)
├── Price: $107.25 (current)
└── Sigma: -0.140σ = meaningful volatility-adjusted position
```

**Sigma tells you**: "Given current year's volatility, price is slightly below mean" (-0.14σ is basically AT the VWAP)

**If volatility was different:**
- Low volatility year (std dev $3): Same $1.47 distance = -0.49σ (more extended)
- High volatility year (std dev $15): Same $1.47 distance = -0.098σ (barely moved)

**Sigma adjusts for volatility. That's why it's useful for current periods.**

---

## Data Structure (Corrected)

```python
{
    'ticker': 'DIS',
    'current_price': 107.25,

    # Current/Active VWAPs (sigma + percent)
    'current_vwaps': {
        'yearly_2025': {
            'vwap': 108.72,
            'std_dev': 10.48,
            'distance': {
                'dollars': -1.47,
                'percent': -1.35,
                'sigma': -0.140  # ✅ Valid (same volatility context)
            }
        },
        'quarterly_q4_2025': {
            'vwap': 112.08,
            'std_dev': 1.42,
            'distance': {
                'dollars': -4.83,
                'percent': -4.31,
                'sigma': -3.402  # ✅ Valid (same volatility context)
            }
        },
        'daily': {
            'vwap': 107.50,
            'std_dev': 0.85,
            'distance': {
                'dollars': -0.25,
                'percent': -0.23,
                'sigma': -0.294  # ✅ Valid (same volatility context)
            }
        }
    },

    # Prior/Completed VWAPs (percent only)
    'prior_vwaps': {
        'quarterly_q3_2025': {
            'vwap': 117.22,
            'period': 'Q3 2025 (July-Sept)',
            'distance': {
                'dollars': -9.97,
                'percent': -8.50  # ✅ Use percent only
                # NO sigma - different volatility context
            }
        },
        'quarterly_q2_2025': {
            'vwap': 102.49,
            'period': 'Q2 2025 (Apr-June)',
            'distance': {
                'dollars': +4.76,
                'percent': +4.64
            }
        },
        'yearly_2024': {
            'vwap': 106.01,
            'period': '2024 (Jan-Dec)',
            'distance': {
                'dollars': +1.24,
                'percent': +1.17
            }
        }
    }
}
```

---

## Display Guidelines

### For Current VWAPs:
```
2025 Yearly VWAP: $108.72
  Distance: -1.35% (-0.140σ)
  Status: AT VWAP (within 0.5σ)
```

### For Prior VWAPs:
```
Prior Levels:
  Q3 2025 VWAP: $117.22 (-8.50%) ← Resistance
  Q1 2025 VWAP: $107.51 (-0.24%) ← CONFLUENCE!
  2024 Yearly: $106.01 (+1.17%) ← Support
```

### For Confluence Detection:
```
Confluence Zone Detected:
├── 2025 Yearly VWAP: $108.72 (-1.35%)
├── Q1 2025 Prior: $107.51 (-0.24%)
├── Daily VWAP: $107.50 (-0.23%)
└── Range: $1.22 (1.14%)

All within 2% = STRONG ZONE
```

---

## Scanner Queries

### Valid Queries (Using Correct Distance Types):

**Current VWAPs:**
```python
# Find stocks at specific sigma levels
"Find stocks at -0.27σ from yearly VWAP"
"Find stocks between +1.0σ and +1.5σ from quarterly VWAP"
"Find stocks at +0.786σ (Fibonacci harmonic)"
```

**Prior VWAPs:**
```python
# Find stocks near prior levels
"Find stocks within 2% of prior quarterly VWAP"
"Find stocks within 5% of 2024 yearly VWAP"
"Find stocks that broke above prior yearly VWAP"
```

**Cross-timeframe:**
```python
# Confluence detection
"Find stocks where price is:
  - Within 0.5σ of current yearly VWAP
  - AND within 2% of prior quarterly VWAP"

→ This catches institutional levels meeting current mean
```

---

## Why This Framework Is Powerful

### 1. Volatility-Adjusted for Current
**Sigma tells you**: "Is this a normal move or extended move?"
```
$5 move on:
├── Low volatility stock (std $2): 2.5σ = EXTREME
└── High volatility stock (std $20): 0.25σ = NORMAL
```

### 2. Universal Comparison for Prior
**Percent tells you**: "How far from that institutional level?"
```
-8.5% from Q3 prior = rejected and sold off
+1.2% from 2024 yearly = bounced and holding
-0.2% from Q1 prior = TESTING the level NOW
```

### 3. Anomaly Detection Works
```
Price at:
├── +0.786σ from yearly (Fibonacci - current context)
└── -8.5% from Q3 prior (rejected - static level)

Both meaningful, different contexts
```

---

## Implementation in Engine

### Current Code (Needs Update):

The engine calculates sigma for everything, which is incorrect for priors.

### Corrected Code:

```python
def get_all_vwaps(self, current_price: Optional[float] = None) -> Dict:
    """Calculate all VWAP types with appropriate distance metrics"""

    # Current VWAPs - use sigma + percent
    for vwap in current_vwaps:
        vwap['distance'] = {
            'percent': calc_percent(current_price, vwap['vwap']),
            'sigma': calc_sigma(current_price, vwap['vwap'], vwap['std_dev'])
        }

    # Prior VWAPs - use percent only (no sigma)
    for vwap in prior_vwaps:
        vwap['distance'] = {
            'percent': calc_percent(current_price, vwap['vwap'])
            # NO sigma - different volatility context
        }
```

---

## Summary

| VWAP Type | Distance Metric | Why |
|-----------|----------------|-----|
| Current Yearly | Sigma + Percent | Active, updating, same volatility context |
| Current Quarterly | Sigma + Percent | Active, updating, same volatility context |
| Daily VWAP | Sigma + Percent | Active, updating, same volatility context |
| Prior Quarterly | Percent only | Static level, old volatility context |
| Prior Yearly | Percent only | Static level, old volatility context |

---

## Key Insight

**Prior VWAPs are like trend lines or Fibonacci levels:**
- They're historical reference points
- Institutions remember them
- They act as S/R in PRICE terms
- Percent distance is clear, universal, comparable

**Current VWAPs are statistical systems:**
- They update with market
- Sigma shows volatility-adjusted position
- Tells you if move is "normal" or "extended"

**Use the right measurement for the right level.**

---

**This methodology is now the foundation for:**
- Display formatting
- Confluence detection
- Scanner algorithms
- Anomaly discovery

**Reference this document when building any VWAP-based feature.**
