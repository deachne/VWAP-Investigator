from vwap_engine import VWAPEngine
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

engine = VWAPEngine('FXC', api_key)
result = engine.get_all_vwaps()

print(f"\n{'='*80}")
print(f"FXC (Canadian Dollar ETF) - USD→CAD Conversion Timing Analysis")
print(f"{'='*80}\n")

print(f"Current Price: ${result['current_price']:.2f}\n")

# Current yearly
yearly = result['vwaps']['current_yearly']
print(f"2025 Yearly VWAP: ${yearly['vwap']:.2f}")
print(f"  Std Dev: ${yearly['std_dev']:.2f}")
print(f"  Current Distance: {yearly['distance']['percent_distance']:+.2f}%")
print(f"  Sigma Distance: {yearly['distance']['sigma_distance']:+.3f}σ")
print(f"  Closest Level: {yearly['distance']['closest_level']:.3f}σ")

# Calculate key levels
print(f"\n  Key Sigma Levels (Yearly):")
for sigma in [2.618, 2.27, 2.0, 1.618, 1.27, 1.0, 0.5, 0.27]:
    level_up = yearly['vwap'] + (sigma * yearly['std_dev'])
    level_down = yearly['vwap'] - (sigma * yearly['std_dev'])
    print(f"    +{sigma}σ: ${level_up:.2f} | -{sigma}σ: ${level_down:.2f}")

print(f"\n{'─'*80}\n")

# Current quarterly
quarterly = result['vwaps']['current_quarterly']
print(f"Q4 2025 VWAP: ${quarterly['vwap']:.2f}")
print(f"  Std Dev: ${quarterly['std_dev']:.2f}")
print(f"  Current Distance: {quarterly['distance']['percent_distance']:+.2f}%")
print(f"  Sigma Distance: {quarterly['distance']['sigma_distance']:+.3f}σ")
print(f"  Closest Level: {quarterly['distance']['closest_level']:.3f}σ\n")

# Prior quarterly VWAPs
print(f"Prior Quarterly VWAPs (Resistance/Support):")
for prior in result['vwaps']['prior_quarterly']:
    dist_pct = ((result['current_price'] - prior['vwap']) / prior['vwap']) * 100
    print(f"  {prior['label']}: ${prior['vwap']:.2f} ({dist_pct:+.2f}%)")

print(f"\n{'─'*80}\n")

# Prior yearly VWAPs
print(f"Prior Yearly VWAPs (Ghost Levels):")
for prior in result['vwaps']['prior_yearly']:
    dist_pct = ((result['current_price'] - prior['vwap']) / prior['vwap']) * 100
    print(f"  {prior['label']}: ${prior['vwap']:.2f} ({dist_pct:+.2f}%)")

# Trading recommendation
print(f"\n{'='*80}")
print(f"💱 USD → CAD Conversion Timing Recommendation:")
print(f"{'='*80}\n")

sigma = yearly['distance']['sigma_distance']

if sigma < -0.5:
    print("✅ GOOD TIME TO CONVERT (FXC oversold)")
    print(f"   Current: {sigma:.3f}σ below yearly VWAP")
    print(f"   Expected: Bounce back to VWAP (+{abs(yearly['distance']['percent_distance']):.1f}% upside)")
    print(f"   Strategy: Convert now, CAD is cheap relative to USD")
elif sigma > 0.5:
    print("⏸ WAIT (FXC extended above VWAP)")
    print(f"   Current: {sigma:.3f}σ above yearly VWAP")
    print(f"   Expected: Revert to VWAP ({abs(yearly['distance']['percent_distance']):.1f}% downside)")
    print(f"   Strategy: Wait for pullback to VWAP or -0.27σ")
else:
    print("💡 NEUTRAL ZONE (Near VWAP)")
    print(f"   Current: {sigma:.3f}σ from yearly VWAP")
    print(f"   Strategy: Fair value - convert if needed, or wait for -0.27σ for better rate")

print(f"\n{'='*80}\n")

