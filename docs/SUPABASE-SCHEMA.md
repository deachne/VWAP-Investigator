# Supabase Database Schema for VWAP Platform

## Overview

**All VWAP platform data lives in BizzyForge's Supabase instance.**

This allows:
- ✅ Single source of truth for all trading/farm data
- ✅ BizzyForge can query VWAP data for recommendations
- ✅ VWAP platform can query farm context (crops, commodities)
- ✅ One database to manage/backup/secure

---

## Table Structure

### Core VWAP Tables

#### `vwap_calculations`
Stores calculated VWAP values for reference and caching.

```sql
CREATE TABLE vwap_calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT NOT NULL,
    timeframe TEXT NOT NULL, -- 'yearly_2025', 'quarterly_q4_2025', 'daily_2025-11-13'
    vwap DECIMAL(10, 4) NOT NULL,
    std_dev DECIMAL(10, 4) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    is_prior BOOLEAN DEFAULT FALSE, -- TRUE if completed period (static)
    num_bars INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(ticker, timeframe, start_date)
);

-- Index for fast lookups
CREATE INDEX idx_vwap_ticker_timeframe ON vwap_calculations(ticker, timeframe);
CREATE INDEX idx_vwap_current ON vwap_calculations(ticker, is_prior) WHERE is_prior = FALSE;
```

#### `sigma_bands`
Pre-calculated sigma band levels for quick reference.

```sql
CREATE TABLE sigma_bands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vwap_calculation_id UUID REFERENCES vwap_calculations(id),
    sigma_level DECIMAL(6, 3) NOT NULL, -- 0.270, 1.270, 2.270, 2.618, etc.
    band_price DECIMAL(10, 4) NOT NULL,
    direction TEXT CHECK(direction IN ('above', 'below')),

    UNIQUE(vwap_calculation_id, sigma_level, direction)
);
```

---

### Pattern Discovery Tables

#### `discovered_patterns`
User-discovered patterns from chart annotations.

```sql
CREATE TABLE discovered_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    pattern_name TEXT NOT NULL, -- Auto-generated or user-named
    discovered_date TIMESTAMP DEFAULT NOW(),

    -- Original observation
    marked_ticker TEXT NOT NULL,
    marked_date TIMESTAMP NOT NULL,
    marked_price DECIMAL(10, 4) NOT NULL,
    marked_timeframe TEXT, -- '5min', '1hour', 'daily'

    -- Captured configuration (JSON)
    vwap_config JSONB NOT NULL,
    /* Example:
    {
        "yearly_sigma": -0.273,
        "quarterly_sigma": +0.045,
        "daily_sigma": -0.012,
        "confluences": [
            {"type": "triple", "levels": ["Q4_VWAP", "Daily_VWAP", "Fib_61.8"]}
        ],
        "volume_ratio": 2.3,
        "time_of_day": "first_hour",
        "pattern_type": "bounce",
        "market_regime": "trending"
    }
    */

    -- User input
    user_notes TEXT,
    user_observation TEXT, -- "Price keeps bouncing here"

    -- Validation status
    status TEXT CHECK(status IN ('discovered', 'testing', 'validated', 'discarded')) DEFAULT 'discovered',
    validation_date TIMESTAMP,

    -- Statistics (populated after validation)
    total_instances INTEGER,
    win_rate DECIMAL(5, 2), -- 89.40
    avg_move_pct DECIMAL(6, 2), -- 5.20
    avg_bars DECIMAL(6, 2), -- 6.8
    r_r_ratio DECIMAL(6, 2), -- 2.76
    sharpe_ratio DECIMAL(6, 2),

    -- Best conditions (JSON)
    best_conditions JSONB,
    /* Example:
    {
        "sectors": {"tech": 0.94, "agriculture": 1.00},
        "regime": {"trending": 0.949, "ranging": 0.625},
        "volume": {"above_2x": 0.95, "below_2x": 0.57},
        "time": {"first_hour": 0.96, "midday": 0.778}
    }
    */

    -- Scanner settings
    scanner_enabled BOOLEAN DEFAULT FALSE,
    scanner_priority INTEGER DEFAULT 50, -- 1-100, higher = scan first

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_patterns_user ON discovered_patterns(user_id);
CREATE INDEX idx_patterns_status ON discovered_patterns(status);
CREATE INDEX idx_patterns_scanner ON discovered_patterns(scanner_enabled, scanner_priority);
```

#### `pattern_instances`
Historical instances of each discovered pattern.

```sql
CREATE TABLE pattern_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_id UUID REFERENCES discovered_patterns(id) NOT NULL,

    ticker TEXT NOT NULL,
    date TIMESTAMP NOT NULL,
    entry_price DECIMAL(10, 4) NOT NULL,

    -- Configuration match
    similarity_score DECIMAL(5, 2), -- 85.0 to 100.0
    vwap_config JSONB, -- Config at this instance

    -- Outcome measurement (lookforward 20 bars)
    outcome TEXT CHECK(outcome IN ('win', 'loss', 'neutral')),
    close_return_pct DECIMAL(6, 2), -- +5.80 or -2.10
    bars_to_high INTEGER,
    bars_to_low INTEGER,
    max_favorable_excursion DECIMAL(6, 2), -- MFE
    max_adverse_excursion DECIMAL(6, 2), -- MAE

    -- Context
    sector TEXT,
    market_regime TEXT,
    volume_ratio DECIMAL(6, 2),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_instances_pattern ON pattern_instances(pattern_id);
CREATE INDEX idx_instances_ticker ON pattern_instances(ticker);
CREATE INDEX idx_instances_outcome ON pattern_instances(outcome);
```

---

### Trade Tracking Tables

#### `trade_annotations`
Manual annotations of setups (validator Phase 1).

```sql
CREATE TABLE trade_annotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,

    ticker TEXT NOT NULL,
    entry_date TIMESTAMP NOT NULL,
    entry_price DECIMAL(10, 4) NOT NULL,
    current_price DECIMAL(10, 4),

    -- User rating
    rating TEXT CHECK(rating IN ('good', 'bad', 'neutral')),
    notes TEXT,
    source TEXT, -- 'youtube', 'discord', 'self', etc.

    -- VWAP data snapshot
    vwap_snapshot JSONB, -- All VWAPs at time of annotation
    patterns_detected JSONB, -- Patterns present at annotation

    -- Outcome tracking (populated later)
    outcome TEXT CHECK(outcome IN ('win', 'loss', 'pending')),
    exit_price DECIMAL(10, 4),
    exit_date TIMESTAMP,
    return_pct DECIMAL(6, 2),
    bars_held INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_annotations_user ON trade_annotations(user_id);
CREATE INDEX idx_annotations_ticker ON trade_annotations(ticker);
CREATE INDEX idx_annotations_rating ON trade_annotations(rating);
```

#### `active_positions`
Current open positions for tracking.

```sql
CREATE TABLE active_positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,

    ticker TEXT NOT NULL,
    entry_date TIMESTAMP NOT NULL,
    entry_price DECIMAL(10, 4) NOT NULL,
    quantity DECIMAL(12, 4), -- Optional: number of shares

    -- Pattern that triggered entry
    pattern_id UUID REFERENCES discovered_patterns(id),
    entry_sigma DECIMAL(6, 3), -- Sigma at entry

    -- Targets and stops
    target_price DECIMAL(10, 4),
    stop_price DECIMAL(10, 4),

    -- Current status (updated daily)
    current_price DECIMAL(10, 4),
    current_sigma DECIMAL(6, 3),
    current_return_pct DECIMAL(6, 2),
    bars_held INTEGER,
    last_updated TIMESTAMP DEFAULT NOW(),

    -- Exit (when closed)
    exit_date TIMESTAMP,
    exit_price DECIMAL(10, 4),
    exit_reason TEXT, -- 'target_hit', 'stop_hit', 'manual', 'time_exit'

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_positions_user_active ON active_positions(user_id, is_active);
CREATE INDEX idx_positions_ticker ON active_positions(ticker);
```

---

### Scanner Tables

#### `scanner_signals`
Daily scanner results for validated patterns.

```sql
CREATE TABLE scanner_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_id UUID REFERENCES discovered_patterns(id) NOT NULL,

    scan_date DATE NOT NULL,
    ticker TEXT NOT NULL,
    signal_price DECIMAL(10, 4) NOT NULL,

    -- Match quality
    similarity_score DECIMAL(5, 2),
    vwap_config JSONB, -- Config at signal

    -- Alert status
    alerted BOOLEAN DEFAULT FALSE,
    alert_sent_at TIMESTAMP,

    -- User action
    user_viewed BOOLEAN DEFAULT FALSE,
    user_action TEXT CHECK(user_action IN ('traded', 'watchlist', 'ignored', null)),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_signals_pattern_date ON scanner_signals(pattern_id, scan_date);
CREATE INDEX idx_signals_unalerted ON scanner_signals(alerted, scan_date) WHERE alerted = FALSE;
CREATE INDEX idx_signals_user_action ON scanner_signals(user_action);
```

---

### Shared Tables (With BizzyForge)

#### `users` (Already exists in BizzyForge)
```sql
-- Use BizzyForge's existing users table
-- No changes needed
```

#### `commodities` (Shared reference)
```sql
CREATE TABLE commodities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol TEXT UNIQUE NOT NULL, -- 'CORN', 'WHEAT', 'CANOLA'
    name TEXT NOT NULL,
    crop_type TEXT, -- Links to BizzyForge crops
    exchange TEXT,
    sector TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `crops` (BizzyForge table - read-only for VWAP)
```sql
-- Existing BizzyForge table
-- VWAP platform reads this for farm context
-- Example: User grows canola → prioritize CANOLA commodity scans
```

---

## Using BizzyForge's Supabase Instance

### Answer to Your Questions:

**1. Do docs mention using BizzyForge database?**
- ✅ YES - mentioned in BIZZYFORGE-INTEGRATION.md
- ⚠️ But schema not fully detailed (until now)

**2. Can you save all VWAP work to it?**
- ✅ YES - absolutely! This is the recommended approach
- All pattern discoveries, validations, testing, signals → Supabase
- Currently you're using SQLite (`trades.db`) → should migrate to Supabase

---

## Benefits of Using BizzyForge's Supabase:

### 1. **Single Source of Truth**
```
One database for everything:
├── Farm operations (BizzyForge)
├── Trading patterns (VWAP platform)
├── Commodity data (shared)
└── User data (shared)

No syncing needed, always in sync
```

### 2. **Integration Ready**
```
BizzyForge can query:
├── Your validated VWAP patterns
├── Current commodity signals
├── "Recommend hedge timing for canola"
└── Uses VWAP platform data directly

VWAP platform can query:
├── Crops you grow (canola, wheat)
├── "Prioritize CORN, WHEAT in scanner"
└── Uses BizzyForge farm context
```

### 3. **Better Infrastructure**
```
Supabase vs SQLite:
├── ✅ Real-time subscriptions (live updates)
├── ✅ Built-in auth (already configured)
├── ✅ API auto-generated (REST + GraphQL)
├── ✅ Automatic backups
├── ✅ Scalable (millions of rows)
└── ✅ Web accessible (query from anywhere)
```

### 4. **One Deployment**
```
Both apps connect to:
├── Same Supabase URL
├── Same API keys
└── Same database

No separate database to manage
```

---

## Migration Plan:

### Current State:
```
~/Desktop/vwap-validator/
└── trades.db (SQLite - local only)
    ├── Trade annotations
    └── Statistics
```

### Target State:
```
BizzyForge Supabase:
├── discovered_patterns table
├── pattern_instances table
├── trade_annotations table
├── active_positions table
├── scanner_signals table
└── Shared: users, commodities, crops
```

### Migration Steps:

**1. Use BizzyForge's existing Supabase project**
```bash
# In vwap-validator .env:
SUPABASE_URL=https://your-bizzyforge-project.supabase.co
SUPABASE_KEY=your_service_role_key
```

**2. Create VWAP tables (SQL migration)**
```sql
-- Run these in BizzyForge Supabase SQL editor
-- Creates all VWAP-specific tables
-- Doesn't touch BizzyForge tables
```

**3. Update code to use Supabase instead of SQLite**
```python
# Replace database.py (SQLite)
# With: supabase_client.py (Supabase)

from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Save pattern
supabase.table('discovered_patterns').insert({...}).execute()
```

---

## Recommended Approach:

**Yes, use BizzyForge's Supabase for VWAP platform:**

✅ **Pros:**
- Already set up and configured
- Integration is trivial (same database)
- Farm context automatically available
- One system to manage

❌ **Cons:**
- None really - this is the smart architecture

**You can save:**
- All pattern discoveries
- All validations and testing
- All scanner results
- All trade annotations
- Everything

**It's all in one place, accessible to both BizzyForge and VWAP platform.**

---

**Want me to:**

**A)** Create the SQL migration file to add VWAP tables to BizzyForge Supabase?

**B)** Update the integration docs with this schema detail?

**C)** Just keep SQLite for now, migrate to Supabase later?

**My recommendation: A - create the migration now so it's ready when you build the frontend.**