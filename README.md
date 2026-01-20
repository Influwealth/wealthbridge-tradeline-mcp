# WealthBridge Tradeline MCP

**Universal Business Tradeline Management & Credit Profiling System**  
Sovereign credit engine for InfluWealth Consult LLC

---

## Overview

WealthBridge Tradeline MCP is a **complete business credit infrastructure** that enables:

1. **Tradeline Management** - Create, track, and report business credit accounts
2. **Credit Scoring** - Proprietary algorithm (0-100 scale)
3. **Bureau Reporting** - Auto-submit to Experian, Equifax, D&B
4. **Federal Integration** - Links with SAM.gov entity data
5. **Vendor Credit Programs** - Manage supplier trade credit
6. **Payment Tracking** - Record and analyze payment performance

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Influwealth/wealthbridge-tradeline-mcp.git
cd wealthbridge-tradeline-mcp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add your API keys

# Test
python cli.py test
```

### CLI Commands

```bash
python cli.py test                  # Test system
python cli.py score BIZ001          # Calculate credit score
python cli.py report BIZ001         # Generate credit report
python cli.py create-tradeline      # Create new tradeline (interactive)
python cli.py list-tradelines BIZ001  # List tradelines
```

---

## Scoring Algorithm

**WealthBridge Score (0-100):**

| Component | Weight |
|-----------|--------|
| Payment History | 35% |
| Credit Utilization | 30% |
| Credit Age | 15% |
| Credit Mix | 10% |
| New Credit | 10% |

**Interpretation:**

- 90-100: Excellent (A)
- 80-89: Very Good (B+)
- 70-79: Good (B)
- 60-69: Fair (C)
- Below 60: Poor (D)

---

## Architecture

```
wealthbridge-tradeline-mcp/
├── config.py              # Central configuration
├── cli.py                 # Command-line interface
├── models/
│   └── tradeline.py       # Data models (Tradeline, Business, etc.)
├── engine/
│   ├── scoring.py         # Proprietary scoring algorithm
│   └── reporter.py        # Bureau reporting (Metro 2)
└── requirements.txt       # Python dependencies
```

---

## License

Proprietary - Copyright © 2025 InfluWealth Consult LLC  
All rights reserved.

---

**Built by InfluWealth Consult LLC**  
Sovereign automation systems for modern enterprise.
