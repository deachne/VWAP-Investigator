# VWAP Trading Platform Documentation

## Documentation Index

### Architecture & Planning
- **[Platform Merge Plan](PLATFORM-MERGE-PLAN.md)** - Complete architecture, roadmap, and integration strategy
- **[Original Vision](ORIGINAL-VISION.md)** - Initial brainstorming and feature roadmap
- **[BizzyForge Integration](BIZZYFORGE-INTEGRATION.md)** - Separation strategy and API integration

### Core Methodology (READ THIS FIRST)
- **[VWAP Distance Methodology](VWAP-DISTANCE-METHODOLOGY.md)** - Critical: Sigma vs Percent distance rules

### Getting Started
- **[Installation Guide](../README.md)** - Quick setup and running the app
- **[Run Engine Guide](RUN-ENGINE.md)** - How to run VWAP calculations (command line, Claude sessions, slash commands)
- **Technical Requirements** - Python 3.8+, Alpha Vantage API key

### Core Features (Current)
- Multi-timeframe VWAP calculations (Yearly, Quarterly, 3-Month, Daily)
- 27% magnet level detection
- Pattern recognition (unbroken priors, confluences, reclaims)
- AI-weighted level scoring
- Trade annotation system (good/bad/neutral ratings)
- Export to CSV

### Planned Features
- Standard deviation bands (1σ, 2σ, 3σ)
- Prior period VWAPs
- Outcome tracking & validation
- Backtesting engine
- Market scanner (10k+ tickers)
- LLM-powered intelligence

### Technical Documentation
- VWAP Calculation Engine (coming soon)
- Pattern Detection System (coming soon)
- AI Scoring Algorithm (coming soon)
- Database Schema (coming soon)

---

## Quick Links

**Current Status:** Prototype phase
**Next Milestone:** Phase 1 - Foundation (restructure + missing features)
**Integration:** Separate from BizzyForge, shared Supabase database

See [Platform Merge Plan](PLATFORM-MERGE-PLAN.md) for complete roadmap.
