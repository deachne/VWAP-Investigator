---
description: Run VWAP analysis on a ticker using the production engine
---

Analyze the ticker symbol provided using the VWAP calculation engine in this repository.

## Instructions:

1. Use the `vwap_engine.py` file in this repository
2. Get the Alpha Vantage API key from the `.env` file
3. Run analysis with the VWAPEngine class
4. Show EXACT sigma values (e.g., 0.757σ, not "close to 1.0σ")

## Display Format:

```
[TICKER] Analysis - Current Price: $XXX

Current Year VWAP:
  VWAP: $XXX.XX
  Std Dev: $XX.XX
  Distance: XX.XX%
  Sigma: X.XXXσ ← EXACT value
  Closest Magnet: X.XXσ

Current Quarter VWAP:
  VWAP: $XXX.XX
  Std Dev: $XX.XX
  Distance: XX.XX%
  Sigma: X.XXXσ

Prior Quarterly VWAPs (Ghost Levels):
  Q3 2025: $XXX.XX (±X.XX% from current)
  Q2 2025: $XXX.XX
  Q1 2025: $XXX.XX
  Q4 2024: $XXX.XX

Prior Yearly VWAPs:
  2024: $XXX.XX
  2023: $XXX.XX
  2022: $XXX.XX

Key Standard Deviation Bands:
  +2.0σ: $XXX.XX
  +1.27σ: $XXX.XX
  +1.0σ: $XXX.XX
  +0.27σ: $XXX.XX
  VWAP: $XXX.XX ← Anchor
  -0.27σ: $XXX.XX
  -1.0σ: $XXX.XX
  -2.0σ: $XXX.XX
```

## Important Notes:

- Show PRECISE sigma values (3 decimal places)
- Include ALL prior period VWAPs (they act as ghost S/R levels)
- Calculate distance to nearest magnet level
- Don't round sigma values - exact readings reveal anomalies
- Prior quarterly and yearly VWAPs are critical for identifying institutional levels

## Example Usage:

```
/vwap DIS
/vwap INTC 37.89
/vwap CORN
```

If a price is provided after the ticker, use that instead of current market price.
