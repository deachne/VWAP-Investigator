# BizzyForge Integration Strategy

## Relationship Between Projects

**VWAP Trading Platform** and **BizzyForge** are **separate repositories** with **shared data integration**.

### Why Separate Repos?

1. **Different purposes:**
   - BizzyForge = Farm operations intelligence
   - VWAP Platform = Commodity trading intelligence

2. **Documentation clarity:**
   - Each has its own focused docs (no confusion)
   - BizzyForge has 40+ doc files (farm-focused)
   - VWAP has trading-focused docs

3. **Independent development:**
   - Can iterate rapidly without breaking farm system
   - Different release cycles
   - Can showcase to different audiences

4. **Clean architecture:**
   - Microservices approach (industry standard)
   - Loosely coupled via API
   - Share data, not code

---

## How They Connect

### Shared Database (Supabase)

Both projects use the same Supabase instance:

```sql
-- Shared tables
users (id, name, email, farm_location)
crops (id, user_id, crop_type, acres, planting_date)
harvests (id, crop_id, bushels, harvest_date)
commodities (id, symbol, crop_type)

-- VWAP-specific tables
vwap_levels (id, commodity_id, timeframe, value, timestamp)
trade_annotations (id, user_id, commodity_id, rating, notes, patterns)
validated_patterns (id, user_id, pattern_name, win_rate, trades_count)

-- BizzyForge-specific tables
field_operations (id, user_id, field_id, operation_type, date)
equipment (id, user_id, equipment_type, status)
```

### API Communication

**BizzyForge → VWAP Platform:**
```typescript
// In BizzyForge: src/lib/integrations/vwap-api.ts
export async function getMarketRecommendation(crop: string, acres: number) {
  const response = await fetch('https://vwap-api.example.com/api/recommend', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${VWAP_API_KEY}` },
    body: JSON.stringify({ crop, acres, user_id: currentUser.id })
  });
  return response.json();
}

// Usage in farm capture:
const capture = "Planted 500 acres canola today";
const recommendation = await getMarketRecommendation('canola', 500);
// Returns: {
//   commodity: 'CANOLA',
//   current_price: 12.45,
//   vwap_level: 'quarterly_support',
//   recommendation: 'Consider hedging 40% of expected yield',
//   confidence: 0.89
// }
```

**VWAP Platform → BizzyForge Database:**
```python
# In VWAP Platform: backend/data/farm_context.py
from supabase import create_client

def get_user_farm_context(user_id: str):
    """Query BizzyForge data for farm context"""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Get crops user grows
    crops = supabase.table('crops')\
        .select('crop_type, acres')\
        .eq('user_id', user_id)\
        .execute()

    return {
        'crops_grown': [c['crop_type'] for c in crops.data],
        'total_acres': sum(c['acres'] for c in crops.data)
    }

# Used in morning brief:
context = get_user_farm_context(user.id)
# Returns: {
//   'crops_grown': ['canola', 'wheat', 'barley'],
//   'total_acres': 2400
// }
# Brief prioritizes CANOLA, WHEAT commodity scans
```

---

## Integration Examples

### Example 1: Planting Decision
```
User in BizzyForge: "Planted 500 acres canola"

BizzyForge:
├── Records in farm database
├── Calls VWAP API: getMarketRecommendation('canola', 500)
└── VWAP responds:
    ├── CANOLA @ $12.45 (quarterly VWAP support)
    ├── Pattern: 89% win rate over 7 days
    └── Recommendation: "Consider hedging 40% (200 acres × 35 bu/acre = 7,000 bu)"

BizzyForge displays:
"✅ Planting recorded
 💡 Market Insight: CANOLA at strong support ($12.45). Consider hedging 7,000 bushels."
```

### Example 2: Harvest Timing
```
User in BizzyForge: "Canola ready to harvest - 600 bu/acre"

BizzyForge:
├── Calculates: 500 acres × 600 bu = 300,000 bu
├── Calls VWAP API: getCurrentSetup('CANOLA')
└── VWAP responds:
    ├── CANOLA @ $13.20 (3-VWAP confluence)
    ├── Pattern: 85% win rate, target $13.80 in 8 days
    └── Recommendation: "Strong sell zone. Consider harvesting now."

BizzyForge displays:
"🌾 Harvest Status: Ready (300,000 bu)
 💰 Market: At confluence zone ($13.20). Pattern suggests $13.80 target.
 💡 Recommendation: Harvest + lock prices now, or wait 8 days for 60¢ upside."
```

### Example 3: Input Cost Optimization
```
User in BizzyForge: Opens spring budget planning

BizzyForge:
├── Sees: "Need fertilizer for 2,400 acres"
├── Calls VWAP API: getCurrentSetup('CF') // CF = fertilizer stock
└── VWAP responds:
    ├── CF @ $82 (falling toward $78 yearly VWAP)
    ├── Pattern: Wait 14 days for support
    └── Recommendation: "Delay purchase 2 weeks, save ~$12,000"

BizzyForge displays:
"📊 Input Costs:
 Fertilizer: $82/bag (trending down)
 💡 Wait 14 days - potential $12K savings at $78 support level"
```

---

## Development Workflow

### Both Repos Run Independently:

**Terminal 1 - BizzyForge:**
```bash
cd ~/BizzyForge
npm run dev
# Runs on localhost:3000
```

**Terminal 2 - VWAP Platform:**
```bash
cd ~/Desktop/vwap-validator
python app.py
# Runs on localhost:5001
```

**Local Testing:**
```typescript
// In BizzyForge .env.local
VWAP_API_URL=http://localhost:5001
VWAP_API_KEY=dev_key_123
```

### Production Deployment:

**Separate deployments:**
- BizzyForge: Vercel or Railway (Next.js app)
- VWAP Platform: Fly.io or Railway (Python FastAPI)
- Shared: Supabase (both connect to same instance)

**Environment variables:**
```bash
# BizzyForge production .env
VWAP_API_URL=https://vwap-api.yourdomain.com
VWAP_API_KEY=prod_secure_key_xyz

# VWAP Platform production .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
ALLOWED_ORIGINS=https://bizzyforge.com
```

---

## API Endpoints (VWAP → BizzyForge)

### `/api/recommend`
Get market recommendation for a crop.

**Request:**
```json
{
  "crop": "canola",
  "acres": 500,
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "commodity": "CANOLA",
  "current_price": 12.45,
  "vwap_level": "quarterly_support",
  "pattern": "unbroken_prior",
  "confidence": 0.89,
  "recommendation": "Consider hedging 40% of expected yield",
  "target_price": 13.20,
  "estimated_days": 7
}
```

### `/api/setup/{symbol}`
Get current VWAP setup for a commodity.

**Response:**
```json
{
  "symbol": "CANOLA",
  "price": 12.45,
  "vwaps": {
    "yearly": 11.80,
    "quarterly": 12.40,
    "three_month": 12.55,
    "daily": 12.48
  },
  "patterns": ["quarterly_support", "confluence"],
  "score": 94
}
```

### `/api/scan`
Get today's top commodity setups.

**Response:**
```json
{
  "date": "2025-11-13",
  "top_setups": [
    {
      "symbol": "CORN",
      "price": 4.23,
      "score": 97,
      "pattern": "unbroken_prior",
      "similarity_to_user_wins": 0.94
    }
  ]
}
```

---

## Security

**API Authentication:**
```python
# VWAP Platform: backend/api/auth.py
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in ALLOWED_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
```

**Database Security:**
- VWAP Platform uses Supabase service role key (full access)
- BizzyForge uses user-scoped RLS policies
- Shared data only: users, crops, commodities
- Private data stays separate

---

## Migration Path (If Needed Later)

If tight integration becomes critical, can migrate to monorepo:

```
farm-intelligence-platform/
├── apps/
│   ├── bizzyforge/        # Farm operations
│   └── vwap-trading/      # Commodity trading
├── packages/
│   ├── shared-db/         # Shared Supabase client
│   ├── shared-types/      # TypeScript types
│   └── shared-ui/         # Common components
└── docs/
```

**But current approach (separate repos, shared data) is industry standard and sufficient.**

---

## Summary

✅ **Separate repos** = Clean docs, independent development
✅ **Shared Supabase** = Data integration without code coupling
✅ **API communication** = Loosely coupled microservices
✅ **BizzyForge calls VWAP** = Market intelligence in farm context
✅ **VWAP queries farm data** = Personalized recommendations

**No code in BizzyForge repo related to VWAP calculations. No farm operations code in VWAP repo. Clean separation, powerful integration.**
